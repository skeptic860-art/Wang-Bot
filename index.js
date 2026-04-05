from flask import Flask
from threading import Thread
import discord
from discord import app_commands
import os, random, json
from datetime import datetime

app = Flask('')

@app.route('/')
@app.route('/health')
def home():
    return {"wang_bot": "🟢 24/7 ONLINE!", "players": len(user_data) if 'user_data' in globals() else 0}

def run_flask():
    app.run(host='0.0.0.0', port=3000)

Thread(target=run_flask).start()

# === WANG BOT RPG ===
USER_DATA_FILE = "users.json"
user_data = {}

def load_data():
    global user_data
    try:
        if os.path.exists(USER_DATA_FILE):
            with open(USER_DATA_FILE, 'r') as f:
                user_data = json.load(f)
    except: pass

def save_data():
    with open(USER_DATA_FILE, 'w') as f:
        json.dump(user_data, f)

load_data()

def init_player(user_id):
    if user_id not in user_data:
        user_data[user_id] = {"level":1,"xp":0,"bones":100,"daily_last":0,"hunt_last":0,"pets":["🐕 Good Doggo"]}
        save_data()

intents = discord.Intents.default()
bot = discord.Client(intents=intents)
tree = app_commands.CommandTree(bot)

@bot.event
async def on_ready():
    await tree.sync()
    print(f'🐕 Wang Bot LIVE as {bot.user}!')

@tree.command(name="start", description="🐕 Start Wang Adventure!")
async def start(interaction: discord.Interaction):
    init_player(str(interaction.user.id))
    embed = discord.Embed(title="🐾 Welcome!", description="💰 100 Bones\n🐕 Good Doggo\n⚔️ Level 1", color=0xffa500)
    await interaction.response.send_message(embed=embed)

@tree.command(name="daily", description="💰 Daily bones!")
async def daily(interaction: discord.Interaction):
    uid = str(interaction.user.id)
    init_player(uid)
    now = datetime.now().timestamp()
    if now - user_data[uid]["daily_last"] < 86400:
        await interaction.response.send_message("⏰ Wait 24h!")
        return
    reward = random.randint(50,150)
    user_data[uid]["bones"] += reward
    user_data[uid]["daily_last"] = now
    save_data()
    await interaction.response.send_message(f"🎁 +{reward} bones!")

@tree.command(name="profile", description="📊 Your stats")
async def profile(interaction: discord.Interaction):
    uid = str(interaction.user.id)
    init_player(uid)
    p = user_data[uid]
    embed = discord.Embed(title="📊 Profile", color=0xffa500)
    embed.add_field(name="⚔️", value=p["level"], inline=True)
    embed.add_field(name="⭐", value=f"{p['xp']}", inline=True)
    embed.add_field(name="💰", value=f"{p['bones']}", inline=True)
    await interaction.response.send_message(embed=embed)

@tree.command(name="hunt", description="🏹 Hunt for loot!")
async def hunt(interaction: discord.Interaction):
    uid = str(interaction.user.id)
    init_player(uid)
    now = datetime.now().timestamp()
    if now - user_data[uid]["hunt_last"] < 3600:
        await interaction.response.send_message("⏰ 1h cooldown!")
        return
    bones = random.randint(20,80)
    user_data[uid]["bones"] += bones
    user_data[uid]["hunt_last"] = now
    save_data()
    if random.random() < 0.15:
        pet = random.choice(["🐩 Fluffy", "🐶 Big Woof"])
        user_data[uid]["pets"].append(pet)
        save_data()
        await interaction.response.send_message(f"🏹 +{bones} bones + {pet}!")
    else:
        await interaction.response.send_message(f"🏹 +{bones} bones!")

@tree.command(name="fight", description="⚔️ Fight for XP!")
async def fight(interaction: discord.Interaction):
    uid = str(interaction.user.id)
    init_player(uid)
    if random.random() < 0.7:
        xp = random.randint(20,50)
        user_data[uid]["xp"] += xp
        save_data()
        await interaction.response.send_message(f"✅ Victory! +{xp} XP")
    else:
        await interaction.response.send_message("💥 Defeat! Try again!")

bot.run(os.getenv('MTQ2Nzc4NzI4ODIzMzY0MDAzMw.GR608-.Ux1g5oQUVmsgGGuHq5RjP2aUVTp1-k0PukETN0'))
