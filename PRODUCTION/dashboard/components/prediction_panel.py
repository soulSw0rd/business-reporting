#!/usr/bin/env python3
"""
Prediction Panel Component
Panneau de prédiction avancé pour le dashboard crypto
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
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Tuple
import logging
import json
import os
from pathlib import Path

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class PredictionPanel:
    """
    Panneau de prédiction avancé avec visualisations interactives
    
    RESPONSABILITÉ : Interface utilisateur pour les prédictions ML
    UTILISATION : Affichage des prédictions, métriques et analyses
    
    FONCTIONNALITÉS :
    - Prédictions en temps réel
    - Métriques de confiance
    - Visualisations de performance
    - Analyse des features importantes
    - Historique des prédictions
    """
    
    def __init__(self):
        """Initialisation du panneau de prédiction"""
        self.prediction_history = []
        self.model_metrics = {}
        self.feature_importance = {}
        
        # Configuration des couleurs
        self.colors = {
            'profitable': '#2ecc71',
            'unprofitable': '#e74c3c',
            'neutral': '#95a5a6',
            'high_confidence': '#27ae60',
            'medium_confidence': '#f39c12',
            'low_confidence': '#e67e22'
        }
        
        logger.info("PredictionPanel initialisé")
    
    def display_prediction_overview(self, prediction_data: Dict[str, Any]):
        """
        Affiche un aperçu des prédictions
        
        PARAMÈTRES:
        - prediction_data: Données de prédiction
        """
        st.subheader("🔮 Aperçu des Prédictions")
        
        # Métriques principales
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            total_predictions = len(prediction_data.get('predictions', []))
            st.metric("Total Prédictions", total_predictions)
        
        with col2:
            profitable_count = sum(1 for p in prediction_data.get('predictions', []) 
                                 if p.get('is_profitable', False))
            profit_rate = (profitable_count / total_predictions * 100) if total_predictions > 0 else 0
            st.metric("Taux de Profit", f"{profit_rate:.1f}%")
        
        with col3:
            avg_confidence = np.mean([p.get('confidence', 0) for p in prediction_data.get('predictions', [])])
            st.metric("Confiance Moyenne", f"{avg_confidence:.1f}%")
        
        with col4:
            high_conf_count = sum(1 for p in prediction_data.get('predictions', []) 
                                if p.get('confidence', 0) > 80)
            st.metric("Haute Confiance", high_conf_count)
    
    def create_prediction_distribution_chart(self, predictions: List[Dict]) -> go.Figure:
        """
        Crée un graphique de distribution des prédictions
        
        PARAMÈTRES:
        - predictions: Liste des prédictions
        
        RETOURNE:
        - go.Figure: Graphique Plotly
        """
        if not predictions:
            return self._create_empty_chart("Aucune prédiction disponible")
        
        df = pd.DataFrame(predictions)
        
        # Préparation des données
        profitable = df[df.get('is_profitable', False) == True]
        unprofitable = df[df.get('is_profitable', False) == False]
        
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=(
                'Distribution des Prédictions', 'Confiance vs Profitabilité',
                'Répartition par Confiance', 'Timeline des Prédictions'
            ),
            specs=[
                [{"type": "bar"}, {"type": "scatter"}],
                [{"type": "pie"}, {"type": "scatter"}]
            ]
        )
        
        # Distribution des prédictions
        fig.add_trace(
            go.Bar(
                x=['Profitable', 'Non-Profitable'],
                y=[len(profitable), len(unprofitable)],
                marker_color=[self.colors['profitable'], self.colors['unprofitable']],
                name='Prédictions'
            ),
            row=1, col=1
        )
        
        # Confiance vs Profitabilité
        fig.add_trace(
            go.Scatter(
                x=df.get('confidence', []),
                y=df.get('expected_return', []),
                mode='markers',
                marker=dict(
                    color=[self.colors['profitable'] if p else self.colors['unprofitable'] 
                          for p in df.get('is_profitable', [])],
                    size=10,
                    opacity=0.7
                ),
                name='Confiance vs Return',
                hovertemplate='<b>Confiance:</b> %{x:.1f}%<br><b>Return:</b> %{y:.2f}%<extra></extra>'
            ),
            row=1, col=2
        )
        
        # Répartition par confiance
        confidence_ranges = ['Faible (0-60%)', 'Moyenne (60-80%)', 'Élevée (80-100%)']
        confidence_counts = [
            sum(1 for c in df.get('confidence', []) if c < 60),
            sum(1 for c in df.get('confidence', []) if 60 <= c < 80),
            sum(1 for c in df.get('confidence', []) if c >= 80)
        ]
        
        fig.add_trace(
            go.Pie(
                labels=confidence_ranges,
                values=confidence_counts,
                marker_colors=[self.colors['low_confidence'], 
                             self.colors['medium_confidence'], 
                             self.colors['high_confidence']],
                name='Confiance'
            ),
            row=2, col=1
        )
        
        # Timeline des prédictions
        if 'timestamp' in df.columns:
            fig.add_trace(
                go.Scatter(
                    x=df['timestamp'],
                    y=df.get('confidence', []),
                    mode='lines+markers',
                    name='Évolution Confiance',
                    line=dict(color='blue', width=2),
                    marker=dict(size=6)
                ),
                row=2, col=2
            )
        
        fig.update_layout(
            title="Analyse des Prédictions",
            height=600,
            showlegend=False
        )
        
        return fig
    
    def create_model_performance_chart(self, model_metrics: Dict[str, Any]) -> go.Figure:
        """
        Crée un graphique de performance du modèle
        
        PARAMÈTRES:
        - model_metrics: Métriques du modèle
        
        RETOURNE:
        - go.Figure: Graphique de performance
        """
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=(
                'Métriques de Classification', 'Courbe ROC',
                'Matrice de Confusion', 'Feature Importance'
            ),
            specs=[
                [{"type": "bar"}, {"type": "scatter"}],
                [{"type": "heatmap"}, {"type": "bar"}]
            ]
        )
        
        # Métriques de classification
        metrics_names = ['Accuracy', 'Precision', 'Recall', 'F1-Score']
        metrics_values = [
            model_metrics.get('accuracy', 0),
            model_metrics.get('precision', 0),
            model_metrics.get('recall', 0),
            model_metrics.get('f1_score', 0)
        ]
        
        fig.add_trace(
            go.Bar(
                x=metrics_names,
                y=metrics_values,
                marker_color='lightblue',
                name='Métriques'
            ),
            row=1, col=1
        )
        
        # Courbe ROC
        if 'roc_curve' in model_metrics:
            roc_data = model_metrics['roc_curve']
            fig.add_trace(
                go.Scatter(
                    x=roc_data.get('fpr', []),
                    y=roc_data.get('tpr', []),
                    mode='lines',
                    name=f'ROC (AUC = {roc_data.get("auc", 0):.3f})',
                    line=dict(color='red', width=2)
                ),
                row=1, col=2
            )
            
            # Ligne de référence
            fig.add_trace(
                go.Scatter(
                    x=[0, 1],
                    y=[0, 1],
                    mode='lines',
                    name='Référence',
                    line=dict(color='gray', dash='dash')
                ),
                row=1, col=2
            )
        
        # Matrice de confusion
        if 'confusion_matrix' in model_metrics:
            cm = model_metrics['confusion_matrix']
            fig.add_trace(
                go.Heatmap(
                    z=cm,
                    x=['Prédit Non-Profitable', 'Prédit Profitable'],
                    y=['Réel Non-Profitable', 'Réel Profitable'],
                    colorscale='Blues',
                    showscale=True,
                    hovertemplate='<b>%{y}</b><br><b>%{x}</b><br>Valeur: %{z}<extra></extra>'
                ),
                row=2, col=1
            )
        
        # Feature Importance
        if 'feature_importance' in model_metrics:
            importance = model_metrics['feature_importance']
            features = list(importance.keys())[:10]  # Top 10
            values = list(importance.values())[:10]
            
            fig.add_trace(
                go.Bar(
                    x=values,
                    y=features,
                    orientation='h',
                    marker_color='green',
                    name='Importance'
                ),
                row=2, col=2
            )
        
        fig.update_layout(
            title="Performance du Modèle ML",
            height=700,
            showlegend=False
        )
        
        return fig
    
    def display_prediction_details(self, prediction: Dict[str, Any]):
        """
        Affiche les détails d'une prédiction spécifique
        
        PARAMÈTRES:
        - prediction: Données de prédiction
        """
        st.subheader("📊 Détails de la Prédiction")
        
        # Informations principales
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### 📈 Résultat")
            is_profitable = prediction.get('is_profitable', False)
            confidence = prediction.get('confidence', 0)
            
            if is_profitable:
                st.success(f"✅ **PROFITABLE** (Confiance: {confidence:.1f}%)")
            else:
                st.error(f"❌ **NON-PROFITABLE** (Confiance: {confidence:.1f}%)")
            
            # Métriques détaillées
            expected_return = prediction.get('expected_return', 0)
            risk_score = prediction.get('risk_score', 0)
            
            st.metric("Return Attendu", f"{expected_return:.2f}%")
            st.metric("Score de Risque", f"{risk_score:.2f}")
        
        with col2:
            st.markdown("### 🎯 Facteurs Clés")
            
            # Features importantes pour cette prédiction
            features = prediction.get('key_features', {})
            
            for feature, value in features.items():
                st.metric(feature.replace('_', ' ').title(), f"{value:.3f}")
    
    def create_prediction_timeline(self, historical_predictions: List[Dict]) -> go.Figure:
        """
        Crée une timeline des prédictions historiques
        
        PARAMÈTRES:
        - historical_predictions: Historique des prédictions
        
        RETOURNE:
        - go.Figure: Graphique timeline
        """
        if not historical_predictions:
            return self._create_empty_chart("Aucun historique disponible")
        
        df = pd.DataFrame(historical_predictions)
        
        # Conversion des timestamps
        if 'timestamp' in df.columns:
            df['timestamp'] = pd.to_datetime(df['timestamp'])
        
        fig = go.Figure()
        
        # Prédictions profitables
        profitable = df[df.get('is_profitable', False) == True]
        if not profitable.empty:
            fig.add_trace(
                go.Scatter(
                    x=profitable['timestamp'],
                    y=profitable.get('confidence', []),
                    mode='markers',
                    name='Profitable',
                    marker=dict(
                        color=self.colors['profitable'],
                        size=10,
                        symbol='circle'
                    ),
                    hovertemplate='<b>Profitable</b><br>Date: %{x}<br>Confiance: %{y:.1f}%<extra></extra>'
                )
            )
        
        # Prédictions non-profitables
        unprofitable = df[df.get('is_profitable', False) == False]
        if not unprofitable.empty:
            fig.add_trace(
                go.Scatter(
                    x=unprofitable['timestamp'],
                    y=unprofitable.get('confidence', []),
                    mode='markers',
                    name='Non-Profitable',
                    marker=dict(
                        color=self.colors['unprofitable'],
                        size=10,
                        symbol='x'
                    ),
                    hovertemplate='<b>Non-Profitable</b><br>Date: %{x}<br>Confiance: %{y:.1f}%<extra></extra>'
                )
            )
        
        # Ligne de tendance
        if len(df) > 1:
            fig.add_trace(
                go.Scatter(
                    x=df['timestamp'],
                    y=df.get('confidence', []).rolling(window=5, min_periods=1).mean(),
                    mode='lines',
                    name='Tendance (MA5)',
                    line=dict(color='blue', width=2, dash='dash'),
                    opacity=0.7
                )
            )
        
        fig.update_layout(
            title="Timeline des Prédictions",
            xaxis_title="Date",
            yaxis_title="Confiance (%)",
            height=400,
            hovermode='x unified'
        )
        
        return fig
    
    def display_real_time_predictions(self, live_data: Dict[str, Any]):
        """
        Affiche les prédictions en temps réel
        
        PARAMÈTRES:
        - live_data: Données en temps réel
        """
        st.subheader("⚡ Prédictions en Temps Réel")
        
        # Placeholder pour les données en temps réel
        placeholder = st.empty()
        
        with placeholder.container():
            if 'current_prediction' in live_data:
                prediction = live_data['current_prediction']
                
                # Affichage en temps réel
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    is_profitable = prediction.get('is_profitable', False)
                    status_color = "green" if is_profitable else "red"
                    status_text = "PROFITABLE" if is_profitable else "NON-PROFITABLE"
                    
                    st.markdown(f"""
                    <div style="text-align: center; padding: 20px; 
                                background-color: {status_color}; 
                                color: white; border-radius: 10px;">
                        <h3>{status_text}</h3>
                        <p>Confiance: {prediction.get('confidence', 0):.1f}%</p>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col2:
                    st.metric(
                        "Return Attendu",
                        f"{prediction.get('expected_return', 0):.2f}%",
                        delta=f"{prediction.get('return_change', 0):.2f}%"
                    )
                
                with col3:
                    st.metric(
                        "Score de Risque",
                        f"{prediction.get('risk_score', 0):.2f}",
                        delta=f"{prediction.get('risk_change', 0):.2f}"
                    )
                
                # Graphique en temps réel
                if 'recent_predictions' in live_data:
                    fig = self.create_prediction_timeline(live_data['recent_predictions'])
                    st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("⏳ En attente des données en temps réel...")
    
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
            text=message,
            xref="paper", yref="paper",
            x=0.5, y=0.5,
            showarrow=False,
            font=dict(size=16, color="gray")
        )
        fig.update_layout(
            xaxis=dict(showgrid=False, showticklabels=False),
            yaxis=dict(showgrid=False, showticklabels=False),
            height=400
        )
        return fig
    
    def export_predictions(self, predictions: List[Dict], filename: str = None):
        """
        Exporte les prédictions vers un fichier
        
        PARAMÈTRES:
        - predictions: Liste des prédictions
        - filename: Nom du fichier (optionnel)
        """
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"predictions_export_{timestamp}.json"
        
        export_path = Path("RESOURCES/data/exports") / filename
        export_path.parent.mkdir(parents=True, exist_ok=True)
        
        try:
            with open(export_path, 'w', encoding='utf-8') as f:
                json.dump(predictions, f, indent=2, ensure_ascii=False, default=str)
            
            st.success(f"✅ Prédictions exportées vers: {export_path}")
            
            # Bouton de téléchargement
            with open(export_path, 'r', encoding='utf-8') as f:
                st.download_button(
                    label="📥 Télécharger les prédictions",
                    data=f.read(),
                    file_name=filename,
                    mime="application/json"
                )
                
        except Exception as e:
            st.error(f"❌ Erreur lors de l'export: {str(e)}")
            logger.error(f"Erreur export prédictions: {e}") 