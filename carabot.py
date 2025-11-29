import discord
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from selenium.webdriver.chrome.service import Service
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

short_wait_time = 0.2
long_wait_time = 2

client = discord.Client(intents=discord.Intents.all())

def setup_chrome_options():
    """Configure Chrome pour Render"""
    chrome_options = Options()
    
    # Configuration pour Render
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--headless=new')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--window-size=1400,1000')
    chrome_options.add_argument('--font-render-hinting=none')
    chrome_options.add_argument('--disable-features=VizDisplayCompositor')
    
    # Configuration polices
    prefs = {
        'webkit.webprefs.default_font_size': 16,
        'webkit.webprefs.default_fixed_font_size': 13,
        'webkit.webprefs.minimum_font_size': 6,
        'webkit.webprefs.minimum_logical_font_size': 6,
        'webkit.webprefs.fonts': {
            'standard': 'Arial',
            'serif': 'Times New Roman', 
            'sansserif': 'Arial',
            'fixed': 'Courier New',
        }
    }
    chrome_options.add_experimental_option('prefs', prefs)
    
    return chrome_options

def download_table_image(driver):
    """Télécharge directement l'image du tableau depuis son URL"""
    try:
        print("🔍 Recherche de l'image du tableau...")
        
        images = driver.find_elements(By.CSS_SELECTOR, "img")
        
        for img in images:
            if img.is_displayed():
                width = img.size['width']
                height = img.size['height']
                
                if width > 100 and height > 50:
                    src = img.get_attribute('src')
                    print("✅ Image du tableau trouvée")
                    
                    # URL absolue
                    if src and src.startswith('http'):
                        response = requests.get(src, timeout=10)
                        if response.status_code == 200:
                            print("📥 Image téléchargée depuis URL")
                            return response.content
                    
                    # URL relative
                    elif src and src.startswith('/'):
                        full_url = urljoin(driver.current_url, src)
                        response = requests.get(full_url, timeout=10)
                        if response.status_code == 200:
                            print("📥 Image téléchargée depuis URL relative")
                            return response.content
                    
                    # Base64
                    elif src and src.startswith('data:image/'):
                        print("📥 Image en base64 détectée")
                        base64_data = src.split(',')[1]
                        image_data = base64.b64decode(base64_data)
                        return image_data
        
        # Méthode de secours
        print("❌ Téléchargement direct échoué, capture par screenshot")
        return capture_table_fallback(driver)
        
    except Exception as e:
        print(f"❌ Erreur téléchargement image: {e}")
        return capture_table_fallback(driver)

def capture_table_fallback(driver):
    """Méthode de secours : capture par screenshot"""
    try:
        print("🔍 Capture par screenshot...")
        
        images = driver.find_elements(By.CSS_SELECTOR, "img")
        
        for img in images:
            if img.is_displayed():
                width = img.size['width']
                height = img.size['height']
                
                if width > 100 and height > 50:
                    print(f"✅ Tableau trouvé: {width}x{height}")
                    return img.screenshot_as_png
        
        return driver.get_screenshot_as_png()
                
    except Exception as e:
        print(f"❌ Erreur capture: {e}")
        return driver.get_screenshot_as_png()

def close_popup(driver):
    """Ferme les pop-ups de consentement"""
    try:
        buttons = driver.find_elements(By.CSS_SELECTOR, "button")
        
        for button in buttons:
            if button.is_displayed():
                button_text = button.text.lower()
                if any(word in button_text for word in ['accept', 'agree', 'ok', 'consent']):
                    button.click()
                    print("✅ Pop-up fermé")
                    time.sleep(short_wait_time)
                    return True
    except:
        pass
    return False

def close_modal_popup(driver):
    """Ferme les popups modaux"""
    try:
        actions = ActionChains(driver)
        actions.send_keys(Keys.ESCAPE).perform()
        print("✅ Popup fermé")
        time.sleep(short_wait_time)
        return True
    except:
        pass
    return False

def find_and_click_customize(driver):
    """Trouve et clique sur le bouton Customize"""
    try:
        buttons = driver.find_elements(By.CSS_SELECTOR, "button.go1782636986.accent")
        
        for button in buttons:
            if button.is_displayed():
                button.click()
                time.sleep(short_wait_time)
                return True
    except Exception as e:
        print(f"❌ Erreur Customize: {e}")
    return False

def find_and_click_manage_styles(driver):
    """Trouve et clique sur Manage styles"""
    try:
        buttons = driver.find_elements(By.CSS_SELECTOR, "button[title='Manage styles']")
        
        for button in buttons:
            if button.is_displayed():
                button.click()
                time.sleep(short_wait_time)
                return True
    except Exception as e:
        print(f"❌ Erreur Manage styles: {e}")
    return False

def find_and_click_import(driver):
    """Trouve et clique sur Import"""
    try:
        all_buttons = driver.find_elements(By.CSS_SELECTOR, "button")
        
        for button in all_buttons:
            if button.is_displayed() and "import" in button.text.lower():
                button.click()
                time.sleep(short_wait_time)
                return True
    except Exception as e:
        print(f"❌ Erreur Import: {e}")
    return False

def upload_json_file(driver):
    """Upload le fichier JSON"""
    try:
        file_inputs = driver.find_elements(By.CSS_SELECTOR, "input[type='file']")
        
        for file_input in file_inputs:
            if file_input.is_displayed() or file_input.is_enabled():
                file_path = os.path.abspath("ztix.json")
                
                if os.path.exists(file_path):
                    file_input.send_keys(file_path)
                    print("✅ Fichier uploadé")
                    time.sleep(short_wait_time)
                    return True
                else:
                    print(f"❌ Fichier {file_path} non trouvé")
                    return False
    except Exception as e:
        print(f"❌ Erreur upload: {e}")
    return False

def handle_alert(driver):
    """Gère les alertes"""
    try:
        alert = driver.switch_to.alert
        alert_text = alert.text
        
        if "Successfully imported" in alert_text:
            alert.accept()
            print("✅ Alerte acceptée")
            return True
    except:
        pass
    return False

def find_and_select_ztix(driver):
    """Trouve et sélectionne le style Ztix"""
    try:
        comboboxes = driver.find_elements(By.CSS_SELECTOR, "select")
        
        for combobox in comboboxes:
            if combobox.is_displayed():
                select = Select(combobox)
                select.select_by_visible_text("Ztix")
                print("✅ Ztix sélectionné")
                time.sleep(0.5)
                return True
    except Exception as e:
        print(f"❌ Erreur sélection Ztix: {e}")
    return False

def import_json_styles(driver):
    """Importe le fichier JSON de styles"""
    print("🔄 Import styles JSON...")
    
    try:
        if not find_and_click_customize(driver):
            return False
        
        if not find_and_click_manage_styles(driver):
            return False
        
        if not find_and_click_import(driver):
            return False
        
        if not upload_json_file(driver):
            return False
        
        handle_alert(driver)
        close_modal_popup(driver)
        
        print("✅ Import terminé")
        return True
        
    except Exception as e:
        print(f"❌ Erreur import: {e}")
        return False

def select_ztix_style(driver):
    """Sélectionne le style Ztix"""
    print("🎨 Sélection style Ztix...")
    
    try:
        if not find_and_click_customize(driver):
            return False
        
        style_selected = find_and_select_ztix(driver)
        
        if style_selected:
            close_modal_popup(driver)
        
        return style_selected
        
    except Exception as e:
        print(f"❌ Erreur sélection style: {e}")
        return False

def generate_table_image(table_text):
    driver = None
    try:
        print("🌐 Démarrage navigateur...")

        chrome_options = setup_chrome_options()
        
        # Utilisation de ChromeDriver avec service
        service = Service()
        driver = webdriver.Chrome(service=service, options=chrome_options)

        driver.execute_script("""
            var style = document.createElement('style');
            style.textContent = `* { font-family: Arial, Helvetica, sans-serif !important; }`;
            document.head.appendChild(style);
        """)
        
        print("📡 Navigation...")
        driver.get("https://gb2.hlorenzi.com/table")
        
        print("⏳ Chargement...")
        time.sleep(short_wait_time)
        
        close_popup(driver)
        
        print("🔄 Application styles...")
        import_success = import_json_styles(driver)
        
        if import_success:
            style_selected = select_ztix_style(driver)
            if not style_selected:
                print("⚠️ Style par défaut")
        else:
            print("⚠️ Import échoué")
        
        print("📝 Génération tableau...")
        try:
            textarea = driver.find_element(By.CSS_SELECTOR, "textarea")
            if textarea.is_displayed():
                textarea.click()
                time.sleep(short_wait_time)
                
                actions = ActionChains(driver)
                actions.key_down(Keys.COMMAND).send_keys('a').key_up(Keys.COMMAND).perform()
                time.sleep(0.05)
                actions.send_keys(Keys.DELETE).perform()
                time.sleep(0.05)
                actions.send_keys(table_text).perform()
                time.sleep(short_wait_time)
        except Exception as e:
            print(f"❌ Erreur textarea: {e}")
            raise Exception("Erreur zone de texte")
        
        print("⏳ Génération...")
        time.sleep(long_wait_time)
        
        image_data = download_table_image(driver)
        print("✅ Tableau récupéré!")
        return image_data
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
        raise Exception(f"Erreur génération: {str(e)}")
    
    finally:
        if driver:
            driver.quit()
            print("🔒 Navigateur fermé")

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
            
            processing_msg = await message.channel.send("🔄 Génération en cours...")
            
            def generate_image():
                return generate_table_image(table_text)
            
            image_data = await asyncio.get_event_loop().run_in_executor(None, generate_image)
            
            image_file = discord.File(io.BytesIO(image_data), filename="tableau.png")
            
            await message.channel.send(
                content=f"📊 Tableau généré pour {message.author.mention}",
                file=image_file
            )
            
            await processing_msg.delete()
            
        except Exception as e:
            error_msg = f"❌ Erreur: {str(e)}"
            await message.channel.send(error_msg)
            print(f"Erreur détaillée: {e}")

@client.event
async def on_ready():
    print(f'✅ Bot connecté en tant que {client.user}')
    print(f'✅ Serveur Render - Prêt à générer des tableaux!')

if __name__ == "__main__":
    print("🚀 Démarrage du bot Discord sur Render...")
    client.run(token)
