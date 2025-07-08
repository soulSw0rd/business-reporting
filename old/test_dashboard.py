#!/usr/bin/env python3
"""
Script de test pour valider le chargement des données du dashboard
"""

import json
import pandas as pd
from pathlib import Path
import sys

def test_data_loading():
    """Test le chargement de tous les fichiers de données"""
    data_path = Path("data/processed")
    
    if not data_path.exists():
        print("❌ Dossier data/processed introuvable")
        return False
    
    files_to_test = [
        "top_traders_extended.json",
        "market_data_extended.json", 
        "historical_data.json",
        "sentiment_data.json"
    ]
    
    all_loaded = True
    
    for file_name in files_to_test:
        file_path = data_path / file_name
        
        if not file_path.exists():
            print(f"❌ {file_name} introuvable")
            all_loaded = False
            continue
            
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Test spécifique par fichier
            if file_name == "top_traders_extended.json":
                if isinstance(data, list) and len(data) > 0:
                    df = pd.DataFrame(data)
                    required_cols = ['trader_id', 'username', 'total_pnl', 'win_rate', 'roi_percentage']
                    if all(col in df.columns for col in required_cols):
                        print(f"✅ {file_name} - {len(data)} traders chargés")
                    else:
                        print(f"❌ {file_name} - colonnes manquantes")
                        all_loaded = False
                else:
                    print(f"❌ {file_name} - format incorrect")
                    all_loaded = False
                    
            elif file_name == "market_data_extended.json":
                if isinstance(data, dict) and 'cryptocurrencies' in data:
                    cryptos = data['cryptocurrencies']
                    print(f"✅ {file_name} - {len(cryptos)} cryptos chargées")
                else:
                    print(f"❌ {file_name} - format incorrect")
                    all_loaded = False
                    
            elif file_name == "historical_data.json":
                if isinstance(data, list) and len(data) > 0:
                    print(f"✅ {file_name} - {len(data)} points de données historiques")
                else:
                    print(f"❌ {file_name} - format incorrect")
                    all_loaded = False
                    
            elif file_name == "sentiment_data.json":
                if isinstance(data, dict) and 'overall_sentiment' in data:
                    signals = data.get('signals', [])
                    print(f"✅ {file_name} - sentiment global + {len(signals)} signaux")
                else:
                    print(f"❌ {file_name} - format incorrect")
                    all_loaded = False
                    
        except Exception as e:
            print(f"❌ Erreur lors du chargement de {file_name}: {e}")
            all_loaded = False
    
    return all_loaded

def test_dataframe_operations():
    """Test les opérations DataFrame utilisées dans le dashboard"""
    try:
        # Test chargement top traders
        with open("data/processed/top_traders_extended.json", 'r', encoding='utf-8') as f:
            traders_data = json.load(f)
        
        df = pd.DataFrame(traders_data)
        
        # Test des opérations du dashboard
        # 1. Filtrage par ROI
        filtered = df[df['roi_percentage'] > 50]
        print(f"✅ Filtrage ROI: {len(filtered)} traders avec ROI > 50%")
        
        # 2. Tri par PnL
        sorted_df = df.sort_values('total_pnl', ascending=False)
        print(f"✅ Tri PnL: Top trader a {sorted_df.iloc[0]['total_pnl']:.2f}$ de PnL")
        
        # 3. Formatage des colonnes
        df['total_pnl_formatted'] = df['total_pnl'].apply(lambda x: f"${x:,.2f}")
        df['roi_formatted'] = df['roi_percentage'].apply(lambda x: f"{x:.1f}%")
        print("✅ Formatage des colonnes réussi")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur lors des opérations DataFrame: {e}")
        return False

if __name__ == "__main__":
    print("🧪 Test du dashboard de crypto business intelligence")
    print("=" * 60)
    
    # Test 1: Chargement des données
    print("\n📊 Test 1: Chargement des fichiers de données")
    data_ok = test_data_loading()
    
    # Test 2: Opérations DataFrame
    print("\n🔧 Test 2: Opérations DataFrame")
    operations_ok = test_dataframe_operations()
    
    # Résumé
    print("\n" + "=" * 60)
    if data_ok and operations_ok:
        print("✅ Tous les tests sont passés!")
        print("🚀 Le dashboard devrait fonctionner sans erreur.")
        sys.exit(0)
    else:
        print("❌ Certains tests ont échoué.")
        print("🔍 Vérifiez les erreurs ci-dessus.")
        sys.exit(1)
