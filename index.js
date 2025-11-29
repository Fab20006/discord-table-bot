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

// Fonction pour interagir avec gb2.hlorenzi.com
async function generateTableWithPuppeteer(tableText) {
  let browser;
  try {
    console.log('🌐 Lancement du navigateur...');
    
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
      ],
      defaultViewport: { width: 1200, height: 800 }
    });

    const page = await browser.newPage();
    
    // Naviguer vers le NOUVEAU site
    console.log('📡 Navigation vers gb2.hlorenzi.com/table...');
    await page.goto('https://gb2.hlorenzi.com/table', {
      waitUntil: 'networkidle2',
      timeout: 30000
    });

    console.log('⏳ Attente du chargement de la page...');
    await page.waitForTimeout(3000);

    // Prendre une capture pour debug
    console.log('📸 Capture de la page chargée...');
    const initialScreenshot = await page.screenshot({ type: 'png' });
    
    // Chercher la zone de texte - essayer différents sélecteurs
    console.log('🔍 Recherche de la zone de texte...');
    const textareaSelectors = [
      'textarea',
      'input[type="text"]',
      'input[type="textarea"]',
      '.input',
      '#input',
      '[contenteditable="true"]',
      'pre',
      'code',
      '.code-input',
      '.text-input'
    ];

    let textArea = null;
    let foundSelector = null;
    
    for (const selector of textareaSelectors) {
      textArea = await page.$(selector);
      if (textArea) {
        foundSelector = selector;
        console.log(`✅ Zone de texte trouvée avec: ${selector}`);
        break;
      }
    }

    if (!textArea) {
      // Si aucun sélecteur ne marche, prendre une capture pour debug
      const debugScreenshot = await page.screenshot({ type: 'png', fullPage: true });
      throw new Error('Aucune zone de texte trouvée. Capture de debug prise.');
    }

    // Effacer le contenu existant
    console.log('🧹 Nettoyage du contenu existant...');
    await page.evaluate((selector) => {
      const element = document.querySelector(selector);
      if (element) {
        element.value = '';
        element.textContent = '';
        element.focus();
        
        // Déclencher les événements de changement
        const inputEvent = new Event('input', { bubbles: true });
        element.dispatchEvent(inputEvent);
      }
    }, foundSelector);

    // Écrire le nouveau texte
    console.log('📝 Écriture du tableau...');
    await page.type(foundSelector, tableText, { delay: 30 });

    // Attendre que le tableau se génère automatiquement
    console.log('⏳ Attente de la génération du tableau...');
    await page.waitForTimeout(4000);

    // Chercher la zone du tableau généré
    console.log('🔍 Recherche du tableau généré...');
    const tableSelectors = [
      '.table',
      '.output',
      '.result',
      '.generated',
      'canvas',
      'svg',
      'img',
      '.image-result',
      '#output',
      '[class*="table"]',
      '[class*="output"]',
      '[class*="result"]'
    ];

    let tableElement = null;
    for (const selector of tableSelectors) {
      tableElement = await page.$(selector);
      if (tableElement) {
        console.log(`✅ Tableau trouvé avec: ${selector}`);
        break;
      }
    }

    let screenshot;
    if (tableElement) {
      // Capturer seulement le tableau
      console.log('📸 Capture du tableau...');
      screenshot = await tableElement.screenshot({ 
        type: 'png',
        quality: 90
      });
    } else {
      // Capturer toute la page si le tableau n'est pas trouvé spécifiquement
      console.log('📸 Capture de toute la page...');
      screenshot = await page.screenshot({ 
        type: 'png',
        quality: 90,
        fullPage: true 
      });
    }

    console.log('✅ Tableau généré avec succès!');
    return screenshot;

  } catch (error) {
    console.error('❌ Erreur lors de l\'interaction avec le site:', error);
    throw new Error('Impossible de générer le tableau: ' + error.message);
  } finally {
    if (browser) {
      await browser.close();
      console.log('🔒 Navigateur fermé');
    }
  }
}

// Fonction pour valider le format
function validateTableFormat(tableText) {
  const lines = tableText.split('\n').filter(line => line.trim() !== '');
  const teamLines = lines.filter(line => line.includes('-'));
  
  if (teamLines.length < 1) {
    return '❌ **Format incorrect!** Il faut au moins 1 équipe.\nExemple: `Tag - NomÉquipe`';
  }
  
  const playerLines = lines.filter(line => !line.includes('-') && line.trim() !== '');
  if (playerLines.length === 0) {
    return '❌ **Aucun joueur trouvé!** Format: `Joueur Score`';
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
      
      const processingMsg = await message.reply('🔄 Interaction avec gb2.hlorenzi.com... (10-15 secondes)');
      
      // Extraire le texte du tableau
      const lines = message.content.split('\n');
      lines.shift();
      const tableText = lines.join('\n').trim();
      
      // Validation
      if (!tableText) {
        await processingMsg.edit('❌ **Message vide!**\n\n**Format:**\n```/maketable\nA - Équipe Rouge\nJoueur1 1500\nJoueur2 1400\n\nB - Équipe Bleue\nJoueur3 1500\nJoueur4 1400```');
        return;
      }

      const validationError = validateTableFormat(tableText);
      if (validationError) {
        await processingMsg.edit(validationError);
        return;
      }

      console.log('📋 Génération à partir de:', tableText);
      
      // Générer l'image avec Puppeteer
      const imageBuffer = await generateTableWithPuppeteer(tableText);
      
      // Envoyer le résultat
      await message.channel.send({
        content: `📊 Tableau généré depuis gb2.hlorenzi.com pour ${message.author}`,
        files: [{ 
          attachment: imageBuffer, 
          name: 'tableau.png' 
        }]
      });
      
      await processingMsg.delete();
      console.log('✅ Tableau envoyé avec succès!');
      
    } catch (error) {
      console.error('❌ Erreur finale:', error);
      
      // En cas d'erreur, envoyer le texte formaté
      const lines = message.content.split('\n');
      lines.shift();
      const tableText = lines.join('\n').trim();
      
      const errorMessage = `❌ **Erreur avec gb2.hlorenzi.com**\n\n${error.message}\n\n**Votre tableau:**\n\`\`\`\n${tableText}\n\`\`\``;
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