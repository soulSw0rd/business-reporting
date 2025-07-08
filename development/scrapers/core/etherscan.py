# -*- coding: utf-8 -*-
"""
OBJECTIF : Scraper la liste des "Top Accounts" sur Etherscan.
"""
import cloudscraper
from bs4 import BeautifulSoup
from typing import List, Dict, Any, Optional

URL = "https://etherscan.io/accounts"

def scrape_top_eth_accounts() -> Optional[List[Dict[str, Any]]]:
    """
    Scrape les 25 premiers comptes Ethereum les plus riches depuis Etherscan.

    LOGIQUE :
    1. Utilise 'cloudscraper' pour passer la protection Cloudflare d'Etherscan.
    2. Parse le HTML de la page avec BeautifulSoup.
    3. Navigue dans le tableau pour extraire l'adresse, le nom (si disponible),
       le solde et le pourcentage de chaque compte.

    RETOURNE :
        Une liste de dictionnaires, chaque dictionnaire représentant un compte.
        Retourne None si le scraping échoue.
    """
    scraper = cloudscraper.create_scraper()
    print("Récupération des Top Comptes Ethereum sur Etherscan...")
    try:
        response = scraper.get(URL, timeout=20)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')
        accounts_data = []

        # Cibler les lignes du tableau dans le corps de la table
        rows = soup.select("tbody tr")
        
        if not rows:
            print("❌ Erreur Etherscan : Le tableau des comptes n'a pas été trouvé.")
            return None

        for row in rows[:25]:  # Limiter aux 25 premiers
            cols = row.find_all('td')
            if len(cols) >= 4:
                address_link = cols[1].find('a')
                if not address_link:
                    continue
                
                address = address_link.text
                name_tag = cols[2].text.strip()
                balance = cols[3].text.strip()
                percentage = cols[4].text.strip()

                accounts_data.append({
                    "address": address,
                    "name_tag": name_tag,
                    "balance": balance,
                    "percentage": percentage
                })
        
        print(f"✅ {len(accounts_data)} comptes Ethereum récupérés.")
        return accounts_data

    except requests.exceptions.RequestException as e:
        print(f"❌ Erreur Etherscan : Échec de la requête vers Etherscan : {e}")
        return None
    except Exception as e:
        print(f"❌ Erreur Etherscan : Une erreur s'est produite lors du parsing : {e}")
        return None 