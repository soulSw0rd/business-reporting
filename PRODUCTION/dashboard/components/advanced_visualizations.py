#!/usr/bin/env python3
"""
Advanced Visualizations
Composants de visualisation avancés pour le dashboard crypto
Auteur: Crypto-Tracker Team
Date: 2025-01-08
Version: 1.0.0
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import seaborn as sns
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
import logging

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AdvancedVisualizationComponents:
    """
    Composants de visualisation avancés pour le dashboard
    
    RESPONSABILITÉ : Création de graphiques explicatifs et interactifs
    UTILISATION : Amélioration de l'expérience utilisateur avec des visualisations riches
    
    FONCTIONNALITÉS :
    - Graphiques de performance multi-dimensionnels
    - Visualisations de corrélation et patterns
    - Graphiques de sentiment et marché
    - Dashboards interactifs avec filtres
    - Animations et transitions fluides
    """
    
    def __init__(self):
        """Initialisation des composants de visualisation"""
        self.color_palette = {
            'primary': '#1f77b4',
            'success': '#2ca02c',
            'warning': '#ff7f0e',
            'danger': '#d62728',
            'info': '#17becf',
            'secondary': '#7f7f7f'
        }
        
        self.chart_config = {
            'displayModeBar': True,
            'displaylogo': False,
            'modeBarButtonsToRemove': ['pan2d', 'lasso2d', 'select2d']
        }
        
        logger.info("AdvancedVisualizationComponents initialisé")
    
    def create_performance_heatmap(self, traders_data: List[Dict], title: str = "Performance des Traders") -> go.Figure:
        """
        Crée une heatmap de performance des traders
        
        PARAMÈTRES:
        - traders_data: Liste des données traders
        - title: Titre du graphique
        
        RETOURNE:
        - go.Figure: Graphique Plotly
        """
        if not traders_data:
            return self._create_empty_chart("Aucune donnée disponible")
        
        # Préparation des données
        df = pd.DataFrame(traders_data)
        
        # Sélection des métriques clés
        metrics = ['pnl_7d', 'pnl_30d', 'win_rate', 'long_percentage']
        available_metrics = [m for m in metrics if m in df.columns]
        
        if not available_metrics:
            return self._create_empty_chart("Métriques non disponibles")
        
        # Normalisation des données pour la heatmap
        df_normalized = df[available_metrics].copy()
        for col in available_metrics:
            if df_normalized[col].dtype in ['object', 'string']:
                df_normalized[col] = pd.to_numeric(df_normalized[col], errors='coerce')
        
        # Création de la heatmap
        fig = go.Figure(data=go.Heatmap(
            z=df_normalized.values.T,
            x=[f"Trader {i+1}" for i in range(len(df))],
            y=[col.replace('_', ' ').title() for col in available_metrics],
            colorscale='RdYlGn',
            colorbar=dict(title="Performance"),
            hoverongaps=False,
            hovertemplate='<b>%{y}</b><br>Trader: %{x}<br>Valeur: %{z:.2f}<extra></extra>'
        ))
        
        fig.update_layout(
            title=title,
            xaxis_title="Traders",
            yaxis_title="Métriques",
            height=400,
            font=dict(size=12)
        )
        
        return fig
    
    def create_correlation_matrix(self, data: pd.DataFrame, title: str = "Matrice de Corrélation") -> go.Figure:
        """
        Crée une matrice de corrélation interactive
        
        PARAMÈTRES:
        - data: DataFrame avec les données
        - title: Titre du graphique
        
        RETOURNE:
        - go.Figure: Graphique Plotly
        """
        # Sélection des colonnes numériques
        numeric_cols = data.select_dtypes(include=[np.number]).columns
        
        if len(numeric_cols) < 2:
            return self._create_empty_chart("Pas assez de données numériques")
        
        # Calcul de la corrélation
        corr_matrix = data[numeric_cols].corr()
        
        # Création de la heatmap de corrélation
        fig = go.Figure(data=go.Heatmap(
            z=corr_matrix.values,
            x=corr_matrix.columns,
            y=corr_matrix.columns,
            colorscale='RdBu',
            zmid=0,
            colorbar=dict(title="Corrélation"),
            hovertemplate='<b>%{x}</b> vs <b>%{y}</b><br>Corrélation: %{z:.3f}<extra></extra>'
        ))
        
        fig.update_layout(
            title=title,
            height=500,
            font=dict(size=10)
        )
        
        return fig
    
    def create_performance_distribution(self, data: List[Dict], metric: str = 'pnl_30d') -> go.Figure:
        """
        Crée un graphique de distribution de performance
        
        PARAMÈTRES:
        - data: Données des traders
        - metric: Métrique à analyser
        
        RETOURNE:
        - go.Figure: Graphique Plotly
        """
        if not data:
            return self._create_empty_chart("Aucune donnée disponible")
        
        df = pd.DataFrame(data)
        
        if metric not in df.columns:
            return self._create_empty_chart(f"Métrique '{metric}' non disponible")
        
        # Conversion en numérique
        values = pd.to_numeric(df[metric], errors='coerce').dropna()
        
        if len(values) == 0:
            return self._create_empty_chart("Aucune valeur numérique")
        
        # Création du graphique combiné
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=('Distribution', 'Box Plot', 'Histogramme', 'Statistiques'),
            specs=[[{"secondary_y": False}, {"secondary_y": False}],
                   [{"secondary_y": False}, {"type": "table"}]]
        )
        
        # Distribution (violin plot)
        fig.add_trace(
            go.Violin(y=values, name=metric, box_visible=True, meanline_visible=True),
            row=1, col=1
        )
        
        # Box plot
        fig.add_trace(
            go.Box(y=values, name=metric, boxpoints='outliers'),
            row=1, col=2
        )
        
        # Histogramme
        fig.add_trace(
            go.Histogram(x=values, name=metric, nbinsx=20),
            row=2, col=1
        )
        
        # Statistiques descriptives
        stats_data = [
            ['Moyenne', f"{values.mean():.2f}"],
            ['Médiane', f"{values.median():.2f}"],
            ['Écart-type', f"{values.std():.2f}"],
            ['Min', f"{values.min():.2f}"],
            ['Max', f"{values.max():.2f}"],
            ['Q1', f"{values.quantile(0.25):.2f}"],
            ['Q3', f"{values.quantile(0.75):.2f}"]
        ]
        
        fig.add_trace(
            go.Table(
                header=dict(values=['Statistique', 'Valeur']),
                cells=dict(values=list(zip(*stats_data)))
            ),
            row=2, col=2
        )
        
        fig.update_layout(
            title=f"Analyse de Distribution - {metric}",
            height=600,
            showlegend=False
        )
        
        return fig
    
    def create_market_sentiment_gauge(self, sentiment_data: Dict[str, Any]) -> go.Figure:
        """
        Crée une jauge de sentiment de marché
        
        PARAMÈTRES:
        - sentiment_data: Données de sentiment
        
        RETOURNE:
        - go.Figure: Graphique Plotly
        """
        # Extraction du score de sentiment
        fear_greed = sentiment_data.get('fear_and_greed_index', {}).get('value', 50)
        
        # Création de la jauge
        fig = go.Figure(go.Indicator(
            mode = "gauge+number+delta",
            value = fear_greed,
            domain = {'x': [0, 1], 'y': [0, 1]},
            title = {'text': "Fear & Greed Index"},
            delta = {'reference': 50},
            gauge = {
                'axis': {'range': [None, 100]},
                'bar': {'color': "darkblue"},
                'steps': [
                    {'range': [0, 25], 'color': "red"},
                    {'range': [25, 50], 'color': "orange"},
                    {'range': [50, 75], 'color': "yellow"},
                    {'range': [75, 100], 'color': "green"}
                ],
                'threshold': {
                    'line': {'color': "red", 'width': 4},
                    'thickness': 0.75,
                    'value': 90
                }
            }
        ))
        
        fig.update_layout(
            height=300,
            font={'color': "darkblue", 'family': "Arial"}
        )
        
        return fig
    
    def create_trader_performance_radar(self, trader_data: Dict[str, Any]) -> go.Figure:
        """
        Crée un graphique radar pour analyser un trader
        
        PARAMÈTRES:
        - trader_data: Données du trader
        
        RETOURNE:
        - go.Figure: Graphique Plotly
        """
        # Métriques pour le radar
        metrics = {
            'PnL 7d': trader_data.get('pnl_7d', 0),
            'PnL 30d': trader_data.get('pnl_30d', 0),
            'Win Rate': trader_data.get('win_rate', 0.5),
            'Long %': trader_data.get('long_percentage', 50) / 100,
            'Sharpe Ratio': trader_data.get('sharpe_ratio', 0),
            'Consistency': trader_data.get('consistency_score', 0.5)
        }
        
        # Normalisation des valeurs (0-1)
        normalized_values = []
        for key, value in metrics.items():
            if key in ['PnL 7d', 'PnL 30d']:
                # Normalisation des PnL (-1 à 1 -> 0 à 1)
                normalized = (value + 1) / 2
            elif key == 'Sharpe Ratio':
                # Normalisation Sharpe (0 à 3 -> 0 à 1)
                normalized = min(max(value, 0), 3) / 3
            else:
                # Déjà normalisé ou en pourcentage
                normalized = value
            
            normalized_values.append(max(0, min(1, normalized)))
        
        # Création du radar
        fig = go.Figure()
        
        fig.add_trace(go.Scatterpolar(
            r=normalized_values,
            theta=list(metrics.keys()),
            fill='toself',
            name='Performance',
            line_color='rgba(31, 119, 180, 0.8)',
            fillcolor='rgba(31, 119, 180, 0.3)'
        ))
        
        fig.update_layout(
            polar=dict(
                radialaxis=dict(
                    visible=True,
                    range=[0, 1]
                )),
            showlegend=True,
            title="Profil de Performance du Trader",
            height=400
        )
        
        return fig
    
    def create_prediction_confidence_chart(self, predictions: List[Dict]) -> go.Figure:
        """
        Crée un graphique de confiance des prédictions
        
        PARAMÈTRES:
        - predictions: Liste des prédictions
        
        RETOURNE:
        - go.Figure: Graphique Plotly
        """
        if not predictions:
            return self._create_empty_chart("Aucune prédiction disponible")
        
        # Préparation des données
        df = pd.DataFrame(predictions)
        
        # Graphique de confiance
        fig = go.Figure()
        
        # Barres de confiance
        fig.add_trace(go.Bar(
            x=[f"Trader {i+1}" for i in range(len(df))],
            y=df.get('confidence', [0.5] * len(df)),
            name='Confiance',
            marker_color=['green' if pred > 0.7 else 'orange' if pred > 0.5 else 'red' 
                         for pred in df.get('confidence', [0.5] * len(df))],
            hovertemplate='<b>%{x}</b><br>Confiance: %{y:.2%}<extra></extra>'
        ))
        
        # Ligne de seuil
        fig.add_hline(y=0.7, line_dash="dash", line_color="green", 
                     annotation_text="Seuil de confiance élevée")
        
        fig.update_layout(
            title="Confiance des Prédictions ML",
            xaxis_title="Traders",
            yaxis_title="Niveau de Confiance",
            yaxis=dict(range=[0, 1], tickformat='.0%'),
            height=400
        )
        
        return fig
    
    def create_market_overview_dashboard(self, market_data: Dict[str, Any]) -> go.Figure:
        """
        Crée un dashboard complet du marché
        
        PARAMÈTRES:
        - market_data: Données de marché
        
        RETOURNE:
        - go.Figure: Graphique Plotly
        """
        # Création des sous-graphiques
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=('Prix Bitcoin', 'Volume 24h', 'Fear & Greed', 'Funding Rates'),
            specs=[[{"secondary_y": False}, {"secondary_y": False}],
                   [{"type": "indicator"}, {"secondary_y": False}]]
        )
        
        # Prix Bitcoin (exemple de données temporelles)
        btc_price = market_data.get('coingecko_btc', {}).get('price', 50000)
        dates = [datetime.now() - timedelta(days=i) for i in range(30, 0, -1)]
        prices = [btc_price * (1 + np.random.normal(0, 0.02)) for _ in dates]
        
        fig.add_trace(
            go.Scatter(x=dates, y=prices, name='BTC Price', line=dict(color='orange')),
            row=1, col=1
        )
        
        # Volume 24h (barres)
        volumes = [np.random.uniform(20, 80) for _ in dates]
        fig.add_trace(
            go.Bar(x=dates[-7:], y=volumes[-7:], name='Volume 24h', marker_color='blue'),
            row=1, col=2
        )
        
        # Fear & Greed (jauge)
        fear_greed = market_data.get('fear_and_greed_index', {}).get('value', 50)
        fig.add_trace(
            go.Indicator(
                mode="gauge+number",
                value=fear_greed,
                title={'text': "Fear & Greed"},
                gauge={'axis': {'range': [0, 100]},
                       'bar': {'color': "darkblue"},
                       'steps': [{'range': [0, 50], 'color': "red"},
                                {'range': [50, 100], 'color': "green"}]}
            ),
            row=2, col=1
        )
        
        # Funding Rates
        funding_rates = [np.random.uniform(-0.1, 0.1) for _ in dates[-10:]]
        fig.add_trace(
            go.Scatter(x=dates[-10:], y=funding_rates, name='Funding Rate', 
                      line=dict(color='red'), mode='lines+markers'),
            row=2, col=2
        )
        
        fig.update_layout(
            title="Dashboard Marché Crypto",
            height=600,
            showlegend=False
        )
        
        return fig
    
    def create_performance_timeline(self, historical_data: List[Dict]) -> go.Figure:
        """
        Crée une timeline de performance
        
        PARAMÈTRES:
        - historical_data: Données historiques
        
        RETOURNE:
        - go.Figure: Graphique Plotly
        """
        if not historical_data:
            return self._create_empty_chart("Aucune donnée historique")
        
        df = pd.DataFrame(historical_data)
        
        # Conversion des dates
        if 'timestamp' in df.columns:
            df['timestamp'] = pd.to_datetime(df['timestamp'])
        else:
            df['timestamp'] = pd.date_range(start='2024-01-01', periods=len(df), freq='D')
        
        # Création de la timeline
        fig = go.Figure()
        
        # Performance cumulée
        if 'pnl_30d' in df.columns:
            cumulative_pnl = df['pnl_30d'].cumsum()
            fig.add_trace(go.Scatter(
                x=df['timestamp'],
                y=cumulative_pnl,
                mode='lines',
                name='Performance Cumulée',
                line=dict(color='blue', width=2)
            ))
        
        # Drawdown
        if 'max_drawdown' in df.columns:
            fig.add_trace(go.Scatter(
                x=df['timestamp'],
                y=-df['max_drawdown'],
                mode='lines',
                name='Drawdown',
                line=dict(color='red', width=1),
                fill='tonexty'
            ))
        
        fig.update_layout(
            title="Timeline de Performance",
            xaxis_title="Date",
            yaxis_title="Performance (%)",
            height=400,
            hovermode='x unified'
        )
        
        return fig
    
    def create_advanced_market_analysis(self, market_data: Dict[str, Any]) -> go.Figure:
        """
        Crée une analyse de marché avancée avec multiple métriques
        
        PARAMÈTRES:
        - market_data: Données de marché
        
        RETOURNE:
        - go.Figure: Dashboard de marché complet
        """
        fig = make_subplots(
            rows=3, cols=2,
            subplot_titles=(
                'Prix BTC & Volume', 'Fear & Greed Index',
                'Funding Rates', 'Volatilité',
                'Corrélations', 'Sentiment Social'
            ),
            specs=[
                [{"secondary_y": True}, {"type": "indicator"}],
                [{"secondary_y": False}, {"secondary_y": False}],
                [{"type": "bar"}, {"type": "indicator"}]
            ]
        )
        
        # Prix BTC et Volume
        if 'btc_price' in market_data:
            fig.add_trace(
                go.Scatter(
                    x=list(range(len(market_data['btc_price']))),
                    y=market_data['btc_price'],
                    name='Prix BTC',
                    line=dict(color='orange', width=2)
                ),
                row=1, col=1
            )
        
        # Fear & Greed Index
        fear_greed_value = market_data.get('fear_greed_index', 50)
        fig.add_trace(
            go.Indicator(
                mode="gauge+number+delta",
                value=fear_greed_value,
                domain={'x': [0, 1], 'y': [0, 1]},
                title={'text': "Fear & Greed"},
                gauge={
                    'axis': {'range': [None, 100]},
                    'bar': {'color': "darkblue"},
                    'steps': [
                        {'range': [0, 25], 'color': "red"},
                        {'range': [25, 50], 'color': "orange"},
                        {'range': [50, 75], 'color': "yellow"},
                        {'range': [75, 100], 'color': "green"}
                    ],
                    'threshold': {
                        'line': {'color': "red", 'width': 4},
                        'thickness': 0.75,
                        'value': 90
                    }
                }
            ),
            row=1, col=2
        )
        
        # Funding Rates
        if 'funding_rates' in market_data:
            funding_data = market_data['funding_rates']
            fig.add_trace(
                go.Scatter(
                    x=list(range(len(funding_data))),
                    y=funding_data,
                    name='Funding Rates',
                    line=dict(color='purple', width=2)
                ),
                row=2, col=1
            )
        
        # Volatilité
        if 'volatility' in market_data:
            vol_data = market_data['volatility']
            fig.add_trace(
                go.Scatter(
                    x=list(range(len(vol_data))),
                    y=vol_data,
                    name='Volatilité',
                    line=dict(color='red', width=2),
                    fill='tonexty'
                ),
                row=2, col=2
            )
        
        # Corrélations
        if 'correlations' in market_data:
            corr_data = market_data['correlations']
            fig.add_trace(
                go.Bar(
                    x=list(corr_data.keys()),
                    y=list(corr_data.values()),
                    name='Corrélations',
                    marker_color='lightblue'
                ),
                row=3, col=1
            )
        
        # Sentiment Social
        social_sentiment = market_data.get('social_sentiment', 0)
        fig.add_trace(
            go.Indicator(
                mode="number+gauge",
                value=social_sentiment,
                title={'text': "Sentiment Social"},
                gauge={
                    'axis': {'range': [-1, 1]},
                    'bar': {'color': "green" if social_sentiment > 0 else "red"},
                    'bgcolor': "white",
                    'borderwidth': 2,
                    'bordercolor': "gray"
                }
            ),
            row=3, col=2
        )
        
        fig.update_layout(
            title="Analyse de Marché Avancée",
            height=800,
            showlegend=True
        )
        
        return fig
    
    def create_trader_comparison_chart(self, traders_data: List[Dict]) -> go.Figure:
        """
        Crée un graphique de comparaison entre traders
        
        PARAMÈTRES:
        - traders_data: Liste des données traders
        
        RETOURNE:
        - go.Figure: Graphique de comparaison
        """
        if not traders_data:
            return self._create_empty_chart("Aucune donnée trader disponible")
        
        df = pd.DataFrame(traders_data)
        
        # Métriques à comparer
        metrics = ['pnl_7d', 'pnl_30d', 'win_rate', 'sharpe_ratio', 'max_drawdown']
        available_metrics = [m for m in metrics if m in df.columns]
        
        if not available_metrics:
            return self._create_empty_chart("Métriques de comparaison non disponibles")
        
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=('Performance PnL', 'Win Rate vs Sharpe', 'Drawdown Analysis', 'Risk-Return'),
            specs=[
                [{"secondary_y": False}, {"secondary_y": False}],
                [{"secondary_y": False}, {"secondary_y": False}]
            ]
        )
        
        # Performance PnL
        if 'pnl_7d' in df.columns and 'pnl_30d' in df.columns:
            fig.add_trace(
                go.Scatter(
                    x=pd.to_numeric(df['pnl_7d'], errors='coerce'),
                    y=pd.to_numeric(df['pnl_30d'], errors='coerce'),
                    mode='markers',
                    name='PnL Comparison',
                    marker=dict(size=10, color='blue', opacity=0.6),
                    text=[f"Trader {i+1}" for i in range(len(df))],
                    hovertemplate='<b>%{text}</b><br>PnL 7d: %{x:.2f}<br>PnL 30d: %{y:.2f}<extra></extra>'
                ),
                row=1, col=1
            )
        
        # Win Rate vs Sharpe
        if 'win_rate' in df.columns and 'sharpe_ratio' in df.columns:
            fig.add_trace(
                go.Scatter(
                    x=pd.to_numeric(df['win_rate'], errors='coerce'),
                    y=pd.to_numeric(df['sharpe_ratio'], errors='coerce'),
                    mode='markers',
                    name='Win Rate vs Sharpe',
                    marker=dict(size=10, color='green', opacity=0.6),
                    text=[f"Trader {i+1}" for i in range(len(df))],
                    hovertemplate='<b>%{text}</b><br>Win Rate: %{x:.2f}%<br>Sharpe: %{y:.2f}<extra></extra>'
                ),
                row=1, col=2
            )
        
        # Drawdown Analysis
        if 'max_drawdown' in df.columns:
            fig.add_trace(
                go.Bar(
                    x=[f"Trader {i+1}" for i in range(len(df))],
                    y=pd.to_numeric(df['max_drawdown'], errors='coerce'),
                    name='Max Drawdown',
                    marker_color='red',
                    opacity=0.7
                ),
                row=2, col=1
            )
        
        # Risk-Return
        if 'volatility' in df.columns and 'pnl_30d' in df.columns:
            fig.add_trace(
                go.Scatter(
                    x=pd.to_numeric(df['volatility'], errors='coerce'),
                    y=pd.to_numeric(df['pnl_30d'], errors='coerce'),
                    mode='markers',
                    name='Risk-Return',
                    marker=dict(size=10, color='purple', opacity=0.6),
                    text=[f"Trader {i+1}" for i in range(len(df))],
                    hovertemplate='<b>%{text}</b><br>Volatilité: %{x:.2f}<br>Return: %{y:.2f}<extra></extra>'
                ),
                row=2, col=2
            )
        
        fig.update_layout(
            title="Comparaison des Traders",
            height=600,
            showlegend=False
        )
        
        return fig
    
    def _create_empty_chart(self, message: str) -> go.Figure:
        """
        Crée un graphique vide avec un message
        
        PARAMÈTRES:
        - message: Message à afficher
        
        RETOURNE:
        - go.Figure: Graphique vide
        """
        fig = go.Figure()
        fig.add_annotation(
            x=0.5, y=0.5,
            text=message,
            showarrow=False,
            font=dict(size=16, color="gray")
        )
        fig.update_layout(
            xaxis=dict(showgrid=False, showticklabels=False),
            yaxis=dict(showgrid=False, showticklabels=False),
            height=300
        )
        return fig
    
    def display_metrics_cards(self, metrics: Dict[str, Any], cols: int = 4):
        """
        Affiche des cartes de métriques
        
        PARAMÈTRES:
        - metrics: Dictionnaire des métriques
        - cols: Nombre de colonnes
        """
        columns = st.columns(cols)
        
        for i, (key, value) in enumerate(metrics.items()):
            with columns[i % cols]:
                if isinstance(value, (int, float)):
                    if key.lower().find('rate') != -1 or key.lower().find('percentage') != -1:
                        st.metric(key, f"{value:.1%}")
                    elif key.lower().find('pnl') != -1:
                        delta_color = "normal" if value >= 0 else "inverse"
                        st.metric(key, f"{value:.2f}%", delta=f"{value:.2f}%")
                    else:
                        st.metric(key, f"{value:.2f}")
                else:
                    st.metric(key, str(value))
    
    def create_feature_importance_chart(self, feature_importance: Dict[str, float]) -> go.Figure:
        """
        Crée un graphique d'importance des features
        
        PARAMÈTRES:
        - feature_importance: Importance des features
        
        RETOURNE:
        - go.Figure: Graphique Plotly
        """
        if not feature_importance:
            return self._create_empty_chart("Aucune donnée d'importance")
        
        # Tri par importance
        sorted_features = dict(sorted(feature_importance.items(), key=lambda x: x[1], reverse=True))
        
        fig = go.Figure(go.Bar(
            x=list(sorted_features.values()),
            y=list(sorted_features.keys()),
            orientation='h',
            marker_color='lightblue',
            hovertemplate='<b>%{y}</b><br>Importance: %{x:.3f}<extra></extra>'
        ))
        
        fig.update_layout(
            title="Importance des Features ML",
            xaxis_title="Importance",
            yaxis_title="Features",
            height=400
        )
        
        return fig 

    def display(self, scraped_data: Dict[str, Any]):
        """
        Méthode principale d'affichage des visualisations avancées
        
        PARAMÈTRES:
        - scraped_data: Données du système
        """
        st.subheader("🎨 Visualisations Avancées")
        
        # Extraction des données
        traders_data = scraped_data.get('traders_for_analysis', [])
        market_data = scraped_data.get('market_data_extended', {})
        prediction_data = scraped_data.get('traders_for_prediction', [])
        
        # Onglets pour organiser les visualisations
        tab1, tab2, tab3, tab4 = st.tabs([
            "📊 Analyse Traders", 
            "🌐 Marché Crypto", 
            "🔮 Prédictions ML",
            "📈 Comparaisons"
        ])
        
        with tab1:
            self._display_trader_analysis(traders_data)
        
        with tab2:
            self._display_market_analysis(market_data)
        
        with tab3:
            self._display_prediction_analysis(prediction_data)
        
        with tab4:
            self._display_comparison_analysis(traders_data, market_data)
    
    def _display_trader_analysis(self, traders_data: List[Dict]):
        """Affichage des analyses de traders"""
        st.subheader("👑 Analyse des Traders")
        
        if not traders_data:
            st.warning("Aucune donnée de trader disponible")
            return
        
        # Métriques de performance
        col1, col2 = st.columns(2)
        
        with col1:
            st.plotly_chart(
                self.create_performance_heatmap(traders_data, "Performance Heatmap"),
                use_container_width=True
            )
        
        with col2:
            df = pd.DataFrame(traders_data)
            st.plotly_chart(
                self.create_performance_distribution(traders_data, 'total_pnl'),
                use_container_width=True
            )
        
        # Graphique de comparaison
        st.plotly_chart(
            self.create_trader_comparison_chart(traders_data),
            use_container_width=True
        )
    
    def _display_market_analysis(self, market_data: Dict[str, Any]):
        """Affichage des analyses de marché"""
        st.subheader("🌐 Analyse de Marché")
        
        if not market_data:
            st.warning("Aucune donnée de marché disponible")
            return
        
        # Préparer les données de marché pour la visualisation
        market_viz_data = {
            'btc_price': [45000, 46000, 45500, 47000, 46500],  # Exemple
            'fear_greed_index': market_data.get('fear_greed_index', 50),
            'funding_rates': [0.01, 0.015, 0.008, 0.012, 0.009],  # Exemple
            'volatility': [0.02, 0.025, 0.018, 0.03, 0.022],  # Exemple
            'correlations': {
                'BTC-ETH': 0.8,
                'BTC-S&P500': 0.3,
                'BTC-Gold': -0.1,
                'BTC-USD': -0.6
            },
            'social_sentiment': 0.2
        }
        
        # Graphique de marché avancé
        st.plotly_chart(
            self.create_advanced_market_analysis(market_viz_data),
            use_container_width=True
        )
        
        # Matrice de corrélation si données disponibles
        if 'cryptocurrencies' in market_data:
            crypto_df = pd.DataFrame(market_data['cryptocurrencies'])
            if len(crypto_df) > 1:
                st.plotly_chart(
                    self.create_correlation_matrix(crypto_df, "Corrélations Crypto"),
                    use_container_width=True
                )
    
    def _display_prediction_analysis(self, prediction_data: List[Dict]):
        """Affichage des analyses de prédiction"""
        st.subheader("🔮 Analyse des Prédictions")
        
        if not prediction_data:
            st.warning("Aucune donnée de prédiction disponible")
            return
        
        # Simuler des prédictions pour la démonstration
        simulated_predictions = []
        for i, trader in enumerate(prediction_data[:20]):  # Limiter à 20 pour la demo
            prediction = {
                'trader_id': i,
                'is_profitable': np.random.choice([True, False], p=[0.6, 0.4]),
                'confidence': np.random.uniform(60, 95),
                'expected_return': np.random.uniform(-5, 15),
                'timestamp': datetime.now() - timedelta(hours=i)
            }
            simulated_predictions.append(prediction)
        
        # Métriques de confiance
        self.display_metrics_cards({
            'Total Prédictions': len(simulated_predictions),
            'Taux de Réussite': f"{sum(1 for p in simulated_predictions if p['is_profitable']) / len(simulated_predictions) * 100:.1f}%",
            'Confiance Moyenne': f"{np.mean([p['confidence'] for p in simulated_predictions]):.1f}%",
            'Return Moyen': f"{np.mean([p['expected_return'] for p in simulated_predictions]):.2f}%"
        })
        
        # Graphique de distribution des prédictions
        st.plotly_chart(
            self.create_prediction_confidence_chart(simulated_predictions),
            use_container_width=True
        )
    
    def _display_comparison_analysis(self, traders_data: List[Dict], market_data: Dict[str, Any]):
        """Affichage des analyses comparatives"""
        st.subheader("📈 Analyses Comparatives")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if traders_data:
                df = pd.DataFrame(traders_data)
                st.plotly_chart(
                    self.create_correlation_matrix(df, "Corrélations Traders"),
                    use_container_width=True
                )
        
        with col2:
            if market_data and 'cryptocurrencies' in market_data:
                crypto_data = market_data['cryptocurrencies']
                if crypto_data:
                    # Créer des données de timeline simulées
                    timeline_data = []
                    for i in range(30):  # 30 jours
                        timeline_data.append({
                            'date': datetime.now() - timedelta(days=i),
                            'btc_price': 45000 + np.random.normal(0, 2000),
                            'market_cap': 800000000000 + np.random.normal(0, 50000000000),
                            'volume': 20000000000 + np.random.normal(0, 5000000000)
                        })
                    
                    st.plotly_chart(
                        self.create_performance_timeline(timeline_data),
                        use_container_width=True
                    ) 