import discord
from discord import app_commands
from discord.ext import commands

import server_manager


class AdminCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="addserver", description="[Admin] Tambah server ke daftar")
    @app_commands.describe(
        nama="Keyword server (untuk dipanggil di command lain, tanpa spasi)",
        code="Kode CFX server (contoh: bak4pl)"
    )
    async def addserver(self, interaction: discord.Interaction, nama: str, code: str):
        if not server_manager.is_admin(interaction):
            embed = discord.Embed(
                title="Akses Ditolak",
                description="Kamu tidak punya role yang diizinkan untuk mengelola server.",
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        nama = nama.lower().strip()
        code = code.strip()

        if not nama or not code:
            embed = discord.Embed(
                title="Input Tidak Valid",
                description="Keyword dan kode server tidak boleh kosong.",
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        if nama in server_manager.SERVERS:
            embed = discord.Embed(
                title="Server Sudah Ada",
                description=f"Server `{nama}` sudah terdaftar dengan kode `{server_manager.SERVERS[nama]}`.",
                color=discord.Color.orange()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        server_manager.SERVERS[nama] = code
        server_manager.save_servers()

        embed = discord.Embed(
            title="Server Ditambahkan",
            description=f"**Keyword:** `{nama}`\n**Kode:** `{code}`",
            color=discord.Color.green()
        )
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="removeserver", description="[Admin] Hapus server dari daftar")
    @app_commands.describe(nama="Keyword server yang mau dihapus")
    async def removeserver(self, interaction: discord.Interaction, nama: str):
        if not server_manager.is_admin(interaction):
            embed = discord.Embed(
                title="Akses Ditolak",
                description="Kamu tidak punya role yang diizinkan untuk mengelola server.",
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        nama = nama.lower().strip()

        if nama not in server_manager.SERVERS:
            embed = discord.Embed(
                title="Server Tidak Ditemukan",
                description=f"Server `{nama}` tidak ada di daftar.",
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        removed_code = server_manager.SERVERS.pop(nama)
        # Bersihkan cache server yang dihapus
        server_manager.server_cache.pop(nama, None)
        server_manager.cache_timestamp.pop(nama, None)
        server_manager.save_servers()

        embed = discord.Embed(
            title="Server Dihapus",
            description=f"**Keyword:** `{nama}`\n**Kode:** `{removed_code}`",
            color=discord.Color.green()
        )
        await interaction.response.send_message(embed=embed)


async def setup(bot: commands.Bot):
    await bot.add_cog(AdminCog(bot))
