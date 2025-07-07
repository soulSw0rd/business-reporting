# -*- coding: utf-8 -*-
"""
OBJECTIF : Agréger les données provenant de toutes les sources de marché en un seul dictionnaire.
"""

from asyncio import gather
from typing import Dict, Any

from .etherscan import scrape_top_eth_accounts
from .fear_and_greed import scrape_fear_and_greed_index
from .funding_rates import FundingRatesScraper
from .coingecko import scrape_coingecko_metrics


async def get_market_sentiment_metrics() -> Dict[str, Any]:
    """
    OBJECTIF : Agréger les données de plusieurs scrapers pour obtenir une vue d'ensemble du marché.
    
    RETOURNE :
    - Dict[str, Any] : Un dictionnaire contenant les métriques collectées.
    """
    funding_scraper = FundingRatesScraper()
    metrics: Dict[str, Any] = {}

    # --- Tâches Synchrones ---
    # Tous nos scrapers actuels sont basés sur requests/API, donc synchrones.
    # On les exécute séquentiellement avec une gestion d'erreur robuste.
    
    scraper_tasks = {
        "coingecko_btc_metrics": scrape_coingecko_metrics,
        "top_eth_accounts": scrape_top_eth_accounts,
        "fear_and_greed_index": scrape_fear_and_greed_index,
        "funding_rates": lambda: funding_scraper.get_funding_rates(symbols=['BTCUSDT', 'ETHUSDT']),
    }

    for name, task in scraper_tasks.items():
        try:
            result = task()
            # Les scrapers qui retournent un dictionnaire avec une clé parente sont directement intégrés
            if isinstance(result, dict) and len(result) == 1 and isinstance(list(result.values())[0], dict):
                metrics.update(result)
            else:
                metrics[name] = result
        except Exception as e:
            metrics[name] = {"error": f"Failed to fetch {name}: {e}"}

    return metrics 