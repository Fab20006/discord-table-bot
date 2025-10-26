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

// Fonction pour générer l'image du tableau
async function generateTableImage(tableText) {
  try {
    console.log('📊 Génération du tableau...');
    const response = await axios.post('https://gb.hlorenzi.com/api/table', {
      data: tableText
    }, {
      responseType: 'arraybuffer',
      timeout: 30000
    });

    console.log('✅ Tableau généré avec succès');
    return Buffer.from(response.data);
  } catch (error) {
    console.error('❌ Erreur API:', error.message);
    throw new Error('Le service de génération est temporairement indisponible');
  }
}

// Quand le bot est prêt
client.on('ready', () => {
  console.log(`✅ Bot connecté en tant que ${client.user.tag}`);
  console.log(`📊 Servant ${client.guilds.cache.size} serveurs`);
  client.user.setActivity('/maketable', { type: 'PLAYING' });
});

// Quand un message est envoyé
client.on('messageCreate', async (message) => {
  // Ignorer les messages des autres bots
  if (message.author.bot) return;

  // Réagir seulement à /maketable
  if (message.content.startsWith('/maketable')) {
    try {
      console.log(`🔄 Traitement demande de ${message.author.tag}`);
      
      // Message "en cours de traitement"
      const processingMsg = await message.reply('🔄 Génération du tableau en cours...');
      
      // Extraire le texte du tableau
      const lines = message.content.split('\n');
      lines.shift(); // Retirer /maketable
      const tableText = lines.join('\n').trim();
      
      // Vérifier si le tableau n'est pas vide
      if (!tableText) {
        await processingMsg.edit('❌ **Format incorrect!**\n\n**Exemple d\'utilisation:**\n```/maketable\nTag1 - Équipe Rouge\nJoueur1 1500\nJoueur2 1400\nJoueur3 1300\n\nTag2 - Équipe Bleue\nJoueur4 1500\nJoueur5 1400\nJoueur6 1300```');
        return;
      }

      // Générer l'image
      const imageBuffer = await generateTableImage(tableText);
      
      // Envoyer l'image
      await message.channel.send({
        content: `📊 Tableau généré pour ${message.author}`,
        files: [{ attachment: imageBuffer, name: 'tableau.png' }]
      });
      
      // Supprimer le message "en cours"
      await processingMsg.delete();
      
    } catch (error) {
      console.error('❌ Erreur:', error);
      await message.reply('❌ **Erreur:** ' + error.message);
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

// Démarrer le bot avec le token
const token = process.env.DISCORD_TOKEN;
if (!token) {
  console.error('❌ Token Discord manquant!');
  process.exit(1);
}

client.login(token);