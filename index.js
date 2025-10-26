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

// Fonction pour générer l'image - VERSION CORRECTE
async function generateTableImage(tableText) {
  try {
    console.log('📊 Génération du tableau...');
    
    // URL directe de l'API de génération
    const response = await axios.get('https://gb.hlorenzi.com/api.png', {
      params: {
        data: tableText
      },
      responseType: 'arraybuffer',
      timeout: 30000,
      headers: {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
      }
    });

    console.log('✅ Tableau généré avec succès!');
    return Buffer.from(response.data);
    
  } catch (error) {
    console.error('❌ Erreur API:', error.message);
    
    // Message d'erreur plus détaillé
    if (error.response?.status === 404) {
      throw new Error('Service de génération non trouvé. Le site peut avoir changé.');
    } else if (error.code === 'ECONNREFUSED') {
      throw new Error('Impossible de se connecter au service de génération.');
    } else {
      throw new Error('Erreur lors de la génération: ' + error.message);
    }
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
      
      // Extraire le texte du tableau
      const lines = message.content.split('\n');
      lines.shift(); // Retirer /maketable
      const tableText = lines.join('\n').trim();
      
      // Vérification du format
      if (!tableText) {
        await processingMsg.edit('❌ **Format incorrect!**\n\n**Exemple d\'utilisation:**\n```/maketable\nTag1 - Équipe Rouge\nJoueur1 1500\nJoueur2 1400\nJoueur3 1300\n\nTag2 - Équipe Bleue\nJoueur4 1500\nJoueur5 1400\nJoueur6 1300```');
        return;
      }

      console.log('📋 Texte à générer:', tableText.substring(0, 100) + '...');
      
      // Générer l'image
      const imageBuffer = await generateTableImage(tableText);
      
      // Envoyer l'image
      await message.channel.send({
        content: `📊 Tableau généré pour ${message.author}`,
        files: [{ 
          attachment: imageBuffer, 
          name: 'tableau.png' 
        }]
      });
      
      // Supprimer le message "en cours"
      await processingMsg.delete();
      
    } catch (error) {
      console.error('❌ Erreur finale:', error);
      
      let errorMessage = '❌ **Erreur:** ' + error.message;
      
      // Suggestions selon l'erreur
      if (error.message.includes('non trouvé') || error.message.includes('404')) {
        errorMessage += '\n\n💡 **Solution:** Le site https://gb.hlorenzi.com/table pourrait être en maintenance.';
      } else if (error.message.includes('format')) {
        errorMessage += '\n\n💡 **Vérifiez le format de votre message.**';
      }
      
      await message.reply(errorMessage);
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