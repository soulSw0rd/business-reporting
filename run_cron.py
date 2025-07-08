#!/usr/bin/env python3
"""
Script de collecte de données pour le pipeline de Machine Learning.

Ce script est destiné à être exécuté périodiquement (par exemple, une fois par jour via une tâche cron ou un planificateur de tâches) pour :
1. Scraper les dernières données des traders.
2. Récupérer le contexte du marché.
3. Stocker un "snapshot" de ces données dans la base de données SQLite.
4. Mettre à jour les "targets" (variables cibles) pour les anciennes données.
5. Potentiellement relancer l'entraînement du modèle si de nouvelles données suffisantes sont disponibles.
"""

# Permet d'importer les modules du projet depuis la racine
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent))

from src.ml.predictor import MLDataCollector

def run_collection():
    """
    Lance une session de collecte de données.
    """
    print("="*50)
    print(f"🚀 Lancement du script de collecte de données ML...")
    print("="*50)
    
    collector = MLDataCollector()
    collector.daily_data_collection()
    
    print("\nScript de collecte terminé.")
    print("="*50)

if __name__ == "__main__":
    run_collection() 