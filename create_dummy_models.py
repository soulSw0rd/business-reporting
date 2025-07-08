import joblib
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
from pathlib import Path
import numpy as np

def create_dummy_model_and_scaler():
    """Crée un modèle et un scaler factices avec 7 features."""
    # Créer des données d'entraînement factices avec 7 features
    # Features: ['pnl_24h', 'pnl_7d', 'pnl_30d', 'long_percentage_numeric', 'btc_price', 'fear_greed_index', 'funding_rate']
    
    # Données d'exemple avec 7 features
    X_dummy = np.array([
        [1000, 5000, 20000, 60.0, 65000, 50, 0.0001],  # Trader profitable
        [-500, -2000, -8000, 40.0, 64000, 30, -0.0001], # Trader non profitable
        [2000, 8000, 30000, 70.0, 66000, 70, 0.0002],  # Trader très profitable
        [-1000, -3000, -10000, 30.0, 63000, 20, -0.0002] # Trader en perte
    ])
    
    y_dummy = np.array([1, 0, 1, 0])  # 1 = profitable, 0 = non profitable
    
    # Créer et entraîner le modèle
    model = RandomForestClassifier(n_estimators=10, random_state=42)
    model.fit(X_dummy, y_dummy)

    # Créer et entraîner le scaler avec les bonnes dimensions
    scaler = StandardScaler()
    scaler.fit(X_dummy)

    return model, scaler

def main():
    """Génère et sauvegarde les modèles factices pour les horizons 7 et 30 jours."""
    print("--- Création de modèles de prédiction factices (7 features) ---")
    
    model_dir = Path("data/ml_training/models")
    model_dir.mkdir(parents=True, exist_ok=True)
    
    horizons = [7, 30]
    for horizon in horizons:
        model, scaler = create_dummy_model_and_scaler()
        
        model_path = model_dir / f"model_{horizon}d.pkl"
        scaler_path = model_dir / f"scaler_{horizon}d.pkl"
        
        joblib.dump(model, model_path)
        joblib.dump(scaler, scaler_path)
        
        print(f"✅ Modèle factice J+{horizon} sauvegardé : {model_path}")
        print(f"✅ Scaler factice J+{horizon} sauvegardé : {scaler_path}")

    print("\n🎉 Modèles factices avec 7 features prêts à l'emploi !")

if __name__ == "__main__":
    main() 