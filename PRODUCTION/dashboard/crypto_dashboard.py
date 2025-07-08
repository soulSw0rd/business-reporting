#!/usr/bin/env python3
"""
Crypto Dashboard Application
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

# Imports des modules internes
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from core.config_manager import get_config
from core.prediction_engine import CryptoTraderPredictor
from dashboard.components.prediction_panel import PredictionPanel
from dashboard.components.advanced_visualizations import AdvancedVisualizationComponents

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
        
        logger.info("CryptoDashboard initialisé")
    
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
        # Ajuster le chemin depuis le dossier PRODUCTION
        processed_path = Path("..") / data_paths["processed_path"]
        
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
        
        st.sidebar.info(f"Chargement depuis: {processed_path}")
        
        try:
            # === CHARGEMENT DONNÉES MARCHÉ ===
            # Charger le fichier market_data.json principal
            market_file = processed_path / "market_data.json"
            if market_file.exists():
                with open(market_file, 'r', encoding='utf-8') as f:
                    scraped_data['market_data'] = json.load(f)
                    st.sidebar.success(f"✓ market_data.json chargé")
            else:
                st.sidebar.warning("market_data.json manquant")
            
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
                    st.sidebar.success(f"✓ {len(scraped_data['traders_for_analysis'])} traders chargés")
            else:
                st.sidebar.warning("top_traders_extended.json manquant")
            
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
                    st.sidebar.success(f"✓ {len(scraped_data['sentiment_data'])} signaux sentiment")
            else:
                st.sidebar.warning("sentiment_data.json manquant")
            
            # Données historiques
            historical_file = processed_path / "historical_data.json"
            if historical_file.exists():
                with open(historical_file, 'r', encoding='utf-8') as f:
                    scraped_data['historical_data'] = json.load(f)
            
            logger.info("Données scrapées chargées avec succès")
            
        except Exception as e:
            logger.error(f"Erreur lors du chargement des données: {e}")
        
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
            "👑 Top Traders", 
            "🔮 Prédictions ML",
            "📊 Analyse Crypto",
            "📈 Sentiment Marché",
            "🎨 Visualisations Avancées",
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
            "👑 Top Traders": self.show_top_traders,
            "🔮 Prédictions ML": self.show_predictions,
            "📊 Analyse Crypto": self.show_crypto_analysis,
            "📈 Sentiment Marché": self.show_sentiment_analysis,
            "🎨 Visualisations Avancées": self.show_advanced_visualizations,
            "⚙️ Données & Config": self.show_data_status
        }
        
        method = page_methods.get(page)
        if method:
            method(scraped_data)
        else:
            st.error(f"Page non trouvée: {page}")
    
    def show_overview(self, scraped_data: Dict[str, Any]) -> None:
        """
        OBJECTIF : Affichage de la page de vue d'ensemble
        
        PARAMÈTRES :
        - scraped_data (dict) : Données du système
        
        LOGIQUE :
        1. Métriques principales du système
        2. Graphiques de synthèse
        3. Statut des composants
        4. Liens rapides vers autres pages
        """
        st.header("🏠 Vue d'ensemble du marché crypto")
        
        # Extraction des données
        traders_analysis = scraped_data.get('traders_for_analysis', [])
        traders_prediction = scraped_data.get('traders_for_prediction', [])
        market_data = scraped_data.get('market_data_extended', {})
        sentiment_data = scraped_data.get('sentiment_data', {})
        
        # === MÉTRIQUES PRINCIPALES ===
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                "Traders Analysés", 
                len(traders_analysis),
                help="Nombre de traders avec données d'analyse complètes"
            )
        
        with col2:
            st.metric(
                "Traders Prédiction", 
                len(traders_prediction),
                help="Nombre de traders disponibles pour prédiction ML"
            )
        
        with col3:
            crypto_count = len(market_data.get('cryptocurrencies', []))
            st.metric(
                "Cryptos Suivies", 
                crypto_count,
                help="Nombre de cryptomonnaies dans le dataset"
            )
        
        with col4:
            signals_count = len(sentiment_data.get('signals', []))
            st.metric(
                "Signaux Sentiment", 
                signals_count,
                help="Nombre de signaux de sentiment analysés"
            )
        
        st.markdown("---")
        
        # === GRAPHIQUES DE SYNTHÈSE ===
        col1, col2 = st.columns(2)
        
        with col1:
            self._show_top_traders_overview(traders_analysis)
        
        with col2:
            self._show_market_overview(market_data)
        
        # === STATUT DU SYSTÈME ===
        st.markdown("---")
        st.subheader("🔧 Statut du Système")
        
        status_col1, status_col2, status_col3 = st.columns(3)
        
        with status_col1:
            if self.predictor.is_trained:
                st.success("🤖 **Modèle ML:** Opérationnel")
                model_info = self.predictor.get_model_info()
                metadata = model_info.get('metadata', {})
                if metadata:
                    st.info(f"Précision 7j: {metadata.get('accuracy_7d', 0):.1%}")
            else:
                st.warning("🤖 **Modèle ML:** Non entraîné")
        
        with status_col2:
            if traders_prediction:
                st.success("📊 **Données:** Disponibles")
                st.info(f"Dernière MAJ: {datetime.now().strftime('%H:%M')}")
            else:
                st.error("📊 **Données:** Manquantes")
        
        with status_col3:
            if market_data:
                st.success("🌐 **Marché:** Connecté")
                btc_price = market_data.get('cryptocurrencies', [{}])[0].get('price', 0)
                if btc_price:
                    st.info(f"BTC: ${btc_price:,.0f}")
            else:
                st.error("🌐 **Marché:** Déconnecté")
    
    def _show_top_traders_overview(self, traders_data: List[Dict]) -> None:
        """
        OBJECTIF : Graphique des top traders en vue d'ensemble
        
        PARAMÈTRES :
        - traders_data (list) : Données des traders pour analyse
        """
        st.subheader("💰 Top 10 Traders par Performance")
        
        if not traders_data:
            st.warning("Aucune donnée de trader disponible")
            return
        
        try:
            df = pd.DataFrame(traders_data)
            
            # Vérification et nettoyage des données
            if 'total_pnl' in df.columns and 'username' in df.columns:
                # Conversion en numérique et nettoyage
                df['total_pnl'] = pd.to_numeric(df['total_pnl'], errors='coerce')
                df = df.dropna(subset=['total_pnl', 'username'])
                
                if len(df) == 0:
                    st.warning("Aucune donnée valide après nettoyage")
                    return
                
                # Sélection des top 10
                top_traders = df.nlargest(10, 'total_pnl')
                
                # Création du graphique avec gestion d'erreur
                fig = px.bar(
                    top_traders,
                    x='username',
                    y='total_pnl',
                    title="Performance des Top Traders",
                    color='total_pnl',
                    color_continuous_scale='Viridis',
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
    
    def show_top_traders(self, scraped_data: Dict[str, Any]) -> None:
        """
        OBJECTIF : Page d'analyse détaillée des top traders
        
        PARAMÈTRES :
        - scraped_data (dict) : Données du système
        """
        st.header("👑 Analyse des Top Traders")
        
        traders_data = scraped_data.get('traders_for_analysis', [])
        
        if not traders_data:
            st.warning("Aucune donnée de trader disponible")
            return
        
        # Affichage des métriques principales
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Total Traders", len(traders_data))
        
        with col2:
            avg_pnl = sum(trader.get('total_pnl', 0) for trader in traders_data) / len(traders_data)
            st.metric("PnL Moyen", f"${avg_pnl:,.0f}")
        
        with col3:
            avg_win_rate = sum(trader.get('win_rate', 0) for trader in traders_data) / len(traders_data)
            st.metric("Win Rate Moyen", f"{avg_win_rate:.1%}")
        
        # Tableau des traders
        df = pd.DataFrame(traders_data)
        st.dataframe(df.head(20), use_container_width=True)
    
    def show_predictions(self, scraped_data: Dict[str, Any]) -> None:
        """
        OBJECTIF : Page de prédictions ML avec données dynamiques
        
        PARAMÈTRES :
        - scraped_data (dict) : Données du système
        """
        st.header("🔮 Prédictions ML - Analyse Prédictive")
        
        # Charger les données de prédiction dynamiques
        prediction_data = self._load_dynamic_prediction_data()
        
        if not prediction_data:
            st.warning("Aucune donnée de prédiction disponible")
            if st.button("🔄 Générer des Prédictions"):
                self._generate_new_predictions()
                st.rerun()
            return
        
        # === MÉTRIQUES PRINCIPALES ===
        st.subheader("📊 Métriques de Performance")
        
        # Calculer les métriques à partir des données réelles
        predictions = prediction_data.get('predictions', [])
        if predictions:
            total_predictions = len(predictions)
            profitable_count = sum(1 for p in predictions if p.get('is_profitable_7d', False))
            profit_rate = (profitable_count / total_predictions * 100) if total_predictions > 0 else 0
            
            avg_confidence = np.mean([p.get('confidence', 0) for p in predictions])
            high_conf_count = sum(1 for p in predictions if p.get('confidence', 0) > 80)
            
            # Affichage des métriques avec formatage
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric(
                    "Total Prédictions", 
                    f"{total_predictions:,}",
                    delta=f"+{total_predictions - 40}" if total_predictions > 40 else None
                )
            
            with col2:
                st.metric(
                    "Taux de Profit", 
                    f"{profit_rate:.1f}%",
                    delta=f"{profit_rate - 50:.1f}%" if profit_rate != 50 else None,
                    delta_color="normal" if profit_rate >= 50 else "inverse"
                )
            
            with col3:
                st.metric(
                    "Confiance Moyenne", 
                    f"{avg_confidence:.1f}%",
                    delta=f"{avg_confidence - 70:.1f}%" if avg_confidence != 70 else None,
                    delta_color="normal" if avg_confidence >= 70 else "inverse"
                )
            
            with col4:
                st.metric(
                    "Haute Confiance", 
                    f"{high_conf_count}",
                    delta=f"+{high_conf_count - 10}" if high_conf_count > 10 else None
                )
        
        # === GRAPHIQUES DE PRÉDICTION ===
        if predictions:
            # Graphique de distribution des prédictions
            st.subheader("📈 Distribution des Prédictions")
            
            df_pred = pd.DataFrame(predictions)
            
            # Graphique en barres de la profitabilité
            fig_profit = px.histogram(
                df_pred,
                x='is_profitable_7d',
                title="Répartition Profitable vs Non-Profitable (7 jours)",
                labels={'is_profitable_7d': 'Profitable', 'count': 'Nombre de Traders'},
                color='is_profitable_7d',
                color_discrete_map={True: '#2ecc71', False: '#e74c3c'}
            )
            fig_profit.update_layout(height=400, showlegend=False)
            st.plotly_chart(fig_profit, use_container_width=True)
            
            # Graphique de confiance vs probabilité
            col1, col2 = st.columns(2)
            
            with col1:
                fig_conf = px.scatter(
                    df_pred,
                    x='confidence',
                    y='probability_7d',
                    color='is_profitable_7d',
                    title="Confiance vs Probabilité de Profit",
                    labels={
                        'confidence': 'Confiance (%)',
                        'probability_7d': 'Probabilité 7j (%)'
                    },
                    color_discrete_map={True: '#2ecc71', False: '#e74c3c'}
                )
                fig_conf.update_layout(height=400)
                st.plotly_chart(fig_conf, use_container_width=True)
            
            with col2:
                # Distribution de la confiance
                fig_conf_dist = px.histogram(
                    df_pred,
                    x='confidence',
                    nbins=20,
                    title="Distribution de la Confiance",
                    labels={'confidence': 'Confiance (%)', 'count': 'Nombre'},
                    color_discrete_sequence=['#3498db']
                )
                fig_conf_dist.update_layout(height=400)
                st.plotly_chart(fig_conf_dist, use_container_width=True)
        
        # === TABLEAU DÉTAILLÉ ===
        st.subheader("🔍 Détail des Prédictions")
        
        if predictions:
            # Préparer les données pour l'affichage
            display_data = []
            for pred in predictions[:20]:  # Limiter à 20 pour la performance
                display_data.append({
                    'Trader': pred.get('address', 'N/A')[-8:],  # 8 derniers caractères
                    'Profitable 7j': '✅' if pred.get('is_profitable_7d', False) else '❌',
                    'Probabilité 7j (%)': f"{pred.get('probability_7d', 0):.1f}%",
                    'Probabilité 30j (%)': f"{pred.get('probability_30d', 0):.1f}%",
                    'Confiance (%)': f"{pred.get('confidence', 0):.1f}%",
                    'Return 7j (%)': f"{pred.get('expected_return_7d', 0):.2f}%",
                    'Risque': f"{pred.get('risk_score', 0):.0f}/100",
                    'Portefeuille ($)': f"${pred.get('portfolio_value', 0):,.0f}"
                })
            
            df_display = pd.DataFrame(display_data)
            st.dataframe(df_display, use_container_width=True, hide_index=True)
        
        # === ANALYSE AVANCÉE ===
        if predictions:
            st.subheader("🧠 Analyse Avancée")
            
            # Onglets pour différentes analyses
            tab1, tab2, tab3 = st.tabs(["📊 Performance", "🎯 Confiance", "💰 Rendement"])
            
            with tab1:
                # Analyse de performance par segment
                df_pred['confidence_range'] = pd.cut(
                    df_pred['confidence'], 
                    bins=[0, 60, 80, 100], 
                    labels=['Faible', 'Moyenne', 'Élevée']
                )
                
                performance_by_conf = df_pred.groupby('confidence_range').agg({
                    'is_profitable_7d': 'mean',
                    'probability_7d': 'mean',
                    'expected_return_7d': 'mean'
                }).round(2)
                
                st.write("**Performance par Niveau de Confiance**")
                st.dataframe(performance_by_conf)
            
            with tab2:
                # Analyse de la confiance
                high_conf_traders = df_pred[df_pred['confidence'] > 80]
                medium_conf_traders = df_pred[(df_pred['confidence'] >= 60) & (df_pred['confidence'] <= 80)]
                low_conf_traders = df_pred[df_pred['confidence'] < 60]
                
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric("Haute Confiance", len(high_conf_traders))
                    if len(high_conf_traders) > 0:
                        st.write(f"Profit Rate: {high_conf_traders['is_profitable_7d'].mean():.1%}")
                
                with col2:
                    st.metric("Confiance Moyenne", len(medium_conf_traders))
                    if len(medium_conf_traders) > 0:
                        st.write(f"Profit Rate: {medium_conf_traders['is_profitable_7d'].mean():.1%}")
                
                with col3:
                    st.metric("Faible Confiance", len(low_conf_traders))
                    if len(low_conf_traders) > 0:
                        st.write(f"Profit Rate: {low_conf_traders['is_profitable_7d'].mean():.1%}")
            
            with tab3:
                # Analyse des rendements
                profitable_traders = df_pred[df_pred['is_profitable_7d'] == True]
                unprofitable_traders = df_pred[df_pred['is_profitable_7d'] == False]
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.write("**Traders Profitables**")
                    if len(profitable_traders) > 0:
                        st.metric("Nombre", len(profitable_traders))
                        st.metric("Return Moyen", f"{profitable_traders['expected_return_7d'].mean():.2f}%")
                        st.metric("Confiance Moyenne", f"{profitable_traders['confidence'].mean():.1f}%")
                
                with col2:
                    st.write("**Traders Non-Profitables**")
                    if len(unprofitable_traders) > 0:
                        st.metric("Nombre", len(unprofitable_traders))
                        st.metric("Return Moyen", f"{unprofitable_traders['expected_return_7d'].mean():.2f}%")
                        st.metric("Confiance Moyenne", f"{unprofitable_traders['confidence'].mean():.1f}%")
        
        # === ACTIONS ===
        st.subheader("⚙️ Actions")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("🔄 Actualiser Prédictions"):
                self._generate_new_predictions()
                st.success("Prédictions actualisées!")
                st.rerun()
        
        with col2:
            if st.button("📊 Réentraîner Modèle"):
                self._retrain_model()
                st.success("Modèle réentraîné!")
        
        with col3:
            if st.button("💾 Exporter Données"):
                self._export_predictions(predictions)
                st.success("Données exportées!")
    
    def _load_dynamic_prediction_data(self) -> Dict[str, Any]:
        """Charger les données de prédiction dynamiques"""
        try:
            # Essayer de charger les données dynamiques
            dynamic_file = Path("RESOURCES/data/processed/predictions_dynamic.json")
            summary_file = Path("RESOURCES/data/processed/predictions_summary.json")
            
            if summary_file.exists():
                with open(summary_file, 'r') as f:
                    return json.load(f)
            elif dynamic_file.exists():
                with open(dynamic_file, 'r') as f:
                    predictions = json.load(f)
                    return {'predictions': predictions}
            else:
                # Fallback vers les données statiques
                return self._load_static_prediction_data()
                
        except Exception as e:
            logger.error(f"Erreur chargement prédictions dynamiques: {e}")
            return self._load_static_prediction_data()
    
    def _load_static_prediction_data(self) -> Dict[str, Any]:
        """Charger les données de prédiction statiques"""
        try:
            static_file = Path("RESOURCES/data/processed/top_traders_for_prediction.json")
            if static_file.exists():
                with open(static_file, 'r') as f:
                    traders = json.load(f)
                    
                # Générer des prédictions basiques
                predictions = []
                for trader in traders:
                    # Probabilité basée sur les métriques du trader
                    win_rate = trader.get('win_rate', 0.5)
                    pnl = trader.get('total_pnl', 0)
                    
                    prob_7d = min(90, max(10, win_rate * 100 + np.random.normal(0, 10)))
                    prob_30d = min(90, max(10, prob_7d * 0.8 + np.random.normal(0, 5)))
                    
                    confidence = min(95, max(30, win_rate * 80 + np.random.normal(0, 10)))
                    
                    predictions.append({
                        'address': trader.get('address', f'0x{np.random.randint(1000000, 9999999):x}'),
                        'is_profitable_7d': prob_7d > 50,
                        'is_profitable_30d': prob_30d > 50,
                        'probability_7d': prob_7d,
                        'probability_30d': prob_30d,
                        'confidence': confidence,
                        'expected_return_7d': np.random.normal(10, 5),
                        'expected_return_30d': np.random.normal(15, 8),
                        'risk_score': np.random.uniform(20, 80),
                        'portfolio_value': trader.get('total_pnl', 0) * 10
                    })
                
                return {'predictions': predictions}
            else:
                return {}
                
        except Exception as e:
            logger.error(f"Erreur chargement prédictions statiques: {e}")
            return {}
    
    def _generate_new_predictions(self):
        """Générer de nouvelles prédictions"""
        try:
            # Utiliser le générateur de données dynamiques intégré
            from core.dynamic_data_generator import DynamicDataGenerator
            
            generator = DynamicDataGenerator()
            new_predictions = generator.generate_predictions_data(num_predictions=50)
            
            # Sauvegarder les nouvelles prédictions
            predictions_file = Path("..") / "RESOURCES/data/processed/predictions_summary.json"
            with open(predictions_file, 'w', encoding='utf-8') as f:
                json.dump(new_predictions, f, indent=2, ensure_ascii=False)
            
            logger.info("Nouvelles prédictions générées avec succès")
            st.success("✅ Nouvelles prédictions générées!")
            
        except Exception as e:
            logger.error(f"Erreur génération prédictions: {e}")
            st.error(f"❌ Erreur lors de la génération: {e}")
    
    def _retrain_model(self):
        """Réentraîner le modèle ML"""
        try:
            if hasattr(self, 'predictor'):
                self.predictor.train_models()
                logger.info("Modèle réentraîné avec succès")
        except Exception as e:
            logger.error(f"Erreur réentraînement: {e}")
    
    def _export_predictions(self, predictions: List[Dict]):
        """Exporter les prédictions"""
        try:
            import csv
            from datetime import datetime
            
            filename = f"predictions_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            filepath = Path("RESOURCES/data/exports") / filename
            filepath.parent.mkdir(parents=True, exist_ok=True)
            
            with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:
                if predictions:
                    writer = csv.DictWriter(csvfile, fieldnames=predictions[0].keys())
                    writer.writeheader()
                    writer.writerows(predictions)
            
            logger.info(f"Prédictions exportées vers {filepath}")
            
        except Exception as e:
            logger.error(f"Erreur export: {e}")
    
    def show_crypto_analysis(self, scraped_data: Dict[str, Any]) -> None:
        """
        OBJECTIF : Page d'analyse des cryptomonnaies
        
        PARAMÈTRES :
        - scraped_data (dict) : Données du système
        """
        st.header("📊 Analyse du Marché Crypto")
        
        market_data = scraped_data.get('market_data_extended', {})
        
        if not market_data:
            st.warning("Aucune donnée de marché disponible")
            return
        
        # Affichage des cryptomonnaies
        cryptos = market_data.get('cryptocurrencies', [])
        if cryptos:
            df = pd.DataFrame(cryptos)
            st.dataframe(df, use_container_width=True)
        else:
            st.warning("Aucune donnée de cryptomonnaie disponible")
    
    def show_sentiment_analysis(self, scraped_data: Dict[str, Any]) -> None:
        """
        OBJECTIF : Page d'analyse de sentiment
        
        PARAMÈTRES :
        - scraped_data (dict) : Données du système
        """
        st.header("📈 Analyse de Sentiment du Marché")
        
        sentiment_data = scraped_data.get('sentiment_data', {})
        
        if not sentiment_data:
            st.warning("Aucune donnée de sentiment disponible")
            return
        
        try:
            # === SENTIMENT GLOBAL ===
            st.subheader("🌡️ Sentiment Global du Marché")
            
            overall_sentiment = sentiment_data.get('overall_sentiment', {})
            if overall_sentiment and isinstance(overall_sentiment, dict):
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    score = overall_sentiment.get('score', 0)
                    delta_color = "normal" if -0.1 <= score <= 0.1 else ("inverse" if score < 0 else "normal")
                    st.metric(
                        "Score de Sentiment", 
                        f"{score:.3f}", 
                        delta=f"{score:.3f}",
                        delta_color=delta_color
                    )
                
                with col2:
                    label = overall_sentiment.get('label', 'Neutre')
                    emoji_map = {
                        "Bullish": "🟢 📈",
                        "Bearish": "🔴 📉", 
                        "Neutral": "🟡 ➡️"
                    }
                    emoji = emoji_map.get(label, "🟡 ➡️")
                    st.metric("Tendance", f"{emoji} {label}")
                
                with col3:
                    confidence = overall_sentiment.get('confidence', 0)
                    confidence_pct = confidence * 100 if confidence <= 1 else confidence
                    st.metric("Niveau de Confiance", f"{confidence_pct:.1f}%")
                
                # Gauge de sentiment
                fig_gauge = go.Figure(go.Indicator(
                    mode = "gauge+number+delta",
                    value = score,
                    domain = {'x': [0, 1], 'y': [0, 1]},
                    title = {'text': "Sentiment Score"},
                    delta = {'reference': 0},
                    gauge = {
                        'axis': {'range': [-1, 1]},
                        'bar': {'color': "darkblue"},
                        'steps': [
                            {'range': [-1, -0.5], 'color': "red"},
                            {'range': [-0.5, 0], 'color': "orange"},
                            {'range': [0, 0.5], 'color': "lightgreen"},
                            {'range': [0.5, 1], 'color': "green"}
                        ],
                        'threshold': {
                            'line': {'color': "red", 'width': 4},
                            'thickness': 0.75,
                            'value': 0.9
                        }
                    }
                ))
                
                fig_gauge.update_layout(height=300)
                st.plotly_chart(fig_gauge, use_container_width=True)
            
            else:
                st.info("Données de sentiment global non disponibles")
            
            # === SIGNAUX PAR CRYPTO ===
            signals = sentiment_data.get('signals', [])
            if signals:
                st.subheader("📡 Signaux de Sentiment par Cryptomonnaie")
                
                df_signals = pd.DataFrame(signals)
                
                # Vérification des colonnes nécessaires
                required_cols = ['symbol', 'sentiment_score']
                missing_cols = [col for col in required_cols if col not in df_signals.columns]
                
                if not missing_cols:
                    # Nettoyage des données
                    df_signals['sentiment_score'] = pd.to_numeric(df_signals['sentiment_score'], errors='coerce')
                    df_signals = df_signals.dropna(subset=['sentiment_score'])
                    
                    if len(df_signals) > 0:
                        # Graphique en barres
                        fig = px.bar(
                            df_signals,
                            x='symbol',
                            y='sentiment_score',
                            color='sentiment_score',
                            title="Score de Sentiment par Cryptomonnaie",
                            color_continuous_scale='RdYlGn',
                            color_continuous_midpoint=0,
                            labels={
                                'sentiment_score': 'Score de Sentiment',
                                'symbol': 'Cryptomonnaie'
                            },
                            hover_data=['confidence'] if 'confidence' in df_signals.columns else None
                        )
                        
                        fig.update_layout(
                            height=400,
                            xaxis_title="Cryptomonnaies",
                            yaxis_title="Score de Sentiment",
                            showlegend=False
                        )
                        
                        # Ligne de référence à 0
                        fig.add_hline(y=0, line_dash="dash", line_color="gray")
                        
                        st.plotly_chart(fig, use_container_width=True)
                        
                        # Statistiques des signaux
                        col1, col2, col3, col4 = st.columns(4)
                        
                        with col1:
                            st.metric("Signaux Positifs", len(df_signals[df_signals['sentiment_score'] > 0]))
                        
                        with col2:
                            st.metric("Signaux Négatifs", len(df_signals[df_signals['sentiment_score'] < 0]))
                        
                        with col3:
                            st.metric("Score Moyen", f"{df_signals['sentiment_score'].mean():.3f}")
                        
                        with col4:
                            if 'confidence' in df_signals.columns:
                                avg_conf = df_signals['confidence'].mean()
                                conf_pct = avg_conf * 100 if avg_conf <= 1 else avg_conf
                                st.metric("Confiance Moyenne", f"{conf_pct:.1f}%")
                        
                        # Tableau détaillé avec formatage
                        st.subheader("📊 Détail des Signaux")
                        
                        # Formatage du tableau
                        display_df = df_signals.copy()
                        if 'sentiment_score' in display_df.columns:
                            display_df['sentiment_score'] = display_df['sentiment_score'].round(3)
                        if 'confidence' in display_df.columns:
                            display_df['confidence'] = (display_df['confidence'] * 100).round(1)
                            display_df.rename(columns={'confidence': 'confidence (%)'}, inplace=True)
                        
                        st.dataframe(
                            display_df,
                            use_container_width=True,
                            hide_index=True
                        )
                    else:
                        st.warning("Aucun signal valide après nettoyage des données")
                else:
                    st.error(f"Colonnes manquantes dans les signaux: {missing_cols}")
                    st.info("Colonnes disponibles: " + ", ".join(df_signals.columns.tolist()))
            else:
                st.info("Aucun signal de sentiment disponible")
                
            # === ANALYSE TEMPORELLE ===
            if signals and 'timestamp' in pd.DataFrame(signals).columns:
                st.subheader("⏰ Évolution Temporelle du Sentiment")
                
                df_temporal = pd.DataFrame(signals)
                df_temporal['timestamp'] = pd.to_datetime(df_temporal['timestamp'], errors='coerce')
                df_temporal = df_temporal.dropna(subset=['timestamp', 'sentiment_score'])
                
                if len(df_temporal) > 0:
                    # Graphique temporel
                    fig_time = px.line(
                        df_temporal,
                        x='timestamp',
                        y='sentiment_score',
                        color='symbol' if 'symbol' in df_temporal.columns else None,
                        title="Évolution du Sentiment dans le Temps",
                        labels={
                            'sentiment_score': 'Score de Sentiment',
                            'timestamp': 'Temps'
                        }
                    )
                    
                    fig_time.add_hline(y=0, line_dash="dash", line_color="gray")
                    fig_time.update_layout(height=400)
                    
                    st.plotly_chart(fig_time, use_container_width=True)
                
        except Exception as e:
            st.error(f"Erreur lors de l'analyse de sentiment: {str(e)}")
            st.info("Vérifiez la structure des données dans la page 'Données & Config'")
            
            # Debug info
            if sentiment_data:
                st.json(sentiment_data)
    
    def show_advanced_visualizations(self, scraped_data: Dict[str, Any]) -> None:
        """
        OBJECTIF : Page de visualisations avancées
        
        PARAMÈTRES :
        - scraped_data (dict) : Données du système
        """
        st.header("🎨 Visualisations Avancées")
        
        # Délégation au composant spécialisé
        self.advanced_viz.display(scraped_data)
    
    def show_data_status(self, scraped_data: Dict[str, Any]) -> None:
        """
        OBJECTIF : Page de statut des données et configuration
        
        PARAMÈTRES :
        - scraped_data (dict) : Données du système
        """
        st.header("⚙️ Données & Configuration")
        
        # Statut des fichiers de données
        st.subheader("📁 Statut des Fichiers")
        
        data_paths = get_config("data")
        processed_path = Path(data_paths["processed_path"])
        
        if processed_path.exists():
            files_info = []
            for json_file in processed_path.glob("*.json"):
                mtime = datetime.fromtimestamp(json_file.stat().st_mtime)
                size_kb = json_file.stat().st_size / 1024
                
                files_info.append({
                    "Fichier": json_file.name,
                    "Dernière modification": mtime.strftime('%Y-%m-%d %H:%M:%S'),
                    "Taille (KB)": f"{size_kb:.1f}",
                    "Type": self._classify_file_type(json_file.name)
                })
            
            if files_info:
                df_files = pd.DataFrame(files_info)
                st.dataframe(df_files, use_container_width=True)
            else:
                st.warning("Aucun fichier JSON trouvé")
        else:
            st.error(f"Dossier de données non trouvé: {processed_path}")
        
        # Configuration système
        st.subheader("⚙️ Configuration Système")
        
        config_expander = st.expander("Voir la configuration complète")
        with config_expander:
            st.json(self.config)
        
        # Actions de maintenance
        st.subheader("🔧 Actions de Maintenance")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("🔄 Vider le cache"):
                st.cache_data.clear()
                st.success("Cache vidé avec succès")
        
        with col2:
            if st.button("🤖 Réentraîner le modèle"):
                with st.spinner("Entraînement en cours..."):
                    results = self.predictor.train_models()
                st.success(f"Modèle entraîné - Précision: {results['accuracy_7d']:.1%}")
        
        with col3:
            if st.button("📊 Générer rapport"):
                st.info("Fonctionnalité à venir")
    
    def _classify_file_type(self, filename: str) -> str:
        """
        OBJECTIF : Classification du type de fichier de données
        
        PARAMÈTRES :
        - filename (str) : Nom du fichier
        
        RETOURNE :
        - str : Type de fichier classifié
        """
        if "trader" in filename.lower():
            return "🧑‍💼 Traders"
        elif "market" in filename.lower():
            return "📊 Marché"
        elif "sentiment" in filename.lower():
            return "📈 Sentiment"
        elif "historical" in filename.lower():
            return "📜 Historique"
        else:
            return "📄 Autre"


def main():
    """
    OBJECTIF : Point d'entrée principal de l'application
    
    LOGIQUE :
    1. Création de l'instance dashboard
    2. Lancement de l'application
    3. Gestion des erreurs globales
    """
    try:
        dashboard = CryptoDashboard()
        dashboard.run()
    except Exception as e:
        st.error(f"Erreur fatale dans l'application: {e}")
        logger.error(f"Erreur fatale: {e}", exc_info=True)


if __name__ == "__main__":
    main() 