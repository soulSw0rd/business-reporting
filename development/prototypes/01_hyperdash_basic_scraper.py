"""
Service de scraping pour hyperdash.info
Extraction des données de traders et wallets pour prédictions
"""

import requests
from bs4 import BeautifulSoup
import json
import time
import re
from typing import Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime
import logging
from urllib.parse import urljoin, urlparse

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

class HyperdashScraper:
    """Scraper principal pour hyperdash.info"""
    
    def __init__(self):
        self.base_url = "https://hyperdash.info"
        self.session = requests.Session()
        self.setup_session()
        
    def setup_session(self):
        """Configure la session avec headers réalistes"""
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        }
        self.session.headers.update(headers)
        
    def get_page_content(self, url: str, max_retries: int = 3) -> Optional[BeautifulSoup]:
        """Récupère le contenu d'une page avec retry"""
        for attempt in range(max_retries):
            try:
                logger.info(f"📥 Récupération de: {url} (tentative {attempt + 1})")
                
                response = self.session.get(url, timeout=15)
                response.raise_for_status()
                
                soup = BeautifulSoup(response.content, 'html.parser')
                logger.info(f"✅ Page récupérée avec succès: {len(response.content)} bytes")
                return soup
                
            except requests.RequestException as e:
                logger.error(f"❌ Erreur lors de la récupération (tentative {attempt + 1}): {e}")
                if attempt < max_retries - 1:
                    time.sleep(2 ** attempt)  # Backoff exponentiel
                    
        return None
    
    def get_hype_page_traders(self) -> List[Dict]:
        """Récupère la liste des traders depuis la page /hype"""
        url = f"{self.base_url}/hype"
        soup = self.get_page_content(url)
        
        if not soup:
            logger.error("Impossible de récupérer la page /hype")
            return []
            
        traders = []
        
        # Analyser la structure HTML pour extraire les traders
        # Recherche des liens vers les profiles de traders
        trader_links = soup.find_all('a', {'href': re.compile(r'/trader/0x[a-fA-F0-9]{40}')})
        
        logger.info(f"🔍 Trouvé {len(trader_links)} liens de traders")
        
        for link in trader_links:
            try:
                # Extraire l'adresse du wallet depuis l'URL
                href = link.get('href')
                address_match = re.search(r'0x[a-fA-F0-9]{40}', href)
                
                if address_match:
                    address = address_match.group()
                    
                    # Extraire le texte affiché (adresse tronquée)
                    display_text = link.get_text(strip=True)
                    
                    # Rechercher les données dans le parent ou les éléments adjacents
                    parent = link.parent
                    trader_data = self.extract_trader_data_from_element(parent, address)
                    
                    traders.append({
                        'address': address,
                        'display_address': display_text,
                        'profile_url': urljoin(self.base_url, href),
                        **trader_data
                    })
                    
            except Exception as e:
                logger.error(f"Erreur lors de l'extraction du trader: {e}")
                continue
                
        logger.info(f"📊 Extracted {len(traders)} traders from /hype page")
        return traders
    
    def extract_trader_data_from_element(self, element, address: str) -> Dict:
        """Extrait les données d'un trader depuis un élément HTML"""
        data = {}
        
        try:
            # Recherche des métriques dans le contexte de l'élément
            text_content = element.get_text()
            
            # Pattern matching pour différentes métriques
            patterns = {
                'pnl': r'[\+\-]?\$?([0-9,]+\.?[0-9]*)[KMB]?',
                'win_rate': r'([0-9]+\.?[0-9]*)%',
                'volume': r'\$([0-9,]+\.?[0-9]*)[KMB]?',
                'trades': r'([0-9,]+)\s*trades?'
            }
            
            for metric, pattern in patterns.items():
                match = re.search(pattern, text_content, re.IGNORECASE)
                if match:
                    value = match.group(1).replace(',', '')
                    try:
                        data[metric] = float(value)
                    except ValueError:
                        data[metric] = value
                        
        except Exception as e:
            logger.error(f"Erreur extraction données trader {address}: {e}")
            
        return data
    
    def get_trader_profile(self, address: str) -> Optional[TraderData]:
        """Récupère le profil détaillé d'un trader"""
        url = f"{self.base_url}/trader/{address}"
        soup = self.get_page_content(url)
        
        if not soup:
            logger.error(f"Impossible de récupérer le profil du trader {address}")
            return None
            
        try:
            trader_data = TraderData(address=address)
            
            # Extraction du nom d'utilisateur
            username_elem = soup.find('h1') or soup.find('h2')
            if username_elem:
                trader_data.username = username_elem.get_text(strip=True)
            
            # Extraction des métriques principales
            metric_elements = soup.find_all(['div', 'span'], class_=re.compile(r'metric|stat|value'))
            
            for elem in metric_elements:
                text = elem.get_text(strip=True)
                
                # PnL
                if '$' in text and any(word in text.lower() for word in ['pnl', 'profit', 'loss']):
                    pnl_match = re.search(r'[\+\-]?\$?([0-9,]+\.?[0-9]*)', text)
                    if pnl_match:
                        trader_data.pnl = float(pnl_match.group(1).replace(',', ''))
                
                # Win Rate
                if '%' in text and 'win' in text.lower():
                    wr_match = re.search(r'([0-9]+\.?[0-9]*)%', text)
                    if wr_match:
                        trader_data.win_rate = float(wr_match.group(1))
                
                # Volume
                if '$' in text and 'volume' in text.lower():
                    vol_match = re.search(r'\$([0-9,]+\.?[0-9]*)', text)
                    if vol_match:
                        trader_data.volume = float(vol_match.group(1).replace(',', ''))
            
            logger.info(f"✅ Profil trader récupéré: {address[:10]}...")
            return trader_data
            
        except Exception as e:
            logger.error(f"Erreur lors de l'extraction du profil {address}: {e}")
            return None
    
    def scrape_all_data(self, max_traders: int = 10) -> Dict:
        """Scrape complet des données"""
        logger.info(f"🚀 Début du scraping Hyperdash (max {max_traders} traders)")
        
        # 1. Récupérer la liste des traders
        traders_list = self.get_hype_page_traders()
        
        if not traders_list:
            logger.error("Aucun trader trouvé sur la page /hype")
            return {"error": "Aucun trader trouvé"}
        
        # 2. Récupérer les détails de chaque trader
        detailed_traders = []
        
        for i, trader in enumerate(traders_list[:max_traders]):
            if i > 0 and i % 3 == 0:  # Pause tous les 3 traders
                logger.info(f"⏸️ Pause (traité {i}/{len(traders_list)} traders)")
                time.sleep(3)
                
            logger.info(f"📊 Traitement trader {i+1}/{min(max_traders, len(traders_list))}: {trader['address'][:10]}...")
            
            # Profil détaillé
            profile = self.get_trader_profile(trader['address'])
            
            detailed_traders.append({
                'basic_info': trader,
                'profile': profile.__dict__ if profile else None,
                'scraped_at': datetime.now().isoformat()
            })
        
        result = {
            'scraped_at': datetime.now().isoformat(),
            'total_traders_found': len(traders_list),
            'detailed_traders_count': len(detailed_traders),
            'traders': detailed_traders,
            'summary': {
                'source': 'hyperdash.info',
                'method': 'web_scraping',
                'success_rate': len(detailed_traders) / len(traders_list) if traders_list else 0
            }
        }
        
        logger.info(f"✅ Scraping terminé: {len(detailed_traders)} traders analysés")
        return result
    
    def save_data_to_json(self, data: Dict, filename: str = None):
        """Sauvegarde les données en JSON"""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"hyperdash_scraping_{timestamp}.json"
            
        filepath = f"data/{filename}"
        
        # Créer le dossier data s'il n'existe pas
        import os
        os.makedirs("data", exist_ok=True)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False, default=str)
            
        logger.info(f"💾 Données sauvegardées: {filepath}")
        return filepath

# Fonction principale pour tester le scraper
def main():
    """Fonction principale de test"""
    scraper = HyperdashScraper()
    
    # Test avec l'adresse fournie
    test_address = "0xdfc24b077bc1425ad1dea75bcb6f8158e10df303"
    
    logger.info("🧪 Test du scraper Hyperdash")
    
    # 1. Test récupération profil
    logger.info(f"1️⃣ Test profil trader: {test_address}")
    profile = scraper.get_trader_profile(test_address)
    if profile:
        logger.info(f"✅ Profil récupéré: {profile}")
    else:
        logger.error("❌ Impossible de récupérer le profil")
    
    # 2. Test récupération page /hype
    logger.info("2️⃣ Test page /hype")
    traders = scraper.get_hype_page_traders()
    logger.info(f"📊 {len(traders)} traders trouvés sur /hype")
    
    # 3. Scraping complet (limité)
    logger.info("3️⃣ Test scraping complet")
    all_data = scraper.scrape_all_data(max_traders=3)
    
    # 4. Sauvegarde
    filepath = scraper.save_data_to_json(all_data)
    logger.info(f"📁 Données sauvegardées: {filepath}")
    
    return all_data

if __name__ == "__main__":
    main() 