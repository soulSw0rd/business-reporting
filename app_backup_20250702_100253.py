import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import yfinance as yf
from datetime import datetime, timedelta
import seaborn as sns
import matplotlib.pyplot as plt
import requests
import json
import os
from pathlib import Path

# Configuration de la page
st.set_page_config(
    page_title="CryptoTrader Dashboard - Business Intelligence",
    page_icon="₿",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS personnalisé pour améliorer l'apparence
st.markdown("""
<style>
    .main {
        padding: 1rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
    .sidebar .sidebar-content {
        background-color: #1e1e1e;
    }
    .stSelectbox > div > div {
        background-color: white;
    }
    h1 {
        color: #2c3e50;
        text-align: center;
        padding-bottom: 2rem;
    }
    .crypto-positive {
        color: #00d4aa;
        font-weight: bold;
    }
    .crypto-negative {
        color: #ff6b6b;
        font-weight: bold;
    }
    .trader-card {
        border: 1px solid #ddd;
        border-radius: 8px;
        padding: 1rem;
        margin: 0.5rem 0;
        background-color: #f8f9fa;
    }
</style>
""", unsafe_allow_html=True)

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

@st.cache_data(ttl=300)
def get_api_data():
    """Récupère les données via l'API FastAPI si elle est disponible"""
    try:
        response = requests.get("http://127.0.0.1:8000/health", timeout=5)
        if response.status_code == 200:
            # L'API est disponible, récupérer les données
            traders_response = requests.get("http://127.0.0.1:8000/top-traders", timeout=10)
            if traders_response.status_code == 200:
                return traders_response.json()
    except requests.exceptions.RequestException:
        pass
    return None

@st.cache_data
def generate_crypto_sample_data():
    """Génère des données de démonstration crypto pour l'application"""
    np.random.seed(42)
    dates = pd.date_range(start='2024-01-01', end='2024-12-31', freq='h')
    
    # Données de trading crypto
    crypto_symbols = ['BTC', 'ETH', 'ADA', 'DOT', 'LINK', 'SOL', 'AVAX', 'MATIC']
    trading_data = []
    
    for date in dates[::24]:  # Une fois par jour
        for symbol in crypto_symbols:
            base_price = {'BTC': 45000, 'ETH': 3000, 'ADA': 0.5, 'DOT': 8, 
                         'LINK': 15, 'SOL': 100, 'AVAX': 40, 'MATIC': 1}[symbol]
            
            price = base_price * (1 + np.random.normal(0, 0.05))
            volume = np.random.lognormal(15, 1)
            
            trading_data.append({
                'Date': date,
                'Symbol': symbol,
                'Price': price,
                'Volume': volume,
                'Market_Cap': price * np.random.uniform(100000000, 1000000000),
                'Change_24h': np.random.normal(0, 5),
                'Trader_Sentiment': np.random.choice(['Bullish', 'Bearish', 'Neutral'], 
                                                   p=[0.4, 0.3, 0.3])
            })
    
    crypto_df = pd.DataFrame(trading_data)
    
    # Données des top traders (simulation)
    top_traders_data = []
    for i in range(20):
        total_pnl = np.random.normal(50000, 20000)
        win_rate = np.random.uniform(0.55, 0.85)
        
        top_traders_data.append({
            'trader_id': f"Trader_{i+1}",
            'rank': i + 1,
            'username': f"Trader_{i+1}",
            'total_pnl': total_pnl,
            'win_rate': win_rate,
            'total_trades': np.random.poisson(500),
            'roi_percentage': np.random.uniform(15, 200),
            'favorite_pairs': [np.random.choice(['BTC/USDT', 'ETH/USDT', 'ADA/USDT', 'SOL/USDT'])],
            'last_active': np.random.choice(['1h', '2h', '6h', '12h', '1d']),
            'followers': np.random.poisson(1000),
            'copy_traders': np.random.poisson(50)
        })
    
    traders_df = pd.DataFrame(top_traders_data)
    
    return crypto_df, traders_df

@st.cache_data
def get_crypto_prices(symbols, period="1d"):
    """Récupère les prix crypto en temps réel"""
    prices_data = {}
    for symbol in symbols:
        try:
            ticker = f"{symbol}-USD"
            stock = yf.Ticker(ticker)
            data = stock.history(period=period)
            if not data.empty:
                prices_data[symbol] = data
        except:
            continue
    return prices_data

def main():
    st.title("₿ CryptoTrader Dashboard - Business Intelligence")
    st.markdown("---")
    
    # Sidebar pour la navigation
    st.sidebar.title("🚀 Navigation")
    page = st.sidebar.selectbox(
        "Choisir une page",
        ["🏠 Vue d'ensemble", "👑 Top Traders", "📊 Analyse Crypto", " Sentiment", "⚙️ Données"]
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
    elif page == "� Sentiment":
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
        st.subheader("� Top 10 Traders par PnL")
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
    
    st.write(f"📊 {len(filtered_traders)} traders correspondent aux critères")        # Graphiques d'analyse des traders
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("💰 Top 10 - PnL Total")
        top_pnl = filtered_traders.nlargest(10, 'total_pnl')
        
        fig = px.bar(
            top_pnl,
            x='username',
            y='total_pnl',
            color='win_rate',
            title="Traders avec le plus gros PnL",
            color_continuous_scale='Viridis'
        )
        fig.update_xaxes(tickangle=45)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("🎯 Corrélation Win Rate vs ROI")
        fig = px.scatter(
            filtered_traders,
            x='win_rate',
            y='roi_percentage',
            size='total_trades',
            color='total_pnl',
            hover_data=['username', 'followers'],
            title="Performance des traders",
            color_continuous_scale='RdYlGn'
        )
        st.plotly_chart(fig, use_container_width=True)
    
    # Tableau détaillé des top traders
    st.subheader("📋 Classement détaillé")
    
    # Formatage des colonnes pour l'affichage
    display_df = filtered_traders.copy()
    if 'total_pnl' in display_df.columns:
        display_df['total_pnl'] = display_df['total_pnl'].apply(lambda x: f"${x:,.2f}")
    if 'win_rate' in display_df.columns:
        display_df['win_rate'] = display_df['win_rate'].apply(lambda x: f"{x:.1%}")
    if 'roi_percentage' in display_df.columns:
        display_df['roi_percentage'] = display_df['roi_percentage'].apply(lambda x: f"{x:.1f}%")
    
    st.dataframe(
        display_df.sort_values('rank' if 'rank' in display_df.columns else 'total_pnl', ascending=True if 'rank' in display_df.columns else False),
        use_container_width=True
    )

def show_crypto_analysis(crypto_data):
    """Affiche l'analyse des cryptomonnaies"""
    st.header("📊 Analyse du marché crypto")
    
    # Sélection de crypto et période
    col1, col2, col3 = st.columns(3)
    
    with col1:
        selected_crypto = st.selectbox(
            "Cryptomonnaie",
            crypto_data['Symbol'].unique()
        )
    
    with col2:
        timeframe = st.selectbox(
            "Période d'analyse",
            ["7 jours", "30 jours", "90 jours", "1 an"]
        )
    
    with col3:
        analysis_type = st.selectbox(
            "Type d'analyse",
            ["Prix", "Volume", "Market Cap", "Sentiment"]
        )
    
    # Filtrage des données
    crypto_filtered = crypto_data[crypto_data['Symbol'] == selected_crypto].copy()
    crypto_filtered = crypto_filtered.sort_values('Date')
    
    # Métriques de base
    if not crypto_filtered.empty:
        latest = crypto_filtered.iloc[-1]
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                f"💰 Prix {selected_crypto}",
                f"${latest['Price']:,.2f}",
                f"{latest['Change_24h']:+.2f}%"
            )
        
        with col2:
            avg_volume = crypto_filtered['Volume'].mean()
            st.metric("📊 Volume moyen", f"${avg_volume/1e6:.1f}M")
        
        with col3:
            st.metric(
                "🏪 Market Cap",
                f"${latest['Market_Cap']/1e9:.2f}B"
            )
        
        with col4:
            sentiment_counts = crypto_filtered['Trader_Sentiment'].value_counts()
            dominant_sentiment = sentiment_counts.index[0]
            sentiment_emoji = {"Bullish": "🟢", "Bearish": "🔴", "Neutral": "🟡"}
            st.metric(
                "📈 Sentiment",
                f"{sentiment_emoji.get(dominant_sentiment, '⚪')} {dominant_sentiment}"
            )
    
    # Graphiques selon le type d'analyse
    if analysis_type == "Prix":
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=crypto_filtered['Date'],
            y=crypto_filtered['Price'],
            mode='lines',
            name=f"Prix {selected_crypto}",
            line=dict(color='#FFD700', width=2)
        ))
        fig.update_layout(
            title=f"Évolution du prix - {selected_crypto}",
            xaxis_title="Date",
            yaxis_title="Prix ($)",
            height=500
        )
        st.plotly_chart(fig, use_container_width=True)
    
    elif analysis_type == "Volume":
        fig = px.bar(
            crypto_filtered,
            x='Date',
            y='Volume',
            title=f"Volume de trading - {selected_crypto}",
            color='Volume',
            color_continuous_scale='Blues'
        )
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)
    
    elif analysis_type == "Market Cap":
        fig = px.area(
            crypto_filtered,
            x='Date',
            y='Market_Cap',
            title=f"Évolution Market Cap - {selected_crypto}",
            color_discrete_sequence=['#00d4aa']
        )
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)
    
    elif analysis_type == "Sentiment":
        sentiment_data = crypto_filtered.groupby(['Date', 'Trader_Sentiment']).size().reset_index(name='Count')
        
        fig = px.bar(
            sentiment_data,
            x='Date',
            y='Count',
            color='Trader_Sentiment',
            title=f"Évolution du sentiment - {selected_crypto}",
            color_discrete_map={
                'Bullish': '#00d4aa',
                'Bearish': '#ff6b6b',
                'Neutral': '#ffd93d'
            }
        )
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)

def show_live_data():
    """Affiche les données crypto en temps réel"""
    st.header("🔥 Données crypto en temps réel")
    
    # Sélection des cryptos à suivre
    crypto_symbols = st.multiselect(
        "Sélectionner les cryptomonnaies",
        ["BTC", "ETH", "ADA", "DOT", "LINK", "SOL", "AVAX", "MATIC"],
        default=["BTC", "ETH", "ADA"]
    )
    
    if crypto_symbols:
        # Récupération des données live
        with st.spinner("Récupération des données en temps réel..."):
            live_data = get_crypto_prices(crypto_symbols, "1d")
        
        if live_data:
            # Affichage des métriques
            cols = st.columns(len(crypto_symbols))
            
            for i, symbol in enumerate(crypto_symbols):
                if symbol in live_data:
                    data = live_data[symbol]
                    latest_price = data['Close'].iloc[-1]
                    
                    # Calculer le changement seulement s'il y a assez de données
                    if len(data) >= 2:
                        change = ((data['Close'].iloc[-1] / data['Close'].iloc[-2]) - 1) * 100
                    else:
                        change = 0.0
                    
                    with cols[i]:
                        color = "crypto-positive" if change >= 0 else "crypto-negative"
                        st.markdown(f'<div class="{color}">', unsafe_allow_html=True)
                        st.metric(
                            f"{symbol}",
                            f"${latest_price:,.2f}",
                            f"{change:+.2f}%"
                        )
                        st.markdown('</div>', unsafe_allow_html=True)
            
            # Graphique comparatif
            st.subheader("📈 Comparaison des performances")
            
            fig = go.Figure()
            for symbol in crypto_symbols:
                if symbol in live_data:
                    data = live_data[symbol]
                    # Normalisation pour comparaison
                    normalized = (data['Close'] / data['Close'].iloc[0]) * 100
                    
                    fig.add_trace(go.Scatter(
                        x=data.index,
                        y=normalized,
                        mode='lines',
                        name=symbol,
                        line=dict(width=2)
                    ))
            
            fig.update_layout(
                title="Performance relative (base 100)",
                xaxis_title="Date",
                yaxis_title="Performance relative",
                height=500
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Tableau des données détaillées
            st.subheader("📊 Données détaillées")
            for symbol in crypto_symbols:
                if symbol in live_data:
                    with st.expander(f"Données {symbol}"):
                        recent_data = live_data[symbol].tail(10).round(2)
                        st.dataframe(recent_data, use_container_width=True)
        else:
            st.error("Aucune donnée n'a pu être récupérée. Vérifiez votre connexion internet.")

def show_portfolio_performance(crypto_data):
    """Affiche l'analyse de performance de portfolio"""
    st.header("📈 Performance de Portfolio")
    
    st.write("### 💼 Simulateur de Portfolio")
    
    # Configuration du portfolio
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**Allocation du portfolio**")
        crypto_list = crypto_data['Symbol'].unique()
        allocations = {}
        
        remaining = 100.0
        for i, crypto in enumerate(crypto_list[:-1]):
            max_val = max(1.0, min(100.0, remaining))  # Ensure max_val is always >= 1.0
            default_val = max(0.0, min(20.0, remaining))
            
            allocations[crypto] = st.slider(
                f"{crypto} (%)",
                0.0, max_val, 
                default_val,
                step=1.0,
                key=f"alloc_{crypto}"
            )
            remaining = max(0.0, remaining - allocations[crypto])  # Ensure remaining doesn't go negative
        
        # Dernière crypto prend le reste
        allocations[crypto_list[-1]] = max(0.0, remaining)
        st.write(f"{crypto_list[-1]}: {remaining:.1f}%")
    
    with col2:
        st.write("**Paramètres**")
        initial_investment = st.number_input(
            "Investissement initial ($)",
            min_value=1000,
            max_value=1000000,
            value=10000,
            step=1000
        )
        
        rebalance_freq = st.selectbox(
            "Fréquence de rééquilibrage",
            ["Jamais", "Mensuel", "Trimestriel", "Annuel"]
        )
    
    # Calcul de performance
    portfolio_value = []
    dates = sorted(crypto_data['Date'].unique())
    
    for date in dates:
        daily_data = crypto_data[crypto_data['Date'] == date]
        daily_value = 0
        
        for crypto, allocation in allocations.items():
            crypto_data_day = daily_data[daily_data['Symbol'] == crypto]
            if not crypto_data_day.empty:
                price = crypto_data_day['Price'].iloc[0]
                daily_value += (allocation / 100) * initial_investment * (price / crypto_data[crypto_data['Symbol'] == crypto]['Price'].iloc[0])
        
        portfolio_value.append({
            'Date': date,
            'Portfolio_Value': daily_value if daily_value > 0 else initial_investment
        })
    
    portfolio_df = pd.DataFrame(portfolio_value)
    
    # Graphique de performance
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=portfolio_df['Date'],
        y=portfolio_df['Portfolio_Value'],
        mode='lines',
        name='Portfolio',
        line=dict(color='#00d4aa', width=3)
    ))
    
    # Ligne de référence (investissement initial)
    fig.add_hline(
        y=initial_investment,
        line_dash="dash",
        line_color="gray",
        annotation_text="Investissement initial"
    )
    
    fig.update_layout(
        title="Évolution de la valeur du portfolio",
        xaxis_title="Date",
        yaxis_title="Valeur ($)",
        height=500
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Métriques de performance
    final_value = portfolio_df['Portfolio_Value'].iloc[-1]
    total_return = ((final_value / initial_investment) - 1) * 100
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(
            "💰 Valeur finale",
            f"${final_value:,.2f}",
            f"{total_return:+.2f}%"
        )
    
    with col2:
        max_value = portfolio_df['Portfolio_Value'].max()
        st.metric("📈 Pic maximum", f"${max_value:,.2f}")
    
    with col3:
        min_value = portfolio_df['Portfolio_Value'].min()
        max_drawdown = ((min_value / max_value) - 1) * 100
        st.metric("📉 Drawdown max", f"{max_drawdown:.2f}%")

def show_api_status(api_data, scraped_data):
    """Affiche le statut de l'API et des données"""
    st.header("⚙️ Statut du système")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🔌 API FastAPI")
        
        if api_data:
            st.success("✅ API connectée et fonctionnelle")
            st.info("📡 Endpoint: http://127.0.0.1:8000")
            
            # Test des endpoints
            endpoints = [
                "/health",
                "/top-traders",
                "/docs"
            ]
            
            for endpoint in endpoints:
                try:
                    response = requests.get(f"http://127.0.0.1:8000{endpoint}", timeout=5)
                    status = "✅" if response.status_code == 200 else "❌"
                    st.write(f"{status} {endpoint} - Status: {response.status_code}")
                except:
                    st.write(f"❌ {endpoint} - Non accessible")
        else:
            st.error("❌ API non accessible")
            st.write("Pour démarrer l'API:")
            st.code("uvicorn SRC.api.main:app --host 0.0.0.0 --port 8000")
    
    with col2:
        st.subheader("📁 Données locales")
        
        if scraped_data:
            st.success(f"✅ {len(scraped_data)} fichiers de données trouvés")
            
            for filename, data in scraped_data.items():
                file_size = len(str(data)) if data else 0
                data_type = type(data).__name__
                
                st.write(f"📄 **{filename}**")
                st.write(f"   - Type: {data_type}")
                st.write(f"   - Taille: ~{file_size} caractères")
                
                if isinstance(data, list):
                    st.write(f"   - Éléments: {len(data)}")
        else:
            st.warning("⚠️ Aucune donnée scrapée trouvée")
            st.write("Dossier de données: `data/processed/`")
    
    # Section de diagnostic
    st.subheader("🔧 Diagnostic du système")
    
    # Test de connectivité
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.write("**Dépendances**")
        try:
            import requests
            st.write("✅ requests")
        except:
            st.write("❌ requests")
        
        try:
            import pandas
            st.write("✅ pandas")
        except:
            st.write("❌ pandas")
        
        try:
            import yfinance
            st.write("✅ yfinance")
        except:
            st.write("❌ yfinance")
    
    with col2:
        st.write("**Dossiers**")
        data_path = Path("data/processed")
        src_path = Path("SRC")
        
        st.write(f"{'✅' if data_path.exists() else '❌'} data/processed/")
        st.write(f"{'✅' if src_path.exists() else '❌'} SRC/")
        
        if data_path.exists():
            json_files = list(data_path.glob("*.json"))
            st.write(f"📄 {len(json_files)} fichiers JSON")
    
    with col3:
        st.write("**Connectivité**")
        # Test connexion internet
        try:
            response = requests.get("https://httpbin.org/status/200", timeout=5)
            st.write("✅ Internet")
        except:
            st.write("❌ Internet")
        
        # Test API Yahoo Finance
        try:
            yf.Ticker("BTC-USD").history(period="1d")
            st.write("✅ Yahoo Finance")
        except:
            st.write("❌ Yahoo Finance")

if __name__ == "__main__":
    main()

# CSS personnalisé pour améliorer l'apparence
st.markdown("""
<style>
    .main {
        padding: 1rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
    .sidebar .sidebar-content {
        background-color: #1e1e1e;
    }
    .stSelectbox > div > div {
        background-color: white;
    }
    h1 {
        color: #2c3e50;
        text-align: center;
        padding-bottom: 2rem;
    }
    .kpi-container {
        display: flex;
        justify-content: space-around;
        margin-bottom: 2rem;
    }
</style>
""", unsafe_allow_html=True)

# Fonction pour générer des données de démonstration
@st.cache_data
def generate_sample_data():
    """Génère des données de démonstration pour l'application"""
    np.random.seed(42)
    dates = pd.date_range(start='2023-01-01', end='2024-12-31', freq='D')
    
    # Données de ventes
    sales_data = pd.DataFrame({
        'Date': dates,
        'Ventes': np.random.normal(10000, 2000, len(dates)).cumsum(),
        'Coûts': np.random.normal(6000, 1500, len(dates)).cumsum(),
        'Profit': np.random.normal(4000, 1000, len(dates)).cumsum(),
        'Région': np.random.choice(['Nord', 'Sud', 'Est', 'Ouest'], len(dates)),
        'Produit': np.random.choice(['Produit A', 'Produit B', 'Produit C', 'Produit D'], len(dates))
    })
    
    # Données de performance financière
    financial_data = pd.DataFrame({
        'Métrique': ['Chiffre d\'affaires', 'Bénéfice brut', 'Bénéfice net', 'EBITDA', 'ROI'],
        'Valeur_Actuelle': [2500000, 1200000, 800000, 950000, 15.2],
        'Valeur_Précédente': [2200000, 1100000, 750000, 900000, 14.1],
        'Objectif': [2800000, 1400000, 900000, 1100000, 16.0]
    })
    
    return sales_data, financial_data

@st.cache_data
def get_stock_data(symbol, period="1y"):
    """Récupère les données boursières en temps réel"""
    try:
        stock = yf.Ticker(symbol)
        data = stock.history(period=period)
        return data
    except:
        return None

def main():
    st.title("📊 Dashboard Business Intelligence")
    st.markdown("---")
    
    # Sidebar pour la navigation
    st.sidebar.title("Navigation")
    page = st.sidebar.selectbox(
        "Choisir une page",
        ["Vue d'ensemble", "Analyse des ventes", "Performance financière", "Données boursières", "Analyse comparative"]
    )
    
    # Génération des données
    sales_data, financial_data = generate_sample_data()
    
    if page == "Vue d'ensemble":
        show_overview(sales_data, financial_data)
    elif page == "Analyse des ventes":
        show_sales_analysis(sales_data)
    elif page == "Performance financière":
        show_financial_performance(financial_data)
    elif page == "Données boursières":
        show_stock_analysis()
    elif page == "Analyse comparative":
        show_comparative_analysis(sales_data)

def show_overview(sales_data, financial_data):
    """Affiche la page de vue d'ensemble"""
    st.header("🎯 Vue d'ensemble")
    
    # KPI principaux
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="💰 CA Total",
            value=f"{financial_data.iloc[0]['Valeur_Actuelle']:,.0f} €",
            delta=f"{financial_data.iloc[0]['Valeur_Actuelle'] - financial_data.iloc[0]['Valeur_Précédente']:,.0f} €"
        )
    
    with col2:
        st.metric(
            label="📈 Bénéfice Net",
            value=f"{financial_data.iloc[2]['Valeur_Actuelle']:,.0f} €",
            delta=f"{financial_data.iloc[2]['Valeur_Actuelle'] - financial_data.iloc[2]['Valeur_Précédente']:,.0f} €"
        )
    
    with col3:
        roi_current = financial_data.iloc[4]['Valeur_Actuelle']
        roi_previous = financial_data.iloc[4]['Valeur_Précédente']
        st.metric(
            label="🎯 ROI",
            value=f"{roi_current:.1f}%",
            delta=f"{roi_current - roi_previous:.1f}%"
        )
    
    with col4:
        total_sales = sales_data['Ventes'].iloc[-1]
        st.metric(
            label="🛒 Ventes Totales",
            value=f"{total_sales:,.0f} €",
            delta="📊"
        )
    
    st.markdown("---")
    
    # Graphiques de vue d'ensemble
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📊 Évolution des ventes mensuelles")
        monthly_sales = sales_data.groupby(sales_data['Date'].dt.to_period('M'))['Ventes'].sum().reset_index()
        monthly_sales['Date'] = monthly_sales['Date'].astype(str)
        
        fig = px.line(
            monthly_sales, 
            x='Date', 
            y='Ventes',
            title="Évolution mensuelle des ventes",
            color_discrete_sequence=['#3498db']
        )
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("🎯 Atteinte des objectifs")
        fig = go.Figure()
        
        fig.add_trace(go.Bar(
            name='Actuel',
            x=financial_data['Métrique'],
            y=financial_data['Valeur_Actuelle'],
            marker_color='#2ecc71'
        ))
        
        fig.add_trace(go.Bar(
            name='Objectif',
            x=financial_data['Métrique'],
            y=financial_data['Objectif'],
            marker_color='#e74c3c',
            opacity=0.7
        ))
        
        fig.update_layout(
            title="Performance vs Objectifs",
            barmode='group',
            height=400
        )
        st.plotly_chart(fig, use_container_width=True)

def show_sales_analysis(sales_data):
    """Affiche l'analyse des ventes"""
    st.header("📈 Analyse des ventes")
    
    # Filtres
    col1, col2, col3 = st.columns(3)
    
    with col1:
        start_date = st.date_input(
            "Date de début",
            value=sales_data['Date'].min(),
            min_value=sales_data['Date'].min(),
            max_value=sales_data['Date'].max()
        )
    
    with col2:
        end_date = st.date_input(
            "Date de fin",
            value=sales_data['Date'].max(),
            min_value=sales_data['Date'].min(),
            max_value=sales_data['Date'].max()
        )
    
    with col3:
        selected_region = st.selectbox(
            "Région",
            options=['Toutes'] + list(sales_data['Région'].unique())
        )
    
    # Filtrage des données
    filtered_data = sales_data[
        (sales_data['Date'] >= pd.to_datetime(start_date)) &
        (sales_data['Date'] <= pd.to_datetime(end_date))
    ]
    
    if selected_region != 'Toutes':
        filtered_data = filtered_data[filtered_data['Région'] == selected_region]
    
    # Graphiques d'analyse
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📊 Ventes par région")
        region_sales = filtered_data.groupby('Région')['Ventes'].sum().reset_index()
        
        fig = px.pie(
            region_sales,
            values='Ventes',
            names='Région',
            title="Répartition des ventes par région",
            color_discrete_sequence=px.colors.qualitative.Set3
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("🛍️ Performance par produit")
        product_sales = filtered_data.groupby('Produit')['Ventes'].sum().reset_index()
        
        fig = px.bar(
            product_sales,
            x='Produit',
            y='Ventes',
            title="Ventes par produit",
            color='Ventes',
            color_continuous_scale='Blues'
        )
        st.plotly_chart(fig, use_container_width=True)
    
    # Tableau de données détaillées
    st.subheader("📋 Données détaillées")
    st.dataframe(
        filtered_data.groupby(['Région', 'Produit']).agg({
            'Ventes': 'sum',
            'Coûts': 'sum',
            'Profit': 'sum'
        }).round(2),
        use_container_width=True
    )

def show_financial_performance(financial_data):
    """Affiche la performance financière"""
    st.header("💹 Performance financière")
    
    # Tableau de bord financier
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📊 Métriques financières")
        
        for index, row in financial_data.iterrows():
            progress = row['Valeur_Actuelle'] / row['Objectif']
            st.metric(
                label=row['Métrique'],
                value=f"{row['Valeur_Actuelle']:,.0f}" + (" €" if "€" not in str(row['Valeur_Actuelle']) and "%" not in str(row['Valeur_Actuelle']) else ""),
                delta=f"{row['Valeur_Actuelle'] - row['Valeur_Précédente']:+,.0f}"
            )
            st.progress(min(progress, 1.0))
            st.write(f"Objectif: {row['Objectif']:,.0f}")
            st.markdown("---")
    
    with col2:
        st.subheader("📈 Évolution temporelle")
        
        # Simulation d'une évolution temporelle
        months = ['Jan', 'Fév', 'Mar', 'Avr', 'Mai', 'Jun', 'Jul', 'Aoû', 'Sep', 'Oct', 'Nov', 'Déc']
        
        fig = go.Figure()
        
        # Données simulées pour le chiffre d'affaires mensuel
        monthly_revenue = np.cumsum(np.random.normal(200000, 50000, 12))
        monthly_profit = monthly_revenue * 0.35 + np.random.normal(0, 10000, 12)
        
        fig.add_trace(go.Scatter(
            x=months,
            y=monthly_revenue,
            mode='lines+markers',
            name='Chiffre d\'affaires',
            line=dict(color='#3498db', width=3)
        ))
        
        fig.add_trace(go.Scatter(
            x=months,
            y=monthly_profit,
            mode='lines+markers',
            name='Bénéfice',
            line=dict(color='#2ecc71', width=3)
        ))
        
        fig.update_layout(
            title="Évolution financière mensuelle",
            xaxis_title="Mois",
            yaxis_title="Montant (€)",
            height=500
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    # Analyse de rentabilité
    st.subheader("💰 Analyse de rentabilité")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.info("🎯 **Marge brute**")
        marge_brute = (financial_data.iloc[1]['Valeur_Actuelle'] / financial_data.iloc[0]['Valeur_Actuelle']) * 100
        st.metric("Marge brute", f"{marge_brute:.1f}%")
    
    with col2:
        st.info("📊 **Marge nette**")
        marge_nette = (financial_data.iloc[2]['Valeur_Actuelle'] / financial_data.iloc[0]['Valeur_Actuelle']) * 100
        st.metric("Marge nette", f"{marge_nette:.1f}%")
    
    with col3:
        st.info("🚀 **Croissance**")
        croissance = ((financial_data.iloc[0]['Valeur_Actuelle'] / financial_data.iloc[0]['Valeur_Précédente']) - 1) * 100
        st.metric("Croissance CA", f"{croissance:.1f}%")

def show_stock_analysis():
    """Affiche l'analyse des données boursières"""
    st.header("📈 Analyse boursière")
    
    # Sélection d'actions
    col1, col2, col3 = st.columns(3)
    
    with col1:
        symbol = st.selectbox(
            "Symbole boursier",
            ["AAPL", "GOOGL", "MSFT", "TSLA", "AMZN", "NVDA", "META"],
            index=0
        )
    
    with col2:
        period = st.selectbox(
            "Période",
            ["1mo", "3mo", "6mo", "1y", "2y", "5y"],
            index=3
        )
    
    with col3:
        analysis_type = st.selectbox(
            "Type d'analyse",
            ["Prix", "Volume", "Volatilité", "Rendements"]
        )
    
    # Récupération des données
    with st.spinner(f"Chargement des données pour {symbol}..."):
        stock_data = get_stock_data(symbol, period)
    
    if stock_data is not None and not stock_data.empty:
        # Informations de base
        latest_price = stock_data['Close'].iloc[-1]
        price_change = stock_data['Close'].iloc[-1] - stock_data['Close'].iloc[-2]
        price_change_pct = (price_change / stock_data['Close'].iloc[-2]) * 100
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                label=f"💰 Prix {symbol}",
                value=f"${latest_price:.2f}",
                delta=f"{price_change:+.2f} ({price_change_pct:+.2f}%)"
            )
        
        with col2:
            high_52w = stock_data['High'].max()
            st.metric(label="📈 Plus haut 52s", value=f"${high_52w:.2f}")
        
        with col3:
            low_52w = stock_data['Low'].min()
            st.metric(label="📉 Plus bas 52s", value=f"${low_52w:.2f}")
        
        with col4:
            avg_volume = stock_data['Volume'].mean()
            st.metric(label="📊 Volume moyen", value=f"{avg_volume/1e6:.1f}M")
        
        # Graphiques selon le type d'analyse
        if analysis_type == "Prix":
            fig = go.Figure()
            
            fig.add_trace(go.Candlestick(
                x=stock_data.index,
                open=stock_data['Open'],
                high=stock_data['High'],
                low=stock_data['Low'],
                close=stock_data['Close'],
                name=symbol
            ))
            
            fig.update_layout(
                title=f"Graphique en chandelles - {symbol}",
                xaxis_title="Date",
                yaxis_title="Prix ($)",
                height=600
            )
            
            st.plotly_chart(fig, use_container_width=True)
        
        elif analysis_type == "Volume":
            fig = go.Figure()
            
            fig.add_trace(go.Bar(
                x=stock_data.index,
                y=stock_data['Volume'],
                name="Volume",
                marker_color='rgba(55, 128, 191, 0.7)'
            ))
            
            fig.update_layout(
                title=f"Volume de transactions - {symbol}",
                xaxis_title="Date",
                yaxis_title="Volume",
                height=400
            )
            
            st.plotly_chart(fig, use_container_width=True)
        
        elif analysis_type == "Volatilité":
            # Calcul de la volatilité
            stock_data['Returns'] = stock_data['Close'].pct_change()
            stock_data['Volatility'] = stock_data['Returns'].rolling(window=30).std() * np.sqrt(252)
            
            fig = go.Figure()
            
            fig.add_trace(go.Scatter(
                x=stock_data.index,
                y=stock_data['Volatility'] * 100,
                mode='lines',
                name="Volatilité (30j)",
                line=dict(color='red', width=2)
            ))
            
            fig.update_layout(
                title=f"Volatilité - {symbol}",
                xaxis_title="Date",
                yaxis_title="Volatilité (%)",
                height=400
            )
            
            st.plotly_chart(fig, use_container_width=True)
        
        elif analysis_type == "Rendements":
            # Calcul des rendements
            stock_data['Daily_Returns'] = stock_data['Close'].pct_change()
            stock_data['Cumulative_Returns'] = (1 + stock_data['Daily_Returns']).cumprod() - 1
            
            fig = make_subplots(
                rows=2, cols=1,
                subplot_titles=('Rendements cumulés', 'Distribution des rendements quotidiens'),
                row_heights=[0.7, 0.3]
            )
            
            fig.add_trace(
                go.Scatter(
                    x=stock_data.index,
                    y=stock_data['Cumulative_Returns'] * 100,
                    mode='lines',
                    name="Rendements cumulés",
                    line=dict(color='green', width=2)
                ),
                row=1, col=1
            )
            
            fig.add_trace(
                go.Histogram(
                    x=stock_data['Daily_Returns'] * 100,
                    name="Distribution",
                    nbinsx=50,
                    marker_color='lightblue',
                    opacity=0.7
                ),
                row=2, col=1
            )
            
            fig.update_layout(
                title=f"Analyse des rendements - {symbol}",
                height=600
            )
            
            st.plotly_chart(fig, use_container_width=True)
        
        # Tableau de données récentes
        st.subheader("📋 Données récentes")
        recent_data = stock_data.tail(10).round(2)
        st.dataframe(recent_data, use_container_width=True)
        
    else:
        st.error(f"Impossible de charger les données pour {symbol}. Vérifiez le symbole ou votre connexion internet.")

def show_comparative_analysis(sales_data):
    """Affiche l'analyse comparative"""
    st.header("🔄 Analyse comparative")
    
    # Analyse comparative par période
    st.subheader("📊 Comparaison par période")
    
    col1, col2 = st.columns(2)
    
    with col1:
        comparison_type = st.selectbox(
            "Type de comparaison",
            ["Mensuelle", "Trimestrielle", "Annuelle"]
        )
    
    with col2:
        metric = st.selectbox(
            "Métrique",
            ["Ventes", "Coûts", "Profit"]
        )
    
    # Préparation des données selon le type de comparaison
    if comparison_type == "Mensuelle":
        grouped_data = sales_data.groupby([sales_data['Date'].dt.to_period('M'), 'Région'])[metric].sum().reset_index()
        grouped_data['Date'] = grouped_data['Date'].astype(str)
    elif comparison_type == "Trimestrielle":
        grouped_data = sales_data.groupby([sales_data['Date'].dt.to_period('Q'), 'Région'])[metric].sum().reset_index()
        grouped_data['Date'] = grouped_data['Date'].astype(str)
    else:
        grouped_data = sales_data.groupby([sales_data['Date'].dt.to_period('Y'), 'Région'])[metric].sum().reset_index()
        grouped_data['Date'] = grouped_data['Date'].astype(str)
    
    # Graphique de comparaison
    fig = px.line(
        grouped_data,
        x='Date',
        y=metric,
        color='Région',
        title=f"Évolution {comparison_type.lower()} - {metric}",
        markers=True
    )
    
    fig.update_layout(height=500)
    st.plotly_chart(fig, use_container_width=True)
    
    # Analyse de corrélation
    st.subheader("🔗 Analyse de corrélation")
    
    correlation_data = sales_data[['Ventes', 'Coûts', 'Profit']].corr()
    
    fig = px.imshow(
        correlation_data,
        text_auto=True,
        aspect="auto",
        title="Matrice de corrélation",
        color_continuous_scale='RdBu'
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Benchmark de performance
    st.subheader("🎯 Benchmark de performance")
    
    col1, col2 = st.columns(2)
    
    with col1:
        region_performance = sales_data.groupby('Région').agg({
            'Ventes': 'sum',
            'Profit': 'sum'
        }).reset_index()
        
        region_performance['Marge'] = (region_performance['Profit'] / region_performance['Ventes']) * 100
        
        fig = px.scatter(
            region_performance,
            x='Ventes',
            y='Profit',
            size='Marge',
            color='Région',
            title="Performance par région (Ventes vs Profit)",
            hover_data=['Marge']
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        product_performance = sales_data.groupby('Produit').agg({
            'Ventes': 'sum',
            'Profit': 'sum'
        }).reset_index()
        
        product_performance['Marge'] = (product_performance['Profit'] / product_performance['Ventes']) * 100
        
        fig = px.bar(
            product_performance,
            x='Produit',
            y='Marge',
            color='Marge',
            title="Marge par produit (%)",
            color_continuous_scale='Viridis'
        )
        
        st.plotly_chart(fig, use_container_width=True)

if __name__ == "__main__":
    main()
