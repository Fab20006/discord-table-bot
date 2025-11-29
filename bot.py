import discord
from discord import Intents
import asyncio
import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import base64

# Configuration du bot
intents = Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

def validate_table_format(table_text):
    """Valide le format du tableau"""
    lines = [line.strip() for line in table_text.split('\n') if line.strip()]
    team_lines = [line for line in lines if '-' in line]
    
    if len(team_lines) < 1:
        return "❌ **Format incorrect!** Il faut au moins 1 équipe.\nExemple: `Tag - NomÉquipe`"
    
    player_lines = [line for line in lines if '-' not in line and line.strip()]
    if len(player_lines) == 0:
        return "❌ **Aucun joueur trouvé!** Format: `Joueur Score`"
    
    return None

def generate_table_with_selenium(table_text):
    """Génère le tableau avec Selenium"""
    driver = None
    try:
        print("🌐 Configuration de Chrome...")
        
        # Options Chrome pour Render
        chrome_options = Options()
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--window-size=1200,800')
        
        driver = webdriver.Chrome(options=chrome_options)
        
        print("📡 Navigation vers gb2.hlorenzi.com/table...")
        driver.get("https://gb2.hlorenzi.com/table")
        
        # Attendre le chargement
        print("⏳ Attente du chargement...")
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )
        
        # Chercher la zone de texte
        print("🔍 Recherche de la zone de texte...")
        textarea_selectors = [
            "textarea",
            "input[type='text']",
            "input[type='textarea']",
            ".input",
            "#input",
            "[contenteditable='true']"
        ]
        
        textarea = None
        for selector in textarea_selectors:
            try:
                textarea = driver.find_element(By.CSS_SELECTOR, selector)
                if textarea:
                    print(f"✅ Zone trouvée avec: {selector}")
                    break
            except:
                continue
        
        if not textarea:
            raise Exception("Aucune zone de texte trouvée")
        
        # Effacer et écrire le texte
        print("📝 Écriture du tableau...")
        textarea.clear()
        textarea.send_keys(table_text)
        
        # Attendre la génération
        print("⏳ Attente de la génération...")
        driver.implicitly_wait(5)
        
        # Prendre une capture
        print("📸 Capture d'écran...")
        screenshot = driver.get_screenshot_as_png()
        
        print("✅ Capture réussie!")
        return screenshot
        
    except Exception as e:
        print(f"❌ Erreur Selenium: {e}")
        raise Exception(f"Erreur génération: {str(e)}")
    
    finally:
        if driver:
            driver.quit()
            print("🔒 Navigateur fermé")

@client.event
async def on_ready():
    print(f'✅ Bot connecté en tant que {client.user}')
    await client.change_presence(activity=discord.Game(name="/maketable"))

@client.event
async def on_message(message):
    if message.author == client.user:
        return
    
    if message.content.startswith('/maketable'):
        try:
            print(f"🔄 Traitement demande de {message.author}")
            
            processing_msg = await message.reply("🔄 Interaction avec gb2.hlorenzi.com... (10-15 secondes)")
            
            # Extraire le texte
            lines = message.content.split('\n')[1:]  # Retirer /maketable
            table_text = '\n'.join(lines).strip()
            
            # Validation
            if not table_text:
                await processing_msg.edit("❌ **Message vide!**\n\n**Format:**\n```/maketable\nA - Équipe Rouge\nJoueur1 1500\nJoueur2 1400\n\nB - Équipe Bleue\nJoueur3 1500\nJoueur4 1400```")
                return
            
            validation_error = validate_table_format(table_text)
            if validation_error:
                await processing_msg.edit(validation_error)
                return
            
            print(f"📋 Génération: {table_text}")
            
            # Générer l'image
            image_data = generate_table_with_selenium(table_text)
            
            # Envoyer l'image
            from io import BytesIO
            image_file = discord.File(BytesIO(image_data), filename="tableau.png")
            
            await message.channel.send(
                content=f"📊 Tableau généré depuis gb2.hlorenzi.com pour {message.author.mention}",
                file=image_file
            )
            
            await processing_msg.delete()
            print("✅ Tableau envoyé!")
            
        except Exception as e:
            print(f"❌ Erreur: {e}")
            
            # En cas d'erreur, envoyer le texte
            lines = message.content.split('\n')[1:]
            table_text = '\n'.join(lines).strip()
            
            error_msg = f"❌ **Erreur avec gb2.hlorenzi.com**\n\n{str(e)}\n\n**Votre tableau:**\n```\n{table_text}\n```"
            await message.reply(error_msg)

# Lancer le bot
if __name__ == "__main__":
    token = os.getenv('DISCORD_TOKEN')
    if not token:
        print("❌ Token Discord manquant!")
        exit(1)
    
    client.run(token)