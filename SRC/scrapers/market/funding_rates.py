import requests
from datetime import datetime
import logging
from typing import Dict, List, Optional, Any

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class FundingRatesScraper:
    """
    OBJECTIF : Scraper les taux de financement (funding rates) depuis l'API publique de Binance.
    """
    BASE_URL = "https://fapi.binance.com"
    ENDPOINT = "/fapi/v1/fundingRate"

    def get_funding_rates(self, symbols: Optional[List[str]] = None) -> Dict[str, Optional[Dict[str, Any]]]:
        """
        OBJECTIF : Récupérer les derniers taux de financement pour une liste de symboles.

        PARAMÈTRES :
        - symbols (Optional[List[str]]): Liste de symboles (ex: ['BTCUSDT', 'ETHUSDT']).
                                         Par défaut, utilise ['BTCUSDT'].

        RETOURNE :
        - Dict[str, Optional[Dict[str, Any]]] : Dictionnaire mappant chaque symbole à ses données de funding,
                                                ou None si la récupération a échoué pour ce symbole.
        
        LOGIQUE :
        1. Itère sur chaque symbole fourni.
        2. Construit et exécute une requête vers l'API de Binance.
        3. Parse la réponse JSON pour extraire le taux de financement, l'heure et le "mark price".
        4. Gère les erreurs de connexion et les réponses vides.
        """
        if symbols is None:
            symbols = ['BTCUSDT']
            
        logging.info(f"Fetching funding rates for symbols: {symbols}")
        
        rates: Dict[str, Optional[Dict[str, Any]]] = {}
        for symbol in symbols:
            url = f"{self.BASE_URL}{self.ENDPOINT}"
            params = {
                'symbol': symbol,
                'limit': 1
            }
            try:
                response = requests.get(url, params=params)
                response.raise_for_status()
                
                data = response.json()
                if data:
                    latest_rate_info = data[0]
                    rates[symbol] = {
                        'funding_rate': float(latest_rate_info['fundingRate']),
                        'funding_time': datetime.fromtimestamp(latest_rate_info['fundingTime'] / 1000).isoformat(),
                        'mark_price': float(latest_rate_info['markPrice'])
                    }
                    logging.info(f"Successfully fetched funding rate for {symbol}: {rates[symbol]['funding_rate']}")
                else:
                    logging.warning(f"No funding rate data returned for {symbol}")
                    rates[symbol] = None

            except requests.exceptions.RequestException as e:
                logging.error(f"Error fetching funding rate for {symbol}: {e}")
                rates[symbol] = None
        
        return rates

    def calculate_average_funding(self, rates: Dict[str, Optional[Dict[str, Any]]]) -> float:
        """
        OBJECTIF : Calculer la moyenne des taux de financement à partir des données récupérées.

        PARAMÈTRES :
        - rates (Dict): Dictionnaire des taux de financement retourné par get_funding_rates.

        RETOURNE :
        - float : La moyenne des taux de financement valides, ou 0.0 si aucun n'est trouvé.
        
        LOGIQUE :
        1. Crée une liste contenant uniquement les valeurs de "funding_rate" valides.
        2. Calcule et retourne la moyenne de cette liste.
        """
        valid_rates = [
            rate_info['funding_rate'] 
            for rate_info in rates.values() 
            if rate_info and 'funding_rate' in rate_info
        ]
        
        if not valid_rates:
            logging.warning("No valid funding rates found to calculate an average.")
            return 0.0
            
        average = sum(valid_rates) / len(valid_rates)
        logging.info(f"Calculated average funding rate: {average}")
        return average 