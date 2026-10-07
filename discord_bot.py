"""
RODRIGUEZ LAWNCARE - DISCORD BOT WEB GALLERY MANAGER
Connects your Discord channel directly to your website's real-work gallery.
- Upload up to 5 photos at once (drag & drop, @bot, or /subir)
- Automatically tags new photos with '🔥 NEW' badge for 3 days (72 hours)
- Lists all active web photos with their numbers and status
- Delete photos by number or dropdown menu
"""

import os
import sys
import json
import time
import asyncio
import aiohttp
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


# ----------------- UI VIEWS & MENUS -----------------
class DeleteSelect(discord.ui.Select):
    def __init__(self, gallery):
        options = []
        for item in gallery[-25:]: # Limit 25 options
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


class DeleteView(discord.ui.View):
    def __init__(self, gallery):
        super().__init__(timeout=60)
        self.add_item(DeleteSelect(gallery))


class ControlPanelView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None) # Persistent view

    @discord.ui.button(label="Checar Fotos en Web", style=discord.ButtonStyle.success, emoji="📸", custom_id="btn_check_photos")
    async def check_photos_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        gallery = load_gallery()
        if not gallery:
            await interaction.response.send_message("ℹ️ No hay fotos publicadas en la web actualmente.", ephemeral=True)
            return

        now = int(time.time() * 1000)
        embed = discord.Embed(
            title="📸 Fotos Activas en la Web (Rodriguez LawnCare)",
            description=f"Total de fotos publicadas: **{len(gallery)}**\nLas fotos con etiqueta `🔥 NEW` están dentro de sus primeros 3 días en la web.\n",
            color=discord.Color.from_rgb(22, 163, 74)
        )

        lines = []
        for item in gallery:
            pid = item.get("id")
            up_time = item.get("uploaded_at", 0)
            diff_ms = now - up_time
            is_new = diff_ms < THREE_DAYS_MS

            if is_new:
                remaining_hours = max(1, int((THREE_DAYS_MS - diff_ms) / (1000 * 60 * 60)))
                tag = f"**🔥 NEW** (quedan ~{remaining_hours}h)"
            else:
                tag = f"`#{pid}` (Normal)"

            date_str = time.strftime("%d/%m/%Y %H:%M", time.localtime(up_time / 1000)) if up_time else "Reciente"
            title = item.get("title", "Trabajo en Killeen")
            lines.append(f"• **Foto #{pid}** • {tag}\n  ↳ *{title}* (Subida: {date_str})")

        embed.description += "\n" + "\n\n".join(lines[:15])
        if len(lines) > 15:
            embed.set_footer(text=f"Mostrando 15 de {len(lines)} fotos. Usa /eliminar para borrar fotos antiguas.")

        await interaction.response.send_message(embed=embed, ephemeral=True)

    @discord.ui.button(label="Eliminar Foto", style=discord.ButtonStyle.danger, emoji="🗑️", custom_id="btn_delete_photo")
    async def delete_photo_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        gallery = load_gallery()
        if not gallery:
            await interaction.response.send_message("ℹ️ No hay fotos en la web para eliminar.", ephemeral=True)
            return
        view = DeleteView(gallery)
        await interaction.response.send_message("Selecciona la foto que quieres eliminar:", view=view, ephemeral=True)

    @discord.ui.button(label="¿Cómo Subir Fotos?", style=discord.ButtonStyle.secondary, emoji="💡", custom_id="btn_help_upload")
    async def help_upload_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        msg = (
            "**¡Es súper fácil subir fotos a tu web!** 🚀\n\n"
            "**Método 1 (Directo):** Arrastra o adjunta de **1 a 5 fotos** en este canal y envíalas.\n"
            "**Método 2 (Comando):** Escribe `/subir`, adjunta la foto y puedes ponerle un título opcional.\n\n"
            "✨ *El bot las publicará inmediatamente en tu página web con la etiqueta `🔥 NEW` por 3 días (72h).*"
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
        print(f"Message Content Intent: {'ACTIVADO (Direct Drag & Drop listo)' if enable_message_content else 'DESACTIVADO (Usa /subir o menciona al bot)'}")
        print("==================================================")

        # Sync Slash Commands with Guild
        try:
            guild = discord.Object(id=SERVER_ID)
            bot.tree.copy_global_to(guild=guild)
            synced = await bot.tree.sync(guild=guild)
            print(f"✅ {len(synced)} Slash commands sincronizados en el servidor.")
        except Exception as e:
            print(f"⚠️ Error sincronizando slash commands: {e}")

        # Post or refresh Control Panel in dedicated channel
        channel = bot.get_channel(CHANNEL_ID)
        if channel:
            # Check if recent message is already the control panel to avoid flooding
            already_posted = False
            try:
                async for msg in channel.history(limit=5):
                    if msg.author == bot.user and msg.embeds and "PANEL DE CONTROL" in msg.embeds[0].title:
                        already_posted = True
                        break
            except Exception as e:
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

                view = ControlPanelView()
                if files:
                    await channel.send(files=files, embed=embed, view=view)
                else:
                    await channel.send(embed=embed, view=view)

    # Message Listener for direct photo uploads
    @bot.event
    async def on_message(message: discord.Message):
        if message.author.bot:
            return

        if message.channel.id != CHANNEL_ID:
            await bot.process_commands(message)
            return

        # Check for image attachments
        image_attachments = [
            att for att in message.attachments
            if (att.content_type and att.content_type.startswith("image/")) or
               (att.filename.lower().endswith(('.jpg', '.jpeg', '.png', '.webp')))
        ]

        if not image_attachments:
            await bot.process_commands(message)
            return

        if len(image_attachments) > 5:
            await message.reply("⚠️ **Límite:** Puedes subir un máximo de **5 fotos a la vez** para mantener tu galería organizada. Por favor envía hasta 5 fotos.")
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
        await bot.process_commands(message)

    # Slash Commands
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

    @bot.tree.command(name="eliminar", description="Eliminar una foto de tu página web por su número")
    @app_commands.describe(numero="El número de la foto que deseas eliminar (ej. 1, 2, 3)")
    async def cmd_eliminar(interaction: discord.Interaction, numero: int):
        gallery = load_gallery()
        found_item = next((item for item in gallery if item.get("id") == numero), None)

        if not found_item:
            await interaction.response.send_message(f"❌ No se encontró ninguna foto con el número **#{numero}** en tu web.", ephemeral=True)
            return

        # Delete image file
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

    return bot


# ----------------- MAIN RUNNER WITH FALLBACK -----------------
if __name__ == "__main__":
    try:
        print("🤖 Intentando conectar con Message Content Intent activado...")
        bot = build_bot(enable_message_content=True)
        bot.run(BOT_TOKEN)
    except discord.errors.PrivilegedIntentsRequired:
        print("\n" + "="*60)
        print("ℹ️ AVISO: 'Message Content Intent' aún no está activado en:")
        print(f"👉 https://discord.com/developers/applications/{APP_ID}/bot")
        print("Iniciando automáticamente con Slash Commands (/subir, /fotos, /eliminar) y Botones...")
        print("="*60 + "\n")
        bot = build_bot(enable_message_content=False)
        bot.run(BOT_TOKEN)
