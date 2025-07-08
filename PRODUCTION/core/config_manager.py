#!/usr/bin/env python3
"""
Configuration Manager
Gestionnaire centralisé de la configuration du système crypto-tracker
Auteur: Crypto-Tracker Team
Date: 2025-01-08
Version: 1.0.0
"""

import json
import os
from pathlib import Path
from typing import Dict, Any, Optional
import logging

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ConfigManager:
    """
    ConfigManager - Gestionnaire de configuration centralisé
    
    RESPONSABILITÉ : Chargement et gestion des paramètres de configuration
    UTILISATION : Instance singleton pour cohérence globale
    
    FONCTIONNALITÉS :
    - Chargement configuration depuis fichiers JSON
    - Validation des paramètres obligatoires
    - Gestion des valeurs par défaut
    - Cache en mémoire pour performances
    """
    
    _instance = None
    _config_cache = {}
    
    def __new__(cls, config_path: str = "RESOURCES/configs/app_config.json"):
        """
        OBJECTIF : Implémentation du pattern Singleton
        
        PARAMÈTRES :
        - config_path (str) : Chemin vers le fichier de configuration principal
        
        RETOURNE :
        - ConfigManager : Instance unique du gestionnaire
        
        LOGIQUE :
        1. Vérification de l'existence d'une instance
        2. Création si nécessaire
        3. Retour de l'instance unique
        """
        if cls._instance is None:
            cls._instance = super(ConfigManager, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self, config_path: str = "RESOURCES/configs/app_config.json"):
        """
        OBJECTIF : Initialisation du gestionnaire de configuration
        
        PARAMÈTRES :
        - config_path (str) : Chemin vers le fichier de configuration principal
        
        LOGIQUE :
        1. Vérification si déjà initialisé (singleton)
        2. Chargement de la configuration depuis le fichier JSON
        3. Validation des paramètres obligatoires
        4. Application des valeurs par défaut si nécessaire
        """
        if self._initialized:
            return
            
        self.config_path = Path(config_path)
        self.config = self._load_configuration()
        self._initialized = True
        
        logger.info(f"ConfigManager initialisé avec {config_path}")
    
    def _load_configuration(self) -> Dict[str, Any]:
        """
        OBJECTIF : Chargement de la configuration depuis le fichier JSON
        
        RETOURNE :
        - dict : Configuration chargée avec valeurs par défaut
        
        LOGIQUE :
        1. Vérification de l'existence du fichier
        2. Chargement du JSON si disponible
        3. Application des valeurs par défaut
        4. Validation des paramètres obligatoires
        """
        default_config = self._get_default_config()
        
        if not self.config_path.exists():
            logger.warning(f"Fichier de configuration non trouvé: {self.config_path}")
            logger.info("Utilisation de la configuration par défaut")
            return default_config
        
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                file_config = json.load(f)
            
            # Fusion avec les valeurs par défaut
            merged_config = {**default_config, **file_config}
            
            self._validate_configuration(merged_config)
            logger.info("Configuration chargée avec succès")
            
            return merged_config
            
        except json.JSONDecodeError as e:
            logger.error(f"Erreur de parsing JSON: {e}")
            logger.info("Utilisation de la configuration par défaut")
            return default_config
        except Exception as e:
            logger.error(f"Erreur lors du chargement: {e}")
            logger.info("Utilisation de la configuration par défaut")
            return default_config
    
    def _get_default_config(self) -> Dict[str, Any]:
        """
        OBJECTIF : Définition de la configuration par défaut
        
        RETOURNE :
        - dict : Configuration par défaut complète
        
        LOGIQUE :
        1. Définition des paramètres essentiels
        2. Configuration des modules (scraping, ML, API)
        3. Paramètres de sécurité et performance
        """
        return {
            "app": {
                "name": "Crypto-Tracker",
                "version": "1.0.0",
                "debug": False,
                "environment": "production"
            },
            "dashboard": {
                "title": "₿ CryptoTrader Dashboard - Business Intelligence",
                "port": 8501,
                "host": "localhost",
                "cache_ttl": 600,  # 10 minutes
                "max_traders_display": 20
            },
            "api": {
                "host": "0.0.0.0",
                "port": 8000,
                "workers": 4,
                "timeout": 30,
                "rate_limit": "100/minute"
            },
            "ml": {
                "model_path": "PRODUCTION/models/",
                "training_samples": 1000,
                "random_state": 42,
                "test_size": 0.2,
                "cv_folds": 5,
                "confidence_threshold": 0.75
            },
            "scraping": {
                "delay_between_requests": 2,
                "max_retry_attempts": 3,
                "timeout": 30,
                "user_agent": "Crypto-Tracker/1.0.0",
                "respect_robots_txt": True
            },
            "data": {
                "processed_path": "RESOURCES/data/processed/",
                "raw_path": "RESOURCES/data/raw/",
                "training_path": "RESOURCES/data/training/",
                "exports_path": "RESOURCES/data/exports/",
                "max_file_age_days": 7
            },
            "logging": {
                "level": "INFO",
                "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                "file_path": "ADMIN/logs/crypto_tracker.log",
                "max_file_size_mb": 10,
                "backup_count": 5
            }
        }
    
    def _validate_configuration(self, config: Dict[str, Any]) -> None:
        """
        OBJECTIF : Validation de la configuration chargée
        
        PARAMÈTRES :
        - config (dict) : Configuration à valider
        
        LOGIQUE :
        1. Vérification des sections obligatoires
        2. Validation des types de données
        3. Contrôle des valeurs limites
        4. Lancement d'exceptions si erreurs critiques
        """
        required_sections = ["app", "dashboard", "api", "ml", "scraping", "data"]
        
        for section in required_sections:
            if section not in config:
                raise ValueError(f"Section obligatoire manquante: {section}")
        
        # Validation des ports
        if not (1000 <= config["dashboard"]["port"] <= 65535):
            raise ValueError("Port dashboard invalide (doit être entre 1000 et 65535)")
        
        if not (1000 <= config["api"]["port"] <= 65535):
            raise ValueError("Port API invalide (doit être entre 1000 et 65535)")
        
        # Validation des chemins
        for path_key in ["processed_path", "raw_path", "training_path", "exports_path"]:
            path = config["data"][path_key]
            if not isinstance(path, str) or not path:
                raise ValueError(f"Chemin invalide pour {path_key}")
        
        logger.info("Configuration validée avec succès")
    
    def get_config(self, section: Optional[str] = None, key: Optional[str] = None) -> Any:
        """
        OBJECTIF : Récupération de paramètres de configuration
        
        PARAMÈTRES :
        - section (str, optional) : Section de configuration
        - key (str, optional) : Clé spécifique dans la section
        
        RETOURNE :
        - Any : Valeur de configuration demandée
        
        LOGIQUE :
        1. Si aucun paramètre : retour de toute la configuration
        2. Si section uniquement : retour de la section
        3. Si section + clé : retour de la valeur spécifique
        4. Gestion des erreurs avec valeurs par défaut
        """
        if section is None:
            return self.config
        
        if section not in self.config:
            logger.warning(f"Section de configuration non trouvée: {section}")
            return {}
        
        if key is None:
            return self.config[section]
        
        if key not in self.config[section]:
            logger.warning(f"Clé de configuration non trouvée: {section}.{key}")
            return None
        
        return self.config[section][key]
    
    def update_config(self, section: str, key: str, value: Any) -> None:
        """
        OBJECTIF : Mise à jour dynamique de la configuration
        
        PARAMÈTRES :
        - section (str) : Section à modifier
        - key (str) : Clé à modifier
        - value (Any) : Nouvelle valeur
        
        LOGIQUE :
        1. Vérification de l'existence de la section
        2. Mise à jour de la valeur
        3. Sauvegarde optionnelle sur disque
        4. Log de la modification
        """
        if section not in self.config:
            self.config[section] = {}
        
        old_value = self.config[section].get(key, "N/A")
        self.config[section][key] = value
        
        logger.info(f"Configuration mise à jour: {section}.{key} = {value} (ancienne: {old_value})")
    
    def save_config(self) -> bool:
        """
        OBJECTIF : Sauvegarde de la configuration sur disque
        
        RETOURNE :
        - bool : True si succès, False sinon
        
        LOGIQUE :
        1. Création du dossier parent si nécessaire
        2. Écriture du JSON formaté
        3. Gestion des erreurs
        4. Log du résultat
        """
        try:
            # Créer le dossier parent si nécessaire
            self.config_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Configuration sauvegardée: {self.config_path}")
            return True
            
        except Exception as e:
            logger.error(f"Erreur lors de la sauvegarde: {e}")
            return False
    
    def get_data_paths(self) -> Dict[str, Path]:
        """
        OBJECTIF : Récupération des chemins de données formatés
        
        RETOURNE :
        - dict : Chemins de données sous forme de Path objects
        
        LOGIQUE :
        1. Récupération des chemins depuis la configuration
        2. Conversion en objets Path
        3. Création des dossiers si nécessaires
        """
        data_config = self.get_config("data")
        paths = {}
        
        for key, path_str in data_config.items():
            if key.endswith("_path"):
                path_obj = Path(path_str)
                path_obj.mkdir(parents=True, exist_ok=True)
                paths[key.replace("_path", "")] = path_obj
        
        return paths
    
    def is_debug_mode(self) -> bool:
        """
        OBJECTIF : Vérification du mode debug
        
        RETOURNE :
        - bool : True si mode debug activé
        """
        return self.get_config("app", "debug") or False
    
    def get_cache_ttl(self) -> int:
        """
        OBJECTIF : Récupération du TTL du cache
        
        RETOURNE :
        - int : TTL en secondes
        """
        return self.get_config("dashboard", "cache_ttl") or 600


# Instance globale pour utilisation simplifiée
config_manager = ConfigManager()


def get_config(section: Optional[str] = None, key: Optional[str] = None) -> Any:
    """
    OBJECTIF : Fonction utilitaire pour accès rapide à la configuration
    
    PARAMÈTRES :
    - section (str, optional) : Section de configuration
    - key (str, optional) : Clé spécifique
    
    RETOURNE :
    - Any : Valeur de configuration
    
    UTILISATION :
    ```python
    from PRODUCTION.core.config_manager import get_config
    
    # Récupérer toute la config
    config = get_config()
    
    # Récupérer une section
    dashboard_config = get_config("dashboard")
    
    # Récupérer une valeur spécifique
    port = get_config("dashboard", "port")
    ```
    """
    return config_manager.get_config(section, key) 