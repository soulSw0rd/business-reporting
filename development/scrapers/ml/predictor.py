#!/usr/bin/env python3
"""
Crypto ML Prediction System
Architecture complète pour prédire le succès des traders crypto.
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import json
import sqlite3
import joblib
from pathlib import Path

# ML imports
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split, TimeSeriesSplit
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import classification_report, roc_auc_score

# --- MODIFICATION POUR INTÉGRATION ---
# Imports depuis notre structure de projet
from ..core.scrapers import scrape_top_traders
from ..core.coingecko import scrape_coingecko_metrics
from ..core.fear_and_greed import scrape_fear_and_greed_index
from ..core.funding_rates import FundingRatesScraper
# --- FIN MODIFICATION ---


class CryptoMLPredictor:
    """
    Système de prédiction ML pour traders crypto.
    Objectif : Prédire si un trader sera profitable dans les 7 prochains jours.
    """
    
    def __init__(self, data_path="data/ml_training"):
        self.data_path = Path(data_path)
        self.data_path.mkdir(parents=True, exist_ok=True)
        
        self.db_path = self.data_path / "crypto_ml.db"
        self.model_path = self.data_path / "models"
        self.model_path.mkdir(exist_ok=True)
        
        self.models = {}
        self.scaler = StandardScaler()
        
        self._init_database()

    def _init_database(self):
        """Initialise la base de données SQLite pour stocker l'historique."""
        conn = sqlite3.connect(self.db_path)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS trader_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                trader_address TEXT NOT NULL,
                
                -- Performance metrics
                pnl_24h REAL,
                pnl_7d REAL,
                pnl_30d REAL,
                pnl_total REAL,
                
                -- Portfolio composition
                long_percentage REAL,
                
                -- Market context (même timestamp)
                btc_price REAL,
                fear_greed_index INTEGER,
                funding_rate_btc REAL,
                
                -- Target variable (calculé après 7 jours)
                future_profitable BOOLEAN,
                future_pnl_7d REAL,
                
                -- NOUVEAU: Cible pour le long terme
                future_profitable_30d BOOLEAN,
                future_pnl_30d REAL,
                
                UNIQUE(timestamp, trader_address)
            )
        """)
        conn.execute("CREATE INDEX IF NOT EXISTS idx_trader_timestamp ON trader_history(trader_address, timestamp)")
        conn.commit()
        conn.close()

    def store_daily_snapshot(self, traders_data, market_data):
        """Stocke un snapshot quotidien des traders et du marché."""
        conn = sqlite3.connect(self.db_path)
        timestamp = datetime.now().isoformat()
        
        # Fonction pour convertir le PnL en float
        def pnl_to_float(pnl_str):
            if isinstance(pnl_str, (int, float)):
                return float(pnl_str)
            pnl_str = str(pnl_str).replace('$', '').strip()
            if 'M' in pnl_str:
                return float(pnl_str.replace('M', '')) * 1e6
            if 'K' in pnl_str:
                return float(pnl_str.replace('K', '')) * 1e3
            try:
                return float(pnl_str)
            except (ValueError, TypeError):
                return 0.0
        
        for trader in traders_data:
            data = {
                'timestamp': timestamp,
                'trader_address': trader.get('address'),
                
                'pnl_24h': pnl_to_float(trader.get('pnl_24h')),
                'pnl_7d': pnl_to_float(trader.get('pnl_7d')),
                'pnl_30d': pnl_to_float(trader.get('pnl_30d')),
                'pnl_total': pnl_to_float(trader.get('pnl_total')),
                
                'long_percentage': pnl_to_float(trader.get('long_percentage', '0%').replace('%', '')),
                
                'btc_price': market_data.get('coingecko_btc', {}).get('price'),
                'fear_greed_index': market_data.get('fear_and_greed_index', {}).get('value'),
                'funding_rate_btc': market_data.get('funding_rates', {}).get('BTCUSDT', {}).get('last_funding_rate'),
                
                'future_profitable': None,
                'future_pnl_7d': None,
                'future_profitable_30d': None,
                'future_pnl_30d': None
            }
            
            placeholders = ', '.join(['?' for _ in data])
            columns = ', '.join(data.keys())
            
            try:
                conn.execute(f"INSERT OR REPLACE INTO trader_history ({columns}) VALUES ({placeholders})", list(data.values()))
            except Exception as e:
                print(f"Erreur insertion trader {trader.get('address')}: {e}")
        
        conn.commit()
        conn.close()
        print(f"✅ Snapshot sauvé: {len(traders_data)} traders à {timestamp}")

    def update_target_variables(self, horizon_days):
        """Met à jour les variables cibles (profitabilité future) après un certain horizon."""
        conn = sqlite3.connect(self.db_path)
        cutoff_date = (datetime.now() - timedelta(days=horizon_days)).isoformat()
        
        target_col = f"future_profitable_{horizon_days}d"
        pnl_col = f"future_pnl_{horizon_days}d"

        query = f"""
            SELECT t1.id, t1.trader_address, t1.timestamp
            FROM trader_history t1
            WHERE t1.timestamp <= ? AND t1.{target_col} IS NULL
        """
        
        to_update = pd.read_sql_query(query, conn, params=[cutoff_date])
        
        updates_count = 0
        for _, row in to_update.iterrows():
            future_date_start = (datetime.fromisoformat(row['timestamp']) + timedelta(days=horizon_days)).isoformat()
            future_date_end = (datetime.fromisoformat(row['timestamp']) + timedelta(days=horizon_days + 1)).isoformat()
            
            # Pour le long terme, on peut regarder le PnL sur 30 jours
            pnl_metric_to_check = 'pnl_30d' if horizon_days == 30 else 'pnl_7d'
            
            future_pnl_query = f"""
                SELECT {pnl_metric_to_check} FROM trader_history
                WHERE trader_address = ? AND timestamp >= ? AND timestamp < ?
                LIMIT 1
            """
            future_pnl_result = conn.execute(future_pnl_query, (row['trader_address'], future_date_start, future_date_end)).fetchone()
            
            if future_pnl_result:
                future_pnl = future_pnl_result[0]
                is_profitable = future_pnl > 0
                
                update_query = f"UPDATE trader_history SET {target_col} = ?, {pnl_col} = ? WHERE id = ?"
                conn.execute(update_query, (is_profitable, future_pnl, row['id']))
                updates_count += 1
        
        conn.commit()
        conn.close()
        print(f"✅ Mis à jour {updates_count} targets pour l'horizon {horizon_days} jours.")
        return updates_count

    def prepare_training_data(self, horizon_days=7):
        """Prépare les données pour l'entraînement ML pour un horizon spécifique."""
        conn = sqlite3.connect(self.db_path)
        target_col = f"future_profitable_{horizon_days}d"
        query = f"SELECT * FROM trader_history WHERE {target_col} IS NOT NULL"
        df = pd.read_sql_query(query, conn)
        conn.close()
        
        if len(df) < 50:
            print(f"❌ Pas assez de données: {len(df)} (minimum 50)")
            return None, None
        
        # Logique de feature engineering alignée sur le bootstrap et la prédiction
        try:
            market_data_df = df['market_data'].apply(lambda x: json.loads(x)).apply(pd.Series)
            
            # Extraction des données nichées
            df['btc_price'] = market_data_df['coingecko_btc'].apply(lambda x: x.get('price', 0) if isinstance(x, dict) else 0)
            df['fear_greed_index'] = market_data_df['fear_and_greed_index'].apply(lambda x: x.get('value', 50) if isinstance(x, dict) else 50)
            
            def get_funding_rate(data):
                if isinstance(data, dict):
                    return data.get('BTCUSDT', {}).get('last_funding_rate', 0.0)
                return 0.0
            df['funding_rate'] = market_data_df['funding_rates'].apply(get_funding_rate)
            
            df['long_percentage_numeric'] = df['long_percentage'].astype(str).str.replace('%', '').astype(float)
            
            feature_cols = ['pnl_24h', 'pnl_7d', 'pnl_30d', 'long_percentage_numeric', 'btc_price', 'fear_greed_index', 'funding_rate']
            
            # Le reste est identique, mais on cible la bonne colonne
            X = df[feature_cols].fillna(0)
            y = df[target_col].astype(int)
            
            print(f"✅ Données préparées pour J+{horizon_days}: {len(X)} échantillons.")
            return X, y
            
        except Exception as e:
            print(f"❌ Erreur lors de la préparation des données d'entraînement: {e}")
            import traceback
            traceback.print_exc()
            return None, None

    def train_and_save_model(self, horizon_days):
        """Entraîne un modèle pour un horizon spécifique et le sauvegarde."""
        print(f"🤖 Entraînement du modèle pour un horizon de {horizon_days} jours...")
        X, y = self.prepare_training_data(horizon_days=horizon_days)
        
        if X is None or y is None:
            print(f"❌ Pas assez de données pour l'horizon {horizon_days} jours.")
            return

        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
        
        scaler = StandardScaler()
        X_train_scaled = scaler.fit_transform(X_train)
        X_test_scaled = scaler.transform(X_test)
        
        model = RandomForestClassifier(n_estimators=100, random_state=42, class_weight='balanced')
        model.fit(X_train_scaled, y_train)
        
        # Sauvegarde
        model_filename = f"model_{horizon_days}d.pkl"
        scaler_filename = f"scaler_{horizon_days}d.pkl"
        joblib.dump(model, self.model_path / model_filename)
        joblib.dump(scaler, self.model_path / scaler_filename)
        
        auc = roc_auc_score(y_test, model.predict_proba(X_test_scaled)[:, 1])
        print(f"✅ Modèle J+{horizon_days} entraîné et sauvegardé (AUC: {auc:.3f}).")

    def predict_trader_profitability(self, trader_data, market_data, horizon_days=7):
        """
        Prédit la profitabilité future d'un seul trader pour un horizon donné.
        
        RETOURNE:
            Un tuple (prediction_text, probability_score)
        """
        model_filename = f"model_{horizon_days}d.pkl"
        scaler_filename = f"scaler_{horizon_days}d.pkl"
        
        model_file = self.model_path / model_filename
        scaler_file = self.model_path / scaler_filename

        if not model_file.exists() or not scaler_file.exists():
            return "Modèle non entraîné. Veuillez collecter des données pendant au moins 7 jours.", None

        model = joblib.load(model_file)
        scaler = joblib.load(scaler_file)

        # Fonction pour convertir le PnL en float (identique à store_daily_snapshot)
        def pnl_to_float(pnl_str):
            if isinstance(pnl_str, (int, float)): return float(pnl_str)
            pnl_str = str(pnl_str).replace('$', '').strip()
            if 'M' in pnl_str: return float(pnl_str.replace('M', '')) * 1e6
            if 'K' in pnl_str: return float(pnl_str.replace('K', '')) * 1e3
            try: return float(pnl_str)
            except (ValueError, TypeError): return 0.0

        # Préparation du vecteur de features pour ce trader
        features = {
            'pnl_24h': pnl_to_float(trader_data.get('pnl_24h')),
            'pnl_7d': pnl_to_float(trader_data.get('pnl_7d')),
            'pnl_30d': pnl_to_float(trader_data.get('pnl_30d')),
            # 'pnl_total' n'est pas utilisé dans le modèle bootstrap
            'long_percentage_numeric': pnl_to_float(trader_data.get('long_percentage', '0%').replace('%', '')),
            'btc_price': market_data.get('coingecko_btc', {}).get('price'),
            'fear_greed_index': market_data.get('fear_and_greed_index', {}).get('value'),
            # Renommé pour correspondre à l'entraînement
            'funding_rate': market_data.get('funding_rates', {}).get('BTCUSDT', {}).get('last_funding_rate'),
        }
        df = pd.DataFrame([features])

        # Assurer que les colonnes sont dans le bon ordre
        feature_cols_ordered = ['pnl_24h', 'pnl_7d', 'pnl_30d', 'long_percentage_numeric', 'btc_price', 'fear_greed_index', 'funding_rate']
        df = df[feature_cols_ordered]

        # Pas de feature engineering supplémentaire pour la prédiction (pnl_momentum) pour l'instant
        
        # Mise à l'échelle des features
        scaled_features = scaler.transform(df)

        # Prédiction
        probability = model.predict_proba(scaled_features)[:, 1][0]
        
        if probability > 0.6:
            text_result = "Fortement susceptible d'être profitable"
        elif probability > 0.4:
            text_result = "Potentiellement profitable"
        else:
            text_result = "Probablement non profitable"
            
        return text_result, probability


class MLDataCollector:
    """Collecteur de données pour le ML."""
    
    def __init__(self):
        self.predictor = CryptoMLPredictor()
        self.funding_rates_scraper = FundingRatesScraper()

    def get_market_data(self):
        """Récupère les données de marché agrégées."""
        funding_data = self.funding_rates_scraper.scrape()
        
        return {
            "coingecko_btc": scrape_coingecko_metrics() or {},
            "fear_and_greed_index": scrape_fear_and_greed_index() or {},
            "funding_rates": funding_data if funding_data is not None else {},
        }

    def daily_data_collection(self):
        """Script à exécuter quotidiennement."""
        print(f"🔄 Collecte quotidienne - {datetime.now()}")
        
        try:
            print("📊 Scraping des top traders...")
            traders_data = scrape_top_traders()
            
            if not traders_data:
                print("Aucune donnée de trader, la collecte s'arrête.")
                return

            print("📈 Collecte des données de marché...")
            market_data = self.get_market_data()

            # --- AJOUT DE VALIDATION ---
            if not isinstance(market_data.get('coingecko_btc'), dict) or not isinstance(market_data.get('fear_and_greed_index'), dict):
                print("❌ Erreur de validation: les données de marché ne sont pas des dictionnaires.")
                print(f"   - CoinGecko type: {type(market_data.get('coingecko_btc'))}")
                print(f"   - Fear & Greed type: {type(market_data.get('fear_and_greed_index'))}")
                return
            # --- FIN DE VALIDATION ---
            
            self.predictor.store_daily_snapshot(traders_data, market_data)
            updated = self.predictor.update_target_variables(horizon_days=7) # Update for 7 days
            
            if updated > 10:
                print("🤖 Assez de nouvelles données, ré-entraînement du modèle...")
                self.predictor.train_and_save_model(horizon_days=7) # Train for 7 days
            
            print("✅ Collecte quotidienne terminée.")
            
        except Exception as e:
            print(f"❌ Erreur lors de la collecte quotidienne : {e}") 