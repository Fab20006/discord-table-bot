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
      ],
      defaultViewport: { width: 1200, height: 800 }
    });

    const page = await browser.newPage();
    
    // Aller sur le site de génération de tableaux
    console.log('🌐 Navigation vers le site...');
    await page.goto('https://gb.hlorenzi.com/table', { 
      waitUntil: 'networkidle2',
      timeout: 30000 
    });

    console.log('📝 Recherche de la zone de texte de gauche...');
    
    // Attendre que la page soit complètement chargée
    await page.waitForTimeout(3000);
    
    // Trouver le textarea ou l'input de la zone de gauche
    // Sur ce type de site, c'est souvent un textarea pour le code/texte
    const textareaSelector = 'textarea, .input-area, .code-area, #input, [class*="input"], [class*="code"]';
    await page.waitForSelector(textareaSelector, { timeout: 10000 });
    
    // Effacer le contenu existant et écrire le nouveau
    console.log('📋 Écriture du contenu...');
    await page.evaluate((selector, text) => {
      const textarea = document.querySelector(selector);
      if (textarea) {
        textarea.value = text;
        textarea.focus();
        
        // Déclencher les événements de changement
        const event = new Event('input', { bubbles: true });
        textarea.dispatchEvent(event);
        
        const changeEvent = new Event('change', { bubbles: true );
        textarea.dispatchEvent(changeEvent);
      }
    }, textareaSelector, tableText);
    
    // Attendre que le tableau soit généré à droite
    console.log('⏳ Attente de la génération du tableau...');
    await page.waitForTimeout(3000);
    
    // Chercher la zone du tableau à droite
    console.log('🔍 Recherche de la zone du tableau...');
    
    // Sélecteurs possibles pour la zone de droite
    const outputSelectors = [
      '.table-container',
      '.output',
      '.result',
      '.table-area',
      '.right-panel',
      '[class*="output"]',
      '[class*="result"]',
      '[class*="table"]',
      'canvas',
      'svg',
      '.generated-table'
    ];
    
    let tableElement = null;
    for (const selector of outputSelectors) {
      tableElement = await page.$(selector);
      if (tableElement) {
        console.log(`✅ Zone tableau trouvée avec: ${selector}`);
        break;
      }
    }
    
    let screenshot;
    if (tableElement) {
      // Capturer seulement la zone du tableau
      console.log('📸 Capture de la zone du tableau...');
      screenshot = await tableElement.screenshot({ 
        type: 'png',
        quality: 90
      });
    } else {
      // Si on ne trouve pas la zone spécifique, capturer la moitié droite de la page
      console.log('📸 Capture de la moitié droite...');
      const pageSize = await page.evaluate(() => {
        return {
          width: document.documentElement.scrollWidth,
          height: document.documentElement.scrollHeight
        };
      });
      
      screenshot = await page.screenshot({
        type: 'png',
        quality: 90,
        clip: {
          x: pageSize.width / 2,
          y: 0,
          width: pageSize.width / 2,
          height: pageSize.height
        }
      });
    }
    
    console.log('✅ Tableau généré avec succès!');
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
      
      const processingMsg = await message.reply('🔄 Génération du tableau en cours (10-15 secondes)...');
      
      // Extraire le texte du tableau
      const lines = message.content.split('\n');
      lines.shift(); // Retirer /maketable
      const tableText = lines.join('\n').trim();
      
      // Vérification du format
      if (!tableText) {
        await processingMsg.edit('❌ **Format incorrect!**\n\n**Exemple:**\n```/maketable\nTag1 - Équipe Rouge\nJoueur1 1500\nJoueur2 1400\n\nTag2 - Équipe Bleue\nJoueur3 1500\nJoueur4 1400```');
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