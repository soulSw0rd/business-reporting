# -*- coding: utf-8 -*-
"""
OBJECTIF : Scraper des données depuis Etherscan.io, comme la liste des principaux comptes.
"""

from typing import List, Dict, Optional
import requests
from bs4 import BeautifulSoup

# URL pour la première page des comptes les plus importants sur Etherscan
ETHERSCAN_TOP_ACCOUNTS_URL = "https://etherscan.io/accounts"

# Configuration des headers pour simuler un navigateur
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
    'Accept-Language': 'en-US,en;q=0.5',
}

def scrape_top_eth_accounts(limit: int = 25) -> Optional[List[Dict]]:
    """
    OBJECTIF : Récupérer la liste des principaux comptes Ethereum depuis Etherscan.
    
    PARAMÈTRES :
    - limit (int) : Le nombre de comptes à récupérer (max 100 par page).
    
    RETOURNE :
    - Optional[List[Dict]] : Une liste de dictionnaires, chaque dictionnaire représentant un compte,
                              ou None en cas d'échec.
    """
    print("🔎 Scraping des principaux comptes sur Etherscan...")
    try:
        # Etherscan utilise Cloudflare, une simple requête peut être bloquée.
        # On utilise cloudscraper, une librairie spécialisée pour contourner cette protection.
        import cloudscraper
        scraper = cloudscraper.create_scraper()
        
        response = scraper.get(ETHERSCAN_TOP_ACCOUNTS_URL, headers=HEADERS, timeout=20)
        response.raise_for_status()

        soup = BeautifulSoup(response.content, 'html.parser')
        
        accounts = []
        table_rows = soup.select('table.table-hover tbody tr')
        
        for row in table_rows[:limit]:
            cols = row.select('td')
            if len(cols) >= 4:
                rank = cols[0].text.strip()
                address = cols[1].text.strip()
                name_tag = cols[2].text.strip()
                balance = cols[3].text.strip()
                
                accounts.append({
                    "rank": int(rank),
                    "address": address,
                    "name_tag": name_tag,
                    "balance_ether": balance,
                    "source": "Etherscan"
                })

        print(f"✅ {len(accounts)} comptes Ethereum scrapés avec succès.")
        return accounts

    except ImportError:
        print("❌ La librairie 'cloudscraper' est nécessaire. Veuillez l'installer avec 'pip install cloudscraper'.")
        return None
    except requests.RequestException as e:
        print(f"❌ Erreur de requête lors du scraping d'Etherscan : {e}")
        return None
    except Exception as e:
        print(f"❌ Erreur inattendue lors du scraping d'Etherscan : {e}")
        return None

if __name__ == '__main__':
    top_accounts = scrape_top_eth_accounts()
    if top_accounts:
        import json
        print("\n--- RÉSULTAT DU SCRAPING ---")
        print(json.dumps(top_accounts, indent=2)) 