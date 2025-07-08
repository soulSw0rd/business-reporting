#!/usr/bin/env python3
"""
Script de génération de dataset avancé
Génère un large dataset pour les prédictions ML et visualisations
Auteur: Crypto-Tracker Team
Date: 2025-01-08
Version: 1.0.0
"""

import sys
import os
from pathlib import Path
import json
import logging
from datetime import datetime

# Ajout du chemin pour les imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from PRODUCTION.core.advanced_dataset_generator import AdvancedDatasetGenerator

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def main():
    """
    Fonction principale de génération du dataset
    """
    logger.info("🚀 Début de la génération du dataset avancé")
    
    try:
        # Initialisation du générateur
        generator = AdvancedDatasetGenerator()
        
        # Génération du dataset complet
        logger.info("📊 Génération du dataset complet...")
        dataset = generator.generate_complete_dataset(
            num_samples=15000,
            include_predictions=True,
            include_market_cycles=True
        )
        
        # Sauvegarde du dataset
        output_path = Path("RESOURCES/data/processed")
        output_path.mkdir(parents=True, exist_ok=True)
        
        # Dataset principal
        main_dataset_path = output_path / "advanced_dataset_complete.json"
        with open(main_dataset_path, 'w', encoding='utf-8') as f:
            json.dump(dataset, f, indent=2, ensure_ascii=False, default=str)
        
        logger.info(f"✅ Dataset principal sauvegardé: {main_dataset_path}")
        
        # Génération de datasets spécialisés
        logger.info("📈 Génération des datasets spécialisés...")
        
        # Dataset pour prédictions ML
        prediction_dataset = generator.generate_prediction_dataset(5000)
        prediction_path = output_path / "ml_prediction_dataset.json"
        with open(prediction_path, 'w', encoding='utf-8') as f:
            json.dump(prediction_dataset, f, indent=2, ensure_ascii=False, default=str)
        
        # Dataset pour visualisations
        viz_dataset = generator.generate_visualization_dataset(1000)
        viz_path = output_path / "visualization_dataset.json"
        with open(viz_path, 'w', encoding='utf-8') as f:
            json.dump(viz_dataset, f, indent=2, ensure_ascii=False, default=str)
        
        # Dataset de marché étendu
        market_dataset = generator.generate_market_dataset(500)
        market_path = output_path / "market_dataset_extended.json"
        with open(market_path, 'w', encoding='utf-8') as f:
            json.dump(market_dataset, f, indent=2, ensure_ascii=False, default=str)
        
        # Génération des métriques de performance
        logger.info("🎯 Génération des métriques de performance...")
        performance_metrics = generator.generate_performance_metrics(dataset)
        metrics_path = output_path / "performance_metrics.json"
        with open(metrics_path, 'w', encoding='utf-8') as f:
            json.dump(performance_metrics, f, indent=2, ensure_ascii=False, default=str)
        
        # Rapport de génération
        report = {
            "generation_timestamp": datetime.now().isoformat(),
            "datasets_generated": {
                "complete_dataset": {
                    "path": str(main_dataset_path),
                    "samples": len(dataset),
                    "features": len(dataset[0].keys()) if dataset else 0
                },
                "prediction_dataset": {
                    "path": str(prediction_path),
                    "samples": len(prediction_dataset),
                    "features": len(prediction_dataset[0].keys()) if prediction_dataset else 0
                },
                "visualization_dataset": {
                    "path": str(viz_path),
                    "samples": len(viz_dataset),
                    "features": len(viz_dataset[0].keys()) if viz_dataset else 0
                },
                "market_dataset": {
                    "path": str(market_path),
                    "samples": len(market_dataset),
                    "features": len(market_dataset[0].keys()) if market_dataset else 0
                },
                "performance_metrics": {
                    "path": str(metrics_path),
                    "metrics_count": len(performance_metrics)
                }
            },
            "total_samples": len(dataset) + len(prediction_dataset) + len(viz_dataset) + len(market_dataset),
            "generation_success": True
        }
        
        # Sauvegarde du rapport
        report_path = output_path / "generation_report.json"
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False, default=str)
        
        logger.info("📊 Résumé de la génération:")
        logger.info(f"   • Dataset complet: {len(dataset)} échantillons")
        logger.info(f"   • Dataset prédiction: {len(prediction_dataset)} échantillons")
        logger.info(f"   • Dataset visualisation: {len(viz_dataset)} échantillons")
        logger.info(f"   • Dataset marché: {len(market_dataset)} échantillons")
        logger.info(f"   • Total: {report['total_samples']} échantillons")
        logger.info(f"   • Rapport: {report_path}")
        
        logger.info("🎉 Génération terminée avec succès!")
        
    except Exception as e:
        logger.error(f"❌ Erreur lors de la génération: {str(e)}")
        raise


if __name__ == "__main__":
    main() 