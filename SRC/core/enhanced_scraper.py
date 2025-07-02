# -*- coding: utf-8 -*-
"""
Enhanced Hyperdash Scraper avec extraction de métriques prédictives
Amélioration du scraper existant pour capturer toutes les données nécessaires
"""

import json
import os
import re
import time
from datetime import datetime
from typing import List, Dict, Optional
from dataclasses import dataclass

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

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
        options.add_argument("--headless")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-gpu")
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
        
        try:
            self.driver = webdriver.Chrome(options=options)
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
            # Attendre un élément qui semble être un conteneur principal des stats
            WebDriverWait(self.driver, 20).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "div, main, section"))
            )
            time.sleep(4)  # Attente supplémentaire pour le JS
            
            soup = BeautifulSoup(self.driver.page_source, 'html.parser')
            trader = TraderMetrics(address=address, scraped_at=datetime.now().isoformat())
            
            # --- Stratégie d'extraction améliorée ---
            text_content = soup.get_text(separator=" ", strip=True).lower()

            # Username
            username_element = soup.select_one('h1, h2, [class*="username"], [class*="trader-name"]')
            if username_element:
                trader.username = username_element.get_text(strip=True)

            # PnL (7d / 30d)
            pnl_7d_match = re.search(r'pnl \(7d\)\s*\$?([\d,.-]+)', text_content)
            if pnl_7d_match:
                trader.pnl_7d = self._parse_financial_value(pnl_7d_match.group(1))

            pnl_30d_match = re.search(r'pnl \(30d\)\s*\$?([\d,.-]+)', text_content)
            if pnl_30d_match:
                trader.pnl_30d = self._parse_financial_value(pnl_30d_match.group(1))

            # Win Rate
            win_rate_match = re.search(r'win rate\s*([\d.]+)%', text_content)
            if win_rate_match:
                trader.win_rate = float(win_rate_match.group(1)) / 100

            # Total Trades
            trades_match = re.search(r'total trades\s*([\d,]+)', text_content)
            if trades_match:
                trader.total_trades = int(trades_match.group(1).replace(',', ''))

            # Total Volume
            volume_match = re.search(r'volume\s*\$?([\d,.]+[kmb]?)', text_content)
            if volume_match:
                trader.total_volume = self._parse_financial_value(volume_match.group(1))
            
            # ROI (7d / 30d)
            roi_7d_match = re.search(r'roi \(7d\)\s*([\d.]+)%', text_content)
            if roi_7d_match:
                trader.roi_7d = float(roi_7d_match.group(1)) / 100

            roi_30d_match = re.search(r'roi \(30d\)\s*([\d.]+)%', text_content)
            if roi_30d_match:
                trader.roi_30d = float(roi_30d_match.group(1)) / 100

            # Followers
            followers_match = re.search(r'(\d+)\s*followers', text_content)
            if followers_match:
                trader.followers = int(followers_match.group(1))

            trader.confidence_score = self._calculate_confidence_score(trader)
            print(f"✅ Métriques pour {trader.username or address[:10]}: "
                  f"Win Rate: {trader.win_rate}, Volume: {trader.total_volume}, PnL 7d: {trader.pnl_7d}")
            return trader
            
        except Exception as e:
            print(f"❌ Erreur extraction {address}: {e}")
            return None
    
    def _parse_financial_value(self, value_str: str) -> float:
        """Parse une valeur financière avec suffixes k/m/b et gestion des négatifs."""
        if not value_str:
            return 0.0
        
        value_str = value_str.lower().replace(',', '').replace('$', '').strip()
        
        multiplier = 1
        if value_str.endswith('k'):
            multiplier = 1000
            value_str = value_str[:-1]
        elif value_str.endswith('m'):
            multiplier = 1_000_000
            value_str = value_str[:-1]
        elif value_str.endswith('b'):
            multiplier = 1_000_000_000
            value_str = value_str[:-1]
            
        try:
            return float(value_str) * multiplier
        except ValueError:
            return 0.0
    
    def _calculate_confidence_score(self, trader: TraderMetrics) -> float:
        """Calcule un score de confiance basé sur la complétude des données."""
        score = 0.0
        if trader.pnl_7d is not None: score += 0.2
        if trader.win_rate is not None: score += 0.25
        if trader.total_volume is not None: score += 0.15
        if trader.total_trades is not None: score += 0.15
        if trader.roi_7d is not None: score += 0.1
        if trader.followers is not None: score += 0.05
        if trader.username: score += 0.1
        return round(score, 2)
    
    def scrape_enhanced_top_traders(self, max_traders: int = 50) -> List[Dict]:
        if not self.setup_driver():
            return []
        try:
            print(f"🚀 Début scraping enrichi de {max_traders} traders...")
            addresses = self._get_trader_addresses_list()
            if not addresses:
                print("❌ Aucune adresse trouvée")
                return []
            print(f"📋 {len(addresses)} adresses trouvées, analyse de {min(max_traders, len(addresses))}")
            enhanced_traders = []
            for i, address in enumerate(addresses[:max_traders]):
                if i > 0 and i % 5 == 0:
                    print(f"⏸️ Pause (traité {i}/{min(max_traders, len(addresses))} traders)")
                    time.sleep(5)
                trader_metrics = self.extract_trader_metrics_from_profile(address)
                if trader_metrics:
                    enhanced_traders.append(trader_metrics.__dict__)
                else:
                    enhanced_traders.append({'address': address, 'scraped_at': datetime.now().isoformat(), 'confidence_score': 0.0})
            print(f"✅ Scraping terminé: {len(enhanced_traders)} traders traités")
            return enhanced_traders
        except Exception as e:
            print(f"❌ Erreur scraping global: {e}")
            return []
        finally:
            if self.driver:
                self.driver.quit()
    
    def _get_trader_addresses_list(self) -> List[str]:
        url = f"{self.base_url}/top-traders"
        try:
            self.driver.get(url)
            WebDriverWait(self.driver, 30).until(EC.presence_of_element_located((By.CSS_SELECTOR, "#traders-table tbody tr")))
            time.sleep(3)
            soup = BeautifulSoup(self.driver.page_source, 'html.parser')
            addresses = []
            trader_rows = soup.select("#traders-table tbody tr")
            for row in trader_rows:
                link_element = row.find('a', href=lambda href: href and href.startswith('/trader/'))
                if link_element:
                    addresses.append(link_element['href'].split('/')[-1])
            return addresses
        except Exception as e:
            print(f"❌ Erreur récupération adresses: {e}")
            return []
    
    def save_enhanced_data(self, traders_data: List[Dict], include_analytics: bool = True) -> str:
        os.makedirs(self.save_path, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        enhanced_data = {
            'metadata': {'scraped_at': datetime.now().isoformat(), 'total_traders': len(traders_data), 'source': 'hyperdash.info', 'scraper_version': 'enhanced_v2.0'},
            'traders': traders_data
        }
        if include_analytics:
            enhanced_data['analytics'] = self._generate_analytics(traders_data)
        filepath = os.path.join(self.save_path, f"enhanced_traders_{timestamp}.json")
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(enhanced_data, f, indent=2, ensure_ascii=False)
        print(f"💾 Données enrichies sauvegardées: {filepath}")
        return filepath
    
    def _generate_analytics(self, traders_data: List[Dict]) -> Dict:
        if not traders_data:
            return {}
        complete_traders = [t for t in traders_data if t.get('confidence_score', 0) > 0.5]
        analytics = {'data_quality': {'complete_profiles': len(complete_traders), 'partial_profiles': len(traders_data) - len(complete_traders), 'completion_rate': len(complete_traders) / len(traders_data) if traders_data else 0}}
        if complete_traders:
            win_rates = [t.get('win_rate') for t in complete_traders if t.get('win_rate')]
            volumes = [t.get('total_volume') for t in complete_traders if t.get('total_volume')]
            if win_rates:
                analytics['win_rate_stats'] = {'average': sum(win_rates) / len(win_rates), 'top_10_percent': len([wr for wr in win_rates if wr > 0.8]), 'above_70_percent': len([wr for wr in win_rates if wr > 0.7])}
            if volumes:
                analytics['volume_stats'] = {'total_volume': sum(volumes), 'average_volume': sum(volumes) / len(volumes), 'high_volume_traders': len([v for v in volumes if v > 100000])}
        return analytics

def enhanced_scrape_top_traders():
    """Fonction d'amélioration pour remplacer votre scraper actuel"""
    scraper = EnhancedHyperdashScraper()
    traders_data = scraper.scrape_enhanced_top_traders(max_traders=20)
    if traders_data:
        filepath = scraper.save_enhanced_data(traders_data)
        return filepath
    else:
        print("❌ Aucune donnée récupérée")
        return None

if __name__ == "__main__":
    enhanced_scrape_top_traders() 