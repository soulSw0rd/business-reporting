#!/usr/bin/env python3
"""
Crypto Dashboard Application - Version Dossier Principal
Interface utilisateur Streamlit pour le système de prédiction crypto
Auteur: Crypto-Tracker Team
Date: 2025-01-08
Version: 1.0.0
"""


import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import json
import logging
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional

# Imports des modules internes avec chemins corrigés
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'PRODUCTION'))

from PRODUCTION.core.config_manager import get_config
from PRODUCTION.core.prediction_engine import CryptoTraderPredictor
from PRODUCTION.dashboard.components.prediction_panel import PredictionPanel
from PRODUCTION.dashboard.components.advanced_visualizations import AdvancedVisualizationComponents

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class CryptoDashboard:
    """
    CryptoDashboard - Interface utilisateur principale du système crypto-tracker
    
    RESPONSABILITÉ : Affichage des prédictions et métriques crypto
    UTILISATION : Application Streamlit pour utilisateurs finaux
    
    FONCTIONNALITÉS :
    - Interface multi-pages (Vue d'ensemble, Traders, Prédictions, etc.)
    - Visualisations interactives avec Plotly
    - Prédictions ML en temps réel
    - Gestion du cache pour performances
    - Configuration centralisée
    """
    
    def __init__(self):
        """
        OBJECTIF : Initialisation du dashboard crypto
        
        LOGIQUE :
        1. Configuration de la page Streamlit
        2. Initialisation des composants métier
        3. Chargement de la configuration
        4. Setup des composants UI
        """
        # Configuration
        self.config = get_config()
        self.dashboard_config = get_config("dashboard")
        
        # Composants métier
        self.predictor = CryptoTraderPredictor()
        
        # Composants UI
        self.prediction_panel = PredictionPanel()
        self.advanced_viz = AdvancedVisualizationComponents()
        
        # Configuration Streamlit
        self._setup_page_configuration()
        
        # Cache TTL depuis configuration
        self.cache_ttl = self.dashboard_config.get("cache_ttl", 600)
        
        logger.info("CryptoDashboard initialisé depuis le dossier principal")
    
    def _setup_page_configuration(self) -> None:
        """
        OBJECTIF : Configuration de la page Streamlit
        
        LOGIQUE :
        1. Configuration du titre et icône
        2. Layout wide pour plus d'espace
        3. Sidebar étendue par défaut
        4. CSS personnalisé si nécessaire
        """
        st.set_page_config(
            page_title=self.dashboard_config.get("title", "Crypto Dashboard"),
            page_icon="₿",
            layout="wide",
            initial_sidebar_state="expanded"
        )
        
        # CSS personnalisé pour améliorer l'apparence
        st.markdown("""
        <style>
        .main > div {
            padding-top: 2rem;
        }
        .stMetric {
            background-color: #f0f2f6;
            padding: 1rem;
            border-radius: 0.5rem;
            border: 1px solid #e0e0e0;
        }
        .prediction-success {
            background-color: #d4edda;
            border: 1px solid #c3e6cb;
            padding: 1rem;
            border-radius: 0.5rem;
            margin: 1rem 0;
        }
        .prediction-warning {
            background-color: #fff3cd;
            border: 1px solid #ffeaa7;
            padding: 1rem;
            border-radius: 0.5rem;
            margin: 1rem 0;
        }
        .prediction-danger {
            background-color: #f8d7da;
            border: 1px solid #f5c6cb;
            padding: 1rem;
            border-radius: 0.5rem;
            margin: 1rem 0;
        }
        </style>
        """, unsafe_allow_html=True)
    
    @st.cache_data(ttl=600)
    def load_scraped_data(_self) -> Dict[str, Any]:
        """
        OBJECTIF : Chargement des données scrapées depuis les fichiers JSON
        
        RETOURNE :
        - dict : Données organisées par type (traders, market, sentiment)
        
        LOGIQUE :
        1. Chargement depuis RESOURCES/data/processed/
        2. Séparation données analyse vs prédiction
        3. Gestion des erreurs et fichiers manquants
        4. Cache Streamlit pour performances
        """
        data_paths = get_config("data")
        # Chemin depuis le dossier principal
        processed_path = Path(data_paths["processed_path"])
        
        scraped_data = {
            'traders_for_analysis': [],
            'traders_for_prediction': [],
            'market_data': {},
            'sentiment_data': {},
            'historical_data': []
        }
        
        if not processed_path.exists():
            logger.warning(f"Dossier de données non trouvé: {processed_path}")
            st.sidebar.error(f"Dossier non trouvé: {processed_path}")
            return scraped_data
        
        st.sidebar.info(f"📂 Chargement depuis: {processed_path}")
        
        try:
            # === CHARGEMENT DONNÉES MARCHÉ ===
            # Charger le fichier market_data.json principal
            market_file = processed_path / "market_data.json"
            if market_file.exists():
                with open(market_file, 'r', encoding='utf-8') as f:
                    scraped_data['market_data'] = json.load(f)
                    st.sidebar.success("✅ market_data.json chargé")
            else:
                st.sidebar.warning("⚠️ market_data.json manquant")
            
            # Charger aussi les autres fichiers de marché s'ils existent
            market_files = [
                "market_data_extended.json",
                "market_data_coingecko_btc_*.json",
                "market_data_fear_greed_*.json",
                "market_data_funding_rates_*.json"
            ]
            
            for pattern in market_files:
                if "*" in pattern:
                    files = list(processed_path.glob(pattern))
                    if files:
                        latest_file = max(files, key=lambda x: x.stat().st_mtime)
                        with open(latest_file, 'r', encoding='utf-8') as f:
                            key = pattern.replace("_*.json", "").replace(".json", "")
                            scraped_data[key] = json.load(f)
                else:
                    file_path = processed_path / pattern
                    if file_path.exists():
                        with open(file_path, 'r', encoding='utf-8') as f:
                            key = pattern.replace(".json", "")
                            scraped_data[key] = json.load(f)
            
            # === CHARGEMENT DONNÉES TRADERS ===
            # Données pour analyse (avec username, roi_percentage)
            extended_file = processed_path / "top_traders_extended.json"
            if extended_file.exists():
                with open(extended_file, 'r', encoding='utf-8') as f:
                    scraped_data['traders_for_analysis'] = json.load(f)
                    st.sidebar.success(f"✅ {len(scraped_data['traders_for_analysis'])} traders chargés")
            else:
                st.sidebar.warning("⚠️ top_traders_extended.json manquant")
            
            # Données pour prédiction (avec address, pnl_7d, pnl_30d)
            prediction_file = processed_path / "top_traders_for_prediction.json"
            if prediction_file.exists():
                with open(prediction_file, 'r', encoding='utf-8') as f:
                    scraped_data['traders_for_prediction'] = json.load(f)
            
            # === CHARGEMENT AUTRES DONNÉES ===
            # Données de sentiment
            sentiment_file = processed_path / "sentiment_data.json"
            if sentiment_file.exists():
                with open(sentiment_file, 'r', encoding='utf-8') as f:
                    scraped_data['sentiment_data'] = json.load(f)
                    st.sidebar.success(f"✅ {len(scraped_data['sentiment_data'])} signaux sentiment")
            else:
                st.sidebar.warning("⚠️ sentiment_data.json manquant")
            
            # Données historiques
            historical_file = processed_path / "historical_data.json"
            if historical_file.exists():
                with open(historical_file, 'r', encoding='utf-8') as f:
                    scraped_data['historical_data'] = json.load(f)
                    st.sidebar.success(f"✅ Données historiques chargées")
            
            # Données de prédictions
            predictions_file = processed_path / "predictions_summary.json"
            if predictions_file.exists():
                with open(predictions_file, 'r', encoding='utf-8') as f:
                    predictions_data = json.load(f)
                    scraped_data['predictions_summary'] = predictions_data
                    st.sidebar.success(f"✅ {len(predictions_data)} prédictions chargées")
            
            logger.info("Données scrapées chargées avec succès")
            
        except Exception as e:
            logger.error(f"Erreur lors du chargement des données: {e}")
            st.sidebar.error(f"Erreur chargement: {str(e)}")
        
        return scraped_data
    
    def run(self) -> None:
        """
        OBJECTIF : Point d'entrée principal de l'application
        
        LOGIQUE :
        1. Affichage du titre principal
        2. Configuration de la sidebar
        3. Routage vers la page sélectionnée
        4. Gestion des erreurs globales
        """
        try:
            # Titre principal
            st.title(self.dashboard_config.get("title", "₿ CryptoTrader Dashboard"))
            st.markdown("---")
            
            # Configuration de la sidebar
            self._setup_sidebar()
            
            # Chargement des données
            scraped_data = self.load_scraped_data()
            
            # Routage des pages
            page = st.session_state.get('current_page', '🏠 Vue d\'ensemble')
            self._route_to_page(page, scraped_data)
            
        except Exception as e:
            logger.error(f"Erreur dans l'application principale: {e}")
            st.error(f"Une erreur est survenue: {str(e)}")
            
            if get_config("app", "debug"):
                st.exception(e)
    
    def _setup_sidebar(self) -> None:
        """
        OBJECTIF : Configuration de la barre latérale de navigation
        
        LOGIQUE :
        1. Titre de navigation
        2. Bouton de rafraîchissement
        3. Sélecteur de pages
        4. Informations système
        """
        st.sidebar.title("🚀 Navigation")
        
        # Bouton de rafraîchissement
        if st.sidebar.button("🔄 Rafraîchir les données"):
            st.cache_data.clear()
            st.rerun()
        
        # Sélection de page
        pages = [
            "🏠 Vue d'ensemble",
            "🔮 Prédictions ML",
            "📊 Analyse Crypto",
            "📈 Sentiment Marché",
            "⚙️ Données & Config"
        ]
        
        selected_page = st.sidebar.selectbox(
            "Choisir une page",
            pages,
            key="page_selector"
        )
        
        st.session_state['current_page'] = selected_page
        
        # Informations système
        st.sidebar.markdown("---")
        st.sidebar.subheader("ℹ️ Informations")
        
        app_config = get_config("app")
        st.sidebar.info(f"""
        **Version:** {app_config.get('version', '1.0.0')}
        **Environnement:** {app_config.get('environment', 'production')}
        **Cache TTL:** {self.cache_ttl}s
        **Dossier:** Principal + venv
        """)
        
        # Statut du prédicteur ML
        if self.predictor.is_trained:
            st.sidebar.success("🤖 Modèle ML: Entraîné")
        else:
            st.sidebar.warning("🤖 Modèle ML: Non entraîné")
    
    def _route_to_page(self, page: str, scraped_data: Dict[str, Any]) -> None:
        """
        OBJECTIF : Routage vers la page sélectionnée
        
        PARAMÈTRES :
        - page (str) : Page sélectionnée
        - scraped_data (dict) : Données chargées
        
        LOGIQUE :
        1. Correspondance page -> méthode
        2. Appel de la méthode appropriée
        3. Gestion des pages non trouvées
        """
        page_methods = {
            "🏠 Vue d'ensemble": self.show_overview,
            "🔮 Prédictions ML": self.show_predictions,
            "📊 Analyse Crypto": self.show_crypto_analysis,
            "📈 Sentiment Marché": self.show_sentiment_analysis,
            "⚙️ Données & Config": self.show_data_status
        }
        
        method = page_methods.get(page)
        if method:
            method(scraped_data)
        else:
            st.error(f"Page non trouvée: {page}")
    
    def show_overview(self, scraped_data: Dict[str, Any]) -> None:
        """
        OBJECTIF : Page d'accueil avec vue d'ensemble du système
        
        PARAMÈTRES :
        - scraped_data (dict) : Données du système
        """
        st.header("🏠 Vue d'ensemble du Système")
        
        # === MÉTRIQUES PRINCIPALES ===
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            traders_count = len(scraped_data.get('traders_for_analysis', []))
            st.metric("👑 Traders Analysés", f"{traders_count:,}")
        
        with col2:
            market_data = scraped_data.get('market_data', {})
            cryptos_count = len(market_data.get('cryptocurrencies', []))
            st.metric("💰 Cryptomonnaies", f"{cryptos_count:,}")
        
        with col3:
            sentiment_count = len(scraped_data.get('sentiment_data', []))
            st.metric("📊 Signaux Sentiment", f"{sentiment_count:,}")
        
        with col4:
            predictions_count = len(scraped_data.get('predictions_summary', []))
            st.metric("🔮 Prédictions ML", f"{predictions_count:,}")
        
        # === GRAPHIQUES PRINCIPAUX ===
        col1, col2 = st.columns(2)
        
        with col1:
            traders_data = scraped_data.get('traders_for_analysis', [])
            if traders_data:
                self._show_top_traders_overview(traders_data)
        
        with col2:
            market_data = scraped_data.get('market_data', {})
            if market_data:
                self._show_market_overview(market_data)
        
        # === STATUT DU SYSTÈME ===
        st.subheader("🔧 Statut du Système")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if self.predictor.is_trained:
                st.success("🤖 Modèle ML: Entraîné")
            else:
                st.warning("🤖 Modèle ML: Non entraîné")
        
        with col2:
            if scraped_data.get('traders_for_analysis') or scraped_data.get('market_data'):
                st.success("📊 Données: Disponibles")
            else:
                st.error("📊 Données: Manquantes")
        
        with col3:
            current_time = datetime.now().strftime("%H:%M")
            st.info(f"📅 Dernière MAJ: {current_time}")
    
    def _show_top_traders_overview(self, traders_data: List[Dict]) -> None:
        """
        OBJECTIF : Graphique des top traders pour la vue d'ensemble
        
        PARAMÈTRES :
        - traders_data (list) : Liste des traders
        """
        st.subheader("💰 Top 10 Traders par Performance")
        
        if not traders_data:
            st.warning("Aucune donnée de trader disponible")
            return
        
        try:
            df = pd.DataFrame(traders_data)
            
            # Vérification des colonnes nécessaires
            if 'total_pnl' in df.columns and 'username' in df.columns:
                # Tri par PnL et sélection du top 10
                top_traders = df.nlargest(10, 'total_pnl')
                
                # Création du graphique
                fig = px.bar(
                    top_traders,
                    x='username',
                    y='total_pnl',
                    title="PnL Total des Top 10 Traders",
                    color='total_pnl',
                    color_continuous_scale='RdYlGn',
                    labels={'total_pnl': 'PnL Total ($)', 'username': 'Trader'},
                    hover_data=['total_pnl']
                )
                
                # Amélioration de la présentation
                fig.update_layout(
                    height=400,
                    xaxis_tickangle=-45,
                    xaxis_title="Traders",
                    yaxis_title="PnL Total ($)",
                    showlegend=False
                )
                
                # Formatage de l'axe Y
                fig.update_yaxes(tickformat='$,.0f')
                
                st.plotly_chart(fig, use_container_width=True)
                
                # Affichage des statistiques
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Meilleur PnL", f"${top_traders['total_pnl'].max():,.0f}")
                with col2:
                    st.metric("PnL Moyen Top 10", f"${top_traders['total_pnl'].mean():,.0f}")
                with col3:
                    st.metric("Écart-type", f"${top_traders['total_pnl'].std():,.0f}")
                    
            else:
                st.error("Colonnes 'total_pnl' ou 'username' manquantes dans les données")
                st.info("Colonnes disponibles: " + ", ".join(df.columns.tolist()))
                
        except Exception as e:
            st.error(f"Erreur lors de l'affichage des traders: {str(e)}")
            st.info("Vérifiez la structure des données dans la page 'Données & Config'")
    
    def _show_market_overview(self, market_data: Dict) -> None:
        """
        OBJECTIF : Graphique du marché en vue d'ensemble
        
        PARAMÈTRES :
        - market_data (dict) : Données de marché
        """
        st.subheader("📊 Aperçu du Marché Crypto")
        
        cryptos = market_data.get('cryptocurrencies', [])
        if not cryptos:
            st.warning("Aucune donnée de marché disponible")
            return
        
        try:
            df = pd.DataFrame(cryptos)
            
            # Vérification et nettoyage des données
            if 'symbol' in df.columns and 'price' in df.columns:
                # Conversion en numérique
                df['price'] = pd.to_numeric(df['price'], errors='coerce')
                df = df.dropna(subset=['price', 'symbol'])
                
                if len(df) == 0:
                    st.warning("Aucune donnée de prix valide")
                    return
                
                # Limiter à 10 cryptos pour la lisibilité
                df_display = df.head(10).copy()
                
                # Création du graphique
                fig = px.bar(
                    df_display,
                    x='symbol',
                    y='price',
                    title="Prix des Principales Cryptomonnaies",
                    color='price',
                    color_continuous_scale='Blues',
                    labels={'price': 'Prix ($)', 'symbol': 'Crypto'},
                    hover_data=['price']
                )
                
                # Amélioration de la présentation
                fig.update_layout(
                    height=400,
                    xaxis_title="Cryptomonnaies",
                    yaxis_title="Prix ($)",
                    showlegend=False
                )
                
                # Formatage de l'axe Y avec gestion des grandes valeurs
                if df_display['price'].max() > 1000:
                    fig.update_yaxes(tickformat='$,.0f')
                else:
                    fig.update_yaxes(tickformat='$,.2f')
                
                st.plotly_chart(fig, use_container_width=True)
                
                # Statistiques du marché
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Prix Max", f"${df_display['price'].max():,.2f}")
                with col2:
                    st.metric("Prix Moyen", f"${df_display['price'].mean():,.2f}")
                with col3:
                    total_mcap = df.get('market_cap', [0]).sum() if 'market_cap' in df.columns else 0
                    st.metric("Market Cap Total", f"${total_mcap:,.0f}")
                    
            else:
                st.error("Colonnes 'symbol' ou 'price' manquantes dans les données de marché")
                st.info("Colonnes disponibles: " + ", ".join(df.columns.tolist()))
                
        except Exception as e:
            st.error(f"Erreur lors de l'affichage du marché: {str(e)}")
            st.info("Vérifiez la structure des données dans la page 'Données & Config'")
    
    def show_predictions(self, scraped_data: Dict[str, Any]) -> None:
        """
        OBJECTIF : Page de prédictions ML
        
        PARAMÈTRES :
        - scraped_data (dict) : Données du système
        """
        st.header("🔮 Prédictions ML - Analyse Prédictive")
        
        predictions_summary = scraped_data.get('predictions_summary', {})
        
        if not predictions_summary:
            st.warning("Aucune donnée de prédiction disponible")
            return
        
        # Extraire la liste des prédictions depuis l'objet
        predictions_data = predictions_summary.get('predictions', [])
        
        if not predictions_data:
            st.warning("Aucune prédiction trouvée dans les données")
            return
        
        # Métriques de performance depuis le summary ou calculées
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            total_predictions = predictions_summary.get('total_predictions', len(predictions_data))
            st.metric("Total Prédictions", total_predictions)
        
        with col2:
            # Utiliser les données du summary ou calculer
            if 'profit_rate' in predictions_summary:
                profit_rate = predictions_summary['profit_rate']
            else:
                profitable_count = sum(1 for p in predictions_data if isinstance(p, dict) and p.get('is_profitable_7d', False))
                profit_rate = (profitable_count / len(predictions_data) * 100) if predictions_data else 0
            st.metric("Taux de Profit", f"{profit_rate:.1f}%")
        
        with col3:
            # Utiliser les données du summary ou calculer
            if 'average_confidence' in predictions_summary:
                avg_confidence = predictions_summary['average_confidence']
            else:
                confidences = [p.get('confidence', 0) for p in predictions_data if isinstance(p, dict)]
                avg_confidence = np.mean(confidences) if confidences else 0
            st.metric("Confiance Moyenne", f"{avg_confidence:.1f}%")
        
        with col4:
            # Utiliser les données du summary ou calculer
            if 'high_confidence_count' in predictions_summary:
                high_conf_count = predictions_summary['high_confidence_count']
            else:
                high_conf_count = sum(1 for p in predictions_data if isinstance(p, dict) and p.get('confidence', 0) > 80)
            st.metric("Haute Confiance", f"{high_conf_count}")
        
        # Graphiques de performance
        if predictions_data:
            col1, col2 = st.columns(2)
            
            with col1:
                # Graphique de distribution des confiances
                confidences = [p.get('confidence', 0) for p in predictions_data if isinstance(p, dict)]
                if confidences:
                    fig_conf = px.histogram(
                        x=confidences,
                        nbins=20,
                        title="Distribution des Niveaux de Confiance",
                        labels={'x': 'Confiance (%)', 'y': 'Nombre de Prédictions'}
                    )
                    st.plotly_chart(fig_conf, use_container_width=True)
            
            with col2:
                # Graphique des retours attendus
                returns_7d = [p.get('expected_return_7d', 0) for p in predictions_data if isinstance(p, dict)]
                if returns_7d:
                    fig_returns = px.histogram(
                        x=returns_7d,
                        nbins=20,
                        title="Distribution des Retours Attendus (7j)",
                        labels={'x': 'Retour Attendu (%)', 'y': 'Nombre de Prédictions'}
                    )
                    st.plotly_chart(fig_returns, use_container_width=True)
        
        # Tableau des prédictions
        st.subheader("📊 Détail des Prédictions")
        
        # Créer un DataFrame avec gestion des erreurs
        try:
            # Filtrer seulement les dictionnaires valides
            valid_predictions = [p for p in predictions_data if isinstance(p, dict)]
            
            if valid_predictions:
                df = pd.DataFrame(valid_predictions)
                
                # Formatage des colonnes pour l'affichage
                if 'confidence' in df.columns:
                    df['confidence'] = df['confidence'].round(1)
                if 'expected_return_7d' in df.columns:
                    df['expected_return_7d'] = df['expected_return_7d'].round(2)
                if 'expected_return_30d' in df.columns:
                    df['expected_return_30d'] = df['expected_return_30d'].round(2)
                if 'risk_score' in df.columns:
                    df['risk_score'] = df['risk_score'].round(1)
                
                # Affichage avec options de tri
                st.dataframe(
                    df.head(20), 
                    use_container_width=True,
                    column_config={
                        "confidence": st.column_config.NumberColumn("Confiance (%)", format="%.1f"),
                        "expected_return_7d": st.column_config.NumberColumn("Retour 7j (%)", format="%.2f"),
                        "expected_return_30d": st.column_config.NumberColumn("Retour 30j (%)", format="%.2f"),
                        "risk_score": st.column_config.NumberColumn("Score Risque", format="%.1f"),
                        "portfolio_value": st.column_config.NumberColumn("Valeur Portfolio ($)", format="$%.0f")
                    }
                )
                
                # Filtres interactifs
                st.subheader("🔍 Filtres")
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    min_confidence = st.slider("Confiance minimum (%)", 0, 100, 70)
                    filtered_df = df[df['confidence'] >= min_confidence]
                
                with col2:
                    profitable_only = st.checkbox("Seulement les prédictions profitables (7j)")
                    if profitable_only:
                        filtered_df = filtered_df[filtered_df['is_profitable_7d'] == True]
                
                with col3:
                    st.metric("Prédictions filtrées", len(filtered_df))
                
                if len(filtered_df) > 0:
                    st.dataframe(filtered_df, use_container_width=True)
                else:
                    st.info("Aucune prédiction ne correspond aux filtres sélectionnés")
                    
            else:
                st.error("Aucune prédiction valide trouvée dans les données")
                
        except Exception as e:
            st.error(f"Erreur lors de l'affichage des prédictions: {str(e)}")
            st.info("Structure des données reçues:")
            st.json(predictions_summary)
    
    def show_crypto_analysis(self, scraped_data: Dict[str, Any]) -> None:
        """
        OBJECTIF : Page d'analyse crypto détaillée
        
        PARAMÈTRES :
        - scraped_data (dict) : Données du système
        """
        st.header("📊 Analyse Crypto Détaillée")
        
        market_data = scraped_data.get('market_data', {})
        if not market_data:
            st.warning("Aucune donnée de marché disponible")
            return
        
        cryptos = market_data.get('cryptocurrencies', [])
        if cryptos:
            df = pd.DataFrame(cryptos)
            
            # Graphique des prix
            if 'symbol' in df.columns and 'price' in df.columns:
                fig = px.bar(df, x='symbol', y='price', title="Prix des Cryptomonnaies")
                st.plotly_chart(fig, use_container_width=True)
            
            # Tableau détaillé
            st.dataframe(df, use_container_width=True)
    
    def show_sentiment_analysis(self, scraped_data: Dict[str, Any]) -> None:
        """
        OBJECTIF : Page d'analyse du sentiment
        
        PARAMÈTRES :
        - scraped_data (dict) : Données du système
        """
        st.header("📈 Analyse du Sentiment du Marché")
        
        sentiment_data = scraped_data.get('sentiment_data', {})
        
        if not sentiment_data:
            st.warning("Aucune donnée de sentiment disponible")
            return
        
        try:
            # Vérifier si les données sont structurées avec "signals"
            if isinstance(sentiment_data, dict):
                # Afficher les métriques globales si disponibles
                if 'overall_sentiment' in sentiment_data:
                    overall = sentiment_data['overall_sentiment']
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.metric("Sentiment Global", f"{overall.get('score', 0):.2f}", 
                                 delta=overall.get('label', 'Neutre'))
                    
                    with col2:
                        st.metric("Sentiment Social", f"{sentiment_data.get('social_sentiment', 0):.2f}")
                    
                    with col3:
                        st.metric("Sentiment News", f"{sentiment_data.get('news_sentiment', 0):.2f}")
                
                # Récupérer les signaux
                signals = sentiment_data.get('signals', [])
                
                if signals and isinstance(signals, list):
                    # Créer le DataFrame à partir des signaux
                    df = pd.DataFrame(signals)
                    
                    # Vérifier les colonnes nécessaires et les renommer si nécessaire
                    if 'symbol' in df.columns:
                        df['crypto'] = df['symbol']  # Renommer pour compatibilité
                    
                    if 'timestamp' in df.columns and 'crypto' in df.columns and 'sentiment_score' in df.columns:
                        # Graphique d'évolution temporelle
                        fig = px.line(
                            df, 
                            x='timestamp', 
                            y='sentiment_score', 
                            color='crypto',
                            title="Évolution Temporelle du Sentiment par Crypto",
                            labels={'sentiment_score': 'Score de Sentiment', 'timestamp': 'Temps'}
                        )
                        st.plotly_chart(fig, use_container_width=True)
                        
                        # Graphique par source si disponible
                        if 'source' in df.columns:
                            fig_source = px.scatter(
                                df,
                                x='timestamp',
                                y='sentiment_score',
                                color='crypto',
                                size='confidence',
                                symbol='source',
                                title="Sentiment par Source et Crypto",
                                labels={'sentiment_score': 'Score de Sentiment', 'timestamp': 'Temps'}
                            )
                            st.plotly_chart(fig_source, use_container_width=True)
                        
                        # Tableau des données
                        st.subheader("Détail des Signaux")
                        
                        # Formatage pour l'affichage
                        display_df = df.copy()
                        if 'sentiment_score' in display_df.columns:
                            display_df['sentiment_score'] = display_df['sentiment_score'].round(3)
                        if 'confidence' in display_df.columns:
                            display_df['confidence'] = display_df['confidence'].round(3)
                        
                        st.dataframe(display_df, use_container_width=True)
                        
                    else:
                        st.error("Colonnes manquantes dans les données de sentiment")
                        st.info("Colonnes disponibles: " + ", ".join(df.columns.tolist()))
                        st.info("Colonnes requises: timestamp, crypto/symbol, sentiment_score")
                else:
                    st.error("Aucun signal de sentiment trouvé dans les données")
                    
            elif isinstance(sentiment_data, list):
                # Ancienne structure (liste directe)
                valid_data = [item for item in sentiment_data if isinstance(item, dict)]
                
                if valid_data:
                    df = pd.DataFrame(valid_data)
                    
                    if 'timestamp' in df.columns and 'crypto' in df.columns and 'sentiment_score' in df.columns:
                        fig = px.line(
                            df, 
                            x='timestamp', 
                            y='sentiment_score', 
                            color='crypto',
                            title="Évolution Temporelle du Sentiment"
                        )
                        st.plotly_chart(fig, use_container_width=True)
                        st.dataframe(df, use_container_width=True)
                    else:
                        st.error("Colonnes manquantes dans les données de sentiment")
                else:
                    st.error("Aucune donnée de sentiment valide trouvée")
            else:
                st.error("Format de données de sentiment invalide")
                
        except Exception as e:
            st.error(f"Erreur lors de l'analyse du sentiment: {str(e)}")
            st.info("Structure des données reçues:")
            st.json(sentiment_data if isinstance(sentiment_data, dict) else sentiment_data[:5] if len(sentiment_data) > 5 else sentiment_data)
    
    def show_data_status(self, scraped_data: Dict[str, Any]) -> None:
        """
        OBJECTIF : Page de statut des données et configuration
        
        PARAMÈTRES :
        - scraped_data (dict) : Données du système
        """
        st.header("⚙️ Statut des Données et Configuration")
        
        # Statut des données
        st.subheader("📊 Statut des Données")
        
        data_status = {
            "Traders pour analyse": len(scraped_data.get('traders_for_analysis', [])),
            "Traders pour prédiction": len(scraped_data.get('traders_for_prediction', [])),
            "Données de marché": len(scraped_data.get('market_data', {})),
            "Données de sentiment": len(scraped_data.get('sentiment_data', [])),
            "Données historiques": len(scraped_data.get('historical_data', [])),
            "Prédictions": len(scraped_data.get('predictions_summary', []))
        }
        
        for data_type, count in data_status.items():
            if count > 0:
                st.success(f"✅ {data_type}: {count} éléments")
            else:
                st.error(f"❌ {data_type}: Aucune donnée")
        
        # Configuration système
        st.subheader("🔧 Configuration Système")
        
        config = get_config()
        st.json(config)


def main():
    """
    Point d'entrée principal de l'application
    """
    dashboard = CryptoDashboard()
    dashboard.run()


if __name__ == "__main__":
    main() 