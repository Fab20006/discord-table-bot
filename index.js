async function generateTableImage(tableText) {
  let browser;
  try {
    console.log('📊 Lancement du navigateur...');
    
    browser = await puppeteer.launch({
      headless: 'new',
      args: ['--no-sandbox', '--disable-setuid-sandbox'],
      defaultViewport: { width: 1200, height: 800 }
    });

    const page = await browser.newPage();
    
    console.log('🌐 Navigation vers le site...');
    await page.goto('https://gb.hlorenzi.com/table', { 
      waitUntil: 'networkidle2',
      timeout: 30000 
    });

    // CAPTURE 1 : Page avant modification
    const beforeScreenshot = await page.screenshot({ 
      type: 'png',
      fullPage: true 
    });
    console.log('📸 Capture avant modification prise');

    // Trouver et remplir la zone de texte
    console.log('📝 Recherche de la zone de texte...');
    
    // Essayer plusieurs sélecteurs possibles
    const possibleSelectors = [
      'textarea',
      'input[type="text"]',
      '.input',
      '#input',
      '[contenteditable="true"]',
      'pre',
      'code'
    ];
    
    let textElement = null;
    for (const selector of possibleSelectors) {
      textElement = await page.$(selector);
      if (textElement) {
        console.log(`✅ Élément trouvé avec: ${selector}`);
        break;
      }
    }
    
    if (!textElement) {
      throw new Error('Aucune zone de texte trouvée sur la page');
    }

    // Effacer et écrire le texte
    await page.evaluate((element, text) => {
      element.value = text;
      element.textContent = text;
      element.focus();
      
      // Déclencher les événements
      const inputEvent = new Event('input', { bubbles: true });
      element.dispatchEvent(inputEvent);
      
      const changeEvent = new Event('change', { bubbles: true });
      element.dispatchEvent(changeEvent);
      
      const keyupEvent = new Event('keyup', { bubbles: true });
      element.dispatchEvent(keyupEvent);
    }, textElement, tableText);

    // Attendre la génération
    console.log('⏳ Attente de la génération...');
    await page.waitForTimeout(5000);

    // CAPTURE 2 : Page après modification
    const afterScreenshot = await page.screenshot({ 
      type: 'png',
      fullPage: true 
    });
    console.log('📸 Capture après modification prise');

    // Maintenant chercher spécifiquement le tableau
    console.log('🔍 Recherche ciblée du tableau...');
    
    // Prendre une capture de toute la page pour l'instant
    const finalScreenshot = await page.screenshot({ 
      type: 'png',
      fullPage: true,
      quality: 90
    });

    console.log('✅ Capture finale prise');
    return finalScreenshot;

  } catch (error) {
    console.error('❌ Erreur:', error);
    throw new Error('Erreur génération: ' + error.message);
  } finally {
    if (browser) await browser.close();
  }
}