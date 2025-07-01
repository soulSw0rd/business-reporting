#!/usr/bin/env python3
"""
CryptoTracker - Script de démarrage
Démarre l'application Flask avec la configuration optimale
"""

import os
import sys
import subprocess
from pathlib import Path

def check_requirements():
    """Vérifie que les dépendances sont installées"""
    try:
        import flask
        import sqlalchemy
        import requests
        print("✅ Dépendances vérifiées")
        return True
    except ImportError as e:
        print(f"❌ Dépendance manquante: {e}")
        print("💡 Exécutez: pip install -r requirements.txt")
        return False

def start_flask_app():
    """Démarre l'application Flask"""
    app_path = Path("crypto_tracker/flask_app/app.py")
    
    if not app_path.exists():
        print("❌ Fichier app.py introuvable")
        return False
    
    print("🚀 Démarrage de CryptoTracker...")
    print("📍 Interface Web: http://localhost:5000")
    print("🔧 Mode: Développement")
    print("⏹️  Arrêt: Ctrl+C")
    print("-" * 50)
    
    try:
        # Changer vers le répertoire de l'app
        os.chdir("crypto_tracker/flask_app")
        
        # Démarrer Flask
        subprocess.run([sys.executable, "app.py"], check=True)
        
    except KeyboardInterrupt:
        print("\n🛑 Application arrêtée par l'utilisateur")
    except subprocess.CalledProcessError as e:
        print(f"❌ Erreur lors du démarrage: {e}")
        return False
    
    return True

def main():
    """Fonction principale"""
    print("🎯 CryptoTracker - Plateforme Fintech")
    print("=" * 50)
    
    # Vérifier les dépendances
    if not check_requirements():
        sys.exit(1)
    
    # Démarrer l'application
    if not start_flask_app():
        sys.exit(1)

if __name__ == "__main__":
    main() 