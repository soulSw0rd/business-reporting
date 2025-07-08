#!/usr/bin/env python3
"""
Dynamic Data Generator
Générateur de données dynamiques qui s'adapte aux cours réels et aux portefeuilles
Auteur: Crypto-Tracker Team
Date: 2025-01-08
Version: 1.0.0
"""

import pandas as pd
import numpy as np
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Tuple
from pathlib import Path
import requests
from dataclasses import dataclass
import random

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class CryptoPrice:
    """Structure pour les prix des cryptos"""
    symbol: str
    price: float
    change_24h: float
    volume_24h: float
    market_cap: float
    last_updated: datetime


@dataclass
class TraderProfile:
    """Structure pour les profils de traders"""
    address: str
    total_pnl: float
    win_rate: float
    total_trades: int
    roi_percentage: float
    risk_score: float
    favorite_pairs: List[str]
    portfolio_value: float
    last_trade_time: datetime


class DynamicDataGenerator:
    """
    Générateur de données dynamiques pour le dashboard crypto
    
    RESPONSABILITÉ : Génération de données réalistes et dynamiques
    UTILISATION : Création de datasets adaptatifs pour ML et visualisations
    
    FONCTIONNALITÉS :
    - Récupération de prix crypto en temps réel
    - Génération de profils de traders dynamiques
    - Adaptation aux conditions de marché
    - Simulation de portefeuilles réalistes
    - Génération de prédictions crédibles
    """
    
    def __init__(self, config_path: str = "RESOURCES/configs/app_config.json"):
        """Initialisation du générateur"""
        self.config_path = Path(config_path)
        self.config = self._load_config()
        self.crypto_prices = {}
        self.trader_profiles = {}
        self.market_conditions = {}
        
        # APIs pour données réelles
        self.apis = {
            'coingecko': 'https://api.coingecko.com/api/v3',
            'binance': 'https://api.binance.com/api/v3',
            'fear_greed': 'https://api.alternative.me/fng/'
        }
        
        # Cryptos principales à suivre
        self.main_cryptos = [
            'bitcoin', 'ethereum', 'binancecoin', 'cardano', 'solana',
            'polkadot', 'dogecoin', 'avalanche-2', 'chainlink', 'polygon'
        ]
        
        logger.info("DynamicDataGenerator initialisé")
    
    def _load_config(self) -> Dict[str, Any]:
        """Charger la configuration"""
        try:
            if self.config_path.exists():
                with open(self.config_path, 'r') as f:
                    return json.load(f)
            else:
                return self._create_default_config()
        except Exception as e:
            logger.error(f"Erreur chargement config: {e}")
            return self._create_default_config()
    
    def _create_default_config(self) -> Dict[str, Any]:
        """Créer une configuration par défaut"""
        return {
            "data_generation": {
                "update_interval": 300,  # 5 minutes
                "traders_count": 100,
                "min_portfolio_value": 1000,
                "max_portfolio_value": 1000000,
                "volatility_factor": 0.1
            },
            "market_simulation": {
                "bull_market_prob": 0.3,
                "bear_market_prob": 0.2,
                "crab_market_prob": 0.5,
                "sentiment_volatility": 0.15
            }
        }
    
    def fetch_real_crypto_prices(self) -> Dict[str, CryptoPrice]:
        """
        Récupérer les prix réels des cryptomonnaies
        
        RETOURNE:
        - Dict[str, CryptoPrice]: Prix actuels des cryptos
        """
        try:
            # Appel API CoinGecko
            url = f"{self.apis['coingecko']}/simple/price"
            params = {
                'ids': ','.join(self.main_cryptos),
                'vs_currencies': 'usd',
                'include_24hr_change': 'true',
                'include_24hr_vol': 'true',
                'include_market_cap': 'true'
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            crypto_prices = {}
            for crypto_id, price_data in data.items():
                symbol = crypto_id.replace('-', '').upper()
                if crypto_id == 'bitcoin':
                    symbol = 'BTC'
                elif crypto_id == 'ethereum':
                    symbol = 'ETH'
                elif crypto_id == 'binancecoin':
                    symbol = 'BNB'
                
                crypto_prices[symbol] = CryptoPrice(
                    symbol=symbol,
                    price=price_data.get('usd', 0),
                    change_24h=price_data.get('usd_24h_change', 0),
                    volume_24h=price_data.get('usd_24h_vol', 0),
                    market_cap=price_data.get('usd_market_cap', 0),
                    last_updated=datetime.now()
                )
            
            self.crypto_prices = crypto_prices
            logger.info(f"Prix récupérés pour {len(crypto_prices)} cryptos")
            return crypto_prices
            
        except Exception as e:
            logger.error(f"Erreur récupération prix: {e}")
            return self._generate_fallback_prices()
    
    def _generate_fallback_prices(self) -> Dict[str, CryptoPrice]:
        """Générer des prix de fallback si l'API échoue"""
        fallback_prices = {
            'BTC': 45000 + np.random.normal(0, 2000),
            'ETH': 2500 + np.random.normal(0, 200),
            'BNB': 300 + np.random.normal(0, 30),
            'ADA': 0.5 + np.random.normal(0, 0.05),
            'SOL': 100 + np.random.normal(0, 10)
        }
        
        crypto_prices = {}
        for symbol, price in fallback_prices.items():
            crypto_prices[symbol] = CryptoPrice(
                symbol=symbol,
                price=max(price, 0.01),  # Prix minimum
                change_24h=np.random.normal(0, 5),
                volume_24h=np.random.uniform(1e9, 1e11),
                market_cap=price * np.random.uniform(1e6, 1e9),
                last_updated=datetime.now()
            )
        
        return crypto_prices
    
    def generate_dynamic_trader_profiles(self, count: int = 100) -> List[TraderProfile]:
        """
        Générer des profils de traders dynamiques basés sur les conditions de marché
        
        PARAMÈTRES:
        - count: Nombre de traders à générer
        
        RETOURNE:
        - List[TraderProfile]: Profils de traders
        """
        profiles = []
        
        # Obtenir les conditions de marché actuelles
        market_conditions = self._analyze_market_conditions()
        
        for i in range(count):
            # Générer un profil adapté aux conditions de marché
            profile = self._generate_single_trader_profile(i, market_conditions)
            profiles.append(profile)
        
        self.trader_profiles = {p.address: p for p in profiles}
        logger.info(f"Généré {len(profiles)} profils de traders")
        return profiles
    
    def _analyze_market_conditions(self) -> Dict[str, Any]:
        """Analyser les conditions actuelles du marché"""
        if not self.crypto_prices:
            self.fetch_real_crypto_prices()
        
        # Calculer les métriques de marché
        btc_price = self.crypto_prices.get('BTC', self._generate_fallback_prices()['BTC'])
        eth_price = self.crypto_prices.get('ETH', self._generate_fallback_prices()['ETH'])
        
        # Déterminer la tendance générale
        avg_change = np.mean([p.change_24h for p in self.crypto_prices.values()])
        
        market_sentiment = "bullish" if avg_change > 2 else "bearish" if avg_change < -2 else "neutral"
        
        # Volatilité du marché
        volatility = np.std([p.change_24h for p in self.crypto_prices.values()])
        
        conditions = {
            'sentiment': market_sentiment,
            'volatility': volatility,
            'btc_price': btc_price.price,
            'eth_price': eth_price.price,
            'avg_change_24h': avg_change,
            'fear_greed_index': self._get_fear_greed_index()
        }
        
        self.market_conditions = conditions
        return conditions
    
    def _get_fear_greed_index(self) -> float:
        """Récupérer l'indice Fear & Greed"""
        try:
            response = requests.get(self.apis['fear_greed'], timeout=5)
            data = response.json()
            return float(data['data'][0]['value'])
        except:
            # Fallback basé sur les changements de prix
            if not self.crypto_prices:
                return 50.0
            
            avg_change = np.mean([p.change_24h for p in self.crypto_prices.values()])
            # Conversion simple : changement positif = moins de peur
            return max(0, min(100, 50 + avg_change * 2))
    
    def _generate_single_trader_profile(self, index: int, market_conditions: Dict[str, Any]) -> TraderProfile:
        """Générer un profil de trader individuel"""
        
        # Adresse unique
        address = f"0x{random.randint(1000000000, 9999999999):010x}"
        
        # Adaptation aux conditions de marché
        sentiment = market_conditions.get('sentiment', 'neutral')
        volatility = market_conditions.get('volatility', 5.0)
        
        # Profil de base avec adaptation au marché
        if sentiment == 'bullish':
            base_pnl_multiplier = 1.5
            base_win_rate = 0.65
            risk_appetite = 0.7
        elif sentiment == 'bearish':
            base_pnl_multiplier = 0.6
            base_win_rate = 0.45
            risk_appetite = 0.3
        else:
            base_pnl_multiplier = 1.0
            base_win_rate = 0.55
            risk_appetite = 0.5
        
        # Génération des métriques
        portfolio_value = np.random.lognormal(
            np.log(50000), 1.5
        ) * base_pnl_multiplier
        
        # PnL basé sur le portefeuille et les conditions
        total_pnl = portfolio_value * np.random.normal(0.1, 0.3) * base_pnl_multiplier
        
        # Win rate avec adaptation
        win_rate = np.clip(
            np.random.beta(2, 2) * 0.4 + base_win_rate,
            0.2, 0.9
        )
        
        # Nombre de trades basé sur la volatilité
        total_trades = int(np.random.poisson(100 * (1 + volatility / 10)))
        
        # ROI calculé
        roi_percentage = (total_pnl / portfolio_value) * 100 if portfolio_value > 0 else 0
        
        # Score de risque
        risk_score = np.clip(
            (1 - win_rate) * 100 + np.random.normal(0, 10),
            0, 100
        )
        
        # Paires favorites basées sur les cryptos populaires
        available_pairs = list(self.crypto_prices.keys())
        favorite_pairs = random.sample(
            available_pairs, 
            min(3, len(available_pairs))
        )
        
        # Temps de dernière transaction
        last_trade_time = datetime.now() - timedelta(
            hours=np.random.exponential(24)
        )
        
        return TraderProfile(
            address=address,
            total_pnl=total_pnl,
            win_rate=win_rate,
            total_trades=total_trades,
            roi_percentage=roi_percentage,
            risk_score=risk_score,
            favorite_pairs=favorite_pairs,
            portfolio_value=portfolio_value,
            last_trade_time=last_trade_time
        )
    
    def generate_dynamic_predictions(self, trader_profiles: List[TraderProfile]) -> List[Dict[str, Any]]:
        """
        Générer des prédictions dynamiques basées sur les profils de traders et le marché
        
        PARAMÈTRES:
        - trader_profiles: Liste des profils de traders
        
        RETOURNE:
        - List[Dict]: Prédictions avec métriques réalistes
        """
        predictions = []
        market_conditions = self.market_conditions or self._analyze_market_conditions()
        
        for profile in trader_profiles:
            # Calcul de la probabilité de profitabilité
            base_prob = self._calculate_base_profitability(profile)
            
            # Ajustement selon les conditions de marché
            market_adjustment = self._get_market_adjustment(market_conditions)
            
            # Probabilité finale
            final_prob_7d = np.clip(base_prob + market_adjustment, 0.05, 0.95)
            final_prob_30d = np.clip(base_prob + market_adjustment * 0.7, 0.05, 0.95)
            
            # Confiance basée sur l'historique du trader
            confidence = self._calculate_confidence(profile, market_conditions)
            
            # Return attendu
            expected_return_7d = self._calculate_expected_return(profile, final_prob_7d, 7)
            expected_return_30d = self._calculate_expected_return(profile, final_prob_30d, 30)
            
            prediction = {
                'address': profile.address,
                'is_profitable_7d': final_prob_7d > 0.5,
                'is_profitable_30d': final_prob_30d > 0.5,
                'probability_7d': final_prob_7d * 100,
                'probability_30d': final_prob_30d * 100,
                'confidence': confidence,
                'expected_return_7d': expected_return_7d,
                'expected_return_30d': expected_return_30d,
                'risk_score': profile.risk_score,
                'portfolio_value': profile.portfolio_value,
                'timestamp': datetime.now().isoformat(),
                'market_conditions': market_conditions['sentiment']
            }
            
            predictions.append(prediction)
        
        logger.info(f"Généré {len(predictions)} prédictions dynamiques")
        return predictions
    
    def _calculate_base_profitability(self, profile: TraderProfile) -> float:
        """Calculer la probabilité de base de profitabilité"""
        # Facteurs de performance
        pnl_factor = np.tanh(profile.total_pnl / 100000) * 0.2  # Normalisation
        win_rate_factor = (profile.win_rate - 0.5) * 0.3
        roi_factor = np.tanh(profile.roi_percentage / 100) * 0.2
        experience_factor = min(profile.total_trades / 1000, 1) * 0.1
        
        # Probabilité de base
        base_prob = 0.5 + pnl_factor + win_rate_factor + roi_factor + experience_factor
        
        return np.clip(base_prob, 0.1, 0.9)
    
    def _get_market_adjustment(self, market_conditions: Dict[str, Any]) -> float:
        """Calculer l'ajustement basé sur les conditions de marché"""
        sentiment = market_conditions.get('sentiment', 'neutral')
        fear_greed = market_conditions.get('fear_greed_index', 50)
        
        if sentiment == 'bullish':
            sentiment_adj = 0.1
        elif sentiment == 'bearish':
            sentiment_adj = -0.1
        else:
            sentiment_adj = 0.0
        
        # Ajustement Fear & Greed
        fear_greed_adj = (fear_greed - 50) / 500  # Normalisation
        
        return sentiment_adj + fear_greed_adj
    
    def _calculate_confidence(self, profile: TraderProfile, market_conditions: Dict[str, Any]) -> float:
        """Calculer la confiance de la prédiction"""
        # Facteurs de confiance
        experience_conf = min(profile.total_trades / 500, 1) * 30
        consistency_conf = profile.win_rate * 40
        portfolio_conf = min(profile.portfolio_value / 100000, 1) * 20
        market_conf = (100 - market_conditions.get('volatility', 5)) / 100 * 10
        
        total_confidence = experience_conf + consistency_conf + portfolio_conf + market_conf
        
        return np.clip(total_confidence, 20, 95)
    
    def _calculate_expected_return(self, profile: TraderProfile, probability: float, days: int) -> float:
        """Calculer le return attendu"""
        # Return basé sur l'historique et la probabilité
        base_return = profile.roi_percentage / 365 * days  # Annualisé
        
        # Ajustement selon la probabilité
        expected_return = base_return * (probability * 2 - 1)  # -1 à 1
        
        # Ajout de variance
        variance = np.random.normal(0, abs(expected_return) * 0.2)
        
        return expected_return + variance
    
    def save_dynamic_data(self, output_dir: str = "RESOURCES/data/processed"):
        """
        Sauvegarder toutes les données dynamiques
        
        PARAMÈTRES:
        - output_dir: Répertoire de sortie
        """
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        # Générer les données
        crypto_prices = self.fetch_real_crypto_prices()
        trader_profiles = self.generate_dynamic_trader_profiles(100)
        predictions = self.generate_dynamic_predictions(trader_profiles)
        
        # Sauvegarder les prix crypto
        crypto_data = {
            'cryptocurrencies': [
                {
                    'symbol': p.symbol,
                    'price': p.price,
                    'change_24h': p.change_24h,
                    'volume_24h': p.volume_24h,
                    'market_cap': p.market_cap,
                    'last_updated': p.last_updated.isoformat()
                }
                for p in crypto_prices.values()
            ],
            'last_updated': datetime.now().isoformat()
        }
        
        with open(output_path / "market_data_dynamic.json", "w") as f:
            json.dump(crypto_data, f, indent=2)
        
        # Sauvegarder les profils de traders
        traders_data = [
            {
                'address': p.address,
                'username': f"Trader_{p.address[-6:]}",
                'total_pnl': p.total_pnl,
                'win_rate': p.win_rate,
                'total_trades': p.total_trades,
                'roi_percentage': p.roi_percentage,
                'risk_score': p.risk_score,
                'favorite_pairs': p.favorite_pairs,
                'portfolio_value': p.portfolio_value,
                'last_trade_time': p.last_trade_time.isoformat()
            }
            for p in trader_profiles
        ]
        
        with open(output_path / "top_traders_dynamic.json", "w") as f:
            json.dump(traders_data, f, indent=2)
        
        # Sauvegarder les prédictions
        with open(output_path / "predictions_dynamic.json", "w") as f:
            json.dump(predictions, f, indent=2)
        
        # Sauvegarder les conditions de marché
        with open(output_path / "market_conditions.json", "w") as f:
            json.dump(self.market_conditions, f, indent=2)
        
        logger.info(f"Données dynamiques sauvegardées dans {output_path}")
        
        return {
            'crypto_prices': len(crypto_prices),
            'trader_profiles': len(trader_profiles),
            'predictions': len(predictions),
            'market_conditions': self.market_conditions
        }


def main():
    """Fonction principale pour test"""
    generator = DynamicDataGenerator()
    result = generator.save_dynamic_data()
    print(f"Données générées: {result}")


if __name__ == "__main__":
    main() 