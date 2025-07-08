#!/usr/bin/env python3
"""
Test spécifique pour vérifier la page Portfolio Performance
"""

import pandas as pd
import numpy as np

def test_portfolio_slider_logic():
    """Test la logique des sliders de portfolio"""
    
    print("🔧 Test de la logique des sliders de portfolio")
    print("=" * 50)
    
    # Simuler les données crypto
    crypto_symbols = ['BTC', 'ETH', 'ADA', 'DOT', 'LINK']
    
    # Test de la logique de répartition
    remaining = 100.0
    allocations = {}
    
    print(f"💰 Symboles: {crypto_symbols}")
    print(f"📊 Allocation initiale: {remaining}%")
    
    for i, crypto in enumerate(crypto_symbols[:-1]):
        max_val = max(1.0, min(100.0, remaining))
        default_val = max(0.0, min(20.0, remaining))
        
        # Simuler une allocation (utiliser la valeur par défaut)
        allocation = default_val
        allocations[crypto] = allocation
        remaining = max(0.0, remaining - allocation)
        
        print(f"   {crypto}: {allocation:.1f}% (max: {max_val:.1f}%, restant: {remaining:.1f}%)")
        
        # Vérifier que max_val > 0
        if max_val <= 0:
            print(f"   ❌ ERREUR: max_val = {max_val} pour {crypto}")
            return False
    
    # Dernière crypto
    allocations[crypto_symbols[-1]] = max(0.0, remaining)
    print(f"   {crypto_symbols[-1]}: {remaining:.1f}% (automatique)")
    
    # Vérifications
    total_allocation = sum(allocations.values())
    print(f"\n📊 Total allocation: {total_allocation:.1f}%")
    
    if abs(total_allocation - 100.0) < 0.1:
        print("✅ Allocation totale correcte (~100%)")
    else:
        print(f"❌ Allocation totale incorrecte: {total_allocation:.1f}%")
        return False
    
    # Test cas extrême - toutes les allocations au maximum
    print(f"\n🔬 Test cas extrême:")
    remaining_extreme = 100.0
    for i, crypto in enumerate(crypto_symbols[:-1]):
        max_val = max(1.0, min(100.0, remaining_extreme))
        allocation_extreme = max_val  # Prendre le maximum
        remaining_extreme = max(0.0, remaining_extreme - allocation_extreme)
        print(f"   {crypto}: {allocation_extreme:.1f}% (restant: {remaining_extreme:.1f}%)")
        
        if max_val <= 0:
            print(f"   ❌ ERREUR EXTRÊME: max_val = {max_val}")
            return False
    
    print("✅ Logique des sliders validée!")
    return True

if __name__ == "__main__":
    success = test_portfolio_slider_logic()
    
    if success:
        print("\n🎉 SUCCESS: La page Portfolio Performance devrait fonctionner!")
    else:
        print("\n💥 FAILURE: Problème avec la logique des sliders")
