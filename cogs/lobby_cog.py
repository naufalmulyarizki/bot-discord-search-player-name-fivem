import discord
from discord import app_commands
from discord.ext import commands

import config
import server_manager


# ============================================================
# Embed builders (dipakai ulang oleh tombol lobby)
# ============================================================

async def build_servers_embed() -> discord.Embed:
    embed = discord.Embed(
        title="Daftar Server",
        description="Gunakan **keyword** di bawah untuk fitur cari/info/online.",
        color=discord.Color.gold()
    )

    if not server_manager.SERVERS:
        embed.add_field(name="Kosong", value="Belum ada server terdaftar.", inline=False)
        return embed

    for idx, (name, code) in enumerate(server_manager.SERVERS.items(), 1):
        info = await server_manager.get_server_info(name)
        if info:
            pct = (info['players_online'] / info['max_players'] * 100) if info['max_players'] > 0 else 0
            embed.add_field(
                name=f"{idx}. [ONLINE] {info['name']}",
                value=(
                    f"**Keyword:** `{name}`\n"
                    f"**Online:** {info['players_online']}/{info['max_players']} ({pct:.1f}%)"
                ),
                inline=False
            )
        else:
            embed.add_field(
                name=f"{idx}. [OFFLINE] {name}",
                value=f"**Keyword:** `{name}`\nOffline",
                inline=False
            )
    return embed


def build_search_embed(server_info: dict, nama: str) -> discord.Embed:
    results = [p for p in server_info['players'] if nama.lower() in p.get('name', '').lower()]

    embed = discord.Embed(
        title=f"{server_info['name']}",
        description=f"**Cari:** `{nama}`",
        color=0x00A8FF
    )

    if server_info.get('banner'):
        try:
            embed.set_image(url=server_info['banner'])
        except Exception:
            pass
    if server_info.get('icon'):
        try:
            embed.set_thumbnail(url=server_info['icon'])
        except Exception:
            pass

    embed.add_field(
        name="Server",
        value=f"**Online:** {server_info['players_online']}/{server_info['max_players']}",
        inline=False
    )

    if len(results) == 0:
        embed.add_field(name="Hasil", value="Tidak ada", inline=False)
    else:
        for idx, player in enumerate(results[:10], 1):
            embed.add_field(
                name=f"{idx}. {player.get('name')}",
                value=f"ID: `{player.get('id')}` | Ping: `{player.get('ping')}ms`",
                inline=False
            )
    return embed


def build_serverinfo_embed(info: dict, keyword: str) -> discord.Embed:
    pct = (info['players_online'] / info['max_players'] * 100) if info['max_players'] > 0 else 0

    embed = discord.Embed(title=f"{info['name']}", color=0x00A8FF)
    embed.add_field(name="Keyword", value=f"`{keyword}`", inline=False)

    if info.get('banner'):
        try:
            embed.set_image(url=info['banner'])
        except Exception:
            pass
    if info.get('icon'):
        try:
            embed.set_thumbnail(url=info['icon'])
        except Exception:
            pass

    embed.add_field(
        name="Status",
        value=f"**Online:** {info['players_online']}/{info['max_players']} ({pct:.1f}%)",
        inline=False
    )
    return embed


def build_online_embed(info: dict) -> discord.Embed:
    embed = discord.Embed(
        title=f"{info['name']}",
        description=f"**Total:** {info['players_online']} online",
        color=0x00FF00
    )
    for idx, p in enumerate(info['players'][:20], 1):
        embed.add_field(
            name=f"{idx}. {p.get('name')}",
            value=f"ID: `{p.get('id')}` | Ping: `{p.get('ping')}ms`",
            inline=False
        )
    return embed


def deny_embed() -> discord.Embed:
    return discord.Embed(
        title="Akses Ditolak",
        description="Kamu tidak punya role yang diizinkan untuk mengelola server.",
        color=discord.Color.red()
    )


# ============================================================
# View pagination daftar pemain online
# ============================================================

class PlayerListView(discord.ui.View):
    def __init__(self, server_name: str, players: list, per_page: int = 20):
        super().__init__(timeout=180)
        self.server_name = server_name
        self.players = players
        self.per_page = per_page
        self.page = 0
        self.max_page = max(0, (len(players) - 1) // per_page)
        self._update_buttons()

    def build_embed(self) -> discord.Embed:
        start = self.page * self.per_page
        chunk = self.players[start:start + self.per_page]

        embed = discord.Embed(
            title=f"{self.server_name}",
            description=f"**Total:** {len(self.players)} online",
            color=0x00FF00
        )
        for idx, p in enumerate(chunk, start + 1):
            embed.add_field(
                name=f"{idx}. {p.get('name')}",
                value=f"ID: `{p.get('id')}` | Ping: `{p.get('ping')}ms`",
                inline=False
            )
        embed.set_footer(text=f"Halaman {self.page + 1}/{self.max_page + 1}  -  {config.CREDIT_TEXT}")
        return embed

    def _update_buttons(self):
        self.prev_btn.disabled = self.page <= 0
        self.next_btn.disabled = self.page >= self.max_page

    @discord.ui.button(label="Sebelumnya", style=discord.ButtonStyle.secondary)
    async def prev_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.page > 0:
            self.page -= 1
        self._update_buttons()
        await interaction.response.edit_message(embed=self.build_embed(), view=self)

    @discord.ui.button(label="Berikutnya", style=discord.ButtonStyle.primary)
    async def next_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.page < self.max_page:
            self.page += 1
        self._update_buttons()
        await interaction.response.edit_message(embed=self.build_embed(), view=self)


# ============================================================
# Modal: Cari Player
# ============================================================

class SearchModal(discord.ui.Modal, title="Cari Player"):
    server = discord.ui.TextInput(
        label="Keyword Server",
        placeholder="contoh: indopride",
        required=True
    )
    nama = discord.ui.TextInput(
        label="Nama Player",
        placeholder="contoh: John",
        required=True
    )

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        info = await server_manager.get_server_info(str(self.server).lower())
        if not info:
            await interaction.followup.send(
                embed=discord.Embed(title="Server not found", color=discord.Color.red()),
                ephemeral=True
            )
            return
        embed = build_search_embed(info, str(self.nama))
        await interaction.followup.send(embed=embed, ephemeral=True)


# ============================================================
# Select server untuk aksi info / online
# ============================================================

class ServerSelect(discord.ui.Select):
    def __init__(self, action: str):
        self.action = action  # "info" atau "online"
        options = [
            discord.SelectOption(label=name, value=name, description=f"Kode: {code}")
            for name, code in list(server_manager.SERVERS.items())[:25]
        ]
        super().__init__(placeholder="Pilih server...", options=options, min_values=1, max_values=1)

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        keyword = self.values[0]
        info = await server_manager.get_server_info(keyword)
        if not info:
            await interaction.followup.send(
                embed=discord.Embed(title="Server offline / tidak ditemukan", color=discord.Color.red()),
                ephemeral=True
            )
            return
        if self.action == "info":
            embed = build_serverinfo_embed(info, keyword)
            await interaction.followup.send(embed=embed, ephemeral=True)
        else:
            view = PlayerListView(info['name'], info['players'])
            await interaction.followup.send(embed=view.build_embed(), view=view, ephemeral=True)


class ServerActionView(discord.ui.View):
    def __init__(self, action: str):
        super().__init__(timeout=120)
        self.add_item(ServerSelect(action))


# ============================================================
# Admin: modal tambah server + select hapus server
# ============================================================

class AddServerModal(discord.ui.Modal, title="Tambah Server"):
    nama = discord.ui.TextInput(
        label="Keyword Server",
        placeholder="tanpa spasi, contoh: indopride",
        required=True
    )
    code = discord.ui.TextInput(
        label="Kode CFX",
        placeholder="contoh: bak4pl",
        required=True
    )

    async def on_submit(self, interaction: discord.Interaction):
        if not server_manager.is_admin(interaction):
            await interaction.response.send_message(embed=deny_embed(), ephemeral=True)
            return

        nama = str(self.nama).lower().strip()
        code = str(self.code).strip()

        if not nama or not code:
            await interaction.response.send_message(
                embed=discord.Embed(
                    title="Input Tidak Valid",
                    description="Keyword dan kode server tidak boleh kosong.",
                    color=discord.Color.red()
                ),
                ephemeral=True
            )
            return

        if nama in server_manager.SERVERS:
            await interaction.response.send_message(
                embed=discord.Embed(
                    title="Server Sudah Ada",
                    description=f"Server `{nama}` sudah terdaftar dengan kode `{server_manager.SERVERS[nama]}`.",
                    color=discord.Color.orange()
                ),
                ephemeral=True
            )
            return

        server_manager.SERVERS[nama] = code
        server_manager.save_servers()

        await interaction.response.send_message(
            embed=discord.Embed(
                title="Server Ditambahkan",
                description=f"**Keyword:** `{nama}`\n**Kode:** `{code}`",
                color=discord.Color.green()
            ),
            ephemeral=True
        )


class RemoveServerSelect(discord.ui.Select):
    def __init__(self):
        options = [
            discord.SelectOption(label=name, value=name, description=f"Kode: {code}")
            for name, code in list(server_manager.SERVERS.items())[:25]
        ]
        super().__init__(placeholder="Pilih server untuk dihapus...", options=options, min_values=1, max_values=1)

    async def callback(self, interaction: discord.Interaction):
        if not server_manager.is_admin(interaction):
            await interaction.response.send_message(embed=deny_embed(), ephemeral=True)
            return

        nama = self.values[0]
        if nama not in server_manager.SERVERS:
            await interaction.response.send_message(
                embed=discord.Embed(
                    title="Server Tidak Ditemukan",
                    description=f"Server `{nama}` tidak ada di daftar.",
                    color=discord.Color.red()
                ),
                ephemeral=True
            )
            return

        removed_code = server_manager.SERVERS.pop(nama)
        server_manager.server_cache.pop(nama, None)
        server_manager.cache_timestamp.pop(nama, None)
        server_manager.save_servers()

        await interaction.response.send_message(
            embed=discord.Embed(
                title="Server Dihapus",
                description=f"**Keyword:** `{nama}`\n**Kode:** `{removed_code}`",
                color=discord.Color.green()
            ),
            ephemeral=True
        )


class RemoveServerView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=120)
        self.add_item(RemoveServerSelect())


class AdminPanelView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=120)

    @discord.ui.button(label="Tambah Server", style=discord.ButtonStyle.success)
    async def add_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not server_manager.is_admin(interaction):
            await interaction.response.send_message(embed=deny_embed(), ephemeral=True)
            return
        await interaction.response.send_modal(AddServerModal())

    @discord.ui.button(label="Hapus Server", style=discord.ButtonStyle.danger)
    async def remove_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not server_manager.is_admin(interaction):
            await interaction.response.send_message(embed=deny_embed(), ephemeral=True)
            return
        if not server_manager.SERVERS:
            await interaction.response.send_message(
                embed=discord.Embed(title="Kosong", description="Belum ada server terdaftar.", color=discord.Color.orange()),
                ephemeral=True
            )
            return
        await interaction.response.send_message(
            "Pilih server yang mau dihapus:", view=RemoveServerView(), ephemeral=True
        )


# ============================================================
# View utama lobby (persistent)
# ============================================================

class LobbyView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Daftar Server", style=discord.ButtonStyle.primary, custom_id="lobby:servers")
    async def servers_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer(ephemeral=True)
        embed = await build_servers_embed()
        await interaction.followup.send(embed=embed, ephemeral=True)

    @discord.ui.button(label="Cari Player", style=discord.ButtonStyle.success, custom_id="lobby:search")
    async def search_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(SearchModal())

    @discord.ui.button(label="Info Server", style=discord.ButtonStyle.secondary, custom_id="lobby:info")
    async def info_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not server_manager.SERVERS:
            await interaction.response.send_message(
                embed=discord.Embed(title="Kosong", description="Belum ada server terdaftar.", color=discord.Color.orange()),
                ephemeral=True
            )
            return
        await interaction.response.send_message("Pilih server:", view=ServerActionView("info"), ephemeral=True)

    @discord.ui.button(label="Player Online", style=discord.ButtonStyle.secondary, custom_id="lobby:online")
    async def online_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not server_manager.SERVERS:
            await interaction.response.send_message(
                embed=discord.Embed(title="Kosong", description="Belum ada server terdaftar.", color=discord.Color.orange()),
                ephemeral=True
            )
            return
        await interaction.response.send_message("Pilih server:", view=ServerActionView("online"), ephemeral=True)

    @discord.ui.button(label="Admin Panel", style=discord.ButtonStyle.danger, custom_id="lobby:admin")
    async def admin_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not server_manager.is_admin(interaction):
            await interaction.response.send_message(embed=deny_embed(), ephemeral=True)
            return
        embed = discord.Embed(
            title="Panel Admin",
            description="Kelola daftar server di bawah ini.",
            color=discord.Color.blurple()
        )
        await interaction.response.send_message(embed=embed, view=AdminPanelView(), ephemeral=True)


# ============================================================
# Cog
# ============================================================

class LobbyCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="lobby", description="Tampilkan panel lobby dengan semua fitur")
    async def lobby(self, interaction: discord.Interaction):
        embed = discord.Embed(
            title="Lobby Panel",
            description=(
                "Selamat datang! Pilih menu di bawah:\n\n"
                "**Daftar Server** - lihat semua server & status\n"
                "**Cari Player** - cari pemain di server\n"
                "**Info Server** - detail sebuah server\n"
                "**Player Online** - daftar pemain online\n"
                "**Admin Panel** - kelola server (khusus admin)"
            ),
            color=0x00A8FF
        )
        # Banner gambar (kalau URL diisi di config)
        if config.LOBBY_BANNER:
            embed.set_image(url=config.LOBBY_BANNER)
        # Credit di footer
        embed.set_footer(text=config.CREDIT_TEXT)
        await interaction.response.send_message(embed=embed, view=LobbyView())


async def setup(bot: commands.Bot):
    await bot.add_cog(LobbyCog(bot))
    # Daftarkan view persistent agar tombol tetap aktif setelah bot restart
    bot.add_view(LobbyView())
