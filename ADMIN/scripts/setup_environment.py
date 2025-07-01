#!/usr/bin/env python3
"""
Script de configuration pour CryptoTracker avec API Zerion
Crée le fichier .env avec la configuration nécessaire
"""

import os

def create_env_file():
    """Crée le fichier .env avec la configuration par défaut"""
    
    env_content = """# CryptoTracker - Configuration Environment
# Configuration pour l'intégration API Zerion

# === APPLICATION ===
APP_NAME=CryptoTracker
DEBUG=True
HOST=0.0.0.0
PORT=5000
SECRET_KEY=your-secret-key-change-in-production

# === BASE DE DONNÉES ===
DATABASE_URL=sqlite:///crypto_tracker.db
# Pour PostgreSQL : postgresql://user:password@localhost:5432/crypto_tracker

# === REDIS ===
REDIS_URL=redis://localhost:6379/0

# === APIs CRYPTO ===
# CoinGecko (gratuit)
COINGECKO_API_KEY=your_coingecko_api_key_here

# CoinMarketCap
COINMARKETCAP_API_KEY=your_coinmarketcap_api_key_here

# Binance (optionnel)
BINANCE_API_KEY=your_binance_api_key_here
BINANCE_SECRET_KEY=your_binance_secret_key_here

# === API ZERION ===
# Obtenez votre clé sur https://developers.zerion.io
# IMPORTANT : Cette clé est nécessaire pour l'analyse DeFi
ZERION_API_KEY=your_zerion_api_key_here

# === BLOCKCHAIN RPC URLs ===
ETHEREUM_RPC_URL=https://mainnet.infura.io/v3/YOUR_PROJECT_ID
POLYGON_RPC_URL=https://polygon-mainnet.infura.io/v3/YOUR_PROJECT_ID
BSC_RPC_URL=https://bsc-dataseed.binance.org/

# === LOGGING ===
LOG_LEVEL=INFO

# === FEATURES ===
ENABLE_ML_FEATURES=True
DEMO_MODE=False
"""
    
    # Vérifier si .env existe déjà
    if os.path.exists('.env'):
        response = input("Le fichier .env existe déjà. Voulez-vous le remplacer ? (y/N): ")
        if response.lower() not in ['y', 'yes', 'oui']:
            print("❌ Configuration annulée.")
            return False
    
    # Créer le fichier .env
    try:
        with open('.env', 'w', encoding='utf-8') as f:
            f.write(env_content)
        
        print("✅ Fichier .env créé avec succès!")
        print("\n📋 Prochaines étapes:")
        print("1. Éditez le fichier .env avec vos clés API")
        print("2. Obtenez votre clé Zerion sur: https://developers.zerion.io")
        print("3. Remplacez 'your_zerion_api_key_here' par votre vraie clé")
        print("4. Testez avec: python test_zerion_integration.py")
        print("5. Lancez l'app avec: python start.py")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur lors de la création du fichier .env: {e}")
        return False

def check_zerion_config():
    """Vérifie la configuration Zerion"""
    if not os.path.exists('.env'):
        print("❌ Fichier .env non trouvé")
        return False
    
    try:
        from dotenv import load_dotenv
        load_dotenv()
        
        zerion_key = os.getenv('ZERION_API_KEY')
        
        if not zerion_key or zerion_key == 'your_zerion_api_key_here':
            print("❌ Clé API Zerion non configurée")
            print("💡 Éditez .env et ajoutez votre clé Zerion")
            return False
        
        print("✅ Configuration Zerion détectée")
        print(f"🔑 Clé API: {zerion_key[:8]}...{zerion_key[-4:] if len(zerion_key) > 12 else '***'}")
        return True
        
    except ImportError:
        print("❌ Module python-dotenv non installé")
        print("💡 Installez avec: pip install python-dotenv")
        return False
    except Exception as e:
        print(f"❌ Erreur vérification config: {e}")
        return False

def main():
    """Fonction principale"""
    print("🚀 Configuration CryptoTracker avec API Zerion")
    print("=" * 50)
    
    # Vérifier si .env existe et est configuré
    if os.path.exists('.env'):
        print("📁 Fichier .env trouvé")
        if check_zerion_config():
            print("\n🎯 Configuration complète!")
            print("Vous pouvez maintenant tester avec: python test_zerion_integration.py")
            return
        else:
            print("\n⚠️  Configuration incomplète")
    
    # Créer ou reconfigurer .env
    print("\n📝 Création du fichier de configuration...")
    if create_env_file():
        print("\n🎯 Configuration créée!")
        print("\n🔧 Étapes suivantes:")
        print("1. Obtenez une clé API Zerion:")
        print("   • Visitez: https://developers.zerion.io")
        print("   • Créez un compte développeur")
        print("   • Générez votre clé API")
        print("2. Éditez .env et remplacez 'your_zerion_api_key_here'")
        print("3. Testez avec: python test_zerion_integration.py")

if __name__ == "__main__":
    main() 