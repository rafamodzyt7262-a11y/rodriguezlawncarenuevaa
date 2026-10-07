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
LEADS_CHANNEL_ID = int(get_env_var("LEADS_CHANNEL_ID", "1557306528078237706"))

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


# ----------------- JOB CATEGORIES & PRESETS -----------------
JOB_PRESETS = {
    "front": {
        "category": "Front Yard",
        "icon": "🏡",
        "default_title": "Front Yard Clean & Sharp Mowing"
    },
    "back": {
        "category": "Back Yard",
        "icon": "🌿",
        "default_title": "Back Yard Mowing & Clean Lines"
    },
    "mulch": {
        "category": "Mulch",
        "icon": "🪵",
        "default_title": "Fresh Dark Mulch Installation"
    },
    "tree": {
        "category": "Tree Care",
        "icon": "🌳",
        "default_title": "Tree Care & Precision Trimming"
    },
    "bush": {
        "category": "Shrubs & Bushes",
        "icon": "✂️",
        "default_title": "Hedge Trimming & Shrub Shaping"
    },
    "clean": {
        "category": "Yard Cleanups",
        "icon": "🧹",
        "default_title": "Property Cleanup & Debris Removal"
    },
    "edge": {
        "category": "Edging & Stripes",
        "icon": "📐",
        "default_title": "Precision Sidewalk Edging"
    },
    "mow": {
        "category": "Lawn Mowing",
        "icon": "🌱",
        "default_title": "Commercial Stripe Lawn Mowing"
    }
}

KEYWORD_MAPPINGS = [
    (["front", "frente", "delantero", "delantera", "frontyard", "porch"], "front"),
    (["back", "trasero", "trasera", "atras", "backyard", "patio trasero"], "back"),
    (["mulch", "mulching", "acolchado", "corteza", "bark"], "mulch"),
    (["tree", "trees", "arbol", "arboles", "rama", "ramas", "poda"], "tree"),
    (["bush", "bushes", "shrub", "shrubs", "hedge", "hedges", "arbusto", "arbustos", "seto", "setos"], "bush"),
    (["clean", "cleanup", "limpieza", "junk", "debris", "hojas", "leaf", "leaves", "escombros"], "clean"),
    (["edge", "edging", "orilla", "orillas", "filo", "sidewalk", "banqueta"], "edge"),
    (["mow", "mowing", "corte", "zacate", "pasto", "cesped", "lawn", "grass"], "mow"),
]

def parse_job_details(text: str):
    """Detects category, icon, and formatted title from user text or keyword."""
    if not text or not text.strip():
        return {
            "category": "General LawnCare",
            "icon": "🌱",
            "title": "Trabajo de Lawn Care"
        }
    clean = text.strip()
    low = clean.lower()

    for kw_list, preset_key in KEYWORD_MAPPINGS:
        if any(kw in low for kw in kw_list):
            preset = JOB_PRESETS[preset_key]
            if len(clean) <= 12 or clean.lower() in [k for k in kw_list]:
                return {
                    "category": preset["category"],
                    "icon": preset["icon"],
                    "title": preset["default_title"]
                }
            return {
                "category": preset["category"],
                "icon": preset["icon"],
                "title": clean[0].upper() + clean[1:]
            }

    return {
        "category": "General LawnCare",
        "icon": "✨",
        "title": clean[0].upper() + clean[1:]
    }


# ----------------- UI VIEWS & MENUS -----------------
class CustomJobModal(discord.ui.Modal, title="Nombre del Trabajo"):
    job_name = discord.ui.TextInput(
        label="¿Qué trabajo se realizó?",
        placeholder="Ej: Front yard, Mulch nuevo, Podado de árboles...",
        min_length=2,
        max_length=90,
        required=True
    )

    def __init__(self, item_ids: list):
        super().__init__()
        self.item_ids = item_ids if isinstance(item_ids, list) else [item_ids]

    async def on_submit(self, interaction: discord.Interaction):
        custom_text = self.job_name.value.strip()
        details = parse_job_details(custom_text)
        gallery = load_gallery()

        updated_count = 0
        for item in gallery:
            if item.get("id") in self.item_ids:
                item["title"] = details["title"]
                item["category"] = details["category"]
                updated_count += 1

        if updated_count > 0:
            save_gallery(gallery)
            embed = discord.Embed(
                title="✅ ¡Trabajo Asignado con Éxito!",
                description=(
                    f"📸 **Foto(s):** `#{', #'.join(str(i) for i in self.item_ids)}`\n"
                    f"🏷️ **Nombre:** `{details['icon']} {details['title']}`\n"
                    f"📂 **Categoría Web:** `{details['category']}`\n\n"
                    f"🌐 *Ya se actualizó en tu página web en tiempo real.*"
                ),
                color=discord.Color.green()
            )
            await interaction.response.send_message(embed=embed, ephemeral=False)
        else:
            await interaction.response.send_message("❌ No se encontró la foto para actualizar.", ephemeral=True)


class JobCategoryPickerView(discord.ui.View):
    def __init__(self, item_ids: list):
        super().__init__(timeout=None)
        self.item_ids = item_ids if isinstance(item_ids, list) else [item_ids]

    async def apply_preset(self, interaction: discord.Interaction, key: str):
        details = JOB_PRESETS[key]
        gallery = load_gallery()
        updated = 0
        for item in gallery:
            if item.get("id") in self.item_ids:
                item["title"] = details["default_title"]
                item["category"] = details["category"]
                updated += 1

        if updated > 0:
            save_gallery(gallery)
            embed = discord.Embed(
                title="✅ ¡Trabajo Asignado a la Web!",
                description=(
                    f"📸 **Foto(s):** `#{', #'.join(str(i) for i in self.item_ids)}`\n"
                    f"🏷️ **Nombre:** `{details['icon']} {details['default_title']}`\n"
                    f"📂 **Categoría Web:** `{details['category']}`\n\n"
                    f"🌐 *Visible al instante en tu página web.*"
                ),
                color=discord.Color.green()
            )
            await interaction.response.send_message(embed=embed, ephemeral=False)
        else:
            await interaction.response.send_message("⚠️ Foto no encontrada en la web.", ephemeral=True)

    @discord.ui.button(label="Front Yard", emoji="🏡", style=discord.ButtonStyle.primary, row=0)
    async def btn_front(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.apply_preset(interaction, "front")

    @discord.ui.button(label="Back Yard", emoji="🌿", style=discord.ButtonStyle.primary, row=0)
    async def btn_back(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.apply_preset(interaction, "back")

    @discord.ui.button(label="Mulch", emoji="🪵", style=discord.ButtonStyle.success, row=0)
    async def btn_mulch(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.apply_preset(interaction, "mulch")

    @discord.ui.button(label="Tree Care", emoji="🌳", style=discord.ButtonStyle.success, row=1)
    async def btn_tree(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.apply_preset(interaction, "tree")

    @discord.ui.button(label="Arbustos", emoji="✂️", style=discord.ButtonStyle.secondary, row=1)
    async def btn_bush(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.apply_preset(interaction, "bush")

    @discord.ui.button(label="Limpieza", emoji="🧹", style=discord.ButtonStyle.secondary, row=1)
    async def btn_clean(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.apply_preset(interaction, "clean")

    @discord.ui.button(label="Escribir Otro Nombre...", emoji="✏️", style=discord.ButtonStyle.secondary, row=2)
    async def btn_custom(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(CustomJobModal(self.item_ids))


class RenameSelect(discord.ui.Select):
    def __init__(self, gallery):
        options = []
        for item in gallery[-25:]:
            cat = item.get("category", "General")
            title = item.get("title", "Trabajo")[:40]
            options.append(
                discord.SelectOption(
                    label=f"Foto #{item['id']} ({cat})",
                    description=title,
                    value=str(item["id"]),
                    emoji="🏷️"
                )
            )
        super().__init__(
            placeholder="Selecciona la foto a la que deseas cambiar nombre...",
            min_values=1,
            max_values=1,
            options=options
        )

    async def callback(self, interaction: discord.Interaction):
        photo_id = int(self.values[0])
        gallery = load_gallery()
        found_item = next((item for item in gallery if item.get("id") == photo_id), None)
        if not found_item:
            await interaction.response.send_message(f"❌ La foto #{photo_id} no existe.", ephemeral=True)
            return

        view = JobCategoryPickerView([photo_id])
        msg = (
            f"✏️ **Cambiando nombre a la Foto #{photo_id}**\n"
            f"• **Título actual:** *{found_item.get('title', 'Sin título')}*\n"
            f"• **Categoría actual:** `{found_item.get('category', 'General')}`\n\n"
            f"👇 **Selecciona el nuevo trabajo o escribe un nombre personalizado:**"
        )
        await interaction.response.send_message(msg, view=view, ephemeral=True)


class RenameView(discord.ui.View):
    def __init__(self, gallery):
        super().__init__(timeout=60)
        self.add_item(RenameSelect(gallery))


class DeleteSelect(discord.ui.Select):
    def __init__(self, gallery):
        options = []
        for item in gallery[-25:]:
            now = int(time.time() * 1000)
            is_new = (now - item.get("uploaded_at", 0)) < THREE_DAYS_MS
            status_text = "NEW" if is_new else "Normal"
            cat = item.get("category", "Trabajo")
            title_preview = f"[{cat}] {item.get('title', 'Trabajo')}"[:45]
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
        super().__init__(timeout=None)

    @discord.ui.button(label="Checar Fotos en Web", style=discord.ButtonStyle.success, emoji="📸", custom_id="btn_check_photos")
    async def check_photos_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        gallery = load_gallery()
        if not gallery:
            await interaction.response.send_message("ℹ️ No hay fotos publicadas en la web actualmente.", ephemeral=True)
            return

        now = int(time.time() * 1000)
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

            cat = item.get("category", "General")
            title = item.get("title", "Trabajo en Killeen")
            lines.append(f"• **Foto #{pid}** • {tag} • `[{cat}]`\n  ↳ *{title}*")

        embed = discord.Embed(
            title="📸 Estado de la Galería en Vivo",
            description=(
                f"• Total en la web: **{len(gallery)} fotos**\n\n"
                + "\n\n".join(lines[:15])
            ),
            color=discord.Color.from_rgb(22, 163, 74)
        )

        if len(lines) > 15:
            embed.set_footer(text=f"Mostrando 15 de {len(lines)} fotos. Usa /eliminar para borrar.")

        await interaction.response.send_message(embed=embed, ephemeral=True)

    @discord.ui.button(label="Cambiar Nombre / Trabajo", style=discord.ButtonStyle.primary, emoji="✏️", custom_id="btn_rename_photo")
    async def rename_photo_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        gallery = load_gallery()
        if not gallery:
            await interaction.response.send_message("ℹ️ No hay fotos en la web para renombrar.", ephemeral=True)
            return
        view = RenameView(gallery)
        await interaction.response.send_message("Selecciona la foto a la que deseas cambiar el nombre o categoría:", view=view, ephemeral=True)

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
            "**¡Es súper fácil subir fotos a tu web desde tu celular!** 🚀\n\n"
            "**1. Escribe el trabajo al adjuntar la foto:**\n"
            "   Al mandar la foto en este canal escribe: `front`, `back`, `mulch`, `tree`, etc.\n"
            "   El bot le asignará automáticamente el nombre y categoría en tu web.\n\n"
            "**2. O mándala sin texto:**\n"
            "   El bot te responderá al instante con botones fáciles `[Front Yard]` `[Back Yard]` `[Mulch]` `[Tree Care]` para que toques el que hiciste con un solo dedo.\n\n"
            "**3. Con comando `/subir`:**\n"
            "   Escribe `/subir`, adjunta la foto y elige la categoría en la lista desplegable.\n\n"
            "✨ *El bot las publica al instante con la insignia `🔥 NEW` por 3 días (72h).*"
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
        print(f"Message Content Intent: {'ACTIVADO' if enable_message_content else 'DESACTIVADO (Usa /subir o Botones)'}")
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
                        "• **📤 Subir Trabajos:** Envía de **1 a 5 fotos** en este chat con el nombre (`front`, `back`, `mulch`, `tree`) o usa `/subir`.\n"
                        "• **🏷️ Botones Rápidos:** Si mandas la foto sola, toca los botones `[Front]` `[Back]` `[Mulch]` `[Tree]` para nombrarla al instante.\n"
                        "• **✏️ Renombrar:** Puedes cambiarle el nombre a cualquier foto con **Cambiar Nombre / Trabajo** o `/renombrar`.\n"
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

        raw_caption = message.content.strip() if message.content else ""
        has_caption = bool(raw_caption)
        parsed_caption = parse_job_details(raw_caption) if has_caption else None

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
                            if parsed_caption:
                                item_title = parsed_caption["title"]
                                item_cat = parsed_caption["category"]
                            else:
                                item_title = f"Trabajo Real #{next_id}"
                                item_cat = "General LawnCare"

                            item = {
                                "id": next_id,
                                "filename": filename,
                                "url": f"./assets/gallery/{filename}",
                                "uploaded_at": now_ms,
                                "title": item_title,
                                "category": item_cat
                            }
                            gallery.append(item)
                            uploaded_items.append(item)
                except Exception as e:
                    print(f"Error descargando imagen: {e}")

        save_gallery(gallery)

        uploaded_ids = [i["id"] for i in uploaded_items]
        picker_view = JobCategoryPickerView(uploaded_ids)

        if parsed_caption:
            embed = discord.Embed(
                title="✅ ¡Fotos Publicadas en la Web con Éxito!",
                description=(
                    f"Se agregaron **{len(uploaded_items)} foto(s)** a tu galería en tiempo real:\n\n"
                    f"🏷️ **Trabajo Asignado:** `{parsed_caption['icon']} {parsed_caption['title']}`\n"
                    f"📂 **Categoría Web:** `{parsed_caption['category']}`\n"
                    f"🔥 **Etiqueta:** `🔥 NEW` activa por **3 días** (72 horas)\n\n"
                    f"*(Si deseas cambiar el trabajo o nombre de estas fotos, toca un botón abajo)*"
                ),
                color=discord.Color.green()
            )
        else:
            embed = discord.Embed(
                title="📸 ¡Fotos Subidas a la Web!",
                description=(
                    f"Se agregaron **{len(uploaded_items)} foto(s)** (`#{', #'.join(str(i) for i in uploaded_ids)}`) con etiqueta `🔥 NEW`.\n\n"
                    f"👇 **¿Qué trabajo realizaste?** Toca un botón para que el nombre y categoría aparezcan en tu página web:"
                ),
                color=discord.Color.blue()
            )

        embed.set_footer(text="Rodriguez LawnCare • Galería en Vivo")
        if uploaded_items:
            embed.set_image(url=image_attachments[0].url)

        await processing_msg.edit(content=None, embed=embed, view=picker_view)
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
            cat = item.get("category", "General")
            embed.description += f"• **Foto #{item['id']}** ({status}) - `[{cat}]` *{item.get('title', 'Trabajo')}*\n"

        await interaction.response.send_message(embed=embed, ephemeral=True)

    @bot.tree.command(name="subir", description="Subir una foto a la página web con su trabajo y nombre")
    @app_commands.describe(
        foto="Selecciona la foto de tu trabajo para subir a la web",
        trabajo="Tipo de trabajo realizado (Front Yard, Mulch, Tree, etc.)",
        nombre_personalizado="Nombre o detalle opcional del trabajo (ej: Casa en Belton, Mulch oscuro...)"
    )
    @app_commands.choices(trabajo=[
        app_commands.Choice(name="🏡 Front Yard (Frente)", value="front"),
        app_commands.Choice(name="🌿 Back Yard (Patio Trasero)", value="back"),
        app_commands.Choice(name="🪵 Mulch Installation (Mulch)", value="mulch"),
        app_commands.Choice(name="🌳 Tree Care & Trimming (Árboles)", value="tree"),
        app_commands.Choice(name="✂️ Hedge & Bush Trimming (Arbustos)", value="bush"),
        app_commands.Choice(name="🧹 Yard Cleanup & Debris (Limpieza)", value="clean"),
        app_commands.Choice(name="🌱 Lawn Mowing & Edging (Corte)", value="mow"),
        app_commands.Choice(name="✏️ Personalizado (Escribe en 'nombre_personalizado')", value="custom"),
    ])
    async def cmd_subir(
        interaction: discord.Interaction,
        foto: discord.Attachment,
        trabajo: app_commands.Choice[str] = None,
        nombre_personalizado: str = ""
    ):
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

        # Determine category and title
        if nombre_personalizado.strip():
            details = parse_job_details(nombre_personalizado.strip())
            if trabajo and trabajo.value != "custom" and trabajo.value in JOB_PRESETS:
                details["category"] = JOB_PRESETS[trabajo.value]["category"]
                details["icon"] = JOB_PRESETS[trabajo.value]["icon"]
        elif trabajo and trabajo.value != "custom" and trabajo.value in JOB_PRESETS:
            preset = JOB_PRESETS[trabajo.value]
            details = {
                "category": preset["category"],
                "icon": preset["icon"],
                "title": preset["default_title"]
            }
        else:
            preset = JOB_PRESETS["front"]
            details = {
                "category": preset["category"],
                "icon": preset["icon"],
                "title": preset["default_title"]
            }

        item = {
            "id": next_id,
            "filename": filename,
            "url": f"./assets/gallery/{filename}",
            "uploaded_at": now_ms,
            "title": details["title"],
            "category": details["category"]
        }
        gallery.append(item)
        save_gallery(gallery)

        picker_view = JobCategoryPickerView([next_id])

        embed = discord.Embed(
            title="✅ ¡Foto Publicada en la Web!",
            description=(
                f"📸 **Foto #{next_id}** agregada con éxito a tu página web.\n"
                f"🏷️ **Trabajo:** `{details['icon']} {details['title']}`\n"
                f"📂 **Categoría Web:** `{details['category']}`\n"
                f"🔥 **Insignia:** `🔥 NEW` activa durante los próximos **3 días**."
            ),
            color=discord.Color.green()
        )
        embed.set_image(url=foto.url)
        embed.set_footer(text="Rodriguez LawnCare Live Web Gallery")

        await interaction.followup.send(embed=embed, view=picker_view)

    @bot.tree.command(name="renombrar", description="Cambiar el nombre o categoría de una foto en la web")
    @app_commands.describe(
        numero="El número de la foto que deseas renombrar (ej. 2, 3, 4)",
        nuevo_nombre="Nuevo nombre o categoría (ej. front, mulch, tree, o nombre personalizado)"
    )
    async def cmd_renombrar(interaction: discord.Interaction, numero: int, nuevo_nombre: str):
        gallery = load_gallery()
        found_item = next((item for item in gallery if item.get("id") == numero), None)

        if not found_item:
            await interaction.response.send_message(f"❌ No se encontró ninguna foto con el número **#{numero}** en tu web.", ephemeral=True)
            return

        details = parse_job_details(nuevo_nombre)
        old_title = found_item.get("title", "Sin título")
        old_cat = found_item.get("category", "General")

        found_item["title"] = details["title"]
        found_item["category"] = details["category"]
        save_gallery(gallery)

        embed = discord.Embed(
            title="✅ ¡Foto Renombrada en la Web!",
            description=(
                f"📸 **Foto #{numero}** actualizada con éxito:\n\n"
                f"🏷️ **Nuevo Nombre:** `{details['icon']} {details['title']}`\n"
                f"📂 **Nueva Categoría:** `{details['category']}`\n\n"
                f"*(Antes: [{old_cat}] {old_title})*\n"
                f"🌐 *Ya se ve reflejado en tu página web en tiempo real.*"
            ),
            color=discord.Color.green()
        )
        await interaction.response.send_message(embed=embed)

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
