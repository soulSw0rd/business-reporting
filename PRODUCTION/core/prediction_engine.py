#!/usr/bin/env python3

"""
Prediction Engine
Moteur de prédiction ML pour l'analyse de profitabilité des traders crypto
Auteur: Crypto-Tracker Team
Date: 2025-01-08
Version: 1.0.0
"""

import numpy as np
import pandas as pd
import pickle
import logging
from pathlib import Path
from typing import Dict, Any, Tuple, Optional, List
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix

from .config_manager import get_config

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class CryptoTraderPredictor:
    """
    CryptoTraderPredictor - Moteur de prédiction de profitabilité des traders
    
    RESPONSABILITÉ : Prédiction de la profitabilité future des traders crypto
    UTILISATION : Analyse des performances traders avec contexte marché
    
    FONCTIONNALITÉS :
    - Prédictions court terme (7 jours) et long terme (30 jours)
    - Feature engineering automatique
    - Modèles Random Forest optimisés
    - Évaluation de confiance des prédictions
    - Gestion automatique des modèles pré-entraînés
    """
    
    def __init__(self, model_path: Optional[str] = None):
        """
        OBJECTIF : Initialisation du moteur de prédiction
        
        PARAMÈTRES :
        - model_path (str, optional) : Chemin vers les modèles pré-entraînés
        
        LOGIQUE :
        1. Chargement de la configuration
        2. Initialisation des modèles et scalers
        3. Tentative de chargement des modèles existants
        4. Configuration des paramètres ML
        """
        self.config = get_config("ml")
        self.model_path = Path(model_path or self.config["model_path"])
        
        # Modèles pour différents horizons temporels
        self.model_7d = None
        self.model_30d = None
        self.scaler = StandardScaler()
        
        # État d'entraînement
        self.is_trained = False
        self.model_metadata = {}
        
        # Paramètres ML
        self.n_estimators = 100
        self.random_state = self.config.get("random_state", 42)
        self.test_size = self.config.get("test_size", 0.2)
        self.confidence_threshold = self.config.get("confidence_threshold", 0.75)
        
        # Tentative de chargement des modèles existants
        self._load_existing_models()
        
        logger.info("CryptoTraderPredictor initialisé")
    
    def _load_existing_models(self) -> bool:
        """
        OBJECTIF : Chargement des modèles pré-entraînés depuis le disque
        
        RETOURNE :
        - bool : True si modèles chargés avec succès
        
        LOGIQUE :
        1. Vérification de l'existence des fichiers modèles
        2. Chargement des modèles RandomForest
        3. Chargement du scaler
        4. Chargement des métadonnées
        """
        try:
            model_7d_path = self.model_path / "crypto_predictor_7d.pkl"
            model_30d_path = self.model_path / "crypto_predictor_30d.pkl"
            scaler_path = self.model_path / "scaler.pkl"
            metadata_path = self.model_path / "model_metadata.json"
            
            if all(p.exists() for p in [model_7d_path, model_30d_path, scaler_path]):
                # Chargement des modèles
                with open(model_7d_path, 'rb') as f:
                    self.model_7d = pickle.load(f)
                
                with open(model_30d_path, 'rb') as f:
                    self.model_30d = pickle.load(f)
                
                with open(scaler_path, 'rb') as f:
                    self.scaler = pickle.load(f)
                
                # Chargement des métadonnées si disponibles
                if metadata_path.exists():
                    import json
                    with open(metadata_path, 'r') as f:
                        self.model_metadata = json.load(f)
                
                self.is_trained = True
                logger.info("Modèles pré-entraînés chargés avec succès")
                return True
                
        except Exception as e:
            logger.warning(f"Impossible de charger les modèles existants: {e}")
        
        return False
    
    def prepare_features(self, trader_data: Dict[str, Any], market_data: Dict[str, Any]) -> np.ndarray:
        """
        OBJECTIF : Préparation des features pour la prédiction ML
        
        PARAMÈTRES :
        - trader_data (dict) : Données du trader {address, pnl_7d, win_rate, etc.}
        - market_data (dict) : Contexte marché {btc_price, fear_greed, etc.}
        
        RETOURNE :
        - np.ndarray : Features normalisées prêtes pour la prédiction
        
        LOGIQUE :
        1. Extraction des métriques trader (PnL, win rate, exposition)
        2. Extraction des métriques marché (prix BTC, sentiment, funding)
        3. Feature engineering (ratios, tendances)
        4. Normalisation et formatage pour le modèle
        """
        features = []
        
        # === FEATURES TRADER ===
        # Performance financière
        pnl_7d = float(trader_data.get('pnl_7d', 0))
        pnl_30d = float(trader_data.get('pnl_30d', 0))
        features.extend([pnl_7d, pnl_30d])
        
        # Métriques de trading
        win_rate = float(trader_data.get('win_rate', 0.5))
        long_percentage = float(trader_data.get('long_percentage', 50))
        features.extend([win_rate, long_percentage])
        
        # Features dérivées trader
        pnl_ratio = pnl_7d / max(abs(pnl_30d), 1)  # Éviter division par zéro
        risk_score = (100 - long_percentage) / 100  # Score de risque basé sur exposition
        features.extend([pnl_ratio, risk_score])
        
        # === FEATURES MARCHÉ ===
        # Prix et volatilité Bitcoin
        btc_price = float(market_data.get('coingecko_btc', {}).get('price', 50000))
        btc_normalized = btc_price / 100000  # Normalisation approximative
        features.extend([btc_price, btc_normalized])
        
        # Sentiment de marché
        fear_greed = float(market_data.get('fear_and_greed_index', {}).get('value', 50))
        fear_greed_normalized = fear_greed / 100
        features.extend([fear_greed, fear_greed_normalized])
        
        # Taux de financement
        funding_rate = float(market_data.get('funding_rates', {}).get('BTCUSDT', {}).get('last_funding_rate', 0))
        funding_normalized = funding_rate * 10000  # Amplification pour visibilité
        features.extend([funding_rate, funding_normalized])
        
        # === FEATURES CONTEXTUELLES ===
        # Interaction trader-marché
        trader_market_alignment = win_rate * fear_greed_normalized
        market_risk_factor = abs(funding_normalized) * (1 - fear_greed_normalized)
        features.extend([trader_market_alignment, market_risk_factor])
        
        # Conversion en array numpy et reshape pour prédiction
        features_array = np.array(features, dtype=np.float32)
        
        # Gestion des valeurs manquantes ou infinies
        features_array = np.nan_to_num(features_array, nan=0.0, posinf=1.0, neginf=-1.0)
        
        return features_array.reshape(1, -1)
    
    def generate_training_data(self, n_samples: int = 1000) -> pd.DataFrame:
        """
        OBJECTIF : Génération de données d'entraînement simulées réalistes
        
        PARAMÈTRES :
        - n_samples (int) : Nombre d'échantillons à générer
        
        RETOURNE :
        - pd.DataFrame : Dataset d'entraînement avec features et targets
        
        LOGIQUE :
        1. Génération de features traders réalistes
        2. Génération de contexte marché varié
        3. Calcul des labels de profitabilité avec logique métier
        4. Ajout de bruit pour simuler l'incertitude réelle
        """
        np.random.seed(self.random_state)
        data = []
        
        logger.info(f"Génération de {n_samples} échantillons d'entraînement")
        
        for i in range(n_samples):
            # === GÉNÉRATION FEATURES TRADER ===
            # PnL avec distribution réaliste (la plupart perdent de l'argent)
            pnl_7d = np.random.normal(0, 1000) - 200  # Biais négatif
            pnl_30d = np.random.normal(0, 3000) - 500  # Biais négatif plus fort
            
            # Win rate réaliste (entre 30% et 80%)
            win_rate = np.random.beta(2, 3) * 0.5 + 0.3  # Distribution réaliste
            
            # Exposition long/short
            long_percentage = np.random.uniform(20, 80)
            
            # === GÉNÉRATION CONTEXTE MARCHÉ ===
            # Prix Bitcoin avec volatilité
            btc_price = np.random.uniform(30000, 80000)
            
            # Fear & Greed avec tendance centrale
            fear_greed = np.random.beta(2, 2) * 100  # Distribution en cloche
            
            # Funding rate réaliste
            funding_rate = np.random.normal(0, 0.0001)
            
            # === CALCUL FEATURES DÉRIVÉES ===
            pnl_ratio = pnl_7d / max(abs(pnl_30d), 1)
            risk_score = (100 - long_percentage) / 100
            btc_normalized = btc_price / 100000
            fear_greed_normalized = fear_greed / 100
            funding_normalized = funding_rate * 10000
            trader_market_alignment = win_rate * fear_greed_normalized
            market_risk_factor = abs(funding_normalized) * (1 - fear_greed_normalized)
            
            # === LOGIQUE DE PROFITABILITÉ ===
            # Probabilité de base basée sur les performances passées
            base_prob_7d = 0.5 + (pnl_7d / 5000) + (win_rate - 0.5) * 0.4
            base_prob_30d = 0.5 + (pnl_30d / 10000) + (win_rate - 0.5) * 0.3
            
            # Influence du marché
            market_boost = (fear_greed - 50) / 200  # Marché bullish = boost
            funding_penalty = abs(funding_rate) * 1000  # Funding élevé = risque
            
            # Probabilités finales avec bruit
            prob_7d = base_prob_7d + market_boost - funding_penalty + np.random.normal(0, 0.1)
            prob_30d = base_prob_30d + market_boost * 0.5 - funding_penalty + np.random.normal(0, 0.1)
            
            # Limitation des probabilités
            prob_7d = np.clip(prob_7d, 0.05, 0.95)
            prob_30d = np.clip(prob_30d, 0.05, 0.95)
            
            # Conversion en labels binaires
            profitable_7d = 1 if prob_7d > 0.5 else 0
            profitable_30d = 1 if prob_30d > 0.5 else 0
            
            # Stockage de l'échantillon
            data.append({
                # Features brutes
                'pnl_7d': pnl_7d,
                'pnl_30d': pnl_30d,
                'win_rate': win_rate,
                'long_percentage': long_percentage,
                'btc_price': btc_price,
                'fear_greed': fear_greed,
                'funding_rate': funding_rate,
                # Features dérivées
                'pnl_ratio': pnl_ratio,
                'risk_score': risk_score,
                'btc_normalized': btc_normalized,
                'fear_greed_normalized': fear_greed_normalized,
                'funding_normalized': funding_normalized,
                'trader_market_alignment': trader_market_alignment,
                'market_risk_factor': market_risk_factor,
                # Targets
                'profitable_7d': profitable_7d,
                'profitable_30d': profitable_30d,
                # Métadonnées
                'prob_7d': prob_7d,
                'prob_30d': prob_30d
            })
        
        df = pd.DataFrame(data)
        logger.info(f"Dataset généré: {len(df)} échantillons, {len(df.columns)} features")
        
        return df
    
    def train_models(self, training_data: Optional[pd.DataFrame] = None) -> Dict[str, Any]:
        """
        OBJECTIF : Entraînement des modèles Random Forest pour 7 et 30 jours
        
        PARAMÈTRES :
        - training_data (pd.DataFrame, optional) : Données d'entraînement
        
        RETOURNE :
        - dict : Métriques d'évaluation des modèles
        
        LOGIQUE :
        1. Génération des données si non fournies
        2. Préparation des features et targets
        3. Division train/test
        4. Entraînement des modèles RandomForest
        5. Évaluation et sauvegarde des modèles
        """
        if training_data is None:
            training_samples = self.config.get("training_samples", 1000)
            training_data = self.generate_training_data(training_samples)
        
        logger.info("Début de l'entraînement des modèles")
        
        # === PRÉPARATION DES DONNÉES ===
        feature_columns = [
            'pnl_7d', 'pnl_30d', 'win_rate', 'long_percentage', 'btc_price',
            'fear_greed', 'funding_rate', 'pnl_ratio', 'risk_score',
            'btc_normalized', 'fear_greed_normalized', 'funding_normalized',
            'trader_market_alignment', 'market_risk_factor'
        ]
        
        X = training_data[feature_columns].values
        y_7d = training_data['profitable_7d'].values
        y_30d = training_data['profitable_30d'].values
        
        # Normalisation des features
        X_scaled = self.scaler.fit_transform(X)
        
        # Division train/test
        X_train, X_test, y_7d_train, y_7d_test = train_test_split(
            X_scaled, y_7d, test_size=self.test_size, random_state=self.random_state
        )
        _, _, y_30d_train, y_30d_test = train_test_split(
            X_scaled, y_30d, test_size=self.test_size, random_state=self.random_state
        )
        
        # === ENTRAÎNEMENT MODÈLE 7 JOURS ===
        logger.info("Entraînement du modèle 7 jours")
        self.model_7d = RandomForestClassifier(
            n_estimators=self.n_estimators,
            random_state=self.random_state,
            max_depth=10,
            min_samples_split=5,
            min_samples_leaf=2,
            class_weight='balanced'
        )
        self.model_7d.fit(X_train, y_7d_train)
        
        # === ENTRAÎNEMENT MODÈLE 30 JOURS ===
        logger.info("Entraînement du modèle 30 jours")
        self.model_30d = RandomForestClassifier(
            n_estimators=self.n_estimators,
            random_state=self.random_state,
            max_depth=12,
            min_samples_split=5,
            min_samples_leaf=2,
            class_weight='balanced'
        )
        self.model_30d.fit(X_train, y_30d_train)
        
        # === ÉVALUATION ===
        y_7d_pred = self.model_7d.predict(X_test)
        y_30d_pred = self.model_30d.predict(X_test)
        
        accuracy_7d = accuracy_score(y_7d_test, y_7d_pred)
        accuracy_30d = accuracy_score(y_30d_test, y_30d_pred)
        
        # Métadonnées des modèles
        self.model_metadata = {
            'training_date': pd.Timestamp.now().isoformat(),
            'training_samples': len(training_data),
            'feature_columns': feature_columns,
            'accuracy_7d': accuracy_7d,
            'accuracy_30d': accuracy_30d,
            'test_size': self.test_size,
            'n_estimators': self.n_estimators,
            'random_state': self.random_state
        }
        
        self.is_trained = True
        
        # Sauvegarde automatique
        self._save_models()
        
        logger.info(f"Entraînement terminé - Précision 7j: {accuracy_7d:.3f}, 30j: {accuracy_30d:.3f}")
        
        return {
            'accuracy_7d': accuracy_7d,
            'accuracy_30d': accuracy_30d,
            'samples_count': len(training_data),
            'feature_importance_7d': dict(zip(feature_columns, self.model_7d.feature_importances_)),
            'feature_importance_30d': dict(zip(feature_columns, self.model_30d.feature_importances_))
        }
    
    def predict_profitability(self, trader_data: Dict[str, Any], market_data: Dict[str, Any], 
                            horizon_days: int = 7) -> Dict[str, Any]:
        """
        OBJECTIF : Prédiction de la profitabilité d'un trader
        
        PARAMÈTRES :
        - trader_data (dict) : Données du trader
        - market_data (dict) : Contexte marché
        - horizon_days (int) : Horizon de prédiction (7 ou 30 jours)
        
        RETOURNE :
        - dict : Résultat de prédiction complet
        
        LOGIQUE :
        1. Vérification de l'état d'entraînement
        2. Préparation des features
        3. Prédiction avec le modèle approprié
        4. Interprétation et formatage du résultat
        """
        if not self.is_trained:
            logger.info("Modèles non entraînés, lancement de l'entraînement")
            training_results = self.train_models()
            logger.info(f"Entraînement terminé: {training_results}")
        
        try:
            # Préparation des features
            features = self.prepare_features(trader_data, market_data)
            features_scaled = self.scaler.transform(features)
            
            # Prédictions pour les deux horizons
            prob_7d = self.model_7d.predict_proba(features_scaled)[0][1]
            prob_30d = self.model_30d.predict_proba(features_scaled)[0][1]
            
            # Interprétation des résultats
            result_7d = self._interpret_prediction(prob_7d, 7)
            result_30d = self._interpret_prediction(prob_30d, 30)
            
            # Calcul de la confiance globale
            confidence = (prob_7d + prob_30d) / 2 * 100
            
            result = {
                'prediction_7d': prob_7d * 100,  # Pourcentage
                'prediction_30d': prob_30d * 100,  # Pourcentage
                'confidence': confidence,
                'interpretation_7d': result_7d,
                'interpretation_30d': result_30d,
                'trader_address': trader_data.get('address', 'Unknown'),
                'timestamp': pd.Timestamp.now().isoformat()
            }
            
            logger.info(f"Prédiction complète: 7j={prob_7d:.3f}, 30j={prob_30d:.3f}")
            
            return result
            
        except Exception as e:
            logger.error(f"Erreur lors de la prédiction: {e}")
            return {
                'prediction_7d': 0.0,
                'prediction_30d': 0.0,
                'confidence': 0.0,
                'interpretation_7d': f"Erreur: {str(e)}",
                'interpretation_30d': f"Erreur: {str(e)}",
                'trader_address': trader_data.get('address', 'Unknown'),
                'timestamp': pd.Timestamp.now().isoformat()
            }
    
    def _interpret_prediction(self, probability: float, horizon_days: int) -> str:
        """
        OBJECTIF : Interprétation textuelle de la probabilité de profit
        
        PARAMÈTRES :
        - probability (float) : Probabilité de profit (0-1)
        - horizon_days (int) : Horizon temporel
        
        RETOURNE :
        - str : Interprétation textuelle avec émojis
        
        LOGIQUE :
        1. Classification par seuils de probabilité
        2. Adaptation du message selon l'horizon
        3. Ajout d'émojis pour clarté visuelle
        """
        if probability > 0.8:
            return f"🟢 Très fortement profitable à {horizon_days} jours"
        elif probability > 0.7:
            return f"🟢 Fortement profitable à {horizon_days} jours"
        elif probability > 0.6:
            return f"🟡 Potentiellement profitable à {horizon_days} jours"
        elif probability > 0.4:
            return f"🟠 Incertain à {horizon_days} jours"
        elif probability > 0.3:
            return f"🔴 Peu probable d'être profitable à {horizon_days} jours"
        else:
            return f"🔴 Très peu probable d'être profitable à {horizon_days} jours"
    
    def _save_models(self) -> bool:
        """
        OBJECTIF : Sauvegarde des modèles entraînés sur disque
        
        RETOURNE :
        - bool : True si sauvegarde réussie
        
        LOGIQUE :
        1. Création du dossier de destination
        2. Sauvegarde des modèles RandomForest
        3. Sauvegarde du scaler
        4. Sauvegarde des métadonnées
        """
        try:
            # Création du dossier
            self.model_path.mkdir(parents=True, exist_ok=True)
            
            # Sauvegarde des modèles
            with open(self.model_path / "crypto_predictor_7d.pkl", 'wb') as f:
                pickle.dump(self.model_7d, f)
            
            with open(self.model_path / "crypto_predictor_30d.pkl", 'wb') as f:
                pickle.dump(self.model_30d, f)
            
            with open(self.model_path / "scaler.pkl", 'wb') as f:
                pickle.dump(self.scaler, f)
            
            # Sauvegarde des métadonnées
            import json
            with open(self.model_path / "model_metadata.json", 'w') as f:
                json.dump(self.model_metadata, f, indent=2)
            
            logger.info(f"Modèles sauvegardés dans {self.model_path}")
            return True
            
        except Exception as e:
            logger.error(f"Erreur lors de la sauvegarde: {e}")
            return False
    
    def get_feature_importance(self, horizon_days: int = 7) -> Dict[str, float]:
        """
        OBJECTIF : Récupération de l'importance des features
        
        PARAMÈTRES :
        - horizon_days (int) : Horizon temporel (7 ou 30)
        
        RETOURNE :
        - dict : Importance des features par nom
        
        LOGIQUE :
        1. Sélection du modèle approprié
        2. Extraction des importances
        3. Formatage avec noms des features
        """
        if not self.is_trained:
            return {}
        
        model = self.model_7d if horizon_days == 7 else self.model_30d
        if model is None:
            return {}
        
        feature_names = self.model_metadata.get('feature_columns', [])
        importances = model.feature_importances_
        
        return dict(zip(feature_names, importances))
    
    def get_model_info(self) -> Dict[str, Any]:
        """
        OBJECTIF : Récupération des informations sur les modèles
        
        RETOURNE :
        - dict : Métadonnées complètes des modèles
        """
        return {
            'is_trained': self.is_trained,
            'metadata': self.model_metadata,
            'model_path': str(self.model_path),
            'config': self.config
        } 