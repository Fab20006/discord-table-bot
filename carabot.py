import discord
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import io
import asyncio
import time
import os
import requests
from urllib.parse import urljoin
import base64

# Configuration pour Render
token = os.environ.get('DISCORD_TOKEN')
if not token:
    raise Exception("❌ DISCORD_TOKEN non trouvé dans les variables d'environnement")

# Temps d'attente optimisés pour Render
short_wait_time = 0.15
long_wait_time = 1.5

client = discord.Client(intents=discord.Intents.all())

def setup_chrome_options():
    """Configuration Chrome optimisée pour Render"""
    chrome_options = Options()
    
    # Configuration CRITIQUE pour Render
    chrome_options.add_argument('--headless=new')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--window-size=1200,800')  # Réduit la taille
    chrome_options.add_argument('--disable-extensions')
    chrome_options.add_argument('--disable-images')  # ACCÉLÉRATION IMPORTANTE
    
    # Optimisations performances
    chrome_options.add_argument('--disable-background-timer-throttling')
    chrome_options.add_argument('--disable-backgrounding-occluded-windows')
    chrome_options.add_argument('--disable-renderer-backgrounding')
    
    # Configuration polices
    prefs = {
        'profile.default_content_setting_values': {
            'images': 2,  # Désactive les images
        },
        'profile.managed_default_content_settings.images': 2,
    }
    chrome_options.add_experimental_option('prefs', prefs)
    
    return chrome_options

def smart_wait(driver, condition, timeout=5):
    """Attente intelligente avec timeout court"""
    try:
        wait = WebDriverWait(driver, timeout)
        return wait.until(condition)
    except:
        return None

def download_table_image(driver):
    """Version optimisée pour télécharger l'image"""
    try:
        print("🔍 Recherche image...")
        
        # Attente courte pour l'image
        image = smart_wait(driver, EC.presence_of_element_located((By.TAG_NAME, "img")), 3)
        
        if image and image.is_displayed():
            src = image.get_attribute('src')
            print("✅ Image trouvée")
            
            # Priorité: Base64 (le plus rapide)
            if src and src.startswith('data:image/'):
                print("📥 Image base64")
                base64_data = src.split(',')[1]
                return base64.b64decode(base64_data)
            
            # Fallback: Screenshot
            print("📸 Capture screenshot")
            return image.screenshot_as_png
        
        # Dernier recours
        print("🖼️ Screenshot page")
        return driver.get_screenshot_as_png()
        
    except Exception as e:
        print(f"❌ Erreur capture: {e}")
        return driver.get_screenshot_as_png()

def close_popup_fast(driver):
    """Ferme les pop-ups rapidement"""
    try:
        # Escape d'abord
        actions = ActionChains(driver)
        actions.send_keys(Keys.ESCAPE).perform()
        time.sleep(0.3)
        
        # Boutons rapidement
        buttons = driver.find_elements(By.CSS_SELECTOR, "button")[:3]
        for button in buttons:
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
        print(f"⚠️ Pop-up: {e}")
        return False

def find_and_click_fast(driver, selector, description):
    """Trouve et clique rapidement"""
    try:
        element = smart_wait(driver, EC.element_to_be_clickable((By.CSS_SELECTOR, selector)), 3)
        if element:
            element.click()
            print(f"✅ {description}")
            time.sleep(short_wait_time)
            return True
    except Exception as e:
        print(f"❌ {description}: {e}")
    return False

def setup_styles_fast(driver):
    """Configuration rapide des styles"""
    try:
        print("⚡ Configuration styles...")
        
        # Essayer rapidement d'importer
        if find_and_click_fast(driver, "button.go1782636986.accent", "Customize"):
            if find_and_click_fast(driver, "button[title='Manage styles']", "Manage styles"):
                
                # Chercher Import
                buttons = driver.find_elements(By.TAG_NAME, "button")[:8]
                for button in buttons:
                    if "import" in button.text.lower():
                        button.click()
                        print("✅ Import cliqué")
                        time.sleep(short_wait_time)
                        
                        # Upload fichier
                        file_inputs = driver.find_elements(By.CSS_SELECTOR, "input[type='file']")
                        if file_inputs:
                            file_path = os.path.abspath("ztix.json")
                            if os.path.exists(file_path):
                                file_inputs[0].send_keys(file_path)
                                print("✅ Fichier uploadé")
                                time.sleep(short_wait_time)
                                
                                # Fermer modaux
                                close_popup_fast(driver)
                                return True
        
        print("⚠️ Configuration partielle")
        return False
        
    except Exception as e:
        print(f"⚠️ Configuration: {e}")
        return False

def input_text_fast(driver, table_text):
    """Saisie rapide du texte"""
    try:
        print("📝 Saisie texte...")
        
        textarea = smart_wait(driver, EC.element_to_be_clickable((By.TAG_NAME, "textarea")), 3)
        if textarea:
            # Méthode directe
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
    """Version ULTRA optimisée pour Render"""
    driver = None
    try:
        print("🚀 Démarrage Chrome...")
        start_time = time.time()
        
        chrome_options = setup_chrome_options()
        
        # IMPORTANT: Utilisation directe sans Service
        driver = webdriver.Chrome(options=chrome_options)
        
        # Timeouts courts
        driver.set_page_load_timeout(10)
        driver.set_script_timeout(8)
        
        print("🌐 Navigation...")
        driver.get("https://gb2.hlorenzi.com/table")
        
        print("⏳ Chargement...")
        time.sleep(1)  # Réduit
        
        # Fermer pop-ups
        close_popup_fast(driver)
        
        # Configuration rapide
        config_start = time.time()
        setup_styles_fast(driver)
        print(f"⚙️ Config: {time.time() - config_start:.1f}s")
        
        # Saisie
        input_start = time.time()
        if not input_text_fast(driver, table_text):
            raise Exception("Erreur saisie")
        print(f"📝 Saisie: {time.time() - input_start:.1f}s")
        
        # Génération réduite
        print("⏳ Génération...")
        time.sleep(long_wait_time)  # Réduit
        
        # Capture
        capture_start = time.time()
        image_data = download_table_image(driver)
        print(f"📸 Capture: {time.time() - capture_start:.1f}s")
        
        total_time = time.time() - start_time
        print(f"✅ Succès: {total_time:.1f}s")
        
        return image_data
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
        raise Exception(f"Erreur génération: {str(e)}")
    
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
            
            processing_msg = await message.channel.send("🔄 Génération en cours...")
            
            def generate_image():
                return generate_table_image(table_text)
            
            # Timeout de 30 secondes max
            image_data = await asyncio.wait_for(
                asyncio.get_event_loop().run_in_executor(None, generate_image),
                timeout=30.0
            )
            
            image_file = discord.File(io.BytesIO(image_data), filename="tableau.png")
            
            await message.channel.send(
                content=f"📊 Tableau généré pour {message.author.mention}",
                file=image_file
            )
            
            await processing_msg.delete()
            
        except asyncio.TimeoutError:
            await message.channel.send("❌ **Timeout - génération trop longue (>30s)**")
        except Exception as e:
            error_msg = f"❌ Erreur: {str(e)}"
            await message.channel.send(error_msg)
            print(f"Erreur détaillée: {e}")
    
    elif message.content.lower() == "!ping":
        await message.channel.send("🏓 Pong! Bot optimisé Render")

@client.event
async def on_ready():
    print(f'✅ Bot connecté: {client.user}')
    print(f'🚀 Version optimisée Render - Prêt!')

if __name__ == "__main__":
    print("🚀 Démarrage bot optimisé Render...")
    
    # Import time ici
    import time
    
    client.run(token)
