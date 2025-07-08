#!/usr/bin/env python3
"""
Script de vérification de l'intégrité des données pour le dashboard crypto
"""
import json
import pandas as pd
import os

def verify_data_files():
    """Vérifie l'intégrité de tous les fichiers de données"""
    data_dir = "data/processed"
    
    print("🔍 Vérification de l'intégrité des données...\n")
    
    # Liste des fichiers à vérifier
    files_to_check = [
        "top_traders_extended.json",
        "market_data_extended.json", 
        "historical_data.json",
        "sentiment_data.json"
    ]
    
    all_good = True
    
    for file_name in files_to_check:
        file_path = os.path.join(data_dir, file_name)
        print(f"📄 Vérification de {file_name}...")
        
        try:
            if not os.path.exists(file_path):
                print(f"   ❌ Fichier manquant: {file_path}")
                all_good = False
                continue
                
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
            if not data:
                print(f"   ❌ Fichier vide: {file_name}")
                all_good = False
                continue
                
            # Vérifications spécifiques par type de fichier
            if file_name == "top_traders_extended.json":
                required_columns = ['trader_id', 'username', 'total_pnl', 'win_rate', 'roi_percentage']
                df = pd.DataFrame(data)
                missing_cols = [col for col in required_columns if col not in df.columns]
                if missing_cols:
                    print(f"   ❌ Colonnes manquantes dans {file_name}: {missing_cols}")
                    all_good = False
                else:
                    print(f"   ✅ Structure correcte ({len(data)} traders)")
                    
            elif file_name == "market_data_extended.json":
                if isinstance(data, dict) and 'cryptocurrencies' in data:
                    crypto_data = data['cryptocurrencies']
                    if len(crypto_data) > 0:
                        required_keys = ['symbol', 'price', 'change_24h']
                        missing_keys = [key for key in required_keys if key not in crypto_data[0]]
                        if missing_keys:
                            print(f"   ❌ Clés manquantes dans {file_name}: {missing_keys}")
                            all_good = False
                        else:
                            print(f"   ✅ Structure correcte ({len(crypto_data)} cryptos)")
                    else:
                        print(f"   ❌ Aucune donnée crypto dans {file_name}")
                        all_good = False
                else:
                    print(f"   ❌ Format incorrect pour {file_name}")
                    all_good = False
                    
            elif file_name == "historical_data.json":
                if isinstance(data, list) and len(data) > 0:
                    required_keys = ['date', 'symbol', 'open', 'high', 'low', 'close', 'volume']
                    missing_keys = [key for key in required_keys if key not in data[0]]
                    if missing_keys:
                        print(f"   ❌ Clés manquantes dans {file_name}: {missing_keys}")
                        all_good = False
                    else:
                        # Compter les symboles uniques
                        symbols = set(item['symbol'] for item in data if 'symbol' in item)
                        # Compter les dates uniques
                        dates = set(item['date'] for item in data if 'date' in item)
                        print(f"   ✅ Structure correcte ({len(data)} entrées, {len(symbols)} symboles, {len(dates)} dates)")
                else:
                    print(f"   ❌ Format incorrect pour {file_name} (doit être une liste)")
                    all_good = False
                    
            elif file_name == "sentiment_data.json":
                if isinstance(data, dict) and all(key in data for key in ['timestamp', 'overall_sentiment', 'signals']):
                    overall = data.get('overall_sentiment', {})
                    signals = data.get('signals', [])
                    
                    if isinstance(overall, dict) and 'score' in overall and 'label' in overall:
                        print(f"   ✅ Structure correcte (sentiment: {overall.get('label', 'N/A')}, {len(signals)} signaux)")
                    else:
                        print(f"   ❌ Structure 'overall_sentiment' incorrecte dans {file_name}")
                        all_good = False
                else:
                    print(f"   ❌ Format incorrect pour {file_name} (clés manquantes)")
                    all_good = False
                    
        except json.JSONDecodeError as e:
            print(f"   ❌ Erreur JSON dans {file_name}: {e}")
            all_good = False
        except Exception as e:
            print(f"   ❌ Erreur lors de la vérification de {file_name}: {e}")
            all_good = False
    
    print("\n" + "="*50)
    if all_good:
        print("✅ Toutes les vérifications sont passées avec succès!")
        print("🚀 Le dashboard devrait fonctionner correctement.")
    else:
        print("❌ Des problèmes ont été détectés dans les données.")
        print("💡 Exécutez 'python generate_sample_data.py' pour regénérer les données.")
    print("="*50)
    
    return all_good

if __name__ == "__main__":
    verify_data_files()
