@echo off
echo 🚀 Lancement du Dashboard Crypto
echo =================================

echo 📂 Dossier actuel: %CD%

REM Vérifier l'existence de l'environnement virtuel
if exist "venv\Scripts\activate.bat" (
    echo ✅ Environnement virtuel trouvé
    
    REM Activer l'environnement virtuel
    echo 🔧 Activation de l'environnement virtuel...
    call venv\Scripts\activate.bat
    
    REM Vérifier Python et Streamlit
    echo 🐍 Vérification de Python...
    python --version
    
    echo 📊 Vérification de Streamlit...
    python -c "import streamlit as st; print(f'Streamlit version: {st.__version__}')"
    
    REM Vérifier les données
    echo 📁 Vérification des données...
    if exist "RESOURCES\data\processed\market_data.json" (
        echo ✅ market_data.json trouvé
    ) else (
        echo ❌ market_data.json manquant
    )
    
    if exist "RESOURCES\data\processed\top_traders_extended.json" (
        echo ✅ top_traders_extended.json trouvé
    ) else (
        echo ❌ top_traders_extended.json manquant
    )
    
    if exist "RESOURCES\configs\app_config.json" (
        echo ✅ app_config.json trouvé
    ) else (
        echo ❌ app_config.json manquant
    )
    
    REM Lancer le dashboard
    echo 🎯 Lancement du dashboard sur http://localhost:8504
    echo Appuyez sur Ctrl+C pour arrêter le dashboard
    echo =================================
    
    REM Lancer Streamlit
    streamlit run crypto_dashboard.py --server.port 8504
    
) else (
    echo ❌ Environnement virtuel non trouvé dans venv\Scripts\activate.bat
    echo Veuillez créer l'environnement virtuel avec: python -m venv venv
    echo Puis installer les dépendances: pip install -r requirements.txt
    pause
) 