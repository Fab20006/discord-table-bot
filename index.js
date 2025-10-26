const { Client, GatewayIntentBits } = require('discord.js');

console.log('🚀 Démarrage du bot...');

const client = new Client({
  intents: [
    GatewayIntentBits.Guilds,
    GatewayIntentBits.GuildMessages,
    GatewayIntentBits.MessageContent
  ]
});

// Fonction pour valider le format
function validateTableFormat(tableText) {
  const lines = tableText.split('\n').filter(line => line.trim() !== '');
  
  // Vérifier qu'il y a au moins 2 équipes et des joueurs
  const teamLines = lines.filter(line => line.includes('-'));
  if (teamLines.length < 2) {
    return '❌ **Format incorrect!** Il faut au moins 2 équipes.\nExemple: `Tag1 - NomÉquipe`';
  }
  
  // Vérifier qu'il y a des scores
  const playerLines = lines.filter(line => !line.includes('-') && line.trim() !== '');
  if (playerLines.length === 0) {
    return '❌ **Aucun joueur trouvé!** Ajoutez des joueurs avec leurs scores.';
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
      
      const processingMsg = await message.reply('🔄 Traitement de votre tableau...');
      
      // Extraire le texte du tableau
      const lines = message.content.split('\n');
      lines.shift(); // Retirer /maketable
      const tableText = lines.join('\n').trim();
      
      // Vérification basique
      if (!tableText) {
        await processingMsg.edit('❌ **Message vide!**\n\n**Format requis:**\n```/maketable\nTag1 - Nom Équipe 1\nJoueur1 Score1\nJoueur2 Score2\n\nTag2 - Nom Équipe 2\nJoueur3 Score3\nJoueur4 Score4```');
        return;
      }

      // Validation du format
      const validationError = validateTableFormat(tableText);
      if (validationError) {
        await processingMsg.edit(validationError);
        return;
      }

      console.log('📋 Tableau reçu:', tableText);
      
      // Pour l'instant, on va juste formatter le texte et le renvoyer
      // En attendant de résoudre la génération d'image
      
      const formattedTable = `📊 **Tableau généré pour ${message.author}**\n\`\`\`\n${tableText}\n\`\`\`\n\n*⚠️ La génération d\'image est temporairement désactivée*`;
      
      await message.channel.send(formattedTable);
      
      // Supprimer le message "en cours"
      await processingMsg.delete();
      
      console.log('✅ Tableau envoyé avec succès');
      
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