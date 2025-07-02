import requests
from bs4 import BeautifulSoup
import re
import json
from typing import Dict, Any
import time

class BlockchainScraper:
    def __init__(self):
        self.session = requests.Session()
        # Headers pour simuler un navigateur réel
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'fr-FR,fr;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        })

    def scrape_block_info(self, block_number: int) -> Dict[str, Any]:
        """
        Scrape les informations d'un bloc Bitcoin depuis blockchain.com
        """
        url = f"https://www.blockchain.com/fr/explorer/blocks/btc/{block_number}"
        
        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extraction des données principales
            block_data = self._extract_block_data(soup)
            
            return {
                'success': True,
                'block_number': block_number,
                'url': url,
                'data': block_data
            }
            
        except requests.RequestException as e:
            return {
                'success': False,
                'error': f"Erreur de requête: {str(e)}",
                'block_number': block_number
            }
        except Exception as e:
            return {
                'success': False,
                'error': f"Erreur de parsing: {str(e)}",
                'block_number': block_number
            }

    def _extract_block_data(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """
        Extrait les données du bloc depuis le HTML parsé
        """
        data = {}
        
        # Extraction du titre principal
        title = soup.find('h1') or soup.find('title')
        if title:
            data['title'] = title.get_text(strip=True)
        
        # Recherche de toutes les données dans le texte
        text_content = soup.get_text()
        
        # Extraction par regex des informations principales
        patterns = {
            'hash': r'Hachage\s*([a-f0-9\-]+)',
            'timestamp': r'Miné le\s*([^•]+)',
            'transactions': r'(\d+)\s*transactions?',
            'size': r'Taille\s*([\d\s,]+)',
            'height': r'Hauteur\s*(\d+)',
            'confirmations': r'Confirmations\s*(\d+)',
            'difficulty': r'Difficulté\s*([\d\s,\.]+)',
            'nonce': r'Nonce\s*([\d\s,]+)',
            'total_btc': r'total de\s*([\d,\.]+)\s*BTC',
            'total_value': r'\$([0-9,\s]+)',
            'reward': r'récompense totale de\s*([\d,\.]+)\s*BTC',
            'fees': r'Frais\s*([\d,\.]+)\s*BTC',
            'miner': r'Mineur\s*([^\n]+)'
        }
        
        for key, pattern in patterns.items():
            match = re.search(pattern, text_content, re.IGNORECASE)
            if match:
                data[key] = match.group(1).strip()
        
        # Extraction plus spécifique avec BeautifulSoup
        self._extract_specific_elements(soup, data)
        
        return data

    def _extract_specific_elements(self, soup: BeautifulSoup, data: Dict[str, Any]):
        """
        Extraction plus précise avec des sélecteurs CSS
        """
        # Recherche de divs ou spans contenant des données spécifiques
        for element in soup.find_all(['div', 'span', 'td', 'th']):
            text = element.get_text(strip=True)
            
            # Détection de patterns spécifiques
            if 'BTC' in text and '$' in text:
                # Extraction de valeurs en BTC et USD
                btc_match = re.search(r'([\d,\.]+)\s*BTC', text)
                usd_match = re.search(r'\$([\d,\s]+)', text)
                
                if btc_match and usd_match:
                    data['btc_amount'] = btc_match.group(1)
                    data['usd_amount'] = usd_match.group(1)

    def scrape_multiple_blocks(self, start_block: int, count: int = 5, delay: float = 1.0) -> list:
        """
        Scrape plusieurs blocs consécutifs avec délai pour éviter le rate limiting
        """
        results = []
        
        for i in range(count):
            block_num = start_block + i
            print(f"Scraping bloc {block_num}...")
            
            result = self.scrape_block_info(block_num)
            results.append(result)
            
            if i < count - 1:  # Pas de délai après le dernier bloc
                time.sleep(delay)
        
        return results

    def save_to_json(self, data: Dict[str, Any], filename: str):
        """
        Sauvegarde les données dans un fichier JSON
        """
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)


# Exemple d'utilisation
def main():
    scraper = BlockchainScraper()
    
    # Scraping d'un bloc spécifique
    block_info = scraper.scrape_block_info(903523)
    
    if block_info['success']:
        print("✅ Scraping réussi!")
        print(json.dumps(block_info, indent=2, ensure_ascii=False))
        
        # Sauvegarde
        scraper.save_to_json(block_info, f"block_{903523}.json")
    else:
        print("❌ Erreur lors du scraping:")
        print(block_info['error'])

    # Scraping de plusieurs blocs
    print("\n" + "="*50)
    print("Scraping de plusieurs blocs...")
    
    multiple_blocks = scraper.scrape_multiple_blocks(903520, count=3, delay=2.0)
    
    for result in multiple_blocks:
        if result['success']:
            print(f"✅ Bloc {result['block_number']}: {len(result['data'])} données extraites")
        else:
            print(f"❌ Bloc {result['block_number']}: {result['error']}")


# Version simplifiée pour un usage rapide
def quick_scrape(block_number: int) -> Dict[str, str]:
    """
    Version simplifiée pour scraper rapidement un bloc
    """
    url = f"https://www.blockchain.com/fr/explorer/blocks/btc/{block_number}"
    
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        
        # Extraction simple du texte
        soup = BeautifulSoup(response.content, 'html.parser')
        text = soup.get_text()
        
        # Regex basiques pour les infos principales
        info = {}
        
        patterns = {
            'transactions': r'(\d+)\s*transactions',
            'btc_total': r'total de\s*([\d,\.]+)\s*BTC',
            'timestamp': r'Miné le\s*([^•]+)',
            'height': r'Hauteur\s*(\d+)',
            'confirmations': r'Confirmations\s*(\d+)'
        }
        
        for key, pattern in patterns.items():
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                info[key] = match.group(1).strip()
        
        return info
        
    except Exception as e:
        return {'error': str(e)}


if __name__ == "__main__":
    main()
    
    # Test de la version rapide
    print("\n" + "="*50)
    print("Test version rapide:")
    quick_info = quick_scrape(903523)
    print(json.dumps(quick_info, indent=2, ensure_ascii=False)) 