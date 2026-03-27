require('dotenv').config();
const { Client, GatewayIntentBits, Collection } = require('discord.js');
const fs = require('fs');
const client = new Client({ intents: [GatewayIntentBits.Guilds] });

const DATA_FILE = './data.json';

// ====== Data helpers ======
function loadData() {
  if (!fs.existsSync(DATA_FILE)) return {};
  return JSON.parse(fs.readFileSync(DATA_FILE));
}
function saveData(data) {
  fs.writeFileSync(DATA_FILE, JSON.stringify(data, null, 2));
}
function getUser(id) {
  const data = loadData();
  if (!data[id]) {
    data[id] = {
      gold: 100,
      xp: 0,
      level: 1,
      inventory: [],
      weapon: null,
      lastDaily: 0
    };
    saveData(data);
  }
  return data[id];
}

// ====== Commands ======
client.commands = new Collection();

client.commands.set('start', {
  description: 'Start your RPG journey',
  execute: async (interaction) => {
    getUser(interaction.user.id); // init user
    await interaction.reply('✅ Your RPG journey started! You have 100 gold.');
  }
});

client.commands.set('daily', {
  description: 'Claim daily reward',
  execute: async (interaction) => {
    const user = getUser(interaction.user.id);
    const now = Date.now();
    if (now - user.lastDaily < 24*60*60*1000) {
      await interaction.reply('⏳ You already claimed your daily reward today.');
      return;
    }
    const gold = Math.floor(Math.random() * 100) + 50;
    user.gold += gold;
    user.lastDaily = now;
    saveData(loadData());
    await interaction.reply(`💰 You got ${gold} gold!`);
  }
});

client.commands.set('hunt', {
  description: 'Go hunting!',
  execute: async (interaction) => {
    const user = getUser(interaction.user.id);
    const monsters = ['🐺 Wolf','🧟 Zombie','🦇 Bat','🐉 Dragon'];
    const monster = monsters[Math.floor(Math.random() * monsters.length)];
    const gold = Math.floor(Math.random() * 50) + 10;
    const xp = Math.floor(Math.random() * 20) + 5;

    user.gold += gold;
    user.xp += xp;

    if (user.xp >= user.level * 100) {
      user.xp = 0;
      user.level += 1;
    }

    saveData(loadData());

    await interaction.reply(`⚔️ You defeated ${monster}!\n💰 +${gold} gold\n⭐ +${xp} XP`);
  }
});

client.commands.set('equip', {
  description: 'Equip a weapon',
  execute: async (interaction) => {
    const user = getUser(interaction.user.id);
    if (user.inventory.length === 0) {
      await interaction.reply('❌ You have no items to equip.');
      return;
    }
    user.weapon = user.inventory[0]; // example: equip first item
    saveData(loadData());
    await interaction.reply(`⚔️ You equipped ${user.weapon}`);
  }
});

client.commands.set('inventory', {
  description: 'Check your inventory',
  execute: async (interaction) => {
    const user = getUser(interaction.user.id);
    const inv = user.inventory.length ? user.inventory.join(', ') : 'Empty';
    await interaction.reply(`🎒 Inventory: ${inv}`);
  }
});

// ====== Ready ======
client.once('ready', () => {
  console.log(`${client.user.tag} is online!`);
});

// ====== Interaction ======
client.on('interactionCreate', async interaction => {
  if (!interaction.isChatInputCommand()) return;
  const command = client.commands.get(interaction.commandName);
  if (!command) return;
  try {
    await command.execute(interaction);
  } catch (err) {
    console.error(err);
    await interaction.reply({ content: '❌ Error executing command', ephemeral: true });
  }
});

// ====== Login ======
client.login(process.env.MTQ2Nzc4NzI4ODIzMzY0MDAzMw.GD_O4U.kWCbEY9RXokgOt9KMZUxq1s6A3Zk8WO-gSpxsc);
