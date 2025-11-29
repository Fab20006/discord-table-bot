import discord
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
import io
import asyncio
import os
import base64
import requests
from urllib.parse import urljoin

# Configuration pour Render
token = os.environ.get('DISCORD_TOKEN')
if not token:
    raise Exception("❌ DISCORD_TOKEN non trouvé dans les variables d'environnement")

# Temps d'attente réduits
short_wait_time = 0.1
long_wait_time = 1

client = discord.Client(intents=discord.Intents.all())

def setup_chrome_options():
    """Configuration Chrome optimisée pour Render"""
    chrome_options = Options()
    
    # Configuration optimisée pour Render
    chrome_options.add_argument('--headless=new')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--window-size=1200,800')  # Réduit pour plus de rapidité
    chrome_options.add_argument('--disable-extensions')
    chrome_options.add_argument('--disable-images')  # Désactive les images pour plus de vitesse
    chrome_options.add_argument('--disable-javascript')  # À tester - peut accélérer
    chrome_options.add_argument('--blink-settings=imagesEnabled=false')
    
    # Optimisations performances
    chrome_options.add_argument('--disable-background-timer-throttling')
    chrome_options.add_argument('--disable-backgrounding-occluded-windows')
    chrome_options.add_argument('--disable-renderer-backgrounding')
    chrome_options.add_argument('--memory-pressure-off')
    
    # Configuration polices simplifiée
    prefs = {
        'profile.default_content_setting_values': {
            'images': 2,  # Désactive les images
        },
        'profile.managed_default_content_settings.images': 2,
    }
    chrome_options.add_experimental_option('prefs', prefs)
    
    return chrome_options

def smart_wait(driver, condition, timeout=10):
    """Attente intelligente avec timeout réduit"""
    try:
        wait = WebDriverWait(driver, timeout)
        return wait.until(condition)
    except:
        return None

def download_table_image_fast(driver):
    """Version optimisée pour télécharger l'image"""
    try:
        print("🔍 Recherche rapide de l'image...")
        
        # Attendre que l'image soit présente mais pas trop longtemps
        image = smart_wait(driver, EC.presence_of_element_located((By.TAG_NAME, "img")), 5)
        
        if image and image.is_displayed():
            src = image.get_attribute('src')
            print(f"✅ Image trouvée: {src[:100] if src else 'No src'}")
            
            # Priorité: Base64 (le plus rapide)
            if src and src.startswith('data:image/'):
                print("📥 Image base64 détectée")
                base64_data = src.split(',')[1]
                return base64.b64decode(base64_data)
            
            # Fallback: Screenshot
            print("📸 Capture par screenshot")
            return image.screenshot_as_png
        
        # Dernier recours: screenshot de la page
        print("🖼️ Screenshot de la page entière")
        return driver.get_screenshot_as_png()
        
    except Exception as e:
        print(f"❌ Erreur capture image: {e}")
        return driver.get_screenshot_as_png()

def close_popup_fast(driver):
    """Ferme les pop-ups rapidement"""
    try:
        # Essayer Escape d'abord (le plus rapide)
        actions = ActionChains(driver)
        actions.send_keys(Keys.ESCAPE).perform()
        print("✅ Escape envoyé")
        time.sleep(0.5)
        
        # Chercher les boutons rapidement
        buttons = driver.find_elements(By.CSS_SELECTOR, "button")
        for button in buttons[:5]:  # Seulement les 5 premiers
            try:
                if button.is_displayed():
                    text = button.text.lower()
                    if any(word in text for word in ['accept', 'agree', 'ok']):
                        button.click()
                        print("✅ Pop-up fermé")
                        return True
            except:
                continue
        return False
    except Exception as e:
        print(f"⚠️ Pop-up non fermé: {e}")
        return False

def find_and_click_fast(driver, selector, description):
    """Trouve et clique rapidement"""
    try:
        element = smart_wait(driver, EC.element_to_be_clickable((By.CSS_SELECTOR, selector)), 5)
        if element:
            element.click()
            print(f"✅ {description}")
            return True
    except Exception as e:
        print(f"❌ {description} échoué: {e}")
    return False

def setup_table_fast(driver):
    """Configuration rapide des styles"""
    try:
        print("⚡ Configuration rapide...")
        
        # Essayer d'importer les styles (mais avec timeout court)
        if find_and_click_fast(driver, "button.go1782636986.accent", "Customize"):
            time.sleep(short_wait_time)
            
            if find_and_click_fast(driver, "button[title='Manage styles']", "Manage styles"):
                time.sleep(short_wait_time)
                
                # Chercher Import rapidement
                buttons = driver.find_elements(By.TAG_NAME, "button")
                for button in buttons[:10]:
                    if "import" in button.text.lower():
                        button.click()
                        print("✅ Import cliqué")
                        time.sleep(short_wait_time)
                        
                        # Upload fichier si trouvé
                        file_inputs = driver.find_elements(By.CSS_SELECTOR, "input[type='file']")
                        if file_inputs:
                            file_path = os.path.abspath("ztix.json")
                            if os.path.exists(file_path):
                                file_inputs[0].send_keys(file_path)
                                print("✅ Fichier uploadé")
                                time.sleep(short_wait_time)
                                
                                # Fermer les modaux
                                close_popup_fast(driver)
                                return True
        
        print("⚠️ Configuration partielle")
        return False
        
    except Exception as e:
        print(f"⚠️ Configuration échouée: {e}")
        return False

def input_table_text_fast(driver, table_text):
    """Saisie rapide du texte"""
    try:
        print("📝 Saisie du texte...")
        
        textarea = smart_wait(driver, EC.element_to_be_clickable((By.TAG_NAME, "textarea")), 5)
        if textarea:
            # Méthode rapide: clear + send_keys
            textarea.clear()
            time.sleep(0.1)
            textarea.send_keys(table_text)
            print("✅ Texte saisi")
            return True
        return False
        
    except Exception as e:
        print(f"❌ Erreur saisie: {e}")
        return False

def generate_table_image(table_text):
    """Version optimisée de la génération"""
    driver = None
    try:
        print("🚀 Démarrage Chrome optimisé...")
        start_time = time.time()
        
        chrome_options = setup_chrome_options()
        service = Service()
        
        # Timeout global pour le driver
        driver = webdriver.Chrome(service=service, options=chrome_options)
        driver.set_page_load_timeout(15)
        driver.set_script_timeout(10)
        
        print("🌐 Navigation...")
        driver.get("https://gb2.hlorenzi.com/table")
        
        print("⏳ Chargement page...")
        time.sleep(1)  # Attente réduite
        
        # Fermer pop-ups rapidement
        close_popup_fast(driver)
        
        # Configuration (mais avec timeout court)
        setup_start = time.time()
        setup_table_fast(driver)
        print(f"⚙️ Configuration: {time.time() - setup_start:.1f}s")
        
        # Saisie du texte
        input_start = time.time()
        if not input_table_text_fast(driver, table_text):
            raise Exception("Erreur saisie texte")
        print(f"📝 Saisie: {time.time() - input_start:.1f}s")
        
        # Attente génération réduite
        print("⏳ Génération tableau...")
        time.sleep(2)  # Réduit de 2 secondes
        
        # Capture image
        capture_start = time.time()
        image_data = download_table_image_fast(driver)
        print(f"📸 Capture: {time.time() - capture_start:.1f}s")
        
        total_time = time.time() - start_time
        print(f"✅ Tableau généré en {total_time:.1f}s")
        
        return image_data
        
    except Exception as e:
        print(f"❌ Erreur génération: {e}")
        raise Exception(f"Erreur: {str(e)}")
    
    finally:
        if driver:
            try:
                driver.quit()
                print("🔒 Navigateur fermé")
            except:
                pass

@client.event
async def on_message(message: discord.Message):
    if message.author.bot:
        return
    
    elif message.content.lower().startswith("maketable"):
        try:
            table_text = message.content[len("maketable"):].strip()
            
            if not table_text:
                await message.channel.send("❌ **Veuillez fournir le texte du tableau!**")
                return
            
            if len(table_text) > 2000:
                await message.channel.send("❌ **Texte trop long! Maximum 2000 caractères.**")
                return
            
            processing_msg = await message.channel.send("🔄 Génération en cours (version optimisée)...")
            
            def generate_image():
                return generate_table_image(table_text)
            
            # Timeout global de 45 secondes
            image_data = await asyncio.wait_for(
                asyncio.get_event_loop().run_in_executor(None, generate_image),
                timeout=45.0
            )
            
            image_file = discord.File(io.BytesIO(image_data), filename="tableau.png")
            
            await message.channel.send(
                content=f"📊 Tableau généré pour {message.author.mention}",
                file=image_file
            )
            
            await processing_msg.delete()
            
        except asyncio.TimeoutError:
            await message.channel.send("❌ **Timeout - génération trop longue (>45s)**")
        except Exception as e:
            error_msg = f"❌ Erreur: {str(e)}"
            await message.channel.send(error_msg)
            print(f"Erreur détaillée: {e}")
    
    elif message.content.lower() == "!ping":
        await message.channel.send("🏓 Pong! Bot Selenium optimisé")

@client.event
async def on_ready():
    print(f'✅ Bot connecté en tant que {client.user}')
    print(f'🚀 Version Selenium optimisée - Prêt!')

if __name__ == "__main__":
    print("🚀 Démarrage du bot Discord optimisé...")
    
    # Import ici pour éviter l'import circulaire
    import time
    
    client.run(token)
