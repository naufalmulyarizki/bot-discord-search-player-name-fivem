import discord
from discord import app_commands
from discord.ext import commands

import server_manager


class ServersCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="servers", description="Lihat daftar semua server")
    async def servers(self, interaction: discord.Interaction):
        await interaction.response.defer()

        embed = discord.Embed(
            title="Daftar Server",
            description="Gunakan **keyword** di bawah untuk perintah `/search`, `/serverinfo`, atau `/online`.",
            color=discord.Color.gold()
        )

        if not server_manager.SERVERS:
            embed.add_field(name="Kosong", value="Belum ada server terdaftar.", inline=False)
            await interaction.followup.send(embed=embed)
            return

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

        await interaction.followup.send(embed=embed)

    @app_commands.command(name="serverinfo", description="Detail sebuah server")
    @app_commands.describe(server="Keyword server")
    async def serverinfo(self, interaction: discord.Interaction, server: str):
        await interaction.response.defer()

        info = await server_manager.get_server_info(server.lower())

        if not info:
            embed = discord.Embed(title="Not found", color=discord.Color.red())
            await interaction.followup.send(embed=embed)
            return

        pct = (info['players_online'] / info['max_players'] * 100) if info['max_players'] > 0 else 0

        embed = discord.Embed(title=f"{info['name']}", color=0x00A8FF)
        embed.add_field(name="Keyword", value=f"`{server.lower()}`", inline=False)

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

        await interaction.followup.send(embed=embed)

    @app_commands.command(name="online", description="Pemain yang sedang online")
    @app_commands.describe(server="Keyword server")
    async def online(self, interaction: discord.Interaction, server: str):
        await interaction.response.defer()

        info = await server_manager.get_server_info(server.lower())

        if not info:
            embed = discord.Embed(title="Offline", color=discord.Color.red())
            await interaction.followup.send(embed=embed)
            return

        from cogs.lobby_cog import PlayerListView

        view = PlayerListView(info['name'], info['players'])
        await interaction.followup.send(embed=view.build_embed(), view=view)


async def setup(bot: commands.Bot):
    await bot.add_cog(ServersCog(bot))
