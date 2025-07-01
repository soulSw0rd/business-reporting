# -*- coding: utf-8 -*-

"""
main.py

Point d'entrée principal pour l'API de prédiction de trading CryptoTracker.
Initialise l'application FastAPI, configure les routes et les services.
"""

# -----------------------------------------------------------------------------
# Imports
# -----------------------------------------------------------------------------

from fastapi import FastAPI, HTTPException
from typing import Dict

# Ajout de l'import pour notre nouveau service de scraping
from ..core.scrapers import scrape_top_traders

# -----------------------------------------------------------------------------
# Initialisation de l'Application
# -----------------------------------------------------------------------------

app = FastAPI(
    title="CryptoTracker API",
    description="API pour fournir des prédictions de trading basées sur l'analyse de wallets.",
    version="1.0.0",
)

# -----------------------------------------------------------------------------
# Routes de l'API
# -----------------------------------------------------------------------------

@app.get("/", tags=["Monitoring"])
def get_api_status() -> Dict[str, str]:
    """
    OBJECTIF : Vérifier l'état de santé de l'API.
    
    PARAMÈTRES :
    - Aucun
    
    RETOURNE :
    - dict : Un dictionnaire indiquant le statut de l'API.
        {"status": "CryptoTracker API is running"}
    
    LOGIQUE :
    1. Retourne une réponse JSON simple pour confirmer que le service est en ligne.
    """
    # ÉTAPE 1: Définir la réponse de statut
    response = {"status": "CryptoTracker API is running"}
    
    # ÉTAPE 2: Retourner la réponse
    return response

@app.get("/scrape/{wallet_address}", tags=["Scraping"])
def scrape_wallet_data(wallet_address: str) -> Dict[str, str]:
    """
    OBJECTIF : Lancer le scraping des données pour une adresse de wallet spécifique.
    
    PARAMÈTRES :
    - wallet_address (str) : L'adresse du wallet à analyser (ex: 0x123...abc).
    
    RETOURNE :
    - dict : Un dictionnaire confirmant le lancement du scraping.
    
    LOGIQUE :
    1. Récupère l'adresse du wallet depuis l'URL.
    2. (Implémentation future) Lance le service de scraping pour cette adresse.
    3. Retourne une confirmation immédiate.
    """
    # ÉTAPE 1: Valider l'adresse (logique de base)
    if not wallet_address.startswith("0x"):
        return {"error": "Invalid wallet address format."}

    # ÉTAPE 2: Simuler le lancement du scraping
    # La logique de scraping réelle sera dans un service dédié.
    print(f"Lancement du scraping pour le wallet : {wallet_address}")
    
    # ÉTAPE 3: Retourner la confirmation
    return {"status": "scraping_initiated", "wallet": wallet_address}

@app.post("/scrape/top-traders", tags=["Scraping"])
def trigger_scrape_top_traders() -> Dict[str, str]:
    """
    OBJECTIF : Déclenche le scraping de la page des meilleurs traders
               et sauvegarde les données.
    
    PARAMÈTRES :
    - Aucun
    
    RETOURNE :
    - dict : Un dictionnaire confirmant le succès et l'emplacement des données.
    
    LOGIQUE :
    1. Appelle la fonction de scraping dédiée `scrape_top_traders`.
    2. Gère les cas où le scraping échoue.
    3. Retourne une réponse JSON avec le statut et le chemin du fichier.
    """
    # ÉTAPE 1: Lancer le scraping
    print("Requête reçue pour scraper les meilleurs traders.")
    filepath = scrape_top_traders()
    
    # ÉTAPE 2: Gérer le résultat
    if filepath is None:
        raise HTTPException(
            status_code=500,
            detail="Le scraping a échoué. Consulter les logs du serveur pour plus de détails."
        )
        
    # ÉTAPE 3: Confirmer le succès
    return {
        "status": "success",
        "message": "Les données des meilleurs traders ont été scrappées.",
        "data_file": filepath
    }

# -----------------------------------------------------------------------------
# Lancement de l'application (pour le développement local)
# -----------------------------------------------------------------------------

if __name__ == "__main__":
    import uvicorn
    
    print("Démarrage du serveur FastAPI pour le développement...")
    uvicorn.run(app, host="0.0.0.0", port=8000) 