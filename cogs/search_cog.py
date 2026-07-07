import discord
from discord import app_commands
from discord.ext import commands

import server_manager


class SearchCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="search", description="Cari pemain di server")
    @app_commands.describe(server="Keyword server", nama="Nama pemain")
    async def search(self, interaction: discord.Interaction, server: str, nama: str):
        await interaction.response.defer()

        server_info = await server_manager.get_server_info(server.lower())

        if not server_info:
            embed = discord.Embed(title="Server not found", color=discord.Color.red())
            await interaction.followup.send(embed=embed)
            return

        results = [p for p in server_info['players'] if nama.lower() in p.get('name', '').lower()]

        embed = discord.Embed(
            title=f"{server_info['name']}",
            description=f"**Cari:** `{nama}`",
            color=0x00A8FF
        )

        # Banner
        if server_info.get('banner'):
            try:
                embed.set_image(url=server_info['banner'])
            except Exception:
                pass

        # Icon
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

        await interaction.followup.send(embed=embed)


async def setup(bot: commands.Bot):
    await bot.add_cog(SearchCog(bot))
