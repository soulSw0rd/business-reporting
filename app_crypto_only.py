#!/usr/bin/env python3
"""
Dashboard Crypto Business Intelligence - Version simplifiée
Utilise uniquement les données du dossier /data
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import json
from pathlib import Path
import requests
from datetime import datetime, timedelta
import subprocess

# --- AJOUT POUR LA PAGE PREDICTIONS ---
from src.ml.predictor import CryptoMLPredictor, MLDataCollector
# --- FIN AJOUT ---

# Configuration de la page
st.set_page_config(
    page_title="Crypto Dashboard",
    page_icon="₿",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialisation du prédicteur ML
# On retire la base de données de simulation qui était source de problèmes
predictor = CryptoMLPredictor(data_path="data/ml_training")

# Fonctions de chargement de données
@st.cache_data(ttl=600) # Cache de 10 minutes
def load_traders_data_for_prediction():
    """Charge le dernier fichier de données de traders pour la prédiction."""
    try:
        data_path = Path("data/processed")
        trader_files = sorted(data_path.glob("top_traders_prediction_*.json"), reverse=True)
        if trader_files:
            with open(trader_files[0], 'r') as f:
                return pd.DataFrame(json.load(f))
    except (FileNotFoundError, IndexError):
        return pd.DataFrame()
    return pd.DataFrame()

@st.cache_data(ttl=600)
def load_market_data_for_prediction():
    """Charge le dernier fichier de données de marché pour la prédiction."""
    try:
        data_path = Path("data/processed")
        market_files = sorted(data_path.glob("market_data_prediction_*.json"), reverse=True)
        if market_files:
            with open(market_files[0], 'r') as f:
                return json.load(f)
    except (FileNotFoundError, IndexError):
        return None
    return None

# Fonctions utilitaires
def display_prediction(prediction, probability, trader_data, market_data):
    """Affiche le résultat d'une prédiction avec une mise en page élégante."""
    if probability is not None:
        # Affichage du résultat texte avec couleur
        if "Fortement" in prediction:
            st.success(f"**Résultat :** {prediction}")
        elif "Potentiellement" in prediction:
            st.warning(f"**Résultat :** {prediction}")
        else:
            st.error(f"**Résultat :** {prediction}")

        # Jauge de probabilité visuelle
        fig = go.Figure(go.Indicator(
            mode = "gauge+number",
            value = probability * 100,
            title = {'text': "Probabilité de Profit"},
            number = {'suffix': "%"},
            gauge = {
                'axis': {'range': [0, 100]},
                'bar': {'color': "white", 'thickness': 0.3},
                'steps': [
                    {'range': [0, 40], 'color': '#EF553B'},
                    {'range': [40, 60], 'color': '#FECB52'},
                    {'range': [60, 100], 'color': '#00CC96'}
                ],
            }))
        fig.update_layout(height=250, margin=dict(l=30, r=30, t=50, b=20))
        st.plotly_chart(fig, use_container_width=True)
        
        # --- Section des Indicateurs Clés (KPIs) ---
        st.markdown("---")
        st.subheader("📊 Indicateurs Clés Analysés")
        st.caption("Voici les données spécifiques qui ont été utilisées par le modèle pour cette prédiction.")

        # KPIs du trader
        st.markdown("##### Performance du Trader")
        col1, col2, col3 = st.columns(3)
        col1.metric("PnL 7 derniers jours", trader_data.get('pnl_7d', 'N/A'))
        col2.metric("PnL 30 derniers jours", trader_data.get('pnl_30d', 'N/A'))
        col3.metric("Exposition 'Long'", trader_data.get('long_percentage', 'N/A'))

        # KPIs du marché
        st.markdown("##### Contexte du Marché")
        btc_price = market_data.get('coingecko_btc', {}).get('price', 0)
        fear_greed = market_data.get('fear_and_greed_index', {}).get('value', 0)
        funding_rate = market_data.get('funding_rates', {}).get('BTCUSDT', {}).get('last_funding_rate', 0)
        
        col4, col5, col6 = st.columns(3)
        col4.metric("Prix du Bitcoin", f"${btc_price:,.0f}")
        col5.metric("Indice Peur & Cupidité", f"{fear_greed} / 100")
        col6.metric("Taux de Financement", f"{funding_rate:.4%}" if funding_rate else "N/A")

    else:
        st.error(f"**Erreur de prédiction :** {prediction}")

# --- MISE À JOUR DES FONCTIONS DE DONNÉES ---
@st.cache_data(ttl=60)
def get_scraped_data():
    """
    Récupère les données scrapées depuis les fichiers JSON locaux.
    Sépare les données pour la prédiction et pour l'analyse.
    """
    data_path = Path("data/processed")
    scraped_data = {
        'traders_for_analysis': [],
        'traders_for_prediction': []
    }
    if not data_path.exists():
        return scraped_data
        
    # Charger tous les fichiers non-traders
    for json_file in data_path.glob("*.json"):
        if "trader" not in json_file.name.lower():
            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    scraped_data[json_file.stem] = json.load(f)
            except Exception:
                pass

    # --- Chargement des données pour l'ANALYSE ---
    # Utilise le fichier "extended" qui a des colonnes comme 'username', 'roi_percentage'
    extended_file = data_path / "top_traders_extended.json"
    if extended_file.exists():
        try:
            with open(extended_file, 'r', encoding='utf-8') as f:
                scraped_data['traders_for_analysis'] = json.load(f)
        except Exception:
            pass # La liste reste vide

    # --- Chargement des données pour la PRÉDICTION ---
    # Utilise le plus récent des fichiers qui a la colonne 'address' et les PNL
    trader_files = sorted(data_path.glob("top_traders_*.json"), reverse=True)
    if trader_files:
        # Exclure le fichier 'extended' pour ne pas le prendre pour la prédiction
        prediction_files = [f for f in trader_files if "extended" not in f.name]
        if prediction_files:
            latest_trader_file = prediction_files[0]
            try:
                with open(latest_trader_file, 'r', encoding='utf-8') as f:
                    scraped_data['traders_for_prediction'] = json.load(f)
            except Exception:
                pass # La liste reste vide
    
    return scraped_data
# --- FIN MISE À JOUR ---

def main():
    st.title("₿ CryptoTrader Dashboard - Business Intelligence")
    st.markdown("---")
    
    # Sidebar pour la navigation
    st.sidebar.title("🚀 Navigation")
    
    # Bouton pour forcer le rafraîchissement
    if st.sidebar.button("🔄 Forcer le rafraîchissement des données"):
        st.cache_data.clear()
        st.rerun()

    page = st.sidebar.selectbox(
        "Choisir une page",
        ["🏠 Vue d'ensemble", "👑 Top Traders", "🔮 Prédictions", "📊 Analyse Crypto", "📈 Sentiment", "⚙️ Données"]
    )
    
    # Vérification des données disponibles
    scraped_data = get_scraped_data()
    
    # Affichage selon la page sélectionnée
    if page == "🏠 Vue d'ensemble":
        show_overview(scraped_data)
    elif page == "👑 Top Traders":
        show_top_traders(scraped_data)
    elif page == "🔮 Prédictions":
        show_predictions_page(scraped_data)
    elif page == "📊 Analyse Crypto":
        show_crypto_analysis(scraped_data)
    elif page == "📈 Sentiment":
        show_sentiment_analysis(scraped_data)
    elif page == "⚙️ Données":
        show_data_status(scraped_data)

def show_overview(scraped_data):
    """Affiche la page de vue d'ensemble basée sur les données réelles"""
    st.header("🏠 Vue d'ensemble du marché crypto")
    
    # --- Utilisation EXPLICITE des données d'ANALYSE ---
    traders_list = scraped_data.get('traders_for_analysis', [])
    market_data = scraped_data.get('market_data_extended', {})
    historical_data = scraped_data.get('historical_data', [])
    sentiment_data = scraped_data.get('sentiment_data', {})

    # Métriques principales
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Traders Analysés", len(traders_list))
    with col2:
        crypto_count = len(market_data.get('cryptocurrencies', []))
        st.metric("Cryptomonnaies Suivies", crypto_count)
    with col3:
        st.metric("Points de Données Historiques", len(historical_data))
    with col4:
        signals_count = len(sentiment_data.get('signals', []))
        st.metric("Signaux de Sentiment", signals_count)
    
    st.markdown("---")
    
    # Graphiques
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("💰 Top 10 Traders par PnL Total")
        st.caption("Basé sur les données d'analyse enrichies.")
        if traders_list:
            df = pd.DataFrame(traders_list)
            if 'total_pnl' in df.columns and 'username' in df.columns:
                top_traders = df.nlargest(10, 'total_pnl')
                fig = px.bar(top_traders, x='username', y='total_pnl', title="Top 10 Traders par Profit", color='total_pnl', color_continuous_scale='Viridis')
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.warning("Données traders d'analyse incomplètes.")
        else:
            st.warning("Aucune donnée d'analyse de trader trouvée.")
    
    with col2:
        st.subheader("📊 Prix Actuels des Cryptomonnaies")
        st.caption("Snapshot des prix du marché.")
        cryptos = market_data.get('cryptocurrencies', [])
        if cryptos:
            df = pd.DataFrame(cryptos)
            if 'symbol' in df.columns and 'price' in df.columns:
                fig = px.bar(df, x='symbol', y='price', title="Prix par Crypto", color='price', color_continuous_scale='Blues')
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.warning("Données de marché incomplètes.")
        else:
            st.warning("Aucune donnée de marché disponible.")

def show_top_traders(scraped_data):
    """Affiche l'analyse des top traders basée sur les données réelles"""
    st.header("👑 Analyse des Top Traders")
    
    # --- Utilisation EXPLICITE des données d'ANALYSE ---
    traders_list = scraped_data.get('traders_for_analysis', [])
    if not traders_list:
        st.error("❌ Aucune donnée d'analyse de trader trouvée.")
        st.info("Vérifiez que le fichier `top_traders_extended.json` existe et est valide.")
        return
        
    traders_df = pd.DataFrame(traders_list)
    
    # Vérifier les colonnes nécessaires pour l'analyse
    required_columns = ['roi_percentage', 'total_trades', 'win_rate', 'total_pnl', 'username']
    missing_columns = [col for col in required_columns if col not in traders_df.columns]
    
    if missing_columns:
        st.error(f"❌ Colonnes manquantes dans les données: {missing_columns}")
        st.write("Colonnes disponibles:", list(traders_df.columns))
        return
    
    # Afficher les colonnes pour debug si nécessaire
    if st.checkbox("🔍 Afficher info debug", key="debug_traders"):
        st.write(f"Colonnes: {list(traders_df.columns)}")
        st.write(f"Forme des données: {traders_df.shape}")
        st.write("Premiers traders:", traders_df.head(2))
    
    # Filtres pour les traders
    col1, col2, col3 = st.columns(3)
    
    with col1:
        min_roi = st.slider("ROI minimum (%)", 0, 200, 20)
    
    with col2:
        min_trades = st.slider("Trades minimum", 0, 1000, 100)
    
    with col3:
        min_winrate = st.slider("Win Rate minimum (%)", 50, 90, 60)
    
    # Filtrage des données
    filtered_traders = traders_df[
        (traders_df['roi_percentage'] >= min_roi) &
        (traders_df['total_trades'] >= min_trades) &
        (traders_df['win_rate'] >= min_winrate/100)
    ]
    
    st.write(f"📊 {len(filtered_traders)} traders correspondent aux critères")
    
    # Graphiques d'analyse des traders
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("💰 Top 10 - PnL Total")
        top_pnl = filtered_traders.nlargest(10, 'total_pnl')
        
        fig = px.bar(
            top_pnl,
            x='username',
            y='total_pnl',
            color='win_rate',
            title="Top Traders par PnL",
            color_continuous_scale='Viridis'
        )
        fig.update_layout(height=400, xaxis_tickangle=-45)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("📊 Distribution ROI")
        fig = px.histogram(
            filtered_traders,
            x='roi_percentage',
            nbins=20,
            title="Distribution des ROI",
            color_discrete_sequence=['#FFD700']
        )
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)
    
    # Tableau des traders
    st.subheader("📋 Tableau des Top Traders")
    
    # Formater les données pour l'affichage
    display_df = filtered_traders.copy()
    display_df['total_pnl'] = display_df['total_pnl'].apply(lambda x: f"${x:,.2f}")
    display_df['roi_percentage'] = display_df['roi_percentage'].apply(lambda x: f"{x:.1f}%")
    display_df['win_rate'] = display_df['win_rate'].apply(lambda x: f"{x:.1%}")
    
    # Sélectionner les colonnes importantes
    cols_to_show = ['username', 'total_pnl', 'roi_percentage', 'win_rate', 'total_trades']
    
    st.dataframe(
        display_df[cols_to_show].head(20),
        use_container_width=True
    )

def show_crypto_analysis(scraped_data):
    """Affiche l'analyse des cryptomonnaies basée sur les données réelles"""
    st.header("📊 Analyse du marché crypto")
    
    # Vérifier les données market_data_extended
    if not scraped_data or 'market_data_extended' not in scraped_data:
        st.error("❌ Fichier market_data_extended.json introuvable")
        return
    
    market_data = scraped_data['market_data_extended']
    if not isinstance(market_data, dict) or 'cryptocurrencies' not in market_data:
        st.error("❌ Structure incorrecte dans market_data_extended.json")
        return
    
    cryptos = market_data['cryptocurrencies']
    if not cryptos:
        st.error("❌ Aucune donnée crypto trouvée")
        return
    
    df = pd.DataFrame(cryptos)
    
    # Correction pour le ArrowTypeError : convertir les colonnes potentiellement mixtes
    if 'max_supply' in df.columns:
        df['max_supply'] = pd.to_numeric(df['max_supply'], errors='coerce').fillna(0)
    
    # Sélection de crypto
    col1, col2 = st.columns(2)
    
    with col1:
        if 'symbol' in df.columns:
            selected_crypto = st.selectbox(
                "Sélectionner une cryptomonnaie",
                df['symbol'].unique()
            )
        else:
            st.error("Colonne 'symbol' manquante")
            return
    
    with col2:
        # Afficher les données historiques si disponibles
        show_historical = st.checkbox("Afficher les données historiques", value=True)
    
    # Données de la crypto sélectionnée
    crypto_info = df[df['symbol'] == selected_crypto].iloc[0]
    
    # Métriques principales
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if 'price' in crypto_info:
            st.metric("💰 Prix", f"${crypto_info['price']:,.2f}")
    
    with col2:
        if 'change_24h' in crypto_info:
            st.metric("📈 Change 24h", f"{crypto_info['change_24h']:+.2f}%")
    
    with col3:
        if 'volume_24h' in crypto_info:
            volume = crypto_info['volume_24h']
            st.metric("📊 Volume 24h", f"${volume/1e6:.1f}M" if volume > 1e6 else f"${volume:,.0f}")
    
    with col4:
        if 'market_cap' in crypto_info:
            mcap = crypto_info['market_cap']
            st.metric("🏪 Market Cap", f"${mcap/1e9:.2f}B" if mcap > 1e9 else f"${mcap/1e6:.1f}M")
    
    st.markdown("---")
    
    # Graphiques
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📊 Comparaison des prix")
        fig = px.bar(
            df,
            x='symbol',
            y='price',
            color='change_24h',
            title="Prix par cryptomonnaie",
            color_continuous_scale='RdYlGn',
            color_continuous_midpoint=0
        )
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("💹 Variations 24h")
        fig = px.bar(
            df,
            x='symbol',
            y='change_24h',
            color='change_24h',
            title="Changements 24h (%)",
            color_continuous_scale='RdYlGn',
            color_continuous_midpoint=0
        )
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)
    
    # Données historiques si disponibles
    if show_historical and scraped_data and 'historical_data' in scraped_data:
        st.subheader(f"📈 Historique des prix - {selected_crypto}")
        
        historical_data = scraped_data['historical_data']
        if isinstance(historical_data, list):
            hist_df = pd.DataFrame(historical_data)
            
            if 'symbol' in hist_df.columns:
                crypto_hist = hist_df[hist_df['symbol'] == selected_crypto]
                
                if not crypto_hist.empty and 'date' in crypto_hist.columns:
                    crypto_hist = crypto_hist.sort_values('date')
                    
                    if 'close' in crypto_hist.columns:
                        fig = px.line(
                            crypto_hist,
                            x='date',
                            y='close',
                            title=f"Évolution du prix de {selected_crypto}",
                            line_shape='linear'
                        )
                        fig.update_layout(height=400)
                        st.plotly_chart(fig, use_container_width=True)
                    else:
                        st.warning("Colonne 'close' manquante dans les données historiques")
                else:
                    st.warning(f"Aucune donnée historique trouvée pour {selected_crypto}")
            else:
                st.warning("Colonne 'symbol' manquante dans les données historiques")
        else:
            st.warning("Format incorrect pour les données historiques")
    
    # Tableau détaillé
    st.subheader("📋 Données détaillées")
    st.dataframe(df, use_container_width=True)

def show_sentiment_analysis(scraped_data):
    """Affiche l'analyse de sentiment basée sur les données réelles"""
    st.header("📈 Analyse de Sentiment")
    
    # Vérifier les données de sentiment
    if not scraped_data or 'sentiment_data' not in scraped_data:
        st.error("❌ Fichier sentiment_data.json introuvable")
        return
    
    sentiment_data = scraped_data['sentiment_data']
    if not isinstance(sentiment_data, dict):
        st.error("❌ Structure incorrecte dans sentiment_data.json")
        return
    
    # Sentiment global
    overall_sentiment = sentiment_data.get('overall_sentiment', {})
    if overall_sentiment:
        col1, col2, col3 = st.columns(3)
        
        with col1:
            score = overall_sentiment.get('score', 0)
            st.metric("📊 Score Global", f"{score:.3f}")
        
        with col2:
            label = overall_sentiment.get('label', 'N/A')
            st.metric("🎯 Sentiment", label)
        
        with col3:
            confidence = overall_sentiment.get('confidence', 0)
            st.metric("🔍 Confiance", f"{confidence:.1%}")
    
    st.markdown("---")
    
    # Signaux par crypto
    signals = sentiment_data.get('signals', [])
    if signals:
        st.subheader("📡 Signaux par Cryptomonnaie")
        
        df_signals = pd.DataFrame(signals)
        
        if 'symbol' in df_signals.columns:
            # Graphique des scores de sentiment
            col1, col2 = st.columns(2)
            
            with col1:
                if 'sentiment_score' in df_signals.columns:
                    fig = px.bar(
                        df_signals,
                        x='symbol',
                        y='sentiment_score',
                        color='sentiment_score',
                        title="Score de sentiment par crypto",
                        color_continuous_scale='RdYlGn',
                        color_continuous_midpoint=0
                    )
                    fig.update_layout(height=400)
                    st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                if 'social_volume' in df_signals.columns:
                    fig = px.bar(
                        df_signals,
                        x='symbol',
                        y='social_volume',
                        title="Volume social par crypto",
                        color='social_volume',
                        color_continuous_scale='Blues'
                    )
                    fig.update_layout(height=400)
                    st.plotly_chart(fig, use_container_width=True)
            
            # Tableau des signaux détaillés
            st.subheader("📋 Signaux détaillés")
            
            # Restructurer les signaux pour l'affichage
            detailed_signals = []
            for signal in signals:
                if 'signals' in signal:
                    for sig in signal['signals']:
                        detailed_signals.append({
                            'Crypto': signal.get('symbol', 'N/A'),
                            'Type': sig.get('type', 'N/A'),
                            'Direction': sig.get('direction', 'N/A'),
                            'Force': sig.get('strength', 'N/A'),
                            'Confiance': f"{sig.get('confidence', 0):.1%}",
                            'Timestamp': sig.get('timestamp', 'N/A')
                        })
            
            if detailed_signals:
                df_detailed = pd.DataFrame(detailed_signals)
                st.dataframe(df_detailed, use_container_width=True)
            
            # Affichage brut des données
            st.subheader("📊 Données brutes")
            st.caption("Données de sentiment brutes agrégées par cryptomonnaie.")
            st.dataframe(df_signals, use_container_width=True)
        else:
            st.warning("Colonne 'symbol' manquante dans les signaux")
    else:
        st.warning("Aucun signal trouvé")

def show_data_status(scraped_data):
    """Affiche le statut des données locales."""
    st.header("⚙️ Statut des Données")
    st.info("Cette page montre les informations sur les derniers fichiers de données chargés.")
    
    data_path = Path("data/processed")
    if not data_path.exists():
        st.error("Le dossier data/processed n'existe pas.")
        return
    
    files_info = []
    for json_file in data_path.glob("*.json"):
        try:
            mtime = datetime.fromtimestamp(json_file.stat().st_mtime)
            files_info.append({
                "Fichier": json_file.name,
                "Dernière modification": mtime.strftime('%Y-%m-%d %H:%M:%S'),
                "Taille (ko)": f"{json_file.stat().st_size / 1024:.2f}"
            })
        except Exception:
            pass

    if files_info:
        df = pd.DataFrame(files_info)
        st.dataframe(df, use_container_width=True)
    else:
        st.warning("Aucun fichier JSON trouvé dans data/processed.")

# --- DEBUT NOUVELLE PAGE PREDICTIONS ---
def show_predictions_page(scraped_data):
    """Affiche la page des prédictions de profitabilité des traders."""
    st.subheader("🔮 Prédictions de Profitabilité des Traders")
    
    if st.button("🔄 Générer de nouvelles données de prédiction"):
        try:
            # Exécuter le nouveau script de génération de données
            result = subprocess.run(['python', 'generate_prediction_data.py'], capture_output=True, text=True, check=True)
            st.toast("Nouvelles données générées !")
            print(result.stdout)
            st.cache_data.clear() # Vider le cache pour recharger les nouvelles données
        except subprocess.CalledProcessError as e:
            st.error(f"Erreur lors de la génération des données : {e.stderr}")
        except FileNotFoundError:
            st.error("Erreur : Le script 'generate_prediction_data.py' est introuvable.")

    # Charger les données depuis les nouveaux fichiers
    traders_df = load_traders_data_for_prediction()
    market_data = load_market_data_for_prediction()

    if traders_df.empty or market_data is None:
        st.warning("Aucune donnée de prédiction disponible. Veuillez d'abord en générer.")
        return

    st.dataframe(traders_df)

    selected_trader_address = st.selectbox(
        "Sélectionnez un trader pour voir les prédictions :",
        traders_df['address'],
        format_func=lambda x: f"{x[:6]}...{x[-4:]}"
    )
            
    if selected_trader_address:
        trader_data = traders_df[traders_df['address'] == selected_trader_address].iloc[0]
        
        st.write(f"#### Analyse pour le trader : `{selected_trader_address}`")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.info("**Prédiction à 7 jours**")
            if st.button("Lancer la prédiction (7 jours)"):
                pred_7d, prob_7d = predictor.predict_trader_profitability(trader_data, market_data, horizon_days=7)
                display_prediction(pred_7d, prob_7d, trader_data, market_data)
        
        with col2:
            st.info("**Prédiction à 30 jours**")
            if st.button("Lancer la prédiction (30 jours)"):
                pred_30d, prob_30d = predictor.predict_trader_profitability(trader_data, market_data, horizon_days=30)
                display_prediction(pred_30d, prob_30d, trader_data, market_data)

# --- FIN NOUVELLE PAGE PREDICTIONS ---

if __name__ == "__main__":
    main()
