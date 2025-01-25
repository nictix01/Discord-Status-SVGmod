import discord
from discord import app_commands
from discord.ext import commands, tasks
from utils.server_status import get_server_status
from config.settings import *
import fade
import os

os.system('cls' if os.name == 'nt' else 'clear')

banner = """
███████ ██████   █████  ██     ██  █████  ██████  ██████  
██      ██   ██ ██   ██ ██     ██ ██   ██ ██   ██ ██   ██ 
█████   ██   ██ ███████ ██  █  ██ ███████ ██████  ██   ██ 
██      ██   ██ ██   ██ ██ ███ ██ ██   ██ ██   ██ ██   ██ 
███████ ██████  ██   ██  ███ ███  ██   ██ ██   ██ ██████  
V.1.0.0"""

b = fade.brazil(banner)
print(b)

class StatusBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        super().__init__(command_prefix="!", intents=intents)
        self.active_statuses = {}

    async def setup_hook(self):
        self.status_loop.start()

    @tasks.loop(seconds=UPDATE_INTERVAL)
    async def status_loop(self):
        for message_id, (ip, port, message) in list(self.active_statuses.items()):
            try:
                status = get_server_status(ip, port)
                embed = discord.Embed(
                    title="Server Status", 
                    color=discord.Color.green() if status["success"] else discord.Color.red()
                )
                
                if status["success"]:
                    embed.add_field(name="Server Name", value=status["name"], inline=False)
                    embed.add_field(name="Map", value=status["map"], inline=True)
                    embed.add_field(name="Players", value=status["players"], inline=True)
                    embed.add_field(name="Players List", value=status["players_list"], inline=True)
                    embed.add_field(name="Game", value=status["game"], inline=True)
                    embed.add_field(name="IP:Port", value=f"{ip}:{port}", inline=False)
                else:
                    embed.description = f"Server {ip}:{port} is offline"
                
                await message.edit(embed=embed)
            except Exception as e:
                print(f"Error updating status: {e}")
                self.active_statuses.pop(message_id, None)

    @status_loop.before_loop
    async def before_status_loop(self):
        await self.wait_until_ready()

bot = StatusBot()

def is_admin():
    def predicate(interaction: discord.Interaction):
        return any(role.name == ADMIN_ROLE_NAME for role in interaction.user.roles)
    return app_commands.check(predicate)

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')
    try:
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} command(s)")
    except Exception as e:
        print(e)

@bot.tree.command(name="status", description="Check GMod server status")
@is_admin()
async def status(interaction: discord.Interaction, ip: str, port: int):
    await interaction.response.defer()
    
    status = get_server_status(ip, port)
    embed = discord.Embed(
        title="Server Status", 
        color=discord.Color.green() if status["success"] else discord.Color.red()
    )
    
    if status["success"]:
        embed.add_field(name="Server Name", value=status["name"], inline=False)
        embed.add_field(name="Map", value=status["map"], inline=True)
        embed.add_field(name="Players", value=status["players"], inline=True)
        embed.add_field(name="Players List", value=status["players_list"], inline=True)
        embed.add_field(name="Game", value=status["game"], inline=True)
        embed.add_field(name="IP:Port", value=f"{ip}:{port}", inline=False)
    else:
        embed.description = f"Server {ip}:{port} is offline"
    
    message = await interaction.followup.send(embed=embed)
    bot.active_statuses[message.id] = (ip, port, message)

@status.error
async def status_error(interaction: discord.Interaction, error):
    if isinstance(error, app_commands.CheckFailure):
        await interaction.response.send_message(
            "You need admin permissions to use this command!", 
            ephemeral=True
        )

bot.run(BOT_TOKEN)