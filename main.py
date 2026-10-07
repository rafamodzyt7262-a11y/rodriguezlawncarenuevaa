"""
RODRIGUEZ LAWNCARE - 24/7 UNIFIED CLOUD SERVER & DISCORD BOT
Runs 24/7 on Railway / Cloud hosting:
1. High-Performance Web Server (serving website & live gallery without cache lags)
2. Live Discord Bot (Upload, delete, and check photos from mobile/Discord)
3. Real-Time Activity Logger in Discord Channel
"""

import os
import sys
import json
import time
import asyncio
import aiohttp
from aiohttp import web
import discord
from discord import app_commands
from discord.ext import commands

# Fix Windows console UTF-8 encoding
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

# ----------------- CONFIGURATION & SECRETS -----------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ENV_FILE = os.path.join(BASE_DIR, ".env")

def get_env_var(key, default=""):
    val = os.environ.get(key)
    if val:
        return val
    if os.path.exists(ENV_FILE):
        try:
            with open(ENV_FILE, "r", encoding="utf-8") as f:
                for line in f:
                    if line.strip().startswith(f"{key}="):
                        return line.strip().split("=", 1)[1].strip('"').strip("'")
        except Exception:
            pass
    return default

APP_ID = int(get_env_var("APP_ID", "1557276640650723393"))
BOT_TOKEN = get_env_var("BOT_TOKEN", "")
SERVER_ID = int(get_env_var("SERVER_ID", "1538269421020258304"))
CHANNEL_ID = int(get_env_var("CHANNEL_ID", "1557277046491578379"))
PORT = int(get_env_var("PORT", "8080"))

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
GALLERY_JSON_PATH = os.path.join(BASE_DIR, "gallery.json")
GALLERY_FOLDER = os.path.join(BASE_DIR, "assets", "gallery")

THREE_DAYS_MS = 3 * 24 * 60 * 60 * 1000

os.makedirs(GALLERY_FOLDER, exist_ok=True)

# ----------------- DATABASE HELPERS -----------------
def load_gallery():
    if not os.path.exists(GALLERY_JSON_PATH):
        return []
    try:
        with open(GALLERY_JSON_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"[Error] Cargando gallery.json: {e}")
        return []

def save_gallery(data):
    try:
        with open(GALLERY_JSON_PATH, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        return True
    except Exception as e:
        print(f"[Error] Guardando gallery.json: {e}")
        return False

def get_next_id(gallery):
    if not gallery:
        return 1
    return max(item.get("id", 0) for item in gallery) + 1


# ----------------- DISCORD LOGGING HELPER -----------------
async def send_discord_log(bot_instance, title: str, description: str, color=discord.Color.blue(), image_url=None):
    """Sends a real-time activity log directly to the Discord channel."""
    try:
        channel = bot_instance.get_channel(CHANNEL_ID)
        if not channel:
            return
        embed = discord.Embed(
            title=title,
            description=description,
            color=color,
            timestamp=discord.utils.utcnow()
        )
        embed.set_footer(text="Rodriguez LawnCare • Sistema en Vivo 24/7")
        if image_url:
            embed.set_image(url=image_url)
        await channel.send(embed=embed)
    except Exception as e:
        print(f"[Error enviando log a Discord]: {e}")


# ----------------- DISCORD UI VIEWS & MENUS -----------------
class DeleteSelect(discord.ui.Select):
    def __init__(self, gallery, bot_ref):
        self.bot_ref = bot_ref
        options = []
        for item in gallery[-25:]:
            now = int(time.time() * 1000)
            is_new = (now - item.get("uploaded_at", 0)) < THREE_DAYS_MS
            status_text = "NEW" if is_new else "Normal"
            title_preview = item.get('title', 'Trabajo')[:45]
            options.append(
                discord.SelectOption(
                    label=f"Foto #{item['id']} ({status_text})",
                    description=title_preview,
                    value=str(item["id"]),
                    emoji="🗑️"
                )
            )
        super().__init__(
            placeholder="Selecciona el número de la foto a eliminar...",
            min_values=1,
            max_values=1,
            options=options
        )

    async def callback(self, interaction: discord.Interaction):
        photo_id = int(self.values[0])
        gallery = load_gallery()
        found_item = next((item for item in gallery if item.get("id") == photo_id), None)

        if not found_item:
            await interaction.response.send_message(f"❌ La foto #{photo_id} ya no existe en la web.", ephemeral=True)
            return

        # Delete image file from disk
        filename = found_item.get("filename")
        if filename:
            file_path = os.path.join(GALLERY_FOLDER, filename)
            if os.path.exists(file_path):
                try:
                    os.remove(file_path)
                except Exception as e:
                    print(f"Error borrando archivo {file_path}: {e}")

        # Remove from JSON
        gallery = [item for item in gallery if item.get("id") != photo_id]
        save_gallery(gallery)

        embed = discord.Embed(
            title="🗑️ Foto Eliminada de la Web",
            description=f"La **Foto #{photo_id}** ha sido eliminada con éxito y ya no aparecerá en tu página web.",
            color=discord.Color.red()
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)

        # Broadcast real-time activity log to channel
        await send_discord_log(
            self.bot_ref,
            title="📋 [REGISTRO EN VIVO] • 🗑️ Foto Eliminada de la Web",
            description=(
                f"• **Foto removida:** `#{photo_id}`\n"
                f"• **Título anterior:** *{found_item.get('title', 'Trabajo')}*\n"
                f"• **Total restante en la web:** **{len(gallery)} fotos**\n"
                f"• **Estado web:** 🟢 Cambios aplicados en tiempo real."
            ),
            color=discord.Color.orange()
        )


class DeleteView(discord.ui.View):
    def __init__(self, gallery, bot_ref):
        super().__init__(timeout=60)
        self.add_item(DeleteSelect(gallery, bot_ref))


class ControlPanelView(discord.ui.View):
    def __init__(self, bot_ref):
        super().__init__(timeout=None)
        self.bot_ref = bot_ref

    @discord.ui.button(label="Checar Fotos en Web", style=discord.ButtonStyle.success, emoji="📸", custom_id="btn_check_photos")
    async def check_photos_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        gallery = load_gallery()
        if not gallery:
            await interaction.response.send_message("ℹ️ No hay fotos publicadas en la web actualmente.", ephemeral=True)
            return

        now = int(time.time() * 1000)
        new_count = 0
        lines = []

        for item in gallery:
            pid = item.get("id")
            up_time = item.get("uploaded_at", 0)
            diff_ms = now - up_time
            is_new = diff_ms < THREE_DAYS_MS
            if is_new:
                new_count += 1
                remaining_hours = max(1, int((THREE_DAYS_MS - diff_ms) / (1000 * 60 * 60)))
                tag = f"**🔥 NEW** (quedan ~{remaining_hours}h)"
            else:
                tag = f"`#{pid}` (Normal)"

            date_str = time.strftime("%d/%m/%Y %H:%M", time.localtime(up_time / 1000)) if up_time else "Reciente"
            title = item.get("title", "Trabajo en Killeen")
            lines.append(f"• **Foto #{pid}** • {tag}\n  ↳ *{title}* (Subida: {date_str})")

        embed = discord.Embed(
            title="📸 Estado de la Galería en Vivo",
            description=(
                f"• Total en la web: **{len(gallery)} fotos**\n"
                f"• Con etiqueta `🔥 NEW`: **{new_count} fotos**\n\n"
                + "\n\n".join(lines[:15])
            ),
            color=discord.Color.from_rgb(22, 163, 74)
        )

        if len(lines) > 15:
            embed.set_footer(text=f"Mostrando 15 de {len(lines)} fotos. Usa /eliminar para borrar.")

        await interaction.response.send_message(embed=embed, ephemeral=True)

    @discord.ui.button(label="Eliminar Foto", style=discord.ButtonStyle.danger, emoji="🗑️", custom_id="btn_delete_photo")
    async def delete_photo_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        gallery = load_gallery()
        if not gallery:
            await interaction.response.send_message("ℹ️ No hay fotos en la web para eliminar.", ephemeral=True)
            return
        view = DeleteView(gallery, self.bot_ref)
        await interaction.response.send_message("Selecciona la foto que quieres eliminar:", view=view, ephemeral=True)

    @discord.ui.button(label="¿Cómo Subir Fotos?", style=discord.ButtonStyle.secondary, emoji="💡", custom_id="btn_help_upload")
    async def help_upload_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        msg = (
            "**¡Es súper fácil subir fotos a tu web desde tu celular!** 🚀\n\n"
            "**1.** Adjunta de **1 a 5 fotos** en este canal y envíalas.\n"
            "**2.** O usa el comando `/subir` con la foto y descripción opcional.\n\n"
            "✨ *El servidor en la nube las publica al instante con la insignia `🔥 NEW` por 3 días (72h). No necesitas abrir tu computadora para nada.*"
        )
        await interaction.response.send_message(msg, ephemeral=True)


# ----------------- BOT FACTORY -----------------
def build_bot(enable_message_content: bool):
    intents = discord.Intents.default()
    intents.guilds = True
    intents.messages = True
    if enable_message_content:
        intents.message_content = True

    bot = commands.Bot(command_prefix="!", intents=intents)

    @bot.event
    async def on_ready():
        print("==================================================")
        print(f"Rodriguez LawnCare Bot conectado como: {bot.user}")
        print(f"Server ID: {SERVER_ID} | Canal ID: {CHANNEL_ID}")
        print(f"Message Content Intent: {'ACTIVADO' if enable_message_content else 'DESACTIVADO (Usa /subir)'}")
        print("==================================================")

        try:
            guild = discord.Object(id=SERVER_ID)
            bot.tree.copy_global_to(guild=guild)
            synced = await bot.tree.sync(guild=guild)
            print(f"✅ {len(synced)} Slash commands sincronizados en el servidor.")
        except Exception as e:
            print(f"⚠️ Error sincronizando slash commands: {e}")

        channel = bot.get_channel(CHANNEL_ID)
        if channel:
            already_posted = False
            try:
                async for msg in channel.history(limit=5):
                    if msg.author == bot.user and msg.embeds and "PANEL DE CONTROL" in msg.embeds[0].title:
                        already_posted = True
                        break
            except Exception:
                pass

            if not already_posted:
                embed = discord.Embed(
                    title="🌱 RODRIGUEZ LAWNCARE • CENTRO DE CONTROL WEB",
                    description=(
                        "**Bienvenido al Administrador Inteligente de tu Sitio Web Oficial**\n\n"
                        "Gestiona en tiempo real todos los trabajos que ven tus clientes sin necesidad de abrir tu computadora o tocar código.\n"
                        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                        "🟢 **Estado del Servidor:** `En Línea 24/7 (Railway Cloud)`\n"
                        "📸 **Galería Activa:** `Fotos Publicadas en Vivo`\n"
                        "🔥 **Insignia Automática:** `Activa por 72 horas (3 días)`\n"
                        "📍 **Cobertura:** `Killeen, Harker Heights, Copperas Cove & Belton, TX`\n"
                        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
                        "⚡ **¿CÓMO FUNCIONA?**\n"
                        "• **📤 Subir Trabajos:** Envía de **1 a 5 fotos** en este chat desde tu móvil o usa `/subir`.\n"
                        "• **🔥 Etiqueta NEW:** Tus fotos aparecerán con brillo **`🔥 NEW`** por 3 días.\n"
                        "• **🗑️ Borrar Trabajos:** Presiona **Eliminar Foto** o usa el comando `/eliminar`.\n"
                    ),
                    color=discord.Color.from_rgb(22, 163, 74)
                )
                embed.set_footer(text="Rodriguez LawnCare • Sistema Autónomo en la Nube")

                files = []
                banner_path = os.path.join(BASE_DIR, "assets", "channel_banner.jpg")
                logo_path = os.path.join(BASE_DIR, "assets", "bot_logo.jpg")
                if os.path.exists(banner_path):
                    files.append(discord.File(banner_path, filename="banner.jpg"))
                    embed.set_image(url="attachment://banner.jpg")
                if os.path.exists(logo_path):
                    files.append(discord.File(logo_path, filename="logo.jpg"))
                    embed.set_thumbnail(url="attachment://logo.jpg")

                view = ControlPanelView(bot)
                if files:
                    await channel.send(files=files, embed=embed, view=view)
                else:
                    await channel.send(embed=embed, view=view)

            # Send boot log
            gallery = load_gallery()
            await send_discord_log(
                bot,
                title="🚀 [SISTEMA EN LÍNEA 24/7] • Web & Bot Activos en la Nube",
                description=(
                    f"• **Servidor Web:** 🟢 Activo en puerto `{PORT}`\n"
                    f"• **Bot de Discord:** 🟢 Escuchando eventos en tiempo real\n"
                    f"• **Fotos en la Web:** `{len(gallery)} fotos activas`\n"
                    f"• **Modo:** 100% Autónomo (no requiere PC encendida)"
                ),
                color=discord.Color.green()
            )

    @bot.event
    async def on_message(message: discord.Message):
        if message.author.bot:
            return

        if message.channel.id != CHANNEL_ID:
            await bot.process_commands(message)
            return

        image_attachments = [
            att for att in message.attachments
            if (att.content_type and att.content_type.startswith("image/")) or
               (att.filename.lower().endswith(('.jpg', '.jpeg', '.png', '.webp')))
        ]

        if not image_attachments:
            await bot.process_commands(message)
            return

        if len(image_attachments) > 5:
            await message.reply("⚠️ **Límite:** Puedes subir un máximo de **5 fotos a la vez**. Por favor envía hasta 5 fotos.")
            return

        processing_msg = await message.reply(f"⏳ Procesando y publicando {len(image_attachments)} foto(s) en tu página web...")

        gallery = load_gallery()
        uploaded_items = []

        async with aiohttp.ClientSession() as session:
            for idx, att in enumerate(image_attachments):
                next_id = get_next_id(gallery)
                ext = att.filename.split(".")[-1].lower() if "." in att.filename else "jpg"
                if ext not in ["jpg", "jpeg", "png", "webp"]:
                    ext = "jpg"
                filename = f"work_{next_id}_{int(time.time())}.{ext}"
                filepath = os.path.join(GALLERY_FOLDER, filename)

                try:
                    async with session.get(att.url) as resp:
                        if resp.status == 200:
                            content = await resp.read()
                            with open(filepath, "wb") as f:
                                f.write(content)

                            now_ms = int(time.time() * 1000)
                            title_text = message.content.strip() if message.content.strip() else f"Trabajo Real #{next_id}"
                            item = {
                                "id": next_id,
                                "filename": filename,
                                "url": f"./assets/gallery/{filename}",
                                "uploaded_at": now_ms,
                                "title": title_text
                            }
                            gallery.append(item)
                            uploaded_items.append(item)
                except Exception as e:
                    print(f"Error descargando imagen: {e}")

        save_gallery(gallery)

        embed = discord.Embed(
            title="✅ ¡Fotos Publicadas en la Web con Éxito!",
            description=f"Se agregaron **{len(uploaded_items)} foto(s)** a tu galería en tiempo real:\n\n",
            color=discord.Color.green()
        )

        for item in uploaded_items:
            embed.description += f"• 📸 **Foto #{item['id']}** • Etiqueta `🔥 NEW` activa por **3 días** (72 horas)\n"

        embed.set_footer(text="Abre tu página web y verás las fotos publicadas al instante.")
        if uploaded_items:
            embed.set_image(url=image_attachments[0].url)

        await processing_msg.edit(content=None, embed=embed)

        # Send activity log
        ids_str = ", ".join(f"#{i['id']}" for i in uploaded_items)
        await send_discord_log(
            bot,
            title="📋 [REGISTRO EN VIVO] • 📥 Nuevas Fotos Agregadas a la Web",
            description=(
                f"• **Fotos agregadas:** `{len(uploaded_items)}`\n"
                f"• **IDs asignados:** `{ids_str}`\n"
                f"• **Etiqueta activa:** `🔥 NEW` (72 horas)\n"
                f"• **Total en la web:** **{len(gallery)} fotos**\n"
                f"• **Origen:** Subido desde celular/Discord"
            ),
            color=discord.Color.green(),
            image_url=image_attachments[0].url if image_attachments else None
        )

        await bot.process_commands(message)

    @bot.tree.command(name="fotos", description="Ver la lista de fotos activas en tu página web")
    async def cmd_fotos(interaction: discord.Interaction):
        gallery = load_gallery()
        if not gallery:
            await interaction.response.send_message("ℹ️ No hay fotos publicadas en la web.", ephemeral=True)
            return

        now = int(time.time() * 1000)
        embed = discord.Embed(
            title="📸 Fotos Publicadas en la Web (Rodriguez LawnCare)",
            description=f"Total: **{len(gallery)} fotos**\n\n",
            color=discord.Color.green()
        )
        for item in gallery:
            is_new = (now - item.get("uploaded_at", 0)) < THREE_DAYS_MS
            status = "🔥 **NEW**" if is_new else f"`#{item['id']}`"
            embed.description += f"• **Foto #{item['id']}** ({status}) - *{item.get('title', 'Trabajo')}*\n"

        await interaction.response.send_message(embed=embed, ephemeral=True)

    @bot.tree.command(name="subir", description="Subir una foto a la página web")
    @app_commands.describe(foto="Selecciona la foto de tu trabajo para subir a la web", titulo="Título opcional del trabajo")
    async def cmd_subir(interaction: discord.Interaction, foto: discord.Attachment, titulo: str = ""):
        if not (foto.content_type and foto.content_type.startswith("image/")) and not foto.filename.lower().endswith(('.jpg', '.jpeg', '.png', '.webp')):
            await interaction.response.send_message("❌ El archivo adjunto debe ser una imagen (JPG, PNG o WEBP).", ephemeral=True)
            return

        await interaction.response.defer(ephemeral=False)

        gallery = load_gallery()
        next_id = get_next_id(gallery)
        ext = foto.filename.split(".")[-1].lower() if "." in foto.filename else "jpg"
        if ext not in ["jpg", "jpeg", "png", "webp"]:
            ext = "jpg"
        filename = f"work_{next_id}_{int(time.time())}.{ext}"
        filepath = os.path.join(GALLERY_FOLDER, filename)

        async with aiohttp.ClientSession() as session:
            async with session.get(foto.url) as resp:
                if resp.status == 200:
                    content = await resp.read()
                    with open(filepath, "wb") as f:
                        f.write(content)

        now_ms = int(time.time() * 1000)
        title_val = titulo.strip() if titulo.strip() else f"Trabajo Real #{next_id}"
        item = {
            "id": next_id,
            "filename": filename,
            "url": f"./assets/gallery/{filename}",
            "uploaded_at": now_ms,
            "title": title_val
        }
        gallery.append(item)
        save_gallery(gallery)

        embed = discord.Embed(
            title="✅ ¡Foto Publicada en la Web!",
            description=f"📸 **Foto #{next_id}** agregada a tu página web.\nEtiqueta `🔥 NEW` activa durante los próximos **3 días**.",
            color=discord.Color.green()
        )
        embed.add_field(name="Título", value=title_val, inline=True)
        embed.set_image(url=foto.url)
        embed.set_footer(text="Rodriguez LawnCare Live Web Gallery")

        await interaction.followup.send(embed=embed)

        # Log
        await send_discord_log(
            bot,
            title="📋 [REGISTRO EN VIVO] • 📥 Foto Subida vía /subir",
            description=(
                f"• **Foto:** `#{next_id}`\n"
                f"• **Título:** *{title_val}*\n"
                f"• **Etiqueta activa:** `🔥 NEW` (72 horas)\n"
                f"• **Total en web:** **{len(gallery)} fotos**"
            ),
            color=discord.Color.green(),
            image_url=foto.url
        )

    @bot.tree.command(name="eliminar", description="Eliminar una foto de tu página web por su número")
    @app_commands.describe(numero="El número de la foto que deseas eliminar (ej. 1, 2, 3)")
    async def cmd_eliminar(interaction: discord.Interaction, numero: int):
        gallery = load_gallery()
        found_item = next((item for item in gallery if item.get("id") == numero), None)

        if not found_item:
            await interaction.response.send_message(f"❌ No se encontró ninguna foto con el número **#{numero}** en tu web.", ephemeral=True)
            return

        filename = found_item.get("filename")
        if filename:
            file_path = os.path.join(GALLERY_FOLDER, filename)
            if os.path.exists(file_path):
                try:
                    os.remove(file_path)
                except Exception as e:
                    print(f"Error borrando archivo: {e}")

        gallery = [item for item in gallery if item.get("id") != numero]
        save_gallery(gallery)

        embed = discord.Embed(
            title="🗑️ Foto Eliminada",
            description=f"La **Foto #{numero}** ha sido eliminada con éxito de tu página web.",
            color=discord.Color.red()
        )
        await interaction.response.send_message(embed=embed)

        # Log
        await send_discord_log(
            bot,
            title="📋 [REGISTRO EN VIVO] • 🗑️ Foto Eliminada vía /eliminar",
            description=(
                f"• **Foto removida:** `#{numero}`\n"
                f"• **Total restante:** **{len(gallery)} fotos**"
            ),
            color=discord.Color.orange()
        )

    return bot


# ----------------- WEB SERVER (AIOHTTP) -----------------
bot_global = None

async def handle_index(request):
    """Serves the main website homepage."""
    index_path = os.path.join(BASE_DIR, "index.html")
    return web.FileResponse(index_path)

async def handle_gallery_json(request):
    """Serves gallery.json with no-cache headers so visitors always see live photos."""
    gallery = load_gallery()
    return web.json_response(gallery, headers={
        "Cache-Control": "no-cache, no-store, must-revalidate",
        "Access-Control-Allow-Origin": "*"
    })

async def handle_lead_submission(request):
    """Handles lead form submissions and sends instant notification to Discord."""
    global bot_global
    try:
        data = await request.json()
        name = data.get("name", "Cliente")
        phone = data.get("phone", "No proporcionado")
        services = data.get("services", [])
        services_str = ", ".join(services) if isinstance(services, list) else str(services)
        address = data.get("address", "Por coordinar por llamada/mensaje")
        date_val = data.get("date", "Lo antes posible")
        time_val = data.get("time", "Horario habitual")
        source = data.get("source", "Estimado 1-Minuto (Web)")

        if bot_global and bot_global.is_ready():
            channel = bot_global.get_channel(CHANNEL_ID)
            if channel:
                clean_phone = "".join(c for c in phone if c.isdigit())
                embed = discord.Embed(
                    title="🚨 ¡NUEVA COTIZACIÓN RECIBIDA EN LA WEB!",
                    description=(
                        f"Un cliente acaba de llenar el formulario en tu página web:\n\n"
                        f"👤 **Nombre:** `{name}`\n"
                        f"📱 **Teléfono:** **`{phone}`**\n"
                        f"🌿 **Servicios Solicitados:**\n*{services_str}*\n\n"
                        f"📍 **Dirección:** `{address}`\n"
                        f"📅 **Fecha sugerida:** `{date_val} ({time_val})`\n"
                        f"🌐 **Origen:** `{source}`\n"
                        f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
                    ),
                    color=discord.Color.from_rgb(22, 163, 74),
                    timestamp=discord.utils.utcnow()
                )
                embed.set_footer(text="Rodriguez LawnCare • Lead Notification System")

                view = discord.ui.View()
                if clean_phone:
                    phone_dial = clean_phone if clean_phone.startswith("1") else f"1{clean_phone}"
                    view.add_item(discord.ui.Button(label="Llamar Cliente", style=discord.ButtonStyle.link, url=f"tel:+{phone_dial}", emoji="📞"))
                    view.add_item(discord.ui.Button(label="Enviar WhatsApp", style=discord.ButtonStyle.link, url=f"https://wa.me/{phone_dial}", emoji="💬"))

                await channel.send(content="@everyone 🔔 **¡Nuevo Cliente interesado en tu página web!**", embed=embed, view=view)

        return web.json_response({"success": True})
    except Exception as e:
        print(f"Error procesando lead web: {e}")
        return web.json_response({"success": False, "error": str(e)}, status=400)

def create_web_app():
    app = web.Application()
    app.router.add_get('/', handle_index)
    app.router.add_get('/index.html', handle_index)
    app.router.add_get('/gallery.json', handle_gallery_json)
    app.router.add_post('/api/lead', handle_lead_submission)
    # Static files (CSS, JS, Assets)
    app.router.add_static('/', path=BASE_DIR, show_index=False)
    return app


# ----------------- MAIN RUNNER (CONCURRENT WEB + BOT) -----------------
async def main():
    global bot_global
    # 1. Start Web Server
    web_app = create_web_app()
    runner = web.AppRunner(web_app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', PORT)
    await site.start()
    print(f"🌐 Servidor Web Rodriguez LawnCare escuchando en http://0.0.0.0:{PORT}")

    # 2. Start Discord Bot
    try:
        print("🤖 Iniciando Discord Bot con Message Content Intent...")
        bot_global = build_bot(enable_message_content=True)
        await bot_global.start(BOT_TOKEN)
    except discord.errors.PrivilegedIntentsRequired:
        print("ℹ️ Iniciando Bot en modo Slash Commands (/subir, /fotos, /eliminar) y Botones...")
        bot_global = build_bot(enable_message_content=False)
        await bot_global.start(BOT_TOKEN)
    except Exception as e:
        print(f"Error en Discord Bot: {e}")
        while True:
            await asyncio.sleep(3600)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        print("Servidor detenido.")
