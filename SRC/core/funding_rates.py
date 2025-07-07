# -*- coding: utf-8 -*-
"""
OBJECTIF : Scraper les taux de financement (Funding Rates) depuis l'API de Binance.
"""
import requests
from typing import List, Dict, Any, Optional

class FundingRatesScraper:
    """
    Classe pour scraper les taux de financement pour une liste de paires de trading.
    """
    BASE_URL = "https://fapi.binance.com/fapi/v1/premiumIndex"
    SYMBOLS = ["BTCUSDT", "ETHUSDT"]

    def scrape(self) -> Optional[Dict[str, Any]]:
        """
        Récupère les taux de financement pour les symboles définis.

        RETOURNE :
            Un dictionnaire où chaque clé est un symbole (ex: BTCUSDT) et la valeur
            est un autre dictionnaire contenant les détails du funding rate.
            Retourne None si une erreur majeure se produit.
        """
        all_metrics = {}
        print("Récupération des taux de financement de Binance...")
        try:
            for symbol in self.SYMBOLS:
                url = f"{self.BASE_URL}?symbol={symbol}"
                response = requests.get(url, timeout=10)
                response.raise_for_status()
                data = response.json()
                
                # Conversion des chaînes en float pour une utilisation numérique
                all_metrics[symbol] = {
                    "last_funding_rate": float(data.get("lastFundingRate", 0.0)),
                    "next_funding_time": int(data.get("nextFundingTime", 0)),
                    "interest_rate": float(data.get("interestRate", 0.0)),
                }
            print(f"✅ Taux de financement pour {len(self.SYMBOLS)} paires récupérés.")
            return all_metrics
            
        except requests.exceptions.RequestException as e:
            print(f"❌ Erreur Funding Rates : Échec de la requête vers l'API Binance : {e}")
            return None
        except (KeyError, ValueError) as e:
            print(f"❌ Erreur Funding Rates : Format de données inattendu de Binance : {e}")
            return None 