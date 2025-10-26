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

// Fonction pour générer l'image - NOUVELLE APPROCHE
async function generateTableImage(tableText) {
  try {
    console.log('📊 Tentative de génération d\'image...');
    
    // Essayer différentes URLs d'API possibles
    const attempts = [
      {
        name: 'API directe avec data',
        url: 'https://gb.hlorenzi.com/api.png',
        method: 'get',
        params: { data: tableText }
      },
      {
        name: 'API avec input', 
        url: 'https://gb.hlorenzi.com/api.png',
        method: 'get',
        params: { input: tableText }
      },
      {
        name: 'Endpoint generate',
        url: 'https://gb.hlorenzi.com/generate',
        method: 'post',
        data: { data: tableText }
      }
    ];

    for (let attempt of attempts) {
      try {
        console.log(`🔄 Essai: ${attempt.name}`);
        
        let response;
        if (attempt.method === 'get') {
          response = await axios.get(attempt.url, {
            params: attempt.params,
            responseType: 'arraybuffer',
            timeout: 15000
          });
        } else {
          response = await axios.post(attempt.url, attempt.data, {
            responseType: 'arraybuffer', 
            timeout: 15000
          });
        }

        // Vérifier si on a bien une image PNG
        if (response.data && response.data.length > 100) { // Image valide
          console.log(`✅ Succès avec: ${attempt.name}`);
          console.log(`📏 Taille image: ${response.data.length} bytes`);
          return Buffer.from(response.data);
        }
        
      } catch (error) {
        console.log(`❌ Échec avec ${attempt.name}: ${error.message}`);
      }
    }

    throw new Error('Aucune méthode de génération n\'a fonctionné');
    
  } catch (error) {
    console.error('❌ Erreur génération image:', error);
    throw error;
  }
}

// Fonction pour valider le format
function validateTableFormat(tableText) {
  const lines = tableText.split('\n').filter(line => line.trim() !== '');
  const teamLines = lines.filter(line => line.includes('-'));
  if (teamLines.length < 2) {
    return '❌ **Format incorrect!** Il faut au moins 2 équipes.\nExemple: `Tag1 - NomÉquipe`';
  }
  return null;
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
      lines.shift();
      const tableText = lines.join('\n').trim();
      
      if (!tableText) {
        await processingMsg.edit('❌ **Message vide!**\n\n**Format:**\n```/maketable\nTag1 - Nom1\nJ1 Score1\nJ2 Score2\n\nTag2 - Nom2\nJ3 Score3\nJ4 Score4```');
        return;
      }

      const validationError = validateTableFormat(tableText);
      if (validationError) {
        await processingMsg.edit(validationError);
        return;
      }

      console.log('📋 Tableau à générer:', tableText);
      
      // Essayer de générer l'image
      try {
        const imageBuffer = await generateTableImage(tableText);
        
        // Si on arrive ici, l'image a été générée !
        await message.channel.send({
          content: `📊 Tableau généré pour ${message.author}`,
          files: [{ 
            attachment: imageBuffer, 
            name: 'tableau.png' 
          }]
        });
        
        console.log('✅ Image envoyée avec succès!');
        
      } catch (imageError) {
        // Si la génération d'image échoue, envoyer le texte formaté
        console.log('🔄 Génération image échouée, envoi du texte...');
        const formattedTable = `📊 **Tableau pour ${message.author}**\n\`\`\`\n${tableText}\n\`\`\`\n\n*❌ Génération d'image temporairement indisponible*`;
        await message.channel.send(formattedTable);
      }
      
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

const token = process.env.DISCORD_TOKEN;
if (!token) {
  console.error('❌ Token Discord manquant!');
  process.exit(1);
}

client.login(token);