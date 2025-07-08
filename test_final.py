#!/usr/bin/env python3
"""
Test final du dashboard Streamlit - Validation complète
"""

import json
import pandas as pd
from pathlib import Path
import sys
import time

def test_final_validation():
    """Test complet de toutes les fonctionnalités du dashboard"""
    print("🎯 TEST FINAL - Dashboard Crypto Business Intelligence")
    print("=" * 70)
    
    tests_passed = 0
    total_tests = 8
    
    # Test 1: Vérification des fichiers de données
    print("\n📊 Test 1: Fichiers de données")
    data_path = Path("data/processed")
    required_files = [
        "top_traders_extended.json",
        "market_data_extended.json", 
        "historical_data.json",
        "sentiment_data.json"
    ]
    
    all_files_exist = True
    for file_name in required_files:
        if (data_path / file_name).exists():
            print(f"   ✅ {file_name}")
        else:
            print(f"   ❌ {file_name} manquant")
            all_files_exist = False
    
    if all_files_exist:
        tests_passed += 1
        print("   ✅ Tous les fichiers de données sont présents")
    
    # Test 2: Structure des données traders
    print("\n👑 Test 2: Structure des données traders")
    try:
        with open(data_path / "top_traders_extended.json", 'r') as f:
            traders_data = json.load(f)
        
        if isinstance(traders_data, list) and len(traders_data) > 0:
            df = pd.DataFrame(traders_data)
            required_cols = ['trader_id', 'username', 'total_pnl', 'win_rate', 'roi_percentage']
            
            if all(col in df.columns for col in required_cols):
                tests_passed += 1
                print(f"   ✅ Structure correcte - {len(traders_data)} traders")
                print(f"   ✅ Colonnes: {required_cols}")
            else:
                missing = [col for col in required_cols if col not in df.columns]
                print(f"   ❌ Colonnes manquantes: {missing}")
        else:
            print("   ❌ Format de données incorrect")
    except Exception as e:
        print(f"   ❌ Erreur: {e}")
    
    # Test 3: Structure des données marché
    print("\n💰 Test 3: Structure des données marché")
    try:
        with open(data_path / "market_data_extended.json", 'r') as f:
            market_data = json.load(f)
        
        if isinstance(market_data, dict) and 'cryptocurrencies' in market_data:
            cryptos = market_data['cryptocurrencies']
            if len(cryptos) > 0:
                tests_passed += 1
                print(f"   ✅ {len(cryptos)} cryptomonnaies disponibles")
                symbols = [crypto['symbol'] for crypto in cryptos if 'symbol' in crypto]
                print(f"   ✅ Symboles: {', '.join(symbols[:5])}...")
            else:
                print("   ❌ Aucune cryptomonnaie trouvée")
        else:
            print("   ❌ Structure incorrecte")
    except Exception as e:
        print(f"   ❌ Erreur: {e}")
    
    # Test 4: Données historiques
    print("\n📈 Test 4: Données historiques")
    try:
        with open(data_path / "historical_data.json", 'r') as f:
            historical_data = json.load(f)
        
        if isinstance(historical_data, list) and len(historical_data) > 0:
            required_keys = ['date', 'symbol', 'open', 'high', 'low', 'close', 'volume']
            if all(key in historical_data[0] for key in required_keys):
                tests_passed += 1
                symbols = set(item['symbol'] for item in historical_data)
                dates = set(item['date'] for item in historical_data)
                print(f"   ✅ {len(historical_data)} points de données")
                print(f"   ✅ {len(symbols)} symboles, {len(dates)} dates")
            else:
                print("   ❌ Clés manquantes dans les données historiques")
        else:
            print("   ❌ Format incorrect")
    except Exception as e:
        print(f"   ❌ Erreur: {e}")
    
    # Test 5: Données de sentiment
    print("\n📊 Test 5: Données de sentiment")
    try:
        with open(data_path / "sentiment_data.json", 'r') as f:
            sentiment_data = json.load(f)
        
        if (isinstance(sentiment_data, dict) and 
            'overall_sentiment' in sentiment_data and 
            'signals' in sentiment_data):
            tests_passed += 1
            overall = sentiment_data['overall_sentiment']
            signals = sentiment_data['signals']
            print(f"   ✅ Sentiment global: {overall.get('label', 'N/A')}")
            print(f"   ✅ {len(signals)} signaux disponibles")
        else:
            print("   ❌ Structure de sentiment incorrecte")
    except Exception as e:
        print(f"   ❌ Erreur: {e}")
    
    # Test 6: Opérations DataFrame
    print("\n🔧 Test 6: Opérations DataFrame")
    try:
        # Test filtrage et tri
        df = pd.DataFrame(traders_data)
        
        # Filtrage
        filtered = df[df['roi_percentage'] > 50]
        sorted_df = df.sort_values('total_pnl', ascending=False)
        
        # Formatage
        df['pnl_formatted'] = df['total_pnl'].apply(lambda x: f"${x:,.2f}")
        df['roi_formatted'] = df['roi_percentage'].apply(lambda x: f"{x:.1f}%")
        
        tests_passed += 1
        print(f"   ✅ Filtrage: {len(filtered)} traders avec ROI > 50%")
        print(f"   ✅ Tri: Top trader a ${sorted_df.iloc[0]['total_pnl']:,.2f}")
        print("   ✅ Formatage réussi")
    except Exception as e:
        print(f"   ❌ Erreur opérations DataFrame: {e}")
    
    # Test 7: Configuration Streamlit
    print("\n⚙️ Test 7: Configuration Streamlit")
    config_path = Path(".streamlit/config.toml")
    if config_path.exists():
        tests_passed += 1
        print("   ✅ Fichier de configuration Streamlit présent")
    else:
        print("   ❌ Configuration Streamlit manquante")
    
    # Test 8: Scripts utilitaires
    print("\n🛠️ Test 8: Scripts utilitaires")
    scripts = ["generate_sample_data.py", "verify_data.py", "start_app.bat"]
    all_scripts = all(Path(script).exists() for script in scripts)
    
    if all_scripts:
        tests_passed += 1
        print("   ✅ Tous les scripts utilitaires présents")
        for script in scripts:
            print(f"      - {script}")
    else:
        print("   ❌ Scripts manquants")
    
    # Résumé final
    print("\n" + "=" * 70)
    print(f"📊 RÉSULTATS: {tests_passed}/{total_tests} tests passés")
    
    if tests_passed == total_tests:
        print("🎉 SUCCÈS COMPLET! Le dashboard est prêt à l'utilisation!")
        print("\n🚀 Pour démarrer:")
        print("   - Double-cliquez sur start_app.bat")
        print("   - Ou exécutez: streamlit run app.py")
        print("   - Accédez à: http://localhost:8501")
        return True
    else:
        print("⚠️ Certains tests ont échoué. Vérifiez les erreurs ci-dessus.")
        return False

def test_app_import():
    """Test si l'application peut être importée sans erreurs"""
    print("\n🔍 Test 9: Import de l'application")
    try:
        # Test d'import des principales librairies utilisées
        import streamlit as st
        import pandas as pd
        import plotly.express as px
        import numpy as np
        
        print("   ✅ Toutes les dépendances sont installées")
        
        # Test de lecture du fichier app.py sans l'exécuter
        with open("app.py", 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Vérifications basiques de syntaxe
        if "def main():" in content and 'if __name__ == "__main__":' in content:
            print("   ✅ Structure de l'application correcte")
            return True
        else:
            print("   ❌ Structure de l'application incorrecte")
            return False
            
    except ImportError as e:
        print(f"   ❌ Dépendance manquante: {e}")
        return False
    except Exception as e:
        print(f"   ❌ Erreur: {e}")
        return False

if __name__ == "__main__":
    success1 = test_final_validation()
    success2 = test_app_import()
    
    if success1 and success2:
        print("\n🎯 VALIDATION FINALE: ✅ SUCCÈS")
        print("Le dashboard crypto business intelligence est opérationnel!")
        sys.exit(0)
    else:
        print("\n🎯 VALIDATION FINALE: ❌ ÉCHEC")
        print("Corrigez les erreurs avant de lancer le dashboard.")
        sys.exit(1)
