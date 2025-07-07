import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CryptoDataValidator:
    """
    OBJECTIF : Valider les données cryptographiques pour garantir leur cohérence et leur fiabilité.
    """

    def validate_trader_profile(self, trader_data: dict) -> dict:
        """
        OBJECTIF : Valider la cohérence interne des données de profil d'un trader.

        PARAMÈTRES :
        - trader_data (dict): Dictionnaire contenant les métriques du trader.

        RETOURNE :
        - dict : Dictionnaire avec un statut de validité et une liste de problèmes.
        
        LOGIQUE :
        1. Vérifie si le PnL est réaliste par rapport au volume.
        2. Vérifie si le "win rate" n'est pas anormalement élevé.
        3. Vérifie si le trader n'est pas inactif depuis trop longtemps.
        """
        issues = []
        
        # ÉTAPE 1: Vérification de la cohérence du PnL
        pnl = trader_data.get('pnl_7d')
        volume = trader_data.get('volume_7d')
        if pnl is not None and volume is not None and volume > 0:
            if pnl > volume * 0.5:
                issues.append(f"Le PnL ({pnl}) semble anormalement élevé par rapport au volume ({volume}).")

        # ÉTAPE 2: Vérification du réalisme du win rate
        win_rate = trader_data.get('win_rate')
        if win_rate is not None and win_rate > 0.95:
            issues.append(f"Le win rate ({win_rate:.2%}) est irréaliste (> 95%).")

        # ÉTAPE 3: Vérification de l'activité récente
        last_trade = trader_data.get('last_trade_days_ago')
        if last_trade is not None and last_trade > 7:
            issues.append(f"Le trader est inactif depuis plus de 7 jours ({last_trade} jours).")

        is_valid = not issues
        return {'valid': is_valid, 'issues': issues}

    def detect_data_anomalies(self, data: list[dict], metric: str, threshold: float = 3.0) -> list:
        """
        OBJECTIF : Détecter les anomalies dans une série de données en utilisant le Z-score.
        
        PARAMÈTRES :
        - data (list[dict]): Liste de dictionnaires à analyser.
        - metric (str): La clé numérique à vérifier pour les anomalies.
        - threshold (float): Le seuil de Z-score pour marquer une donnée comme anomalie.

        RETOURNE :
        - list : Liste des données identifiées comme anormales.
        
        LOGIQUE :
        1. Calcule la moyenne et l'écart-type de la métrique sur l'ensemble des données.
        2. Pour chaque point de donnée, calcule son Z-score.
        3. Si le Z-score dépasse le seuil, le point est considéré comme une anomalie.
        """
        values = [d[metric] for d in data if metric in d and d[metric] is not None]
        if not values:
            return []

        mean = sum(values) / len(values)
        std_dev = (sum([(v - mean) ** 2 for v in values]) / len(values)) ** 0.5
        
        if std_dev == 0:
            return []

        anomalies = []
        for d in data:
            if metric in d and d[metric] is not None:
                z_score = (d[metric] - mean) / std_dev
                if abs(z_score) > threshold:
                    anomalies.append({'data': d, 'z_score': z_score})
        
        if anomalies:
            logger.warning(f"Détection de {len(anomalies)} anomalies pour la métrique '{metric}'.")
        return anomalies

    def get_data_completeness_report(self, data: list[dict], required_fields: list[str]) -> dict:
        """
        OBJECTIF : Générer un rapport sur l'exhaustivité des données pour des champs spécifiés.

        PARAMÈTRES :
        - data (list[dict]): La liste des enregistrements à vérifier.
        - required_fields (list[str]): La liste des champs dont la présence est requise.

        RETOURNE :
        - dict : Un rapport détaillant le taux de complétude global et par champ.
        
        LOGIQUE :
        1. Compte le nombre d'enregistrements totaux.
        2. Pour chaque champ requis, compte combien de fois il est présent et non nul.
        3. Calcule les pourcentages de complétude.
        """
        total_records = len(data)
        if total_records == 0:
            return {
                'overall_completeness': 0.0,
                'completeness_per_field': {field: 0.0 for field in required_fields},
                'missing_counts': {field: 0 for field in required_fields}
            }

        field_counts = {field: 0 for field in required_fields}
        for record in data:
            for field in required_fields:
                if record.get(field) is not None:
                    field_counts[field] += 1
        
        completeness_per_field = {f: (c / total_records) * 100 for f, c in field_counts.items()}
        missing_counts = {f: total_records - c for f, c in field_counts.items()}
        
        overall_completeness = sum(completeness_per_field.values()) / len(required_fields) if required_fields else 0

        return {
            'overall_completeness': round(overall_completeness, 2),
            'completeness_per_field': {f: round(v, 2) for f, v in completeness_per_field.items()},
            'missing_counts': missing_counts
        } 