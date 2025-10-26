const { Client, GatewayIntentBits } = require('discord.js');
const puppeteer = require('puppeteer');

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
  let browser;
  try {
    console.log('📊 Lancement du navigateur...');
    
    browser = await puppeteer.launch({
      headless: 'new',
      args: [
        '--no-sandbox',
        '--disable-setuid-sandbox',
        '--disable-dev-shm-usage',
        '--disable-accelerated-2d-canvas',
        '--no-first-run',
        '--no-zygote',
        '--single-process',
        '--disable-gpu'
      ]
    });

    const page = await browser.newPage();
    
    // Aller sur le site de génération de tableaux
    console.log('🌐 Navigation vers le site...');
    await page.goto('https://gb.hlorenzi.com/table', { 
      waitUntil: 'networkidle2',
      timeout: 30000 
    });

    console.log('📝 Recherche de la zone de texte...');
    
    // Attendre que la page soit chargée
    await page.waitForTimeout(2000);
    
    // Trouver le textarea (c'est généralement un textarea pour ce genre de site)
    const textareaSelector = 'textarea';
    await page.waitForSelector(textareaSelector, { timeout: 10000 });
    
    // Effacer le contenu existant
    await page.evaluate((selector) => {
      const textarea = document.querySelector(selector);
      if (textarea) {
        textarea.value = '';
        textarea.focus();
      }
    }, textareaSelector);
    
    // Coller le texte du tableau
    console.log('📋 Collage du contenu...');
    await page.type(textareaSelector, tableText);
    
    // Attendre un peu pour être sûr que le texte est bien saisi
    await page.waitForTimeout(1000);
    
    // Prendre une capture d'écran de la zone du tableau
    console.log('📸 Capture de la zone du tableau...');
    
    // Essayer de trouver la zone spécifique du tableau, sinon capturer toute la page
    const tableArea = await page.$('.table-container, .output, canvas, #output');
    
    let screenshot;
    if (tableArea) {
      screenshot = await tableArea.screenshot({ 
        type: 'png',
        quality: 90
      });
    } else {
      // Capturer toute la page si la zone spécifique n'est pas trouvée
      screenshot = await page.screenshot({ 
        type: 'png',
        quality: 90,
        fullPage: true 
      });
    }
    
    console.log('✅ Capture réussie!');
    return screenshot;

  } catch (error) {
    console.error('❌ Erreur lors de la génération:', error);
    throw new Error('Erreur lors de la génération du tableau: ' + error.message);
  } finally {
    if (browser) {
      await browser.close();
      console.log('🔒 Navigateur fermé');
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
      
      const processingMsg = await message.reply('🔄 Génération du tableau en cours (cela peut prendre 10-15 secondes)...');
      
      // Extraire le texte du tableau
      const lines = message.content.split('\n');
      lines.shift(); // Retirer /maketable
      const tableText = lines.join('\n').trim();
      
      // Vérification du format
      if (!tableText) {
        await processingMsg.edit('❌ **Format incorrect!**\n\n**Exemple d\'utilisation:**\n```/maketable\nTag1 - Équipe Rouge\nJoueur1 1500\nJoueur2 1400\nJoueur3 1300\n\nTag2 - Équipe Bleue\nJoueur4 1500\nJoueur5 1400\nJoueur6 1300```');
        return;
      }

      console.log('📋 Texte à générer:', tableText);
      
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
      await message.reply('❌ **Erreur:** ' + error.message + '\n\nLe site peut être temporairement indisponible.');
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