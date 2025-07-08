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
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# Configuration de la page
st.set_page_config(
    page_title="Crypto Dashboard",
    page_icon="₿",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Fonctions pour accéder aux données
@st.cache_data(ttl=300)  # Cache pendant 5 minutes
def get_scraped_data():
    """Récupère les données scrapées depuis les fichiers JSON locaux"""
    data_path = Path("data/processed")
    scraped_data = {}
    
    if data_path.exists():
        for json_file in data_path.glob("*.json"):
            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    scraped_data[json_file.stem] = data
            except Exception as e:
                st.error(f"Erreur lors du chargement de {json_file}: {e}")
    
    return scraped_data

def clean_dataframe_for_display(df):
    """Nettoie un DataFrame pour éviter les erreurs de sérialisation PyArrow"""
    if df is None or df.empty:
        return df
    
    df_clean = df.copy()
    
    # Convertir les colonnes problématiques
    for col in df_clean.columns:
        if col in ['max_supply', 'total_supply', 'circulating_supply']:
            # Convertir "N/A" en None puis en float
            df_clean[col] = df_clean[col].apply(lambda x: None if x == "N/A" else x)
            df_clean[col] = pd.to_numeric(df_clean[col], errors='coerce')
        
        # Convertir les autres colonnes objets en string pour éviter les erreurs
        elif df_clean[col].dtype == 'object':
            df_clean[col] = df_clean[col].astype(str)
    
    return df_clean

def main():
    st.title("₿ CryptoTrader Dashboard - Business Intelligence")
    st.markdown("---")
    
    # Sidebar pour la navigation
    st.sidebar.title("🚀 Navigation")
    page = st.sidebar.selectbox(
        "Choisir une page",
        ["🏠 Vue d'ensemble", "👑 Top Traders", "📊 Analyse Crypto", "📈 Sentiment", "⚙️ Données"]
    )
    
    # Vérification des données disponibles
    scraped_data = get_scraped_data()
    
    # Affichage selon la page sélectionnée
    if page == "🏠 Vue d'ensemble":
        show_overview(scraped_data)
    elif page == "👑 Top Traders":
        show_top_traders(scraped_data)
    elif page == "📊 Analyse Crypto":
        show_crypto_analysis(scraped_data)
    elif page == "📈 Sentiment":
        show_sentiment_analysis(scraped_data)
    elif page == "⚙️ Données":
        show_data_status(scraped_data)

def show_overview(scraped_data):
    """Affiche la page de vue d'ensemble basée sur les données réelles"""
    st.header("🏠 Vue d'ensemble du marché crypto")
    
    # Métriques principales basées sur les données réelles
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        traders_count = 0
        if scraped_data and 'top_traders_extended' in scraped_data:
            traders_data = scraped_data['top_traders_extended']
            traders_count = len(traders_data) if isinstance(traders_data, list) else 0
        st.metric("Total Traders", traders_count)
    
    with col2:
        crypto_count = 0
        if scraped_data and 'market_data_extended' in scraped_data:
            market_data = scraped_data['market_data_extended']
            if isinstance(market_data, dict) and 'cryptocurrencies' in market_data:
                crypto_count = len(market_data['cryptocurrencies'])
        st.metric("Cryptomonnaies", crypto_count)
    
    with col3:
        historical_points = 0
        if scraped_data and 'historical_data' in scraped_data:
            historical_data = scraped_data['historical_data']
            historical_points = len(historical_data) if isinstance(historical_data, list) else 0
        st.metric("Points Historiques", historical_points)
    
    with col4:
        signals_count = 0
        if scraped_data and 'sentiment_data' in scraped_data:
            sentiment_data = scraped_data['sentiment_data']
            if isinstance(sentiment_data, dict) and 'signals' in sentiment_data:
                signals_count = len(sentiment_data['signals'])
        st.metric("Signaux Sentiment", signals_count)
    
    st.markdown("---")
    
    # Graphiques basés sur les données réelles
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("💰 Top 10 Traders par PnL")
        if scraped_data and 'top_traders_extended' in scraped_data:
            traders_data = scraped_data['top_traders_extended']
            if isinstance(traders_data, list) and traders_data:
                df = pd.DataFrame(traders_data)
                if 'total_pnl' in df.columns and 'username' in df.columns:
                    top_traders = df.nlargest(10, 'total_pnl')
                    fig = px.bar(
                        top_traders,
                        x='username',
                        y='total_pnl',
                        title="Top 10 Traders",
                        color='total_pnl',
                        color_continuous_scale='Viridis'
                    )
                    fig.update_layout(height=400)
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.warning("Colonnes manquantes dans les données traders")
            else:
                st.warning("Aucune donnée trader disponible")
        else:
            st.warning("Fichier top_traders_extended.json introuvable")
    
    with col2:
        st.subheader("📊 Prix des Cryptomonnaies")
        if scraped_data and 'market_data_extended' in scraped_data:
            market_data = scraped_data['market_data_extended']
            if isinstance(market_data, dict) and 'cryptocurrencies' in market_data:
                cryptos = market_data['cryptocurrencies']
                if cryptos:
                    df = pd.DataFrame(cryptos)
                    if 'symbol' in df.columns and 'price' in df.columns:
                        fig = px.bar(
                            df,
                            x='symbol',
                            y='price',
                            title="Prix par Crypto",
                            color='price',
                            color_continuous_scale='Blues'
                        )
                        fig.update_layout(height=400)
                        st.plotly_chart(fig, use_container_width=True)
                    else:
                        st.warning("Colonnes manquantes dans les données crypto")
                else:
                    st.warning("Aucune donnée crypto disponible")
            else:
                st.warning("Structure incorrecte pour market_data_extended")
        else:
            st.warning("Fichier market_data_extended.json introuvable")

def show_top_traders(scraped_data):
    """Affiche l'analyse des top traders basée sur les données réelles"""
    st.header("👑 Analyse des Top Traders")
    
    # Données des traders depuis les fichiers JSON
    traders_df = None
    
    if scraped_data:
        # Priorité au fichier top_traders_extended
        if 'top_traders_extended' in scraped_data:
            data = scraped_data['top_traders_extended']
            if isinstance(data, list):
                traders_df = pd.DataFrame(data)
                st.info("📁 Données chargées depuis top_traders_extended.json")
        
        # Sinon, chercher d'autres fichiers traders
        if traders_df is None:
            for filename, data in scraped_data.items():
                if 'trader' in filename.lower() and isinstance(data, list) and 'extended' in filename:
                    traders_df = pd.DataFrame(data)
                    st.info(f"📁 Données chargées depuis {filename}")
                    break
    
    if traders_df is None:
        st.error("❌ Aucune donnée trader trouvée dans les fichiers JSON")
        st.info("Assurez-vous que le fichier top_traders_extended.json existe dans data/processed/")
        return
    
    # Vérifier les colonnes nécessaires
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
    
    # Nettoyer les données pour éviter les erreurs de sérialisation
    display_df_clean = clean_dataframe_for_display(display_df)
    
    st.dataframe(
        display_df_clean[cols_to_show].head(20),
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
    
    # Nettoyer les données pour éviter les erreurs de sérialisation
    df = clean_dataframe_for_display(df)
    
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
    df_display = clean_dataframe_for_display(df)
    st.dataframe(df_display, use_container_width=True)

def show_sentiment_analysis(scraped_data):
    """Affiche l'analyse de sentiment basée sur les données réelles"""
    st.header("📈 Analyse de Sentiment du Marché Crypto")
    
    # Vérifier les données de sentiment
    if not scraped_data or 'sentiment_data' not in scraped_data:
        st.error("❌ Fichier sentiment_data.json introuvable")
        return
    
    sentiment_data = scraped_data['sentiment_data']
    if not isinstance(sentiment_data, dict):
        st.error("❌ Structure incorrecte dans sentiment_data.json")
        return
    
    # === SECTION 1: SENTIMENT GLOBAL ===
    st.subheader("🌍 Vue d'ensemble du marché")
    
    overall_sentiment = sentiment_data.get('overall_sentiment', {})
    if overall_sentiment:
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            score = overall_sentiment.get('score', 0)
            delta_color = "normal" if score >= 0 else "inverse"
            st.metric("📊 Score Global", f"{score:.3f}", delta=f"{score:.3f}", delta_color=delta_color)
        
        with col2:
            label = overall_sentiment.get('label', 'N/A')
            emoji = "🟢" if label == "Bullish" else "🔴" if label == "Bearish" else "🟡"
            st.metric("🎯 Sentiment", f"{emoji} {label}")
        
        with col3:
            confidence = overall_sentiment.get('confidence', 0)
            st.metric("🔍 Confiance", f"{confidence:.1%}")
        
        with col4:
            timestamp = sentiment_data.get('timestamp', 'N/A')
            if timestamp != 'N/A':
                dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                st.metric("🕒 Dernière MAJ", dt.strftime("%H:%M"))
    
    st.markdown("---")
    
    # === SECTION 2: ANALYSE PAR CRYPTO ===
    signals = sentiment_data.get('signals', [])
    if not signals:
        st.warning("Aucun signal trouvé")
        return
    
    df_signals = pd.DataFrame(signals)
    if 'symbol' not in df_signals.columns:
        st.warning("Colonne 'symbol' manquante dans les signaux")
        return
    
    st.subheader("💰 Analyse par Cryptomonnaie")
    
    # Filtres interactifs
    col1, col2, col3 = st.columns(3)
    
    with col1:
        selected_cryptos = st.multiselect(
            "🔍 Filtrer par crypto:",
            options=df_signals['symbol'].unique(),
            default=df_signals['symbol'].unique()[:5]  # Afficher les 5 premières par défaut
        )
    
    with col2:
        sort_by = st.selectbox(
            "📊 Trier par:",
            options=['sentiment_score', 'social_volume', 'news_sentiment'],
            index=0
        )
    
    with col3:
        ascending = st.checkbox("📈 Ordre croissant", value=False)
    
    # Filtrer les données
    df_filtered = df_signals[df_signals['symbol'].isin(selected_cryptos)]
    if sort_by in df_filtered.columns:
        df_filtered = df_filtered.sort_values(sort_by, ascending=ascending)
    
    # === GRAPHIQUES PRINCIPAUX ===
    col1, col2 = st.columns(2)
    
    with col1:
        if 'sentiment_score' in df_filtered.columns:
            # Graphique en barres avec couleurs conditionnelles
            colors = ['#00CC96' if x >= 0 else '#EF553B' for x in df_filtered['sentiment_score']]
            
            fig = go.Figure(data=[
                go.Bar(
                    x=df_filtered['symbol'],
                    y=df_filtered['sentiment_score'],
                    marker_color=colors,
                    text=df_filtered['sentiment_score'].round(3),
                    textposition='auto',
                )
            ])
            fig.update_layout(
                title="🎯 Score de Sentiment par Crypto",
                xaxis_title="Cryptomonnaie",
                yaxis_title="Score (-1 à +1)",
                height=400,
                showlegend=False
            )
            fig.add_hline(y=0, line_dash="dash", line_color="gray", annotation_text="Neutralité")
            st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        if 'social_volume' in df_filtered.columns:
            fig = px.bar(
                df_filtered,
                x='symbol',
                y='social_volume',
                title="📢 Volume Social par Crypto",
                color='social_volume',
                color_continuous_scale='Viridis',
                text='social_volume'
            )
            fig.update_traces(texttemplate='%{text}', textposition='outside')
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)
    
    # === GRAPHIQUES SUPPLÉMENTAIRES ===
    col1, col2 = st.columns(2)
    
    with col1:
        if 'news_sentiment' in df_filtered.columns:
            fig = px.scatter(
                df_filtered,
                x='sentiment_score',
                y='news_sentiment',
                size='social_volume',
                color='symbol',
                title="📰 Sentiment News vs Sentiment Global",
                labels={
                    'sentiment_score': 'Sentiment Global',
                    'news_sentiment': 'Sentiment News'
                }
            )
            fig.add_hline(y=0, line_dash="dash", line_color="gray")
            fig.add_vline(x=0, line_dash="dash", line_color="gray")
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Graphique radar pour comparaison multi-dimensionnelle
        if len(df_filtered) > 0 and 'sentiment_score' in df_filtered.columns:
            # Sélectionner les top 5 cryptos pour le radar
            top_cryptos = df_filtered.head(5)
            
            fig = go.Figure()
            
            for _, crypto in top_cryptos.iterrows():
                values = [
                    (crypto.get('sentiment_score', 0) + 1) * 50,  # Normaliser de 0 à 100
                    crypto.get('social_volume', 0) / 10,  # Ajuster l'échelle
                    (crypto.get('news_sentiment', 0) + 1) * 50,  # Normaliser de 0 à 100
                ]
                
                fig.add_trace(go.Scatterpolar(
                    r=values + [values[0]],  # Fermer le polygone
                    theta=['Sentiment', 'Volume Social', 'News', 'Sentiment'],
                    fill='toself',
                    name=crypto['symbol'],
                    opacity=0.6
                ))
            
            fig.update_layout(
                polar=dict(
                    radialaxis=dict(
                        visible=True,
                        range=[0, 100]
                    )),
                title="🎯 Comparaison Multi-dimensionnelle",
                height=400
            )
            st.plotly_chart(fig, use_container_width=True)
    
    # === TABLEAU DE SYNTHESE ===
    st.subheader("📊 Tableau de Synthèse")
    
    # Créer un tableau enrichi
    display_df = df_filtered.copy()
    
    # Ajouter des colonnes calculées
    if 'sentiment_score' in display_df.columns:
        display_df['Tendance'] = display_df['sentiment_score'].apply(
            lambda x: "🟢 Bullish" if x > 0.1 else "🔴 Bearish" if x < -0.1 else "🟡 Neutre"
        )
    
    if 'social_volume' in display_df.columns:
        display_df['Activité'] = display_df['social_volume'].apply(
            lambda x: "🔥 Élevée" if x > 800 else "📈 Moyenne" if x > 400 else "📉 Faible"
        )
    
    # Formater les colonnes numériques
    cols_to_format = ['sentiment_score', 'news_sentiment']
    for col in cols_to_format:
        if col in display_df.columns:
            display_df[col] = display_df[col].apply(lambda x: f"{x:.3f}")
    
    # Sélectionner les colonnes à afficher
    display_cols = ['symbol', 'Tendance', 'sentiment_score', 'social_volume', 'news_sentiment', 'Activité']
    available_cols = [col for col in display_cols if col in display_df.columns]
    
    # Nettoyer les données pour éviter les erreurs de sérialisation
    display_df_clean = clean_dataframe_for_display(display_df)
    
    st.dataframe(
        display_df_clean[available_cols],
        use_container_width=True,
        column_config={
            "symbol": st.column_config.TextColumn("Crypto", width="small"),
            "sentiment_score": st.column_config.NumberColumn("Score Sentiment", width="small"),
            "social_volume": st.column_config.NumberColumn("Volume Social", width="small"),
            "news_sentiment": st.column_config.NumberColumn("Sentiment News", width="small"),
        }
    )
    
    # === SIGNAUX DETAILLES ===
    st.subheader("🚨 Signaux de Trading Détaillés")
    
    # Restructurer les signaux pour l'affichage
    detailed_signals = []
    for signal in signals:
        if signal['symbol'] in selected_cryptos and 'signals' in signal:
            for sig in signal['signals']:
                # Calculer l'âge du signal
                timestamp_str = sig.get('timestamp', '')
                age = 'N/A'
                if timestamp_str:
                    try:
                        sig_time = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
                        now = datetime.now(sig_time.tzinfo)
                        delta = now - sig_time
                        if delta.days > 0:
                            age = f"{delta.days}j"
                        else:
                            hours = delta.seconds // 3600
                            age = f"{hours}h"
                    except:
                        age = 'N/A'
                
                # Émoticônes pour les directions et forces
                direction_emoji = {
                    'Bullish': '🟢',
                    'Bearish': '🔴',
                    'Neutral': '🟡'
                }
                
                strength_emoji = {
                    'Strong': '💪',
                    'Moderate': '👍',
                    'Weak': '👌'
                }
                
                detailed_signals.append({
                    'Crypto': signal.get('symbol', 'N/A'),
                    'Type': sig.get('type', 'N/A'),
                    'Direction': f"{direction_emoji.get(sig.get('direction', ''), '')} {sig.get('direction', 'N/A')}",
                    'Force': f"{strength_emoji.get(sig.get('strength', ''), '')} {sig.get('strength', 'N/A')}",
                    'Confiance': f"{sig.get('confidence', 0):.0%}",
                    'Âge': age
                })
    
    if detailed_signals:
        df_detailed = pd.DataFrame(detailed_signals)
        
        # Filtres pour les signaux
        col1, col2, col3 = st.columns(3)
        
        with col1:
            signal_types = st.multiselect(
                "Type de signal:",
                options=df_detailed['Type'].unique(),
                default=df_detailed['Type'].unique()
            )
        
        with col2:
            directions = st.multiselect(
                "Direction:",
                options=[d.split(' ', 1)[1] if ' ' in d else d for d in df_detailed['Direction'].unique()],
                default=[d.split(' ', 1)[1] if ' ' in d else d for d in df_detailed['Direction'].unique()]
            )
        
        with col3:
            min_confidence = st.slider(
                "Confiance minimale:",
                min_value=0,
                max_value=100,
                value=0,
                step=5
            )
        
        # Filtrer les signaux détaillés
        filtered_detailed = df_detailed[
            (df_detailed['Type'].isin(signal_types)) &
            (df_detailed['Direction'].str.contains('|'.join(directions), na=False)) &
            (df_detailed['Confiance'].str.rstrip('%').astype(float) >= min_confidence)
        ]
        
        # Nettoyer les données pour éviter les erreurs de sérialisation
        filtered_detailed_clean = clean_dataframe_for_display(filtered_detailed)
        
        st.dataframe(filtered_detailed_clean, use_container_width=True)
        
        # Statistiques des signaux
        col1, col2, col3 = st.columns(3)
        
        with col1:
            bullish_count = len([s for s in detailed_signals if 'Bullish' in s['Direction']])
            st.metric("🟢 Signaux Bullish", bullish_count)
        
        with col2:
            bearish_count = len([s for s in detailed_signals if 'Bearish' in s['Direction']])
            st.metric("🔴 Signaux Bearish", bearish_count)
        
        with col3:
            avg_confidence = np.mean([float(s['Confiance'].rstrip('%')) for s in detailed_signals])
            st.metric("📊 Confiance Moyenne", f"{avg_confidence:.0f}%")
    
    else:
        st.info("Aucun signal détaillé trouvé pour les cryptos sélectionnées")
    
    # === DONNEES BRUTES (dans un expandeur) ===
    with st.expander("🔍 Voir les données brutes"):
        st.json(sentiment_data)

def show_data_status(scraped_data):
    """Affiche l'état des données disponibles"""
    st.header("⚙️ État des Données")
    
    if not scraped_data:
        st.error("❌ Aucune donnée chargée")
        return
    
    st.success(f"✅ {len(scraped_data)} fichiers de données chargés")
    
    # Tableau de statut des fichiers
    file_status = []
    expected_files = [
        'top_traders_extended',
        'market_data_extended', 
        'historical_data',
        'sentiment_data'
    ]
    
    for file in expected_files:
        if file in scraped_data:
            data = scraped_data[file]
            if isinstance(data, list):
                count = len(data)
                status = f"✅ {count} entrées"
            elif isinstance(data, dict):
                if 'cryptocurrencies' in data:
                    count = len(data['cryptocurrencies'])
                    status = f"✅ {count} cryptos"
                elif 'signals' in data:
                    count = len(data['signals'])
                    status = f"✅ {count} signaux"
                else:
                    status = "✅ Données disponibles"
            else:
                status = "⚠️ Format inattendu"
        else:
            status = "❌ Manquant"
        
        file_status.append({
            'Fichier': f"{file}.json",
            'Statut': status
        })
    
    df_status = pd.DataFrame(file_status)
    st.dataframe(df_status, use_container_width=True)
    
    # Détails des fichiers
    st.subheader("📁 Détails des fichiers")
    
    for filename, data in scraped_data.items():
        with st.expander(f"📄 {filename}.json"):
            st.write(f"**Type:** {type(data)}")
            
            if isinstance(data, list):
                st.write(f"**Nombre d'entrées:** {len(data)}")
                if data:
                    st.write(f"**Première entrée:**")
                    st.json(data[0])
            elif isinstance(data, dict):
                st.write(f"**Clés principales:** {list(data.keys())}")
                if 'cryptocurrencies' in data:
                    st.write(f"**Nombre de cryptos:** {len(data['cryptocurrencies'])}")
                elif 'signals' in data:
                    st.write(f"**Nombre de signaux:** {len(data['signals'])}")
            else:
                st.json(data)

if __name__ == "__main__":
    main()
