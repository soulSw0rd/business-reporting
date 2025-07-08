import pandas as pd
import numpy as np
import json
from datetime import datetime, timedelta
from pathlib import Path

def create_sample_crypto_data():
    """Génère des données crypto complètes pour le dashboard"""
    
    # Création du dossier de données si nécessaire
    data_dir = Path("data/processed")
    data_dir.mkdir(parents=True, exist_ok=True)
    
    # 1. Données des top traders étendues
    np.random.seed(42)
    top_traders = []
    
    trading_styles = ["Scalping", "Swing Trading", "DeFi Focus", "Algorithmic", "Trend Following", "Mean Reversion"]
    countries = ["Singapore", "Netherlands", "Switzerland", "United Kingdom", "Canada", "Germany", "Japan", "USA"]
    crypto_pairs = ["BTC/USDT", "ETH/USDT", "ADA/USDT", "SOL/USDT", "DOT/USDT", "AVAX/USDT", "MATIC/USDT", "LINK/USDT"]
    
    for i in range(50):  # 50 top traders
        total_pnl = np.random.lognormal(11, 0.5)  # Distribution log-normale pour PnL
        win_rate = np.random.beta(8, 3)  # Distribution beta pour win rate (plus réaliste)
        total_trades = np.random.poisson(1000) + 100
        
        trader = {
            "trader_id": f"TopTrader_{i+1:03d}",
            "rank": i + 1,
            "username": f"Trader{np.random.randint(1000, 9999)}",
            "total_pnl": round(total_pnl, 2),
            "win_rate": round(win_rate, 3),
            "total_trades": total_trades,
            "roi_percentage": round(np.random.gamma(3, 50), 1),
            "favorite_pairs": np.random.choice(crypto_pairs, size=np.random.randint(1, 4), replace=False).tolist(),
            "last_active": np.random.choice(["15m", "30m", "1h", "2h", "6h", "12h", "1d"]),
            "followers": np.random.poisson(5000) + 100,
            "copy_traders": np.random.poisson(300) + 10,
            "avg_trade_size": round(np.random.lognormal(7, 0.8), 2),
            "max_drawdown": round(-np.random.gamma(2, 5), 2),
            "sharpe_ratio": round(np.random.gamma(2, 1), 2),
            "trading_style": np.random.choice(trading_styles),
            "verified": bool(np.random.choice([True, False], p=[0.7, 0.3])),
            "joined_date": (datetime.now() - timedelta(days=np.random.randint(30, 730))).strftime("%Y-%m-%d"),
            "country": np.random.choice(countries),
            "monthly_return": round(np.random.normal(8, 15), 2),
            "risk_score": np.random.randint(1, 11),
            "consistency_score": round(np.random.uniform(60, 95), 1)
        }
        top_traders.append(trader)
    
    # Sauvegarde des données traders
    with open(data_dir / "top_traders_extended.json", "w", encoding="utf-8") as f:
        json.dump(top_traders, f, indent=2, ensure_ascii=False)
    
    # 2. Données de marché détaillées
    cryptos = [
        {"symbol": "BTC", "name": "Bitcoin", "base_price": 45000},
        {"symbol": "ETH", "name": "Ethereum", "base_price": 3500},
        {"symbol": "ADA", "name": "Cardano", "base_price": 0.45},
        {"symbol": "SOL", "name": "Solana", "base_price": 100},
        {"symbol": "DOT", "name": "Polkadot", "base_price": 8},
        {"symbol": "AVAX", "name": "Avalanche", "base_price": 40},
        {"symbol": "MATIC", "name": "Polygon", "base_price": 1.2},
        {"symbol": "LINK", "name": "Chainlink", "base_price": 15},
        {"symbol": "UNI", "name": "Uniswap", "base_price": 25},
        {"symbol": "ATOM", "name": "Cosmos", "base_price": 12}
    ]
    
    market_data = {
        "timestamp": datetime.now().isoformat(),
        "global_stats": {
            "total_market_cap": "2.3T",
            "24h_volume": "95.8B",
            "btc_dominance": 41.8,
            "eth_dominance": 18.7,
            "fear_greed_index": np.random.randint(20, 80),
            "active_cryptos": len(cryptos),
            "total_exchanges": 500
        },
        "cryptocurrencies": []
    }
    
    for crypto in cryptos:
        price = crypto["base_price"] * (1 + np.random.normal(0, 0.05))
        change_24h = np.random.normal(0, 5)
        change_7d = np.random.normal(0, 10)
        volume_24h = np.random.lognormal(20, 1)
        
        crypto_data = {
            "symbol": crypto["symbol"],
            "name": crypto["name"],
            "price": round(price, 8 if price < 1 else 2),
            "change_24h": round(change_24h, 2),
            "change_7d": round(change_7d, 2),
            "change_30d": round(np.random.normal(0, 20), 2),
            "market_cap": round(price * np.random.uniform(1e8, 1e12), 0),
            "volume_24h": round(volume_24h, 0),
            "circulating_supply": round(np.random.uniform(1e6, 1e11), 0),
            "max_supply": round(np.random.uniform(1e8, 1e12), 0) if np.random.choice([True, False]) else "N/A",
            "ath": round(price * np.random.uniform(1.1, 5), 8 if price < 1 else 2),
            "atl": round(price * np.random.uniform(0.1, 0.9), 8 if price < 1 else 2),
            "market_cap_rank": cryptos.index(crypto) + 1,
            "liquidity_score": round(np.random.uniform(0.5, 1.0), 3),
            "volatility_7d": round(np.random.uniform(0.1, 0.8), 3),
            "social_dominance": round(np.random.uniform(0, 15), 2),
            "developer_activity": np.random.randint(1, 101)
        }
        market_data["cryptocurrencies"].append(crypto_data)
    
    # Sauvegarde des données de marché
    with open(data_dir / "market_data_extended.json", "w", encoding="utf-8") as f:
        json.dump(market_data, f, indent=2, ensure_ascii=False)
    
    # 3. Données historiques de trading
    historical_data = []
    start_date = datetime.now() - timedelta(days=90)
    
    for i in range(90):  # 90 jours de données
        date = start_date + timedelta(days=i)
        
        for crypto in cryptos[:5]:  # Top 5 cryptos seulement
            base_price = crypto["base_price"]
            # Simulation d'un mouvement de prix avec tendance et volatilité
            trend = np.sin(i * 0.1) * 0.02  # Tendance sinusoïdale
            volatility = np.random.normal(0, 0.03)
            price = base_price * (1 + trend + volatility)
            
            historical_entry = {
                "date": date.strftime("%Y-%m-%d"),
                "symbol": crypto["symbol"],
                "open": round(price * 0.99, 8 if price < 1 else 2),
                "high": round(price * 1.03, 8 if price < 1 else 2),
                "low": round(price * 0.97, 8 if price < 1 else 2),
                "close": round(price, 8 if price < 1 else 2),
                "volume": round(np.random.lognormal(18, 1), 0),
                "market_cap": round(price * np.random.uniform(1e8, 1e12), 0),
                "trades_count": np.random.poisson(10000),
                "active_addresses": np.random.poisson(50000),
                "transaction_volume": round(np.random.lognormal(15, 1), 0)
            }
            historical_data.append(historical_entry)
    
    # Sauvegarde des données historiques
    with open(data_dir / "historical_data.json", "w", encoding="utf-8") as f:
        json.dump(historical_data, f, indent=2, ensure_ascii=False)
    
    # 4. Données de sentiment et signaux
    sentiment_data = {
        "timestamp": datetime.now().isoformat(),
        "overall_sentiment": {
            "score": np.random.uniform(-1, 1),
            "label": np.random.choice(["Extremely Bearish", "Bearish", "Neutral", "Bullish", "Extremely Bullish"]),
            "confidence": np.random.uniform(0.6, 0.95)
        },
        "signals": []
    }
    
    signal_types = ["Technical", "On-Chain", "Social", "Fundamental"]
    signal_strengths = ["Weak", "Moderate", "Strong"]
    
    for crypto in cryptos[:8]:
        signals = []
        for _ in range(np.random.randint(1, 4)):
            signals.append({
                "type": np.random.choice(signal_types),
                "direction": np.random.choice(["Bullish", "Bearish"]),
                "strength": np.random.choice(signal_strengths),
                "confidence": round(np.random.uniform(0.5, 0.95), 2),
                "timestamp": (datetime.now() - timedelta(hours=np.random.randint(1, 24))).isoformat()
            })
        
        sentiment_data["signals"].append({
            "symbol": crypto["symbol"],
            "sentiment_score": round(np.random.uniform(-1, 1), 3),
            "social_volume": np.random.poisson(1000),
            "news_sentiment": round(np.random.uniform(-1, 1), 3),
            "signals": signals
        })
    
    # Sauvegarde des données de sentiment
    with open(data_dir / "sentiment_data.json", "w", encoding="utf-8") as f:
        json.dump(sentiment_data, f, indent=2, ensure_ascii=False)
    
    print("✅ Données d'exemple créées avec succès!")
    print(f"📁 Fichiers générés dans {data_dir}:")
    print("   - top_traders_extended.json (50 traders)")
    print("   - market_data_extended.json (10 cryptos)")
    print("   - historical_data.json (90 jours, 5 cryptos)")
    print("   - sentiment_data.json (signaux et sentiment)")
    
    return len(top_traders), len(cryptos), len(historical_data)

def create_excel_dashboard_data():
    """Crée un fichier Excel avec toutes les données pour analyse externe"""
    
    # Chargement des données JSON
    data_dir = Path("data/processed")
    
    try:
        # Traders
        with open(data_dir / "top_traders_extended.json", "r", encoding="utf-8") as f:
            traders_data = json.load(f)
        traders_df = pd.DataFrame(traders_data)
        
        # Market data
        with open(data_dir / "market_data_extended.json", "r", encoding="utf-8") as f:
            market_data = json.load(f)
        market_df = pd.DataFrame(market_data["cryptocurrencies"])
        
        # Historical data
        with open(data_dir / "historical_data.json", "r", encoding="utf-8") as f:
            historical_data = json.load(f)
        historical_df = pd.DataFrame(historical_data)
        
        # Sentiment data
        with open(data_dir / "sentiment_data.json", "r", encoding="utf-8") as f:
            sentiment_data = json.load(f)
        sentiment_df = pd.DataFrame(sentiment_data["signals"])
        
        # Création du fichier Excel
        with pd.ExcelWriter('crypto_dashboard_data.xlsx', engine='xlsxwriter') as writer:
            traders_df.to_excel(writer, sheet_name='Top_Traders', index=False)
            market_df.to_excel(writer, sheet_name='Market_Data', index=False)
            historical_df.to_excel(writer, sheet_name='Historical_Prices', index=False)
            sentiment_df.to_excel(writer, sheet_name='Sentiment_Signals', index=False)
            
            # Formatage
            workbook = writer.book
            money_format = workbook.add_format({'num_format': '$#,##0.00'})
            percent_format = workbook.add_format({'num_format': '0.00%'})
            
            # Application des formats
            for sheet_name in writer.sheets:
                worksheet = writer.sheets[sheet_name]
                worksheet.set_column('A:Z', 12)
        
        print("📊 Fichier Excel créé : crypto_dashboard_data.xlsx")
        
    except FileNotFoundError as e:
        print(f"❌ Erreur : {e}")
        print("Exécutez d'abord create_sample_crypto_data()")

if __name__ == "__main__":
    print("🚀 Génération des données d'exemple pour CryptoTrader Dashboard")
    print("=" * 60)
    
    # Génération des données JSON
    num_traders, num_cryptos, num_historical = create_sample_crypto_data()
    
    print()
    print("📈 Création du fichier Excel pour analyse...")
    create_excel_dashboard_data()
    
    print()
    print("✨ Génération terminée!")
    print(f"📊 {num_traders} traders, {num_cryptos} cryptos, {num_historical} points de données historiques")
    print("🔥 Vous pouvez maintenant lancer le dashboard avec toutes les données!")
