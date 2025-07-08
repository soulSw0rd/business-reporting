#!/usr/bin/env python3
"""
Test spécifique pour vérifier le chargement des données traders
"""

import json
import pandas as pd
from pathlib import Path

def test_traders_data_loading():
    """Test le chargement spécifique des données traders"""
    
    print("🔍 Test de chargement des données traders")
    print("=" * 50)
    
    # Simuler la logique de get_scraped_data()
    data_path = Path("data/processed")
    scraped_data = {}
    
    if data_path.exists():
        for json_file in data_path.glob("*.json"):
            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    scraped_data[json_file.stem] = data
                    print(f"✅ Chargé: {json_file.stem}")
            except Exception as e:
                print(f"❌ Erreur: {json_file}: {e}")
    
    print(f"\n📊 Fichiers chargés: {list(scraped_data.keys())}")
    
    # Simuler la logique de show_top_traders() mise à jour
    traders_df = None
    
    if scraped_data:
        # Priorité au fichier top_traders_extended
        if 'top_traders_extended' in scraped_data:
            data = scraped_data['top_traders_extended']
            if isinstance(data, list):
                print(f"\n🎯 Fichier prioritaire trouvé: top_traders_extended")
                print(f"   Type: {type(data)}")
                print(f"   Nombre d'entrées: {len(data)}")
                
                if len(data) > 0:
                    print(f"   Premier élément clés: {list(data[0].keys())}")
                    
                    traders_df = pd.DataFrame(data)
                    print(f"   DataFrame colonnes: {list(traders_df.columns)}")
                    print(f"   DataFrame shape: {traders_df.shape}")
        
        # Sinon, chercher d'autres fichiers traders
        if traders_df is None:
            for filename, data in scraped_data.items():
                if 'trader' in filename.lower() and isinstance(data, list) and 'extended' in filename:
                    print(f"\n🎯 Fichier alternatif trouvé: {filename}")
                    traders_df = pd.DataFrame(data)
                    break
    
    if traders_df is not None:
        # Vérifier les colonnes nécessaires
        required_columns = ['roi_percentage', 'total_trades', 'win_rate', 'total_pnl', 'username']
        missing_columns = [col for col in required_columns if col not in traders_df.columns]
        
        if missing_columns:
            print(f"\n❌ Colonnes manquantes: {missing_columns}")
            print(f"   Colonnes disponibles: {list(traders_df.columns)}")
            return False
        else:
            print(f"\n✅ Toutes les colonnes requises sont présentes!")
            print(f"   Colonnes validées: {required_columns}")
            
            # Test quelques opérations
            print(f"\n🧪 Test des opérations:")
            print(f"   Traders avec ROI > 100%: {len(traders_df[traders_df['roi_percentage'] > 100])}")
            print(f"   Win rate moyen: {traders_df['win_rate'].mean():.3f}")
            print(f"   PnL total max: ${traders_df['total_pnl'].max():,.2f}")
            
            return True
    else:
        print("\n❌ Aucun fichier trader trouvé ou chargé")
        return False

if __name__ == "__main__":
    success = test_traders_data_loading()
    
    if success:
        print("\n🎉 SUCCESS: Les données traders sont correctement chargées!")
    else:
        print("\n💥 FAILURE: Problème avec le chargement des données traders")
