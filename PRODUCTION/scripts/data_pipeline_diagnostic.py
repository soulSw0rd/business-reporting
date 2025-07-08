#!/usr/bin/env python3
"""
Data Pipeline Diagnostic & Repair
Diagnostic et correction du pipeline de données
Auteur: Crypto-Tracker Team
Date: 2025-01-08
Version: 1.0.0
"""

import sys
import os
import json
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List, Optional

# Ajout du chemin pour les imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from PRODUCTION.core.config_manager import get_config

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class DataPipelineDiagnostic:
    """
    Diagnostic et réparation du pipeline de données
    """
    
    def __init__(self):
        """Initialisation du diagnostic"""
        self.config = get_config()
        self.data_config = get_config("data")
        self.processed_path = Path(self.data_config["processed_path"])
        self.issues_found = []
        self.repairs_made = []
        
        logger.info("DataPipelineDiagnostic initialisé")
    
    def run_full_diagnostic(self) -> Dict[str, Any]:
        """
        Exécute un diagnostic complet du pipeline de données
        
        RETOURNE:
        - Dict avec le rapport de diagnostic
        """
        logger.info("🔍 Début du diagnostic complet du pipeline de données")
        
        report = {
            "timestamp": datetime.now().isoformat(),
            "status": "running",
            "checks": {},
            "issues": [],
            "repairs": [],
            "recommendations": []
        }
        
        # 1. Vérification de l'existence des dossiers
        report["checks"]["directories"] = self._check_directories()
        
        # 2. Vérification des fichiers de données
        report["checks"]["data_files"] = self._check_data_files()
        
        # 3. Validation de la structure des données
        report["checks"]["data_structure"] = self._validate_data_structure()
        
        # 4. Vérification de l'intégrité des données
        report["checks"]["data_integrity"] = self._check_data_integrity()
        
        # 5. Test de chargement des données
        report["checks"]["data_loading"] = self._test_data_loading()
        
        # 6. Génération des recommandations
        report["recommendations"] = self._generate_recommendations()
        
        # 7. Application des corrections automatiques
        if self.issues_found:
            logger.info("🔧 Application des corrections automatiques")
            self._apply_automatic_repairs()
            report["repairs"] = self.repairs_made
        
        report["status"] = "completed"
        report["issues"] = self.issues_found
        
        logger.info(f"✅ Diagnostic terminé - {len(self.issues_found)} problèmes détectés")
        
        return report
    
    def _check_directories(self) -> Dict[str, Any]:
        """Vérification de l'existence des dossiers requis"""
        logger.info("📁 Vérification des dossiers")
        
        required_dirs = [
            "RESOURCES/data/processed",
            "RESOURCES/data/raw",
            "RESOURCES/data/training",
            "RESOURCES/data/exports",
            "RESOURCES/configs"
        ]
        
        result = {
            "status": "success",
            "existing_dirs": [],
            "missing_dirs": [],
            "created_dirs": []
        }
        
        for dir_path in required_dirs:
            path = Path(dir_path)
            if path.exists():
                result["existing_dirs"].append(str(path))
            else:
                result["missing_dirs"].append(str(path))
                # Créer le dossier manquant
                path.mkdir(parents=True, exist_ok=True)
                result["created_dirs"].append(str(path))
                self.repairs_made.append(f"Dossier créé: {path}")
        
        if result["missing_dirs"]:
            result["status"] = "repaired"
        
        return result
    
    def _check_data_files(self) -> Dict[str, Any]:
        """Vérification de l'existence des fichiers de données"""
        logger.info("📄 Vérification des fichiers de données")
        
        expected_files = [
            "top_traders_extended.json",
            "top_traders_for_prediction.json",
            "market_data_extended.json",
            "sentiment_data.json",
            "historical_data.json"
        ]
        
        result = {
            "status": "success",
            "existing_files": [],
            "missing_files": [],
            "file_sizes": {}
        }
        
        for filename in expected_files:
            file_path = self.processed_path / filename
            if file_path.exists():
                result["existing_files"].append(filename)
                result["file_sizes"][filename] = file_path.stat().st_size
            else:
                result["missing_files"].append(filename)
                self.issues_found.append(f"Fichier manquant: {filename}")
        
        if result["missing_files"]:
            result["status"] = "issues_found"
        
        return result
    
    def _validate_data_structure(self) -> Dict[str, Any]:
        """Validation de la structure des données JSON"""
        logger.info("🔍 Validation de la structure des données")
        
        result = {
            "status": "success",
            "valid_files": [],
            "invalid_files": [],
            "structure_issues": []
        }
        
        # Schémas attendus
        schemas = {
            "top_traders_extended.json": {
                "type": "array",
                "required_fields": ["trader_id", "username", "total_pnl", "win_rate"]
            },
            "top_traders_for_prediction.json": {
                "type": "array",
                "required_fields": ["address", "pnl_7d", "pnl_30d"]
            },
            "market_data_extended.json": {
                "type": "object",
                "required_fields": ["cryptocurrencies"]
            },
            "sentiment_data.json": {
                "type": "object",
                "required_fields": ["overall_sentiment"]
            }
        }
        
        for filename, schema in schemas.items():
            file_path = self.processed_path / filename
            if file_path.exists():
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    
                    # Validation du type
                    if schema["type"] == "array" and not isinstance(data, list):
                        result["structure_issues"].append(f"{filename}: Attendu array, trouvé {type(data).__name__}")
                        continue
                    elif schema["type"] == "object" and not isinstance(data, dict):
                        result["structure_issues"].append(f"{filename}: Attendu object, trouvé {type(data).__name__}")
                        continue
                    
                    # Validation des champs requis
                    if schema["type"] == "array" and data:
                        sample = data[0]
                        for field in schema["required_fields"]:
                            if field not in sample:
                                result["structure_issues"].append(f"{filename}: Champ manquant '{field}'")
                    elif schema["type"] == "object":
                        for field in schema["required_fields"]:
                            if field not in data:
                                result["structure_issues"].append(f"{filename}: Champ manquant '{field}'")
                    
                    if filename not in [issue.split(":")[0] for issue in result["structure_issues"]]:
                        result["valid_files"].append(filename)
                        
                except json.JSONDecodeError as e:
                    result["invalid_files"].append(filename)
                    result["structure_issues"].append(f"{filename}: Erreur JSON - {str(e)}")
                except Exception as e:
                    result["invalid_files"].append(filename)
                    result["structure_issues"].append(f"{filename}: Erreur - {str(e)}")
        
        if result["structure_issues"]:
            result["status"] = "issues_found"
            self.issues_found.extend(result["structure_issues"])
        
        return result
    
    def _check_data_integrity(self) -> Dict[str, Any]:
        """Vérification de l'intégrité des données"""
        logger.info("🔒 Vérification de l'intégrité des données")
        
        result = {
            "status": "success",
            "integrity_issues": [],
            "data_quality": {}
        }
        
        # Vérification des traders
        traders_file = self.processed_path / "top_traders_extended.json"
        if traders_file.exists():
            try:
                with open(traders_file, 'r', encoding='utf-8') as f:
                    traders = json.load(f)
                
                if traders:
                    # Vérification des valeurs nulles/manquantes
                    null_count = sum(1 for trader in traders if not trader.get('username'))
                    if null_count > 0:
                        result["integrity_issues"].append(f"Traders avec username manquant: {null_count}")
                    
                    # Vérification des valeurs aberrantes
                    pnl_values = [trader.get('total_pnl', 0) for trader in traders if trader.get('total_pnl') is not None]
                    if pnl_values:
                        avg_pnl = sum(pnl_values) / len(pnl_values)
                        extreme_count = sum(1 for pnl in pnl_values if abs(pnl) > abs(avg_pnl) * 100)
                        if extreme_count > 0:
                            result["integrity_issues"].append(f"Valeurs PnL extrêmes détectées: {extreme_count}")
                    
                    result["data_quality"]["traders_count"] = len(traders)
                    result["data_quality"]["avg_pnl"] = avg_pnl if pnl_values else 0
                    
            except Exception as e:
                result["integrity_issues"].append(f"Erreur lecture traders: {str(e)}")
        
        # Vérification des données de marché
        market_file = self.processed_path / "market_data_extended.json"
        if market_file.exists():
            try:
                with open(market_file, 'r', encoding='utf-8') as f:
                    market_data = json.load(f)
                
                if 'cryptocurrencies' in market_data:
                    cryptos = market_data['cryptocurrencies']
                    result["data_quality"]["crypto_count"] = len(cryptos)
                    
                    # Vérification des prix
                    prices = [crypto.get('price', 0) for crypto in cryptos if crypto.get('price')]
                    if prices:
                        zero_prices = sum(1 for price in prices if price <= 0)
                        if zero_prices > 0:
                            result["integrity_issues"].append(f"Cryptos avec prix <= 0: {zero_prices}")
                    
            except Exception as e:
                result["integrity_issues"].append(f"Erreur lecture marché: {str(e)}")
        
        if result["integrity_issues"]:
            result["status"] = "issues_found"
            self.issues_found.extend(result["integrity_issues"])
        
        return result
    
    def _test_data_loading(self) -> Dict[str, Any]:
        """Test de chargement des données comme dans l'application"""
        logger.info("🧪 Test de chargement des données")
        
        result = {
            "status": "success",
            "loading_errors": [],
            "loaded_data": {}
        }
        
        try:
            # Simulation du chargement comme dans le dashboard
            scraped_data = {
                'traders_for_analysis': [],
                'traders_for_prediction': [],
                'market_data_extended': {},
                'sentiment_data': {},
                'historical_data': []
            }
            
            # Test chargement traders pour analyse
            traders_file = self.processed_path / "top_traders_extended.json"
            if traders_file.exists():
                with open(traders_file, 'r', encoding='utf-8') as f:
                    scraped_data['traders_for_analysis'] = json.load(f)
                result["loaded_data"]["traders_analysis"] = len(scraped_data['traders_for_analysis'])
            
            # Test chargement traders pour prédiction
            prediction_file = self.processed_path / "top_traders_for_prediction.json"
            if prediction_file.exists():
                with open(prediction_file, 'r', encoding='utf-8') as f:
                    scraped_data['traders_for_prediction'] = json.load(f)
                result["loaded_data"]["traders_prediction"] = len(scraped_data['traders_for_prediction'])
            
            # Test chargement données de marché
            market_file = self.processed_path / "market_data_extended.json"
            if market_file.exists():
                with open(market_file, 'r', encoding='utf-8') as f:
                    scraped_data['market_data_extended'] = json.load(f)
                result["loaded_data"]["market_data"] = "loaded"
            
            # Test chargement sentiment
            sentiment_file = self.processed_path / "sentiment_data.json"
            if sentiment_file.exists():
                with open(sentiment_file, 'r', encoding='utf-8') as f:
                    scraped_data['sentiment_data'] = json.load(f)
                result["loaded_data"]["sentiment_data"] = "loaded"
            
            # Test chargement historique
            historical_file = self.processed_path / "historical_data.json"
            if historical_file.exists():
                with open(historical_file, 'r', encoding='utf-8') as f:
                    scraped_data['historical_data'] = json.load(f)
                result["loaded_data"]["historical_data"] = len(scraped_data['historical_data'])
            
        except Exception as e:
            result["loading_errors"].append(f"Erreur de chargement: {str(e)}")
            result["status"] = "error"
            self.issues_found.append(f"Erreur de chargement: {str(e)}")
        
        return result
    
    def _generate_recommendations(self) -> List[str]:
        """Génération des recommandations d'amélioration"""
        recommendations = []
        
        if not (self.processed_path / "top_traders_extended.json").exists():
            recommendations.append("Générer des données traders d'exemple")
        
        if not (self.processed_path / "market_data_extended.json").exists():
            recommendations.append("Générer des données de marché d'exemple")
        
        if not (self.processed_path / "sentiment_data.json").exists():
            recommendations.append("Générer des données de sentiment d'exemple")
        
        if len(self.issues_found) > 5:
            recommendations.append("Considérer une régénération complète des données")
        
        recommendations.append("Mettre en place un système de validation automatique")
        recommendations.append("Implémenter un système de sauvegarde des données")
        
        return recommendations
    
    def _apply_automatic_repairs(self):
        """Application des corrections automatiques"""
        logger.info("🔧 Application des corrections automatiques")
        
        # Génération de données manquantes
        self._generate_missing_data()
        
        # Correction des formats de données
        self._fix_data_formats()
        
        # Nettoyage des données corrompues
        self._clean_corrupted_data()
    
    def _generate_missing_data(self):
        """Génération des données manquantes"""
        
        # Génération de données traders si manquantes
        if not (self.processed_path / "top_traders_extended.json").exists():
            self._generate_sample_traders()
        
        # Génération de données de marché si manquantes
        if not (self.processed_path / "market_data_extended.json").exists():
            self._generate_sample_market_data()
        
        # Génération de données de sentiment si manquantes
        if not (self.processed_path / "sentiment_data.json").exists():
            self._generate_sample_sentiment_data()
    
    def _generate_sample_traders(self):
        """Génération de données traders d'exemple"""
        import random
        
        traders = []
        for i in range(20):
            trader = {
                "trader_id": f"TopTrader_{i+1:03d}",
                "rank": i + 1,
                "username": f"trader_{i+1}",
                "total_pnl": random.uniform(-10000, 50000),
                "win_rate": random.uniform(0.4, 0.9),
                "total_trades": random.randint(50, 2000),
                "roi_percentage": random.uniform(-50, 200),
                "favorite_pairs": ["BTC/USDT", "ETH/USDT"],
                "country": "Unknown"
            }
            traders.append(trader)
        
        with open(self.processed_path / "top_traders_extended.json", 'w', encoding='utf-8') as f:
            json.dump(traders, f, indent=2, ensure_ascii=False)
        
        self.repairs_made.append("Données traders générées")
    
    def _generate_sample_market_data(self):
        """Génération de données de marché d'exemple"""
        market_data = {
            "cryptocurrencies": [
                {
                    "symbol": "BTC",
                    "price": 45000,
                    "change_24h": 2.5,
                    "volume_24h": 25000000000,
                    "market_cap": 850000000000
                },
                {
                    "symbol": "ETH",
                    "price": 2800,
                    "change_24h": 3.2,
                    "volume_24h": 15000000000,
                    "market_cap": 340000000000
                }
            ]
        }
        
        with open(self.processed_path / "market_data_extended.json", 'w', encoding='utf-8') as f:
            json.dump(market_data, f, indent=2, ensure_ascii=False)
        
        self.repairs_made.append("Données de marché générées")
    
    def _generate_sample_sentiment_data(self):
        """Génération de données de sentiment d'exemple"""
        import random
        
        sentiment_data = {
            "overall_sentiment": random.uniform(-1, 1),
            "social_sentiment": random.uniform(-1, 1),
            "news_sentiment": random.uniform(-1, 1),
            "signals": []
        }
        
        with open(self.processed_path / "sentiment_data.json", 'w', encoding='utf-8') as f:
            json.dump(sentiment_data, f, indent=2, ensure_ascii=False)
        
        self.repairs_made.append("Données de sentiment générées")
    
    def _fix_data_formats(self):
        """Correction des formats de données"""
        # Correction des formats numériques si nécessaire
        pass
    
    def _clean_corrupted_data(self):
        """Nettoyage des données corrompues"""
        # Suppression des entrées corrompues
        pass
    
    def save_report(self, report: Dict[str, Any], filename: str = None):
        """Sauvegarde du rapport de diagnostic"""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"diagnostic_report_{timestamp}.json"
        
        report_path = Path("ADMIN/logs") / filename
        report_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False, default=str)
        
        logger.info(f"📊 Rapport sauvegardé: {report_path}")
        return report_path


def main():
    """Fonction principale"""
    diagnostic = DataPipelineDiagnostic()
    
    # Exécution du diagnostic complet
    report = diagnostic.run_full_diagnostic()
    
    # Sauvegarde du rapport
    report_path = diagnostic.save_report(report)
    
    # Affichage du résumé
    print("\n" + "="*60)
    print("🔍 RAPPORT DE DIAGNOSTIC DU PIPELINE DE DONNÉES")
    print("="*60)
    print(f"📅 Timestamp: {report['timestamp']}")
    print(f"📊 Statut: {report['status']}")
    print(f"❌ Problèmes détectés: {len(report['issues'])}")
    print(f"🔧 Corrections appliquées: {len(report['repairs'])}")
    print(f"💡 Recommandations: {len(report['recommendations'])}")
    
    if report['issues']:
        print("\n❌ PROBLÈMES DÉTECTÉS:")
        for issue in report['issues']:
            print(f"   • {issue}")
    
    if report['repairs']:
        print("\n🔧 CORRECTIONS APPLIQUÉES:")
        for repair in report['repairs']:
            print(f"   • {repair}")
    
    if report['recommendations']:
        print("\n💡 RECOMMANDATIONS:")
        for rec in report['recommendations']:
            print(f"   • {rec}")
    
    print(f"\n📄 Rapport détaillé: {report_path}")
    print("="*60)


if __name__ == "__main__":
    main() 