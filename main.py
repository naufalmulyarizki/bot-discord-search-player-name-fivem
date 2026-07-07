import discord
from discord.ext import commands

import config
import server_manager

intents = discord.Intents.default()
intents.message_content = True


class FiveMBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix='/', intents=intents)

    async def setup_hook(self):
        # Muat daftar server dari file
        server_manager.load_servers()

        # Load semua modul (cog)
        for ext in config.COGS:
            try:
                await self.load_extension(ext)
                print(f"[LOAD] {ext}")
            except Exception as e:
                print(f"[LOAD] Gagal {ext}: {e}")

        # Sync slash command
        try:
            synced = await self.tree.sync()
            print(f"[SYNC] {len(synced)} commands")
        except Exception as e:
            print(f"[SYNC] Error {e}")

    async def on_ready(self):
        print(f'\n[READY] Bot: {self.user}\n')


bot = FiveMBot()

if __name__ == "__main__":
    print("Bot Discord FiveM (Direct API)")
    bot.run(config.TOKEN)
