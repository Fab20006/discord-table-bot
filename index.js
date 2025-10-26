const { Client, GatewayIntentBits } = require('discord.js');
const axios = require('axios');

console.log('🚀 Démarrage du bot...');

const client = new Client({
  intents: [
    GatewayIntentBits.Guilds,
    GatewayIntentBits.GuildMessages,
    GatewayIntentBits.MessageContent
  ]
});

// Fonction pour générer l'image du tableau (CORRIGÉE)
async function generateTableImage(tableText) {
  try {
    console.log('📊 Génération du tableau...');
    console.log('Texte envoyé:', tableText);
    
    // URL corrigée - celle du site web directement
    const response = await axios.post('https://gb.hlorenzi.com/generate', 
      { input: tableText },  // Le paramètre peut être différent
      {
        responseType: 'arraybuffer',
        timeout: 30000,
        headers: {
          'Content-Type': 'application/json',
          'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
      }
    );

    console.log('✅ Tableau généré avec succès');
    return Buffer.from(response.data);
  } catch (error) {
    console.error('❌ Erreur API:', error.message);
    console.error('Status:', error.response?.status);
    console.error('URL:', error.config?.url);
    throw new Error('Impossible de générer le tableau. Vérifiez le format de votre message.');
  }
}

// Version alternative si l'API POST ne fonctionne pas
async function generateTableImageAlternative(tableText) {
  try {
    console.log('📊 Tentative avec méthode alternative...');
    
    // Essayer avec FormData comme sur le site web
    const FormData = require('form-data');
    const form = new FormData();
    form.append('input', tableText);
    
    const response = await axios.post('https://gb.hlorenzi.com/generate', 
      form,
      {
        responseType: 'arraybuffer',
        timeout: 30000,
        headers: {
          ...form.getHeaders(),
          'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
      }
    );

    console.log('✅ Tableau généré avec succès (méthode alternative)');
    return Buffer.from(response.data);
  } catch (error) {
    console.error('❌ Erreur méthode alternative:', error.message);
    throw error;
  }
}

// Quand le bot est prêt
client.once('clientReady', () => {
  console.log(`✅ Bot connecté en tant que ${client.user.tag}`);
  console.log(`📊 Servant ${client.guilds.cache.size} serveurs`);
  client.user.setActivity('/maketable', { type: 'PLAYING' });
});

// Quand un message est envoyé
client.on('messageCreate', async (message) => {
  if (message.author.bot) return;

  if (message.content.startsWith('/maketable')) {
    try {
      console.log(`🔄 Traitement demande de ${message.author.tag}`);
      
      const processingMsg = await message.reply('🔄 Génération du tableau en cours...');
      
      const lines = message.content.split('\n');
      lines.shift();
      const tableText = lines.join('\n').trim();
      
      if (!tableText) {
        await processingMsg.edit('❌ **Format incorrect!**\n\n**Exemple:**\n```/maketable\nTag1 - Équipe Rouge\nJoueur1 1500\nJoueur2 1400\n\nTag2 - Équipe Bleue\nJoueur3 1500\nJoueur4 1400```');
        return;
      }

      // Essayer la méthode principale d'abord, puis l'alternative
      let imageBuffer;
      try {
        imageBuffer = await generateTableImage(tableText);
      } catch (firstError) {
        console.log('🔄 Essai méthode alternative...');
        imageBuffer = await generateTableImageAlternative(tableText);
      }
      
      await message.channel.send({
        content: `📊 Tableau généré pour ${message.author}`,
        files: [{ attachment: imageBuffer, name: 'tableau.png' }]
      });
      
      await processingMsg.delete();
      
    } catch (error) {
      console.error('❌ Erreur finale:', error);
      await message.reply('❌ **Erreur:** ' + error.message + '\n\nVérifiez le format de votre message.');
    }
  }
});

// Gestion des erreurs
client.on('error', (error) => {
  console.error('❌ Erreur du client:', error);
});

process.on('unhandledRejection', (error) => {
  console.error('❌ Erreur non gérée:', error);
});

const token = process.env.DISCORD_TOKEN;
if (!token) {
  console.error('❌ Token Discord manquant!');
  process.exit(1);
}

client.login(token);