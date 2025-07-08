#!/usr/bin/env python3
"""
Script pour générer des fichiers de données de marché à la demande.

Ce script exécute chaque scraper de données de marché (CoinGecko, Fear & Greed, Funding Rates)
et sauvegarde leur sortie brute dans des fichiers JSON séparés dans le dossier DATA/processed.
C'est utile pour l'inspection, le débogage ou l'archivage manuel.
"""
import json
import os
from datetime import datetime

# Permet d'importer les modules du projet depuis la racine
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent))

# Imports des scrapers du projet
from src.core.coingecko import scrape_coingecko_metrics
from src.core.fear_and_greed import scrape_fear_and_greed_index
from src.core.funding_rates import FundingRatesScraper

# -----------------------------------------------------------------------------
# Constantes
# -----------------------------------------------------------------------------

SAVE_PATH = "DATA/processed"
TIMESTAMP = datetime.now().strftime("%Y%m%d_%H%M%S")

# -----------------------------------------------------------------------------
# Fonctions
# -----------------------------------------------------------------------------

def save_to_json(data, filename_prefix):
    """Sauvegarde les données fournies dans un fichier JSON."""
    if data is None:
        print(f"⏩ Données pour '{filename_prefix}' sont vides (None), fichier non créé.")
        return

    try:
        os.makedirs(SAVE_PATH, exist_ok=True)
        file_path = os.path.join(SAVE_PATH, f"{filename_prefix}_{TIMESTAMP}.json")
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4)
            
        print(f"✅ Données sauvegardées avec succès dans : {file_path}")
    except Exception as e:
        print(f"❌ Erreur lors de la sauvegarde du fichier pour '{filename_prefix}': {e}")


def generate_files():
    """
    Fonction principale qui orchestre le scraping et la sauvegarde.
    """
    print("="*50)
    print("🚀 Lancement de la génération des fichiers de données de marché...")
    print("="*50)

    # 1. Scraper et sauvegarder les données de CoinGecko
    print("\n📊 Récupération des données de CoinGecko...")
    coingecko_data = scrape_coingecko_metrics()
    save_to_json(coingecko_data, "market_data_coingecko_btc")

    # 2. Scraper et sauvegarder les données de Fear & Greed
    print("\n😟 Récupération de l'indice Fear & Greed...")
    fear_greed_data = scrape_fear_and_greed_index()
    save_to_json(fear_greed_data, "market_data_fear_greed")
    
    # 3. Scraper et sauvegarder les taux de financement
    print("\n💰 Récupération des taux de financement (Funding Rates)...")
    funding_scraper = FundingRatesScraper()
    funding_data = funding_scraper.scrape()
    save_to_json(funding_data, "market_data_funding_rates")

    print("\n\n🎉 Génération des fichiers terminée.")
    print("="*50)


if __name__ == "__main__":
    generate_files() 