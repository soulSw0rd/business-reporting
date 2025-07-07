# -*- coding: utf-8 -*-
"""
OBJECTIF : Point d'entrée principal de l'API FastAPI pour le projet de prédiction crypto.
"""
import os
import glob
import json
from fastapi import FastAPI, HTTPException
from typing import Dict, Any, Optional

from src.scrapers.market.aggregator import get_market_sentiment_metrics

app = FastAPI(
    title="Crypto Prediction API",
    description="API pour collecter les données de marché via des scrapers et des API tierces.",
    version="2.2.0",
)

# --- Fonctions Utilitaires ---

def get_latest_file(pattern: str) -> Optional[str]:
    """
    OBJECTIF : Trouver le fichier le plus récent dans l'archive correspondant à un pattern.
    
    PARAMÈTRES :
    - pattern (str) : Le pattern de fichier à rechercher (ex: "enhanced_traders_*.json").
    
    RETOURNE :
    - Optional[str] : Le chemin du fichier le plus récent, ou None si aucun n'est trouvé.
    """
    data_dir = os.path.join('archive', 'processed_data')
    list_of_files = glob.glob(os.path.join(data_dir, pattern))
    if not list_of_files:
        return None
    return max(list_of_files, key=os.path.getctime)

# --- Routes de l'API ---

@app.get("/", tags=["General"])
def get_api_status() -> Dict[str, str]:
    """OBJECTIF : Vérifier l'état de santé de l'API."""
    return {"status": "Crypto Prediction API is running", "version": app.version}

@app.get("/market-data", tags=["Market Data"])
async def get_market_data() -> Dict[str, Any]:
    """
    OBJECTIF : Récupérer un agrégat de métriques de marché (Fear & Greed, Top Wallets, Taux...).
    """
    metrics = await get_market_sentiment_metrics()
    if not metrics:
        raise HTTPException(status_code=503, detail="Impossible de collecter les métriques de marché.")
    return metrics

@app.get("/data/latest-analysis", tags=["Data Access (Legacy)"])
def get_latest_analysis_data() -> Dict[str, Any]:
    """OBJECTIF : Récupérer le contenu du dernier fichier d'analyse de traders (legacy)."""
    latest_file = get_latest_file("analysis_*.json")
    if not latest_file:
        raise HTTPException(status_code=404, detail="Aucun fichier d'analyse trouvé.")
    with open(latest_file, 'r', encoding='utf-8') as f:
        return json.load(f)

if __name__ == "__main__":
    import uvicorn
    print("Running in debug mode...")
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="debug")