#!/usr/bin/env python3
"""
Advanced Dataset Generator
Générateur de dataset avancé pour améliorer les prédictions Random Forest
Auteur: Crypto-Tracker Team
Date: 2025-01-08
Version: 1.0.0
"""

import numpy as np
import pandas as pd
import json
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Any, List, Tuple
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split

from .config_manager import get_config

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AdvancedDatasetGenerator:
    """
    Générateur de dataset avancé pour ML crypto trading
    
    RESPONSABILITÉ : Génération de données d'entraînement réalistes et variées
    UTILISATION : Amélioration des prédictions Random Forest
    
    FONCTIONNALITÉS :
    - Génération de 10,000+ échantillons réalistes
    - Simulation de cycles de marché (bull/bear/crab)
    - Corrélations réalistes entre variables
    - Patterns de trading authentiques
    - Données de validation et test
    """
    
    def __init__(self):
        """Initialisation du générateur"""
        self.config = get_config("ml")
        self.random_state = self.config.get("random_state", 42)
        np.random.seed(self.random_state)
        
        # Paramètres de génération
        self.n_samples = 15000  # Dataset plus large
        self.noise_factor = 0.1
        
        # Cycles de marché
        self.market_cycles = {
            'bull': {'fear_greed': (60, 90), 'btc_trend': 1.5, 'funding_rate': (-0.01, 0.05)},
            'bear': {'fear_greed': (10, 40), 'btc_trend': -1.2, 'funding_rate': (-0.05, 0.01)},
            'crab': {'fear_greed': (40, 60), 'btc_trend': 0.1, 'funding_rate': (-0.02, 0.02)}
        }
        
        logger.info("AdvancedDatasetGenerator initialisé")
    
    def generate_comprehensive_dataset(self) -> pd.DataFrame:
        """
        Génère un dataset complet avec toutes les métriques pertinentes
        
        RETOURNE:
        - pd.DataFrame: Dataset avec 25+ features et labels
        """
        logger.info(f"Génération de {self.n_samples} échantillons...")
        
        # Structures de données
        data = []
        
        # Distribution des cycles de marché
        cycle_distribution = {
            'bull': int(self.n_samples * 0.3),
            'bear': int(self.n_samples * 0.25),
            'crab': int(self.n_samples * 0.45)
        }
        
        sample_id = 0
        
        for cycle_type, n_cycle_samples in cycle_distribution.items():
            logger.info(f"Génération {n_cycle_samples} échantillons pour cycle {cycle_type}")
            
            for _ in range(n_cycle_samples):
                sample = self._generate_sample(cycle_type, sample_id)
                data.append(sample)
                sample_id += 1
        
        # Conversion en DataFrame
        df = pd.DataFrame(data)
        
        # Ajout de features dérivées
        df = self._add_derived_features(df)
        
        # Génération des labels
        df = self._generate_labels(df)
        
        logger.info(f"Dataset généré: {len(df)} échantillons, {len(df.columns)} features")
        
        return df
    
    def _generate_sample(self, cycle_type: str, sample_id: int) -> Dict[str, Any]:
        """
        Génère un échantillon réaliste pour un cycle de marché donné
        
        PARAMÈTRES:
        - cycle_type: Type de cycle (bull/bear/crab)
        - sample_id: ID unique de l'échantillon
        
        RETOURNE:
        - Dict: Échantillon avec toutes les métriques
        """
        cycle_params = self.market_cycles[cycle_type]
        
        # === MÉTRIQUES TRADER ===
        # Performance basée sur le cycle
        base_performance = {
            'bull': np.random.normal(0.15, 0.25),
            'bear': np.random.normal(-0.08, 0.20),
            'crab': np.random.normal(0.02, 0.15)
        }[cycle_type]
        
        # PnL avec corrélation temporelle
        pnl_7d = base_performance + np.random.normal(0, 0.1)
        pnl_30d = base_performance * 3.5 + np.random.normal(0, 0.15)
        pnl_90d = base_performance * 8 + np.random.normal(0, 0.25)
        
        # Métriques de trading
        win_rate = np.clip(0.45 + base_performance * 0.8 + np.random.normal(0, 0.08), 0.2, 0.9)
        
        # Exposition long/short basée sur le cycle
        cycle_bias = {'bull': 0.15, 'bear': -0.12, 'crab': 0.02}[cycle_type]
        long_percentage = np.clip(50 + cycle_bias * 100 + np.random.normal(0, 15), 10, 90)
        
        # Volume et fréquence de trading
        avg_position_size = np.random.lognormal(mean=8, sigma=1.5)  # Distribution réaliste
        trades_per_day = np.random.poisson(lam=12)  # Poisson pour fréquence
        
        # Métriques de risque
        max_drawdown = abs(np.random.beta(2, 5) * 0.4)  # Beta pour drawdown réaliste
        sharpe_ratio = (base_performance * 2) / max(max_drawdown, 0.05)
        
        # === MÉTRIQUES MARCHÉ ===
        # Prix Bitcoin avec tendance
        btc_base = 45000
        btc_trend = cycle_params['btc_trend']
        btc_price = btc_base * (1 + btc_trend * np.random.normal(0.1, 0.05))
        btc_price = max(btc_price, 20000)  # Prix minimum réaliste
        
        # Volatilité Bitcoin
        btc_volatility = np.random.gamma(2, 0.02)  # Gamma pour volatilité réaliste
        
        # Fear & Greed Index
        fg_min, fg_max = cycle_params['fear_greed']
        fear_greed = np.random.uniform(fg_min, fg_max)
        
        # Taux de financement
        funding_min, funding_max = cycle_params['funding_rate']
        funding_rate = np.random.uniform(funding_min, funding_max)
        
        # Volume de marché
        market_volume_24h = np.random.lognormal(mean=15, sigma=0.5)  # Milliards USD
        
        # Dominance Bitcoin
        btc_dominance = np.random.normal(45, 8)
        btc_dominance = np.clip(btc_dominance, 25, 70)
        
        # === MÉTRIQUES SENTIMENT ===
        # Sentiment social media
        social_sentiment = np.random.normal(fear_greed/100, 0.15)
        social_sentiment = np.clip(social_sentiment, 0, 1)
        
        # Activité on-chain
        active_addresses = np.random.lognormal(mean=12, sigma=0.3)
        transaction_count = np.random.lognormal(mean=11, sigma=0.4)
        
        # === MÉTRIQUES MACRO ===
        # Corrélation avec indices traditionnels
        spy_correlation = np.random.normal(0.3, 0.2)  # Corrélation avec S&P 500
        dxy_correlation = np.random.normal(-0.4, 0.2)  # Corrélation avec Dollar Index
        
        # Taux d'intérêt impact
        interest_rate_impact = np.random.normal(-0.1, 0.05)
        
        # === MÉTRIQUES TEMPORELLES ===
        # Jour de la semaine (effet weekend)
        day_of_week = np.random.randint(0, 7)
        is_weekend = 1 if day_of_week >= 5 else 0
        
        # Heure de trading (effet horaire)
        hour_of_day = np.random.randint(0, 24)
        
        # Période du mois (effet salaire)
        day_of_month = np.random.randint(1, 31)
        
        return {
            # Identifiants
            'sample_id': sample_id,
            'cycle_type': cycle_type,
            'timestamp': datetime.now() - timedelta(days=np.random.randint(0, 365)),
            
            # Métriques trader
            'pnl_7d': pnl_7d,
            'pnl_30d': pnl_30d,
            'pnl_90d': pnl_90d,
            'win_rate': win_rate,
            'long_percentage': long_percentage,
            'avg_position_size': avg_position_size,
            'trades_per_day': trades_per_day,
            'max_drawdown': max_drawdown,
            'sharpe_ratio': sharpe_ratio,
            
            # Métriques marché
            'btc_price': btc_price,
            'btc_volatility': btc_volatility,
            'fear_greed': fear_greed,
            'funding_rate': funding_rate,
            'market_volume_24h': market_volume_24h,
            'btc_dominance': btc_dominance,
            
            # Métriques sentiment
            'social_sentiment': social_sentiment,
            'active_addresses': active_addresses,
            'transaction_count': transaction_count,
            
            # Métriques macro
            'spy_correlation': spy_correlation,
            'dxy_correlation': dxy_correlation,
            'interest_rate_impact': interest_rate_impact,
            
            # Métriques temporelles
            'day_of_week': day_of_week,
            'is_weekend': is_weekend,
            'hour_of_day': hour_of_day,
            'day_of_month': day_of_month
        }
    
    def _add_derived_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Ajoute des features dérivées et des interactions
        
        PARAMÈTRES:
        - df: DataFrame original
        
        RETOURNE:
        - DataFrame avec features supplémentaires
        """
        # Ratios de performance
        df['pnl_ratio_7_30'] = df['pnl_7d'] / np.maximum(np.abs(df['pnl_30d']), 0.01)
        df['pnl_ratio_30_90'] = df['pnl_30d'] / np.maximum(np.abs(df['pnl_90d']), 0.01)
        
        # Métriques de consistance
        df['performance_consistency'] = 1 - np.abs(df['pnl_7d'] - df['pnl_30d']/4)
        
        # Risk-adjusted returns
        df['risk_adjusted_return'] = df['pnl_30d'] / np.maximum(df['max_drawdown'], 0.01)
        
        # Alignement avec le marché
        df['market_alignment'] = df['long_percentage'] * df['fear_greed'] / 100
        
        # Momentum indicators
        df['momentum_score'] = (df['pnl_7d'] > 0).astype(int) * df['win_rate']
        
        # Volatility-adjusted metrics
        df['vol_adjusted_pnl'] = df['pnl_30d'] / np.maximum(df['btc_volatility'], 0.01)
        
        # Sentiment-performance correlation
        df['sentiment_performance_corr'] = df['social_sentiment'] * df['pnl_30d']
        
        # Trading intensity
        df['trading_intensity'] = df['trades_per_day'] * df['avg_position_size']
        
        # Market condition score
        df['market_condition_score'] = (df['fear_greed'] + df['btc_dominance']) / 2
        
        return df
    
    def _generate_labels(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Génère les labels de profitabilité basés sur des règles réalistes
        
        PARAMÈTRES:
        - df: DataFrame avec features
        
        RETOURNE:
        - DataFrame avec labels
        """
        # Label binaire principal: profitable dans les 7 prochains jours
        df['profitable_7d'] = (
            (df['pnl_7d'] > 0.05) &  # Performance minimale
            (df['win_rate'] > 0.5) &  # Taux de réussite
            (df['max_drawdown'] < 0.2) &  # Risque contrôlé
            (df['sharpe_ratio'] > 0.5)  # Ratio risque/rendement
        ).astype(int)
        
        # Label pour 30 jours
        df['profitable_30d'] = (
            (df['pnl_30d'] > 0.1) &
            (df['win_rate'] > 0.48) &
            (df['max_drawdown'] < 0.25) &
            (df['performance_consistency'] > 0.3)
        ).astype(int)
        
        # Label catégoriel de performance
        conditions = [
            (df['pnl_30d'] > 0.2) & (df['max_drawdown'] < 0.15),  # Excellent
            (df['pnl_30d'] > 0.1) & (df['max_drawdown'] < 0.25),  # Bon
            (df['pnl_30d'] > 0.0) & (df['max_drawdown'] < 0.35),  # Moyen
        ]
        choices = ['excellent', 'bon', 'moyen']
        df['performance_category'] = np.select(conditions, choices, default='faible')
        
        # Score de confiance basé sur la consistance
        df['confidence_score'] = (
            df['performance_consistency'] * 0.3 +
            df['win_rate'] * 0.3 +
            (1 - df['max_drawdown']) * 0.2 +
            np.clip(df['sharpe_ratio'], 0, 2) / 2 * 0.2
        )
        
        return df
    
    def save_dataset(self, df: pd.DataFrame, filename: str = None) -> str:
        """
        Sauvegarde le dataset généré
        
        PARAMÈTRES:
        - df: DataFrame à sauvegarder
        - filename: Nom du fichier (optionnel)
        
        RETOURNE:
        - str: Chemin du fichier sauvegardé
        """
        if filename is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"advanced_training_dataset_{timestamp}.csv"
        
        # Chemin de sauvegarde
        data_path = Path(get_config("data")["processed_path"])
        data_path.mkdir(parents=True, exist_ok=True)
        
        filepath = data_path / filename
        
        # Sauvegarde
        df.to_csv(filepath, index=False)
        
        # Métadonnées
        metadata = {
            'filename': filename,
            'samples': len(df),
            'features': len(df.columns) - 4,  # Moins les labels
            'generation_date': datetime.now().isoformat(),
            'profitable_7d_ratio': df['profitable_7d'].mean(),
            'profitable_30d_ratio': df['profitable_30d'].mean(),
            'performance_distribution': df['performance_category'].value_counts().to_dict()
        }
        
        metadata_path = data_path / f"metadata_{filename.replace('.csv', '.json')}"
        with open(metadata_path, 'w') as f:
            json.dump(metadata, f, indent=2)
        
        logger.info(f"Dataset sauvegardé: {filepath}")
        logger.info(f"Métadonnées: {metadata_path}")
        
        return str(filepath)
    
    def generate_and_save(self) -> Tuple[str, Dict[str, Any]]:
        """
        Génère et sauvegarde un dataset complet
        
        RETOURNE:
        - Tuple[str, Dict]: (chemin_fichier, statistiques)
        """
        # Génération
        df = self.generate_comprehensive_dataset()
        
        # Sauvegarde
        filepath = self.save_dataset(df)
        
        # Statistiques
        stats = {
            'total_samples': len(df),
            'total_features': len(df.columns) - 4,
            'profitable_7d_ratio': f"{df['profitable_7d'].mean():.2%}",
            'profitable_30d_ratio': f"{df['profitable_30d'].mean():.2%}",
            'performance_distribution': df['performance_category'].value_counts().to_dict(),
            'cycle_distribution': df['cycle_type'].value_counts().to_dict(),
            'feature_correlations': df.corr()['profitable_7d'].abs().sort_values(ascending=False).head(10).to_dict()
        }
        
        return filepath, stats


def main():
    """Test du générateur"""
    generator = AdvancedDatasetGenerator()
    filepath, stats = generator.generate_and_save()
    
    print(f"Dataset généré: {filepath}")
    print(f"Statistiques: {json.dumps(stats, indent=2)}")


if __name__ == "__main__":
    main() 