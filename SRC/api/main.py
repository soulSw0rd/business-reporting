# -*- coding: utf-8 -*-
"""
main.py
Point d'entrée principal de l'API Crypto Prediction.
"""

# -----------------------------------------------------------------------------
# Imports
# -----------------------------------------------------------------------------

import os
import glob
import json
from fastapi import FastAPI, HTTPException, BackgroundTasks
from typing import Dict, Any


# --- Imports des modules principaux du projet ---
# Utilisation de chemins relatifs pour la robustesse
from ..core.enhanced_scraper import EnhancedHyperdashScraper
from ..core.prediction_engine import CryptoPredictionEngine


# -----------------------------------------------------------------------------
# Initialisation de l'Application
# -----------------------------------------------------------------------------

app = FastAPI(
    title="Crypto Prediction API",
    description="API pour scraper les données de traders et générer des prédictions de marché.",
    version="2.0.0",
)

# -----------------------------------------------------------------------------
# Fonctions Utilitaires
# -----------------------------------------------------------------------------

def get_latest_data_file(pattern: str) -> str:
    """Trouve le fichier le plus récent correspondant à un pattern."""
    data_dir = os.path.join('DATA', 'processed')
    list_of_files = glob.glob(os.path.join(data_dir, pattern))
    if not list_of_files:
        return None
    return max(list_of_files, key=os.path.getctime)

def run_scraping_task() -> Dict[str, Any]:
    """Tâche de scraping complète."""
    scraper = EnhancedHyperdashScraper()
    traders_data = scraper.scrape_enhanced_top_traders(max_traders=50)
    if not traders_data:
        raise HTTPException(status_code=500, detail="Le scraping n'a retourné aucune donnée.")
    
    filepath = scraper.save_enhanced_data(traders_data)
    return {"message": "Scraping enrichi réussi.", "file_path": filepath, "traders_found": len(traders_data)}

def run_analysis_task(file_path: str) -> Dict[str, Any]:
    """Tâche d'analyse complète sur un fichier de données."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        traders = data.get('traders')
        if not traders:
            raise ValueError("Le fichier ne contient pas de données de traders.")
            
        engine = CryptoPredictionEngine()
        analysis_result = engine.analyze_traders_data(traders)
        
        # Sauvegarde de l'analyse
        analysis_dir = os.path.join('DATA', 'processed')
        timestamp = os.path.basename(file_path).replace('enhanced_traders_', '').replace('.json', '')
        analysis_filepath = os.path.join(analysis_dir, f"analysis_{timestamp}.json")
        
        # Utilise le 'default=str' pour gérer les types non sérialisables comme Enum et datetime
        with open(analysis_filepath, 'w', encoding='utf-8') as f:
            json.dump(analysis_result, f, indent=2, ensure_ascii=False, default=str)
            
        analysis_result['analysis_saved_to'] = analysis_filepath
        return analysis_result

    except FileNotFoundError:
        raise HTTPException(status_code=404, detail=f"Fichier de données non trouvé : {file_path}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur durant l'analyse : {str(e)}")


# -----------------------------------------------------------------------------
# Routes de l'API
# -----------------------------------------------------------------------------

@app.get("/", tags=["General"])
def get_api_status() -> Dict[str, str]:
    """Vérifie l'état de santé de l'API."""
    return {"status": "Crypto Prediction API is running", "version": app.version}

@app.post("/scrape/enhanced", tags=["Core"])
def scrape_enhanced_traders_data(background_tasks: BackgroundTasks) -> Dict[str, str]:
    """
    Lance le scraping enrichi des top traders en tâche de fond.
    Retourne une confirmation immédiate.
    """
    background_tasks.add_task(run_scraping_task)
    return {"message": "Le scraping enrichi a été lancé en tâche de fond."}


@app.post("/analyze/latest", tags=["Core"])
def analyze_latest_scraped_data() -> Dict[str, Any]:
    """
    Analyse le dernier fichier de données scrapé disponible.
    """
    latest_file = get_latest_data_file("enhanced_traders_*.json")
    if not latest_file:
        raise HTTPException(status_code=404, detail="Aucun fichier de données 'enhanced_traders' trouvé.")
    
    return run_analysis_task(latest_file)


@app.post("/scrape_and_analyze", tags=["Core"])
def scrape_and_analyze() -> Dict[str, Any]:
    """
    Exécute le cycle complet : scraping puis analyse.
    Cette opération est synchrone et peut prendre du temps.
    """
    scraping_result = run_scraping_task()
    file_path = scraping_result.get("file_path")
    
    if not file_path:
        raise HTTPException(status_code=500, detail="Échec de l'étape de scraping, l'analyse ne peut continuer.")

    return run_analysis_task(file_path)

@app.get("/data/latest", tags=["Data"])
def get_latest_data() -> Dict[str, Any]:
    """Récupère le contenu du dernier fichier de données scrapées."""
    latest_file = get_latest_data_file("enhanced_traders_*.json")
    if not latest_file:
        raise HTTPException(status_code=404, detail="Aucun fichier de données trouvé.")
    with open(latest_file, 'r', encoding='utf-8') as f:
        return json.load(f)

@app.get("/analysis/latest", tags=["Data"])
def get_latest_analysis() -> Dict[str, Any]:
    """Récupère le contenu du dernier fichier d'analyse."""
    latest_file = get_latest_data_file("analysis_*.json")
    if not latest_file:
        raise HTTPException(status_code=404, detail="Aucun fichier d'analyse trouvé.")
    with open(latest_file, 'r', encoding='utf-8') as f:
        return json.load(f)

# -----------------------------------------------------------------------------
# Lancement de l'application (pour le développement local)
# -----------------------------------------------------------------------------

if __name__ == "__main__":
    import uvicorn
    
    print("🚀 Démarrage du serveur FastAPI...")
    print("🔗 Accès à la documentation de l'API: http://127.0.0.1:8000/docs")
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)