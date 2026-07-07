import os
from dotenv import load_dotenv

load_dotenv()

# Token bot Discord
TOKEN = os.getenv('DISCORD_TOKEN')

# Role yang boleh mengelola server (add/remove).
# Isi ADMIN_ROLE_ID dengan ID role di file .env, atau ADMIN_ROLE_NAME dengan nama role.
ADMIN_ROLE_ID = os.getenv('ADMIN_ROLE_ID')
ADMIN_ROLE_NAME = os.getenv('ADMIN_ROLE_NAME', 'Admin')

# FiveM API direct
FIVEM_API = "https://frontend.cfx-services.net/api/servers/single"

# Banner gambar untuk panel lobby (isi dengan URL gambar, contoh: https://i.imgur.com/xxxx.png)
# Kosongkan ("") kalau tidak mau menampilkan banner.
LOBBY_BANNER = os.getenv('LOBBY_BANNER', "")

# Teks credit di footer embed
CREDIT_TEXT = "By Naufal Mulyarizki"

# File penyimpanan daftar server
SERVERS_FILE = "servers.json"

# Default server (dipakai kalau file belum ada)
DEFAULT_SERVERS = {
    "indopride": "bak4pl",
}

# Daftar cog/modul yang di-load bot
COGS = (
    "cogs.search_cog",
    "cogs.servers_cog",
    "cogs.admin_cog",
    "cogs.lobby_cog",
)
