import discord
from discord import app_commands, ui
from discord.ext import commands, tasks
import json
import os
import asyncio
import random
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
from flask import Flask
from threading import Thread
import logging

# Configure professional logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("WangBot")

# Flask for 24/7 uptime
app = Flask(__name__)

@app.route('/')
@app.route('/health')
@app.route('/api/status')
def status():
    return {
        "status": "🟢 ACTIVE",
        "version": "2.0.0",
        "players": len(user_data),
        "uptime": "24/7",
        "timestamp": datetime.now().isoformat()
    }

def run_flask():
    app.run(host='0.0.0.0', port=10000, debug=False)

flask_thread = Thread(target=run_flask, daemon=True)
flask_thread.start()

# ==================== DATA MANAGER ====================
class DataManager:
    def __init__(self, filename: str = "wang_production.json"):
        self.filename = filename
        self.data: Dict[str, Dict[str, Any]] = {}
        self.load()
    
    def load(self):
        try:
            if os.path.exists(self.filename):
                with open(self.filename, 'r', encoding='utf-8') as f:
                    self.data = json.load(f)
                logger.info(f"Loaded {len(self.data)} players")
        except Exception as e:
            logger.error(f"Load error: {e}")
            self.data = {}
    
    def save(self):
        try:
            with open(self.filename, 'w', encoding='utf-8') as f:
                json.dump(self.data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Save error: {e}")
    
    def get_player(self, user_id: str) -> Dict[str, Any]:
        if user_id not in self.data:
            self.data[user_id] = {
                "started": False,
                "bones": 0,
                "daily_streak": 0,
                "last_daily": 0,
                "total_dailies": 0,
                "hunts": 0,
                "created_at": datetime.now().isoformat(),
                "profile": {
                    "username": "",
                    "avatar": ""
                }
            }
            self.save()
        return self.data[user_id]

# Global data manager
data_manager = DataManager()

# ==================== PRO BOT ====================
intents = discord.Intents.default()
bot = discord.Client(intents=intents)
tree = app_commands.CommandTree(bot)

@bot.event
async def on_ready():
    await tree.sync()
    logger.info(f"🐕 Wang Pro Bot LIVE as {bot.user} | {len(data_manager.data)} players")
    print("🎮 Commands synced! Bot ready!")

# ==================== SLASH COMMANDS ====================
@tree.command(name="start", description="🚀 Begin your Wang Adventure (One-time only)")
@app_commands.describe(reason="Why start?")
async def start(interaction: discord.Interaction, reason: str = "Adventure!"):
    player = data_manager.get_player(str(interaction.user.id))
    
    if player["started"]:
        embed = discord.Embed(
            title="❌ Already Started!", 
            description="Use `/daily`, `/hunt`, `/inv`",
            color=0xff4444
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return
    
    # First time rewards
    player["bones"] = 10000
    player["started"] = True
    player["profile"]["username"] = str(interaction.user)
    player["profile"]["avatar"] = str(interaction.user.avatar.url) if interaction.user.avatar else ""
    data_manager.save()
    
    embed = discord.Embed(title="🎉 **Welcome to Wang World!** 🚀", color=0xffa500)
    embed.add_field(name="💰 **Starter Pack**", value="**10,000 Bones** ✨", inline=False)
    embed.add_field(name="📋 **Game Guide**", value="`/daily` → Daily rewards\n`/hunt` → Find treasure\n`/inv` → Stats & profile", inline=False)
    embed.add_field(name="🏆 **Goal**", value="**Hunt daily → Become richest!** 💎", inline=False)
    embed.add_field(name="👤 **Player**", value=f"{interaction.user.mention}", inline=False)
    embed.set_thumbnail(url="https://i.imgur.com/pro-dog.png")
    embed.timestamp = datetime.now()
    
    view = ui.View()
    ui.Button(label="Claim Daily Now!", style=discord.ButtonStyle.green, custom_id="daily_btn")
    await interaction.response.send_message(embed=embed, view=view)

@tree.command(name="daily", description="💰 Claim daily + streak bonus (24h)")
async def daily(interaction: discord.Interaction):
    player = data_manager.get_player(str(interaction.user.id))
    
    if not player["started"]:
        await interaction.response.send_message("❌ **`/start` first!**", ephemeral=True)
        return
    
    now = datetime.now().timestamp()
    last_daily = player.get("last_daily", 0)
    
    # 24h cooldown check
    if now - last_daily < 86400:
        remaining = 86400 - (now - last_daily)
        hours = int(remaining // 3600)
        minutes = int((remaining % 3600) // 60)
        embed = discord.Embed(
            title="⏰ Daily Cooldown",
            description=f"**{hours}h {minutes}m** remaining",
            color=0xffaa00
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return
    
    # Streak system (professional logic)
    streak = player.get("daily_streak", 0)
    if last_daily > 0 and now - last_daily < 86400 * 1.5:  # Within ~36h
        streak += 1
    else:
        streak = 1
    
    # Pro reward system: 1000 base + 14×streak
    base_reward = 1000
    streak_bonus = 14 * streak
    total_reward = base_reward + streak_bonus
    
    player["bones"] += total_reward
    player["last_daily"] = now
    player["daily_streak"] = streak
    player["total_dailies"] += 1
    data_manager.save()
    
    embed = discord.Embed(title="💰 **Daily Reward!**", color=0x00ff88)
    embed.add_field(name="🎁 Base", value="1,000", inline=True)
    embed.add_field(name="⭐ Streak x{}".format(streak), value=f"+{streak_bonus:,}", inline=True)
    embed.add_field(name="💎 **TOTAL**", value=f"**{total_reward:,}**", inline=True)
    embed.add_field(name="💰 New Balance", value=f"{player['bones']:,}", inline=True)
    embed.set_footer(text=f"Streak: {streak} | Total dailies: {player['total_dailies']}")
    embed.timestamp = datetime.now()
    
    await interaction.response.send_message(embed=embed)

@tree.command(name="inv", description="📦 Inventory & Stats")
async def inv(interaction: discord.Interaction):
    player = data_manager.get_player(str(interaction.user.id))
    
    if not player["started"]:
        await interaction.response.send_message("❌ **`/start` first!**", ephemeral=True)
        return
    
    embed = discord.Embed(title=f"📦 {interaction.user.display_name}'s Stats", color=0x5865f2)
    embed.add_field(name="💰 Bones", value=f"{player['bones']:,}", inline=True)
    embed.add_field(name="🔥 Streak", value=player.get("daily_streak", 0), inline=True)
    embed.add_field(name="📅 Total Dailies", value=player.get("total_dailies", 0), inline=True)
    embed.add_field(name="🏹 Hunts", value=player.get("hunts", 0), inline=True)
    embed.set_thumbnail(url=player["profile"].get("avatar", ""))
    embed.timestamp = datetime.now()
    
    await interaction.response.send_message(embed=embed)

@tree.command(name="hunt", description="🏹 Hunt for treasure!")
async def hunt(interaction: discord.Interaction):
    player = data_manager.get_player(str(interaction.user.id))
    
    if not player["started"]:
        await interaction.response.send_message("❌ **`/start` first!**", ephemeral=True)
        return
    
    reward = random.randint(200, 1200)
    player["bones"] += reward
    player["hunts"] = player.get("hunts", 0) + 1
    data_manager.save()
    
    embed = discord.Embed(
        title="🏹 **Treasure Hunt!**",
        description=f"**+{reward:,} bones** found! 💰\n*Perfect hunt!*",
        color=0xffd700
    )
    embed.set_footer(text=f"Total hunts: {player['hunts']}")
    
    await interaction.response.send_message(embed=embed)

bot.run(os.getenv('MTQ2Nzc4NzI4ODIzMzY0MDAzMw.GR608-.Ux1g5oQUVmsgGGuHq5RjP2aUVTp1-k0PukETN0'))
