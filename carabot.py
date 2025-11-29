import discord
import aiohttp
import asyncio
import io
import os
import base64
import json
from urllib.parse import urlencode

# Configuration pour Render
token = os.environ.get('DISCORD_TOKEN')
if not token:
    raise Exception("❌ DISCORD_TOKEN non trouvé dans les variables d'environnement")

client = discord.Client(intents=discord.Intents.all())

class TableGenerator:
    def __init__(self):
        self.base_url = "https://gb2.hlorenzi.com"
        self.session = None
    
    async def ensure_session(self):
        if not self.session:
            self.session = aiohttp.ClientSession()
    
    async def close(self):
        if self.session:
            await self.session.close()
    
    async def get_csrf_token(self):
        """Récupère le token CSRF depuis la page"""
        try:
            async with self.session.get(f"{self.base_url}/table") as response:
                html = await response.text()
                # Cherche le token CSRF dans le HTML
                if 'name="csrf-token"' in html:
                    start = html.find('name="csrf-token"') 
                    start = html.find('content="', start) + 9
                    end = html.find('"', start)
                    return html[start:end]
                return None
        except Exception as e:
            print(f"❌ Erreur CSRF token: {e}")
            return None
    
    async def import_styles(self):
        """Importe les styles Ztix via l'API"""
        try:
            # Charge le fichier JSON
            with open("ztix.json", "r", encoding="utf-8") as f:
                styles_data = json.load(f)
            
            csrf_token = await self.get_csrf_token()
            
            headers = {
                'Content-Type': 'application/json',
                'X-Requested-With': 'XMLHttpRequest'
            }
            
            if csrf_token:
                headers['X-CSRF-TOKEN'] = csrf_token
            
            # Essaye d'importer via l'API
            async with self.session.post(
                f"{self.base_url}/api/styles/import",
                json=styles_data,
                headers=headers
            ) as response:
                if response.status == 200:
                    print("✅ Styles importés avec succès")
                    return True
                else:
                    print(f"⚠️ Import API échoué: {response.status}")
                    return False
                    
        except Exception as e:
            print(f"⚠️ Erreur import styles: {e}")
            return False
    
    async def apply_ztix_style(self):
        """Applique le style Ztix"""
        try:
            csrf_token = await self.get_csrf_token()
            
            headers = {
                'Content-Type': 'application/json',
                'X-Requested-With': 'XMLHttpRequest'
            }
            
            if csrf_token:
                headers['X-CSRF-TOKEN'] = csrf_token
            
            data = {
                'style': 'Ztix'
            }
            
            async with self.session.post(
                f"{self.base_url}/api/styles/apply",
                json=data,
                headers=headers
            ) as response:
                if response.status == 200:
                    print("✅ Style Ztix appliqué")
                    return True
                else:
                    print(f"⚠️ Application style échouée: {response.status}")
                    return False
                    
        except Exception as e:
            print(f"⚠️ Erreur application style: {e}")
            return False
    
    async def generate_table_image(self, table_text):
        """Génère l'image du tableau via l'API"""
        try:
            await self.ensure_session()
            
            print("🔄 Configuration des styles...")
            await self.import_styles()
            await self.apply_ztix_style()
            
            print("📊 Génération du tableau...")
            
            # Méthode 1: Essaye l'API directe
            payload = {
                'text': table_text,
                'style': 'Ztix',
                'format': 'png'
            }
            
            headers = {
                'Content-Type': 'application/json',
                'X-Requested-With': 'XMLHttpRequest'
            }
            
            # Essaye l'endpoint API principal
            async with self.session.post(
                f"{self.base_url}/api/generate",
                json=payload,
                headers=headers,
                timeout=30
            ) as response:
                
                if response.status == 200:
                    content_type = response.headers.get('Content-Type', '')
                    
                    if 'image' in content_type:
                        # Réponse directe image
                        image_data = await response.read()
                        print("✅ Image générée via API")
                        return image_data
                    else:
                        # Réponse JSON avec image base64
                        result = await response.json()
                        if 'image' in result and result['image']:
                            base64_data = result['image'].split(',')[1]
                            image_data = base64.b64decode(base64_data)
                            print("✅ Image générée via API base64")
                            return image_data
            
            # Méthode 2: Fallback - requête GET avec paramètres
            print("🔄 Tentative méthode alternative...")
            
            params = {
                'text': table_text,
                'style': 'Ztix'
            }
            
            async with self.session.get(
                f"{self.base_url}/render",
                params=params,
                timeout=30
            ) as response:
                
                if response.status == 200:
                    image_data = await response.read()
                    print("✅ Image générée via render")
                    return image_data
            
            # Si toutes les méthodes échouent
            raise Exception("Aucune méthode de génération n'a fonctionné")
            
        except asyncio.TimeoutError:
            raise Exception("Timeout - le service de génération est trop lent")
        except Exception as e:
            raise Exception(f"Erreur génération: {str(e)}")

# Instance globale du générateur
table_gen = TableGenerator()

@client.event
async def on_message(message: discord.Message):
    if message.author.bot:
        return
    
    if message.content.lower().startswith("maketable"):
        try:
            table_text = message.content[len("maketable"):].strip()
            
            if not table_text:
                await message.channel.send("❌ **Veuillez fournir le texte du tableau!**")
                return
            
            # Vérification longueur
            if len(table_text) > 2000:
                await message.channel.send("❌ **Le texte est trop long! Maximum 2000 caractères.**")
                return
            
            processing_msg = await message.channel.send("🔄 Génération en cours... (version HTTP optimisée)")
            
            try:
                # Génération avec timeout
                image_data = await asyncio.wait_for(
                    table_gen.generate_table_image(table_text),
                    timeout=45.0
                )
                
                # Création du fichier Discord
                image_file = discord.File(
                    io.BytesIO(image_data), 
                    filename="tableau.png"
                )
                
                await message.channel.send(
                    content=f"📊 Tableau généré pour {message.author.mention}",
                    file=image_file
                )
                
                await processing_msg.delete()
                
            except asyncio.TimeoutError:
                await message.channel.send("❌ **Timeout - la génération a pris trop de temps**")
            except Exception as e:
                await message.channel.send(f"❌ **Erreur de génération:** {str(e)}")
            
        except Exception as e:
            await message.channel.send(f"❌ **Erreur:** {str(e)}")
    
    elif message.content.lower() == "!ping":
        await message.channel.send("🏓 Pong! Bot HTTP actif - Version optimisée Render")
    
    elif message.content.lower() == "!status":
        await message.channel.send("✅ Bot fonctionnel - Méthode HTTP sans Selenium")

@client.event
async def on_ready():
    print(f'✅ Bot HTTP connecté en tant que {client.user}')
    print(f'🚀 Version optimisée pour Render - Prêt!')

@client.event
async def on_disconnect():
    await table_gen.close()

async def main():
    await client.start(token)

if __name__ == "__main__":
    print("🚀 Démarrage du bot Discord HTTP sur Render...")
    
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("🛑 Arrêt du bot...")
    finally:
        # Nettoyage propre
        asyncio.run(table_gen.close())
