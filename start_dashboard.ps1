# Script PowerShell pour lancer le dashboard crypto avec environnement virtuel
# Auteur: Crypto-Tracker Team
# Date: 2025-01-08

Write-Host "🚀 Lancement du Dashboard Crypto" -ForegroundColor Green
Write-Host "=================================" -ForegroundColor Green

# Vérifier si on est dans le bon dossier
$currentPath = Get-Location
Write-Host "📂 Dossier actuel: $currentPath" -ForegroundColor Yellow

# Vérifier l'existence de l'environnement virtuel
if (Test-Path "venv\Scripts\activate.ps1") {
    Write-Host "✅ Environnement virtuel trouvé" -ForegroundColor Green
    
    # Activer l'environnement virtuel
    Write-Host "🔧 Activation de l'environnement virtuel..." -ForegroundColor Yellow
    & "venv\Scripts\activate.ps1"
    
    # Vérifier Python et Streamlit
    Write-Host "🐍 Vérification de Python..." -ForegroundColor Yellow
    python --version
    
    Write-Host "📊 Vérification de Streamlit..." -ForegroundColor Yellow
    python -c "import streamlit as st; print(f'Streamlit version: {st.__version__}')"
    
    # Vérifier les données
    Write-Host "📁 Vérification des données..." -ForegroundColor Yellow
    if (Test-Path "RESOURCES\data\processed\market_data.json") {
        Write-Host "✅ market_data.json trouvé" -ForegroundColor Green
    } else {
        Write-Host "❌ market_data.json manquant" -ForegroundColor Red
    }
    
    if (Test-Path "RESOURCES\data\processed\top_traders_extended.json") {
        Write-Host "✅ top_traders_extended.json trouvé" -ForegroundColor Green
    } else {
        Write-Host "❌ top_traders_extended.json manquant" -ForegroundColor Red
    }
    
    if (Test-Path "RESOURCES\configs\app_config.json") {
        Write-Host "✅ app_config.json trouvé" -ForegroundColor Green
    } else {
        Write-Host "❌ app_config.json manquant" -ForegroundColor Red
    }
    
    # Lancer le dashboard
    Write-Host "🎯 Lancement du dashboard sur http://localhost:8504" -ForegroundColor Green
    Write-Host "Appuyez sur Ctrl+C pour arrêter le dashboard" -ForegroundColor Yellow
    Write-Host "=================================" -ForegroundColor Green
    
    # Lancer Streamlit
    streamlit run crypto_dashboard.py --server.port 8504
    
} else {
    Write-Host "❌ Environnement virtuel non trouvé dans venv\Scripts\activate.ps1" -ForegroundColor Red
    Write-Host "Veuillez créer l'environnement virtuel avec: python -m venv venv" -ForegroundColor Yellow
    Write-Host "Puis installer les dépendances: pip install -r requirements.txt" -ForegroundColor Yellow
} 