#!/usr/bin/env python3
"""
Script simple de génération de données d'exemple
"""

import json
import random
import numpy as np
from datetime import datetime, timedelta
from pathlib import Path

def generate_sample_data():
    """Génère des données d'exemple pour tester les visualisations"""
    
    # Créer le dossier de destination
    output_path = Path("RESOURCES/data/processed")
    output_path.mkdir(parents=True, exist_ok=True)
    
    # Générer des données traders étendues
    traders_data = []
    for i in range(50):
        trader = {
            "username": f"trader_{i+1}",
            "address": f"0x{random.randint(1000000, 9999999):07x}",
            "total_pnl": random.uniform(-10000, 50000),
            "pnl_7d": random.uniform(-5000, 15000),
            "pnl_30d": random.uniform(-10000, 30000),
            "win_rate": random.uniform(30, 85),
            "long_percentage": random.uniform(20, 80),
            "short_percentage": random.uniform(20, 80),
            "roi_percentage": random.uniform(-20, 150),
            "sharpe_ratio": random.uniform(-1, 3),
            "max_drawdown": random.uniform(5, 50),
            "volatility": random.uniform(0.1, 0.8),
            "avg_position_size": random.uniform(1000, 100000),
            "trades_count": random.randint(10, 500),
            "last_activity": (datetime.now() - timedelta(days=random.randint(0, 30))).isoformat()
        }
        traders_data.append(trader)
    
    # Sauvegarder les données traders
    with open(output_path / "top_traders_extended.json", 'w') as f:
        json.dump(traders_data, f, indent=2)
    
    with open(output_path / "top_traders_for_prediction.json", 'w') as f:
        json.dump(traders_data, f, indent=2)
    
    # Générer des données de marché
    market_data = {
        "cryptocurrencies": [
            {
                "symbol": "BTC",
                "name": "Bitcoin",
                "price": 45000 + random.uniform(-5000, 5000),
                "market_cap": 850000000000,
                "volume_24h": 25000000000,
                "change_24h": random.uniform(-10, 10)
            },
            {
                "symbol": "ETH",
                "name": "Ethereum",
                "price": 2800 + random.uniform(-300, 300),
                "market_cap": 340000000000,
                "volume_24h": 15000000000,
                "change_24h": random.uniform(-10, 10)
            }
        ],
        "fear_greed_index": random.randint(20, 80),
        "market_sentiment": random.choice(["bullish", "bearish", "neutral"]),
        "total_market_cap": 1200000000000,
        "btc_dominance": random.uniform(40, 60)
    }
    
    with open(output_path / "market_data_extended.json", 'w') as f:
        json.dump(market_data, f, indent=2)
    
    # Générer des données de sentiment
    sentiment_data = {
        "overall_sentiment": random.uniform(-1, 1),
        "social_sentiment": random.uniform(-1, 1),
        "news_sentiment": random.uniform(-1, 1),
        "signals": [
            {
                "type": "social",
                "sentiment": random.uniform(-1, 1),
                "confidence": random.uniform(0.5, 1.0),
                "timestamp": (datetime.now() - timedelta(hours=i)).isoformat()
            } for i in range(24)
        ]
    }
    
    with open(output_path / "sentiment_data.json", 'w') as f:
        json.dump(sentiment_data, f, indent=2)
    
    print("✅ Données d'exemple générées avec succès!")
    print(f"📁 Données sauvegardées dans: {output_path}")
    print(f"👥 Traders: {len(traders_data)}")
    print(f"💰 Cryptos: {len(market_data['cryptocurrencies'])}")
    print(f"📊 Signaux sentiment: {len(sentiment_data['signals'])}")

if __name__ == "__main__":
    generate_sample_data() 