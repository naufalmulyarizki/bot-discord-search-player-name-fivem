import os
import json
from datetime import datetime

import requests
import discord

import config

# State bersama seluruh modul
SERVERS = {}
server_cache = {}
cache_timestamp = {}


def load_servers():
    """Muat daftar server dari file JSON"""
    global SERVERS
    if os.path.exists(config.SERVERS_FILE):
        try:
            with open(config.SERVERS_FILE, 'r', encoding='utf-8') as f:
                SERVERS = json.load(f)
                return SERVERS
        except Exception as e:
            print(f"[SERVERS] Gagal load: {e}")
            SERVERS = dict(config.DEFAULT_SERVERS)
            return SERVERS
    # Pertama kali jalan: buat file dari default
    SERVERS = dict(config.DEFAULT_SERVERS)
    save_servers()
    return SERVERS


def save_servers():
    """Simpan daftar server ke file JSON"""
    try:
        with open(config.SERVERS_FILE, 'w', encoding='utf-8') as f:
            json.dump(SERVERS, f, indent=4, ensure_ascii=False)
        return True
    except Exception as e:
        print(f"[SERVERS] Gagal save: {e}")
        return False


def is_admin(interaction: discord.Interaction) -> bool:
    """Cek apakah user punya role admin yang tervalidasi"""
    # Command harus dipakai di dalam server (bukan DM)
    if not isinstance(interaction.user, discord.Member):
        return False
    # Administrator server selalu diizinkan
    if interaction.user.guild_permissions.administrator:
        return True
    for role in interaction.user.roles:
        if config.ADMIN_ROLE_ID and str(role.id) == str(config.ADMIN_ROLE_ID):
            return True
        if config.ADMIN_ROLE_NAME and role.name.lower() == config.ADMIN_ROLE_NAME.lower():
            return True
    return False


async def get_server_info(server_name):
    """Ambil data langsung dari FiveM API"""

    if server_name not in SERVERS:
        return None

    # Cache 5 menit
    if server_name in server_cache:
        cache_age = (datetime.now() - cache_timestamp.get(server_name, datetime.now())).total_seconds()
        if cache_age < 300:
            return server_cache[server_name]

    try:
        code = SERVERS[server_name]

        print(f"[API] Fetching {config.FIVEM_API}/{code}")

        response = requests.get(f"{config.FIVEM_API}/{code}", timeout=10)
        response.raise_for_status()

        data = response.json()

        if not data.get('Data'):
            return None

        server_data = {
            "name": data['Data'].get('hostname'),
            "banner": data['Data'].get('vars', {}).get('banner_detail'),
            "icon": data['Data'].get('vars', {}).get('icon'),
            "players_online": len(data['Data'].get('players', [])),
            "max_players": data['Data'].get('sv_maxclients', 32),
            "game_type": data['Data'].get('vars', {}).get('gamename', 'Unknown'),
            "players": data['Data'].get('players', []),
        }

        server_cache[server_name] = server_data
        cache_timestamp[server_name] = datetime.now()

        print(f"[API] OK {server_name}")

        return server_data

    except Exception as e:
        print(f"[API] Error {e}")
        return None
