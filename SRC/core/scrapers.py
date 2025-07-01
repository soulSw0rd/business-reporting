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
from datetime import datetime
from typing import List, Dict, Any
import time

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

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