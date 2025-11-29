import discord
from discord import Intents
import os
import asyncio
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import io

# Configuration du bot
intents = Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

def validate_table_format(table_text):
    """Valide le format du tableau"""
    if not table_text or not table_text.strip():
        return "❌ **Message vide!**"
    
    lines = [line.strip() for line in table_text.split('\n') if line.strip()]
    team_lines = [line for line in lines if '-' in line]
    
    if len(team_lines) < 1:
        return "❌ **Format incorrect!** Il faut au moins 1 équipe.\nExemple: `Tag - NomÉquipe`"
    
    return None

def generate_table_screenshot(table_text):
    """Génère une capture d'écran du tableau"""
    driver = None
    try:
        print("🌐 Configuration du navigateur...")
        
        chrome_options = Options()
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--window-size=1200,800')
        
        driver = webdriver.Chrome(options=chrome_options)
        
        print("📡 Navigation vers gb2.hlorenzi.com/table...")
        driver.get("https://gb2.hlorenzi.com/table")
        
        # Attendre un peu
        driver.implicitly_wait(5)
        
        # Chercher et remplir la zone de texte
        print("🔍 Recherche de la zone de texte...")
        textarea = None
        
        # Essayer différents sélecteurs
        selectors = ["textarea", "input[type='text']", ".input", "#input"]
        for selector in selectors:
            try:
                textarea = driver.find_element(By.CSS_SELECTOR, selector)
                if textarea:
                    print(f"✅ Trouvé avec: {selector}")
                    break
            except:
                continue
        
        if not textarea:
            # Prendre une capture de la page telle quelle
            print("⚠️ Zone de texte non trouvée, capture de la page...")
            screenshot = driver.get_screenshot_as_png()
            return screenshot
        
        # Remplir le texte
        print("📝 Remplissage du tableau...")
        textarea.clear()
        textarea.send_keys(table_text)
        
        # Attendre la génération
        print("⏳ Attente de la génération...")
        driver.implicitly_wait(3)
        
        # Prendre la capture
        print("📸 Capture d'écran...")
        screenshot = driver.get_screenshot_as_png()
        
        print("✅ Capture réussie!")
        return screenshot
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
        raise Exception(f"Erreur lors de la génération: {str(e)}")
    
    finally:
        if driver:
            driver.quit()
            print("🔒 Navigateur fermé")

@client.event
async def on_ready():
    print(f'✅ Bot connecté en tant que {client.user}')
    activity = discord.Game(name="/maketable")
    await client.change_presence(activity=activity)

@client.event
async def on_message(message):
    if message.author == client.user:
        return
    
    if message.content.startswith('/maketable'):
        try:
            print(f"🔄 Demande de {message.author}")
            
            # Message de traitement
            processing_msg = await message.reply("🔄 Génération en cours...")
            
            # Extraire le texte
            content = message.content.replace('/maketable', '').strip()
            if not content:
                await processing_msg.edit("❌ **Format incorrect!**\n\nExemple:\n```/maketable\nA - Équipe Rouge\nJ1 1500\nJ2 1400\n\nB - Équipe Bleue\nJ3 1500\nJ4 1400```")
                return
            
            # Valider le format
            error = validate_table_format(content)
            if error:
                await processing_msg.edit(error)
                return
            
            # Générer l'image
            image_data = generate_table_screenshot(content)
            
            # Créer le fichier Discord
            from io import BytesIO
            image_file = discord.File(io.BytesIO(image_data), filename="tableau.png")
            
            # Envoyer le résultat
            await message.channel.send(
                content=f"📊 Tableau pour {message.author.mention}",
                file=image_file
            )
            
            # Supprimer le message de traitement
            await processing_msg.delete()
            
        except Exception as e:
            error_msg = f"❌ Erreur: {str(e)}"
            await message.reply(error_msg)
            print(f"❌ Erreur finale: {e}")

# Lancer le bot
if __name__ == "__main__":
    token = os.getenv('DISCORD_TOKEN')
    if not token:
        print("❌ Token Discord manquant!")
        exit(1)
    
    client.run(token)