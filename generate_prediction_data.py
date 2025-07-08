import json
import random
from datetime import datetime
from pathlib import Path

def generate_market_data():
    """Génère un fichier de données de marché pour la prédiction."""
    return {
        "coingecko_btc": {"price": 65000 + random.uniform(-1000, 1000)},
        "fear_and_greed_index": {"value": random.randint(20, 80)},
        "funding_rates": {"BTCUSDT": {"last_funding_rate": random.uniform(-0.0001, 0.0005)}}
    }

def generate_traders_data(num_traders=50):
    """Génère une liste de traders avec des données pour la prédiction."""
    traders = []
    for i in range(num_traders):
        traders.append({
            "address": f"0xTrader{i:03d}",
            "pnl_24h": random.uniform(-5000, 15000),
            "pnl_7d": random.uniform(-20000, 50000),
            "pnl_30d": random.uniform(-100000, 200000),
            "long_percentage": f"{random.uniform(30, 90):.2f}%",
        })
    return traders

def main():
    """Point d'entrée principal du script."""
    print("--- Démarrage de la génération de données pour la prédiction ---")
    
    output_dir = Path("data/processed")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Générer et sauvegarder les données de marché
    market_data = generate_market_data()
    market_file_path = output_dir / f"market_data_prediction_{datetime.now():%Y%m%d_%H%M%S}.json"
    with open(market_file_path, 'w') as f:
        json.dump(market_data, f, indent=4)
    print(f"✅ Fichier de marché créé : {market_file_path}")

    # Générer et sauvegarder les données des traders
    traders_data = generate_traders_data()
    traders_file_path = output_dir / f"top_traders_prediction_{datetime.now():%Y%m%d_%H%M%S}.json"
    with open(traders_file_path, 'w') as f:
        json.dump(traders_data, f, indent=4)
    print(f"✅ Fichier de traders créé : {traders_file_path}")

    print("\n🎉 Données de prédiction générées avec succès!")

if __name__ == "__main__":
    main() 