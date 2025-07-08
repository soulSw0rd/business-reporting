"""
Scraper avancé pour hyperdash.info avec techniques d'évasion
Utilise Selenium et des méthodes pour contourner les protections anti-bot
"""

import time
import json
import re
import random
from typing import Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime
import logging
import os
from urllib.parse import urljoin
import requests
from bs4 import BeautifulSoup

# Selenium imports
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
# from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import TimeoutException, WebDriverException
import undetected_chromedriver as uc

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class TraderData:
    """Structure des données d'un trader"""
    address: str
    username: Optional[str] = None
    pnl: Optional[float] = None
    win_rate: Optional[float] = None
    total_trades: Optional[int] = None
    volume: Optional[float] = None
    roi: Optional[float] = None
    sharpe_ratio: Optional[float] = None
    followers: Optional[int] = None
    reputation: Optional[float] = None
    last_active: Optional[str] = None

class AdvancedHyperdashScraper:
    """Scraper avancé pour hyperdash.info avec évasion anti-bot"""
    
    def __init__(self, use_selenium: bool = True):
        self.base_url = "https://hyperdash.info"
        self.use_selenium = use_selenium
        self.driver = None
        self.session = requests.Session()
        self.setup_session()
        
    def setup_session(self):
        """Configure la session requests avec headers avancés"""
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'Accept-Language': 'en-US,en;q=0.9,fr;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Cache-Control': 'no-cache',
            'Pragma': 'no-cache',
            'Sec-Ch-Ua': '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
            'Sec-Ch-Ua-Mobile': '?0',
            'Sec-Ch-Ua-Platform': '"Windows"',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1',
            'Upgrade-Insecure-Requests': '1',
            'Connection': 'keep-alive'
        }
        self.session.headers.update(headers)
        
    def setup_selenium_driver(self):
        """Configure le driver Selenium avec options anti-détection"""
        try:
            logger.info("🚀 Configuration du driver Selenium...")
            
            # Options pour undetected-chromedriver
            options = uc.ChromeOptions()
            
            # Options pour éviter la détection
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument('--disable-gpu')
            options.add_argument('--disable-blink-features=AutomationControlled')
            options.add_experimental_option("excludeSwitches", ["enable-automation"])
            options.add_experimental_option('useAutomationExtension', False)
            
            # Simuler un navigateur réel
            options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
            options.add_argument('--window-size=1920,1080')
            
            # Mode headless optionnel
            # options.add_argument('--headless')
            
            # Créer le driver
            self.driver = uc.Chrome(options=options)
            
            # Scripts pour masquer l'automation
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            self.driver.execute_cdp_cmd('Network.setUserAgentOverride', {
                "userAgent": 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            })
            
            logger.info("✅ Driver Selenium configuré avec succès")
            return True
            
        except Exception as e:
            logger.error(f"❌ Erreur configuration Selenium: {e}")
            return False
    
    def get_page_selenium(self, url: str, wait_time: int = 10) -> Optional[BeautifulSoup]:
        """Récupère une page avec Selenium"""
        if not self.driver:
            if not self.setup_selenium_driver():
                return None
        
        try:
            logger.info(f"🌐 Selenium: Récupération de {url}")
            
            # Aller à la page
            self.driver.get(url)
            
            # Attendre le chargement
            time.sleep(random.uniform(2, 4))
            
            # Attendre un élément spécifique (ajuster selon le site)
            try:
                WebDriverWait(self.driver, wait_time).until(
                    EC.presence_of_element_located((By.TAG_NAME, "body"))
                )
            except TimeoutException:
                logger.warning("⚠️ Timeout lors de l'attente du chargement")
            
            # Scroll pour simuler un comportement humain
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight/2);")
            time.sleep(1)
            self.driver.execute_script("window.scrollTo(0, 0);")
            
            # Récupérer le HTML
            html = self.driver.page_source
            soup = BeautifulSoup(html, 'html.parser')
            
            logger.info(f"✅ Page récupérée avec Selenium: {len(html)} bytes")
            return soup
            
        except Exception as e:
            logger.error(f"❌ Erreur Selenium: {e}")
            return None
    
    def get_page_requests(self, url: str, max_retries: int = 3) -> Optional[BeautifulSoup]:
        """Récupère une page avec requests + techniques d'évasion"""
        for attempt in range(max_retries):
            try:
                # Délai aléatoire
                time.sleep(random.uniform(1, 3))
                
                # Rotation des headers
                user_agents = [
                    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0'
                ]
                
                self.session.headers['User-Agent'] = random.choice(user_agents)
                
                # Ajouter des cookies de session
                self.session.cookies.set('visited', 'true')
                
                logger.info(f"📥 Requests: Récupération de {url} (tentative {attempt + 1})")
                
                response = self.session.get(url, timeout=15)
                
                if response.status_code == 403:
                    logger.warning(f"⚠️ 403 Forbidden - Tentative {attempt + 1}")
                    if attempt < max_retries - 1:
                        time.sleep(random.uniform(5, 10))
                        continue
                
                response.raise_for_status()
                
                soup = BeautifulSoup(response.content, 'html.parser')
                logger.info(f"✅ Page récupérée avec requests: {len(response.content)} bytes")
                return soup
                
            except requests.RequestException as e:
                logger.error(f"❌ Erreur requests (tentative {attempt + 1}): {e}")
                if attempt < max_retries - 1:
                    time.sleep(2 ** attempt)
                    
        return None
    
    def get_page(self, url: str) -> Optional[BeautifulSoup]:
        """Récupère une page en utilisant la meilleure méthode disponible"""
        # Essayer d'abord avec Selenium si activé
        if self.use_selenium:
            soup = self.get_page_selenium(url)
            if soup:
                return soup
            logger.warning("⚠️ Selenium a échoué, tentative avec requests...")
        
        # Fallback sur requests
        return self.get_page_requests(url)
    
    def test_access(self) -> Dict[str, bool]:
        """Test l'accessibilité du site avec différentes méthodes"""
        results = {}
        
        # Test page d'accueil
        test_url = self.base_url
        
        # Test avec requests
        logger.info("🧪 Test d'accès avec requests...")
        soup_requests = self.get_page_requests(test_url)
        results['requests'] = soup_requests is not None
        
        # Test avec Selenium
        if self.use_selenium:
            logger.info("🧪 Test d'accès avec Selenium...")
            soup_selenium = self.get_page_selenium(test_url)
            results['selenium'] = soup_selenium is not None
        
        return results
    
    def analyze_page_structure(self, url: str) -> Dict:
        """Analyse la structure d'une page pour comprendre le layout"""
        soup = self.get_page(url)
        
        if not soup:
            return {"error": "Impossible de récupérer la page"}
        
        analysis = {
            "title": soup.title.string if soup.title else "N/A",
            "links_count": len(soup.find_all('a')),
            "trader_links": [],
            "class_names": set(),
            "id_names": set()
        }
        
        # Rechercher les liens de traders
        trader_links = soup.find_all('a', href=re.compile(r'/trader/0x[a-fA-F0-9]{40}'))
        for link in trader_links:
            analysis["trader_links"].append({
                "href": link.get('href'),
                "text": link.get_text(strip=True),
                "classes": link.get('class', [])
            })
        
        # Analyser les classes CSS utilisées
        for elem in soup.find_all(class_=True):
            for cls in elem.get('class', []):
                analysis["class_names"].add(cls)
        
        # Analyser les IDs
        for elem in soup.find_all(id=True):
            analysis["id_names"].add(elem.get('id'))
        
        # Convertir les sets en listes pour JSON
        analysis["class_names"] = list(analysis["class_names"])
        analysis["id_names"] = list(analysis["id_names"])
        
        return analysis
    
    def get_traders_from_hype_page(self) -> List[Dict]:
        """Récupère les traders depuis la page /hype avec analyse avancée"""
        url = f"{self.base_url}/hype"
        soup = self.get_page(url)
        
        if not soup:
            logger.error("❌ Impossible de récupérer la page /hype")
            return []
        
        traders = []
        
        # Recherche flexible des traders
        # 1. Liens directs vers les profils
        direct_links = soup.find_all('a', href=re.compile(r'/trader/0x[a-fA-F0-9]{40}'))
        
        # 2. Recherche par patterns de text (adresses tronquées)
        address_patterns = soup.find_all(text=re.compile(r'0x[a-fA-F0-9]{4}\.\.\.'))
        
        # 3. Recherche par classes CSS communes
        potential_trader_elements = soup.find_all(['div', 'tr', 'li'], class_=re.compile(r'trader|user|profile|row', re.I))
        
        logger.info(f"🔍 Trouvé {len(direct_links)} liens directs, {len(address_patterns)} patterns d'adresse")
        
        for link in direct_links:
            try:
                href = link.get('href')
                address_match = re.search(r'0x[a-fA-F0-9]{40}', href)
                
                if address_match:
                    address = address_match.group()
                    
                    trader_info = {
                        'address': address,
                        'display_address': link.get_text(strip=True),
                        'profile_url': urljoin(self.base_url, href),
                        'scraped_at': datetime.now().isoformat()
                    }
                    
                    # Extraction des métriques depuis le contexte
                    context = link.parent
                    if context:
                        context_text = context.get_text()
                        trader_info['context'] = context_text
                        
                        # Recherche de métriques
                        pnl_match = re.search(r'[\+\-]?\$?([0-9,]+\.?[0-9]*)[KMB]?', context_text)
                        if pnl_match:
                            trader_info['pnl_text'] = pnl_match.group()
                    
                    traders.append(trader_info)
                    
            except Exception as e:
                logger.error(f"❌ Erreur extraction trader: {e}")
                continue
        
        logger.info(f"📊 {len(traders)} traders extraits de /hype")
        return traders
    
    def save_analysis_results(self, data: Dict, filename: str = None):
        """Sauvegarde les résultats d'analyse"""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"hyperdash_analysis_{timestamp}.json"
        
        # Créer le dossier data
        os.makedirs("data", exist_ok=True)
        filepath = f"data/{filename}"
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False, default=str)
        
        logger.info(f"💾 Analyse sauvegardée: {filepath}")
        return filepath
    
    def run_complete_analysis(self) -> Dict:
        """Analyse complète du site hyperdash.info"""
        logger.info("🚀 Début de l'analyse complète Hyperdash")
        
        analysis = {
            "timestamp": datetime.now().isoformat(),
            "access_test": {},
            "home_page_analysis": {},
            "hype_page_analysis": {},
            "traders_found": []
        }
        
        # 1. Test d'accès
        logger.info("1️⃣ Test d'accessibilité...")
        analysis["access_test"] = self.test_access()
        
        # 2. Analyse page d'accueil
        logger.info("2️⃣ Analyse page d'accueil...")
        analysis["home_page_analysis"] = self.analyze_page_structure(self.base_url)
        
        # 3. Analyse page /hype
        logger.info("3️⃣ Analyse page /hype...")
        hype_url = f"{self.base_url}/hype"
        analysis["hype_page_analysis"] = self.analyze_page_structure(hype_url)
        
        # 4. Extraction des traders
        logger.info("4️⃣ Extraction des traders...")
        analysis["traders_found"] = self.get_traders_from_hype_page()
        
        # 5. Statistiques
        analysis["summary"] = {
            "site_accessible": any(analysis["access_test"].values()),
            "traders_count": len(analysis["traders_found"]),
            "recommended_method": "selenium" if analysis["access_test"].get("selenium") else "requests"
        }
        
        return analysis
    
    def cleanup(self):
        """Nettoie les ressources"""
        if self.driver:
            try:
                self.driver.quit()
                logger.info("🧹 Driver Selenium fermé")
            except:
                pass

def main():
    """Fonction principale"""
    scraper = AdvancedHyperdashScraper(use_selenium=True)
    
    try:
        # Analyse complète
        results = scraper.run_complete_analysis()
        
        # Sauvegarde
        filepath = scraper.save_analysis_results(results)
        
        # Affichage des résultats
        print("\n" + "="*50)
        print("📊 RÉSULTATS DE L'ANALYSE HYPERDASH")
        print("="*50)
        print(f"🌐 Site accessible: {results['summary']['site_accessible']}")
        print(f"📈 Traders trouvés: {results['summary']['traders_count']}")
        print(f"🔧 Méthode recommandée: {results['summary']['recommended_method']}")
        print(f"📁 Fichier de résultats: {filepath}")
        
        if results["traders_found"]:
            print("\n🎯 PREMIERS TRADERS TROUVÉS:")
            for i, trader in enumerate(results["traders_found"][:3]):
                print(f"  {i+1}. {trader['address'][:10]}... - {trader.get('display_address', 'N/A')}")
        
        return results
        
    except KeyboardInterrupt:
        logger.info("⚠️ Interruption par l'utilisateur")
    except Exception as e:
        logger.error(f"❌ Erreur générale: {e}")
    finally:
        scraper.cleanup()

if __name__ == "__main__":
    main() 