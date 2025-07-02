# -*- coding: utf-8 -*-

"""
scrapers.py

Module contenant les fonctions de scraping pour les différentes sources de données,
notamment hyperdash.info.
"""

# -----------------------------------------------------------------------------
# Imports
# -----------------------------------------------------------------------------

import json
import os
import re
import time
from datetime import datetime
from typing import List, Dict, Any, Optional
from dataclasses import dataclass

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

# -----------------------------------------------------------------------------
# Constantes
# -----------------------------------------------------------------------------

BASE_URL = "https://hyperdash.info"
SAVE_PATH = "DATA/processed"
WAIT_TIMEOUT = 30 # Augmenté pour les connexions lentes

# -----------------------------------------------------------------------------
# Fonctions de Scraping
# -----------------------------------------------------------------------------

def setup_driver():
    """
    Configure et retourne un driver Selenium.
    Selenium Manager (inclus dans Selenium 4.6+) gère automatiquement le driver.
    """
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
    
    try:
        # Il n'est plus nécessaire de spécifier le chemin du driver.
        # Selenium s'en charge.
        driver = webdriver.Chrome(options=options)
        return driver
    except Exception as e:
        print(f"Échec de l'initialisation du driver Selenium : {e}")
        print("Veuillez vous assurer que Google Chrome est installé sur votre système.")
        return None

def scrape_top_traders():
    """
    Scrape les données des top traders en utilisant Selenium pour gérer le contenu dynamique.
    """
    print("Initialisation du driver Selenium...")
    driver = setup_driver()
    if not driver:
        print("Impossible d'initialiser le driver Selenium. Abandon.")
        return None

    url = f"{BASE_URL}/top-traders"
    print(f"Navigation vers : {url}")

    try:
        driver.get(url)

        print(f"Attente du chargement du tableau des traders (max {WAIT_TIMEOUT}s)...")
        wait = WebDriverWait(driver, WAIT_TIMEOUT)
        # Attendre la présence du tableau ET qu'au moins une ligne <tr> soit visible à l'intérieur
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "#traders-table tbody tr")))

        print("Tableau détecté. Récupération du code source de la page.")
        time.sleep(3) # Laisse un délai pour que tout se stabilise
        
        page_source = driver.page_source

        soup = BeautifulSoup(page_source, 'html.parser')
        traders_data = []
        
        trader_rows = soup.select("#traders-table tbody tr")
        print(f"Trouvé {len(trader_rows)} traders dans le tableau.")

        if not trader_rows:
            print("Aucune ligne de trader trouvée. La structure du site a peut-être changé.")
            return None

        for row in trader_rows:
            link_element = row.find('a', href=lambda href: href and href.startswith('/trader/'))
            if link_element:
                trader_address = link_element['href'].split('/')[-1]
                
                pnl_element = row.find('div', class_=lambda c: c and 'text-green-400' in c)
                pnl = pnl_element.text.strip() if pnl_element else "N/A"

                traders_data.append({
                    "address": trader_address,
                    "pnl_7d": pnl, 
                    "scraped_at": datetime.now().isoformat()
                })

        if not traders_data:
            print("Données extraites mais la liste est vide. Vérifiez les sélecteurs.")
            return None

        os.makedirs(SAVE_PATH, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        file_path = os.path.join(SAVE_PATH, f"top_traders_{timestamp}.json")

        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(traders_data, f, indent=4)

        print(f"Succès ! Données de {len(traders_data)} traders sauvegardées dans {file_path}")
        return file_path

    except Exception as e:
        print(f"Une erreur est survenue pendant le scraping : {e}")
        # Sauvegarde du HTML en cas d'erreur pour le debug
        with open("debug_error_page.html", "w", encoding="utf-8") as f:
            f.write(driver.page_source)
        print("Le HTML de la page au moment de l'erreur a été sauvegardé dans 'debug_error_page.html'")
        return None
    finally:
        print("Fermeture du driver Selenium.")
        if driver:
            driver.quit() 

@dataclass
class TraderMetrics:
    """Structure complète des métriques d'un trader"""
    address: str
    username: Optional[str] = None
    pnl_7d: Optional[float] = None
    pnl_30d: Optional[float] = None
    win_rate: Optional[float] = None
    total_trades: Optional[int] = None
    total_volume: Optional[float] = None
    roi_7d: Optional[float] = None
    roi_30d: Optional[float] = None
    sharpe_ratio: Optional[float] = None
    max_drawdown: Optional[float] = None
    last_trade_time: Optional[str] = None
    followers: Optional[int] = None
    copying_traders: Optional[int] = None
    confidence_score: Optional[float] = None
    scraped_at: str = None

class EnhancedHyperdashScraper:
    """Scraper amélioré avec extraction complète des métriques"""
    
    def __init__(self):
        self.base_url = "https://hyperdash.info"
        self.driver = None
        self.save_path = "DATA/processed"
        
    def setup_driver(self):
        """Configure le driver avec options anti-détection avancées"""
        options = webdriver.ChromeOptions()
        
        # Options de base
        options.add_argument("--headless")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-gpu")
        
        # Anti-détection avancée
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        
        # Headers réalistes
        options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
        
        try:
            self.driver = webdriver.Chrome(options=options)
            
            # Scripts anti-détection
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            return True
            
        except Exception as e:
            print(f"❌ Erreur initialisation driver: {e}")
            return False
    
    def extract_trader_metrics_from_profile(self, address: str) -> Optional[TraderMetrics]:
        """Extrait les métriques complètes depuis le profil d'un trader"""
        url = f"{self.base_url}/trader/{address}"
        
        try:
            print(f"📊 Extraction métriques pour {address[:10]}...")
            self.driver.get(url)
            
            # Attendre le chargement des métriques
            WebDriverWait(self.driver, 15).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            
            time.sleep(3)  # Laisser le JS se charger
            
            soup = BeautifulSoup(self.driver.page_source, 'html.parser')
            
            trader = TraderMetrics(
                address=address,
                scraped_at=datetime.now().isoformat()
            )
            
            # Extraction du nom d'utilisateur
            username_selectors = [
                'h1', 'h2', '.trader-name', '.username', '[data-testid="trader-name"]'
            ]
            for selector in username_selectors:
                element = soup.select_one(selector)
                if element and element.get_text(strip=True):
                    trader.username = element.get_text(strip=True)
                    break
            
            # Extraction des métriques financières
            text_content = soup.get_text()
            
            # PnL patterns
            pnl_patterns = [
                r'PnL.*?[\+\-]?\$?([0-9,]+\.?[0-9]*)[KMB]?',
                r'Profit.*?[\+\-]?\$?([0-9,]+\.?[0-9]*)[KMB]?',
                r'7d.*?[\+\-]?\$?([0-9,]+\.?[0-9]*)[KMB]?'
            ]
            
            for pattern in pnl_patterns:
                match = re.search(pattern, text_content, re.IGNORECASE)
                if match:
                    trader.pnl_7d = self._parse_financial_value(match.group(1))
                    break
            
            # Win Rate
            win_rate_match = re.search(r'win.*?rate.*?([0-9]+\.?[0-9]*)%', text_content, re.IGNORECASE)
            if win_rate_match:
                trader.win_rate = float(win_rate_match.group(1)) / 100
            
            # Volume
            volume_match = re.search(r'volume.*?\$?([0-9,]+\.?[0-9]*)[KMB]?', text_content, re.IGNORECASE)
            if volume_match:
                trader.total_volume = self._parse_financial_value(volume_match.group(1))
            
            # Nombre de trades
            trades_match = re.search(r'([0-9,]+)\s*trades?', text_content, re.IGNORECASE)
            if trades_match:
                trader.total_trades = int(trades_match.group(1).replace(',', ''))
            
            # ROI
            roi_match = re.search(r'roi.*?([0-9]+\.?[0-9]*)%', text_content, re.IGNORECASE)
            if roi_match:
                trader.roi_7d = float(roi_match.group(1)) / 100
            
            # Followers/Copiers
            followers_match = re.search(r'([0-9,]+)\s*followers?', text_content, re.IGNORECASE)
            if followers_match:
                trader.followers = int(followers_match.group(1).replace(',', ''))
            
            # Calculer un score de confiance basé sur les données disponibles
            trader.confidence_score = self._calculate_confidence_score(trader)
            
            print(f"✅ Métriques extraites: Win Rate: {trader.win_rate}, Volume: {trader.total_volume}")
            return trader
            
        except Exception as e:
            print(f"❌ Erreur extraction {address}: {e}")
            return None
    
    def _parse_financial_value(self, value_str: str) -> float:
        """Parse une valeur financière avec suffixes K/M/B"""
        if not value_str:
            return 0.0
            
        value_str = value_str.replace(',', '').strip()
        
        multipliers = {'K': 1000, 'M': 1000000, 'B': 1000000000}
        
        for suffix, multiplier in multipliers.items():
            if value_str.endswith(suffix):
                return float(value_str[:-1]) * multiplier
        
        try:
            return float(value_str)
        except:
            return 0.0
    
    def _calculate_confidence_score(self, trader: TraderMetrics) -> float:
        """Calcule un score de confiance basé sur la complétude des données"""
        score = 0.0
        
        # Points pour chaque métrique disponible
        if trader.pnl_7d is not None:
            score += 0.2
        if trader.win_rate is not None:
            score += 0.25
        if trader.total_volume is not None and trader.total_volume > 0:
            score += 0.2
        if trader.total_trades is not None and trader.total_trades > 0:
            score += 0.15
        if trader.username:
            score += 0.1
        if trader.followers is not None:
            score += 0.1
        
        return round(score, 2)
    
    def scrape_enhanced_top_traders(self, max_traders: int = 50) -> List[Dict]:
        """Scrape complet avec métriques détaillées"""
        if not self.setup_driver():
            return []
        
        try:
            print(f"🚀 Début scraping enrichi de {max_traders} traders...")
            
            # 1. Récupérer la liste des adresses
            addresses = self._get_trader_addresses_list()
            
            if not addresses:
                print("❌ Aucune adresse trouvée")
                return []
            
            print(f"📋 {len(addresses)} adresses trouvées, analyse de {min(max_traders, len(addresses))}")
            
            # 2. Extraire les métriques détaillées pour chaque trader
            enhanced_traders = []
            
            for i, address in enumerate(addresses[:max_traders]):
                if i > 0 and i % 5 == 0:  # Pause tous les 5 traders
                    print(f"⏸️ Pause (traité {i}/{min(max_traders, len(addresses))} traders)")
                    time.sleep(5)
                
                trader_metrics = self.extract_trader_metrics_from_profile(address)
                
                if trader_metrics:
                    enhanced_traders.append(trader_metrics.__dict__)
                else:
                    # Fallback avec adresse seule
                    enhanced_traders.append({
                        'address': address,
                        'scraped_at': datetime.now().isoformat(),
                        'confidence_score': 0.0
                    })
            
            print(f"✅ Scraping terminé: {len(enhanced_traders)} traders traités")
            return enhanced_traders
            
        except Exception as e:
            print(f"❌ Erreur scraping global: {e}")
            return []
        finally:
            if self.driver:
                self.driver.quit()
    
    def _get_trader_addresses_list(self) -> List[str]:
        """Récupère la liste des adresses depuis la page top traders"""
        url = f"{self.base_url}/top-traders"
        
        try:
            self.driver.get(url)
            WebDriverWait(self.driver, 30).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "#traders-table tbody tr"))
            )
            
            time.sleep(3)
            soup = BeautifulSoup(self.driver.page_source, 'html.parser')
            
            addresses = []
            trader_rows = soup.select("#traders-table tbody tr")
            
            for row in trader_rows:
                link_element = row.find('a', href=lambda href: href and href.startswith('/trader/'))
                if link_element:
                    address = link_element['href'].split('/')[-1]
                    addresses.append(address)
            
            return addresses
            
        except Exception as e:
            print(f"❌ Erreur récupération adresses: {e}")
            return []
    
    def save_enhanced_data(self, traders_data: List[Dict], include_analytics: bool = True) -> str:
        """Sauvegarde avec analytics en plus"""
        os.makedirs(self.save_path, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        enhanced_data = {
            'metadata': {
                'scraped_at': datetime.now().isoformat(),
                'total_traders': len(traders_data),
                'source': 'hyperdash.info',
                'scraper_version': 'enhanced_v2.0'
            },
            'traders': traders_data
        }
        
        # Ajouter des analytics
        if include_analytics:
            enhanced_data['analytics'] = self._generate_analytics(traders_data)
        
        filepath = os.path.join(self.save_path, f"enhanced_traders_{timestamp}.json")
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(enhanced_data, f, indent=2, ensure_ascii=False)
        
        print(f"💾 Données enrichies sauvegardées: {filepath}")
        return filepath
    
    def _generate_analytics(self, traders_data: List[Dict]) -> Dict:
        """Génère des analytics sur les données collectées"""
        if not traders_data:
            return {}
        
        # Filtrer les traders avec des données complètes
        complete_traders = [t for t in traders_data if t.get('confidence_score', 0) > 0.5]
        
        analytics = {
            'data_quality': {
                'complete_profiles': len(complete_traders),
                'partial_profiles': len(traders_data) - len(complete_traders),
                'completion_rate': len(complete_traders) / len(traders_data) if traders_data else 0
            }
        }
        
        if complete_traders:
            # Métriques des traders complets
            win_rates = [t.get('win_rate') for t in complete_traders if t.get('win_rate')]
            volumes = [t.get('total_volume') for t in complete_traders if t.get('total_volume')]
            pnls = [t.get('pnl_7d') for t in complete_traders if t.get('pnl_7d')]
            
            if win_rates:
                analytics['win_rate_stats'] = {
                    'average': sum(win_rates) / len(win_rates),
                    'top_10_percent': len([wr for wr in win_rates if wr > 0.8]),
                    'above_70_percent': len([wr for wr in win_rates if wr > 0.7])
                }
            
            if volumes:
                analytics['volume_stats'] = {
                    'total_volume': sum(volumes),
                    'average_volume': sum(volumes) / len(volumes),
                    'high_volume_traders': len([v for v in volumes if v > 100000])
                }
        
        return analytics

# Fonction d'amélioration pour votre API existante
def enhanced_scrape_top_traders():
    """Fonction d'amélioration pour remplacer votre scraper actuel"""
    scraper = EnhancedHyperdashScraper()
    
    # Scraper avec métriques complètes
    traders_data = scraper.scrape_enhanced_top_traders(max_traders=20)
    
    if traders_data:
        filepath = scraper.save_enhanced_data(traders_data)
        return filepath
    else:
        print("❌ Aucune donnée récupérée")
        return None

if __name__ == "__main__":
    # Test du scraper amélioré
    enhanced_scrape_top_traders() 