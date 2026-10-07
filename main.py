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
            # If user typed just a short word like "front", "mulch", "tree"
            if len(clean) <= 12 or clean.lower() in [k for k in kw_list]:
                return {
                    "category": preset["category"],
                    "icon": preset["icon"],
                    "title": preset["default_title"]
                }
            # Otherwise, keep custom details capitalized
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


# ----------------- DISCORD MODALS & UI VIEWS -----------------
class CustomJobModal(discord.ui.Modal, title="Nombre del Trabajo"):
    job_name = discord.ui.TextInput(
        label="¿Qué trabajo se realizó?",
        placeholder="Ej: Front yard, Mulch nuevo, Podado de árboles...",
        min_length=2,
        max_length=90,
        required=True
    )

    def __init__(self, item_ids: list, bot_ref=None):
        super().__init__()
        self.item_ids = item_ids if isinstance(item_ids, list) else [item_ids]
        self.bot_ref = bot_ref

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

            if self.bot_ref:
                await send_discord_log(
                    self.bot_ref,
                    title="📋 [REGISTRO EN VIVO] • ✏️ Foto(s) Renombrada(s)",
                    description=(
                        f"• **Foto(s):** `#{', #'.join(str(i) for i in self.item_ids)}`\n"
                        f"• **Nombre:** *{details['title']}*\n"
                        f"• **Categoría:** `{details['category']}`\n"
                        f"• **Estado web:** 🟢 Actualizado en vivo"
                    ),
                    color=discord.Color.green()
                )
        else:
            await interaction.response.send_message("❌ No se encontró la foto para actualizar.", ephemeral=True)


class JobCategoryPickerView(discord.ui.View):
    def __init__(self, item_ids: list, bot_ref=None):
        super().__init__(timeout=None)
        self.item_ids = item_ids if isinstance(item_ids, list) else [item_ids]
        self.bot_ref = bot_ref

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

            if self.bot_ref:
                await send_discord_log(
                    self.bot_ref,
                    title="📋 [REGISTRO EN VIVO] • 🏷️ Categoría de Foto Asignada",
                    description=(
                        f"• **Foto(s):** `#{', #'.join(str(i) for i in self.item_ids)}`\n"
                        f"• **Trabajo:** `{details['icon']} {details['default_title']}`\n"
                        f"• **Categoría Web:** `{details['category']}`"
                    ),
                    color=discord.Color.green()
                )
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
        await interaction.response.send_modal(CustomJobModal(self.item_ids, self.bot_ref))


class RenameSelect(discord.ui.Select):
    def __init__(self, gallery, bot_ref):
        self.bot_ref = bot_ref
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

        view = JobCategoryPickerView([photo_id], self.bot_ref)
        msg = (
            f"✏️ **Cambiando nombre a la Foto #{photo_id}**\n"
            f"• **Título actual:** *{found_item.get('title', 'Sin título')}*\n"
            f"• **Categoría actual:** `{found_item.get('category', 'General')}`\n\n"
            f"👇 **Selecciona el nuevo trabajo o escribe un nombre personalizado:**"
        )
        await interaction.response.send_message(msg, view=view, ephemeral=True)


class RenameView(discord.ui.View):
    def __init__(self, gallery, bot_ref):
        super().__init__(timeout=60)
        self.add_item(RenameSelect(gallery, bot_ref))


class DeleteSelect(discord.ui.Select):
    def __init__(self, gallery, bot_ref):
        self.bot_ref = bot_ref
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

        # Broadcast real-time activity log to channel
        await send_discord_log(
            self.bot_ref,
            title="📋 [REGISTRO EN VIVO] • 🗑️ Foto Eliminada de la Web",
            description=(
                f"• **Foto removida:** `#{photo_id}`\n"
                f"• **Título anterior:** *{found_item.get('title', 'Trabajo')}*\n"
                f"• **Categoría:** `{found_item.get('category', 'General')}`\n"
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

            cat = item.get("category", "General")
            title = item.get("title", "Trabajo en Killeen")
            lines.append(f"• **Foto #{pid}** • {tag} • `[{cat}]`\n  ↳ *{title}*")

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

    @discord.ui.button(label="Cambiar Nombre / Trabajo", style=discord.ButtonStyle.primary, emoji="✏️", custom_id="btn_rename_photo")
    async def rename_photo_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        gallery = load_gallery()
        if not gallery:
            await interaction.response.send_message("ℹ️ No hay fotos en la web para renombrar.", ephemeral=True)
            return
        view = RenameView(gallery, self.bot_ref)
        await interaction.response.send_message("Selecciona la foto a la que deseas cambiar el nombre o categoría:", view=view, ephemeral=True)

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
            "**1. Escribe el trabajo al adjuntar la foto:**\n"
            "   Al mandar la foto en este canal escribe: `front`, `back`, `mulch`, `tree`, etc.\n"
            "   El bot le asignará automáticamente el nombre y categoría en tu web.\n\n"
            "**2. O mándala sin texto:**\n"
            "   El bot te responderá al instante con botones fáciles `[Front Yard]` `[Back Yard]` `[Mulch]` `[Tree Care]` para que toques el que hiciste con un solo dedo.\n\n"
            "**3. Con comando `/subir`:**\n"
            "   Escribe `/subir`, adjunta la foto y elige la categoría en la lista desplegable.\n\n"
            "✨ *El servidor en la nube las publica al instante con la insignia `🔥 NEW` por 3 días (72h).*"
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
                    f"• **Categorías:** Front Yard, Back Yard, Mulch, Tree Care, etc.\n"
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
        picker_view = JobCategoryPickerView(uploaded_ids, bot)

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

        # Send activity log
        ids_str = ", ".join(f"#{i['id']}" for i in uploaded_items)
        log_title = parsed_caption["title"] if parsed_caption else "Trabajo Reciente"
        log_cat = parsed_caption["category"] if parsed_caption else "General"
        await send_discord_log(
            bot,
            title="📋 [REGISTRO EN VIVO] • 📥 Nuevas Fotos Agregadas a la Web",
            description=(
                f"• **Fotos agregadas:** `{len(uploaded_items)}`\n"
                f"• **IDs asignados:** `{ids_str}`\n"
                f"• **Trabajo:** *{log_title}* (`{log_cat}`)\n"
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
            # If user also selected a specific choice other than custom, override category
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

        picker_view = JobCategoryPickerView([next_id], bot)

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

        # Log
        await send_discord_log(
            bot,
            title="📋 [REGISTRO EN VIVO] • 📥 Foto Subida vía /subir",
            description=(
                f"• **Foto:** `#{next_id}`\n"
                f"• **Trabajo:** *{details['title']}*\n"
                f"• **Categoría:** `{details['category']}`\n"
                f"• **Etiqueta activa:** `🔥 NEW` (72 horas)\n"
                f"• **Total en web:** **{len(gallery)} fotos**"
            ),
            color=discord.Color.green(),
            image_url=foto.url
        )

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

        await send_discord_log(
            bot,
            title="📋 [REGISTRO EN VIVO] • ✏️ Foto Renombrada vía /renombrar",
            description=(
                f"• **Foto:** `#{numero}`\n"
                f"• **Nuevo Nombre:** *{details['title']}*\n"
                f"• **Categoría:** `{details['category']}`\n"
                f"• **Total en web:** **{len(gallery)} fotos**"
            ),
            color=discord.Color.green()
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
