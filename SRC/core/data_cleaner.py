import pandas as pd
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DataCleaner:
    """
    OBJECTIF : Fournir des méthodes pour nettoyer et pré-traiter les données brutes.
    """

    def remove_outliers_iqr(self, df: pd.DataFrame, column: str) -> pd.DataFrame:
        """
        OBJECTIF : Supprimer les outliers d'une colonne en utilisant l'écart interquartile (IQR).

        PARAMÈTRES :
        - df (pd.DataFrame): Le DataFrame à nettoyer.
        - column (str): Le nom de la colonne numérique à traiter.

        RETOURNE :
        - pd.DataFrame: Un nouveau DataFrame sans les outliers.
        
        LOGIQUE :
        1. Calcule le premier (Q1) et le troisième (Q3) quartile.
        2. Détermine l'écart interquartile (IQR).
        3. Définit les bornes inférieure et supérieure pour détecter les outliers.
        4. Filtre le DataFrame pour ne conserver que les valeurs dans ces bornes.
        """
        if column not in df.columns:
            logger.warning(f"La colonne '{column}' n'a pas été trouvée pour la suppression des valeurs aberrantes.")
            return df

        Q1 = df[column].quantile(0.25)
        Q3 = df[column].quantile(0.75)
        IQR = Q3 - Q1
        lower_bound = Q1 - 1.5 * IQR
        upper_bound = Q3 + 1.5 * IQR

        original_rows = len(df)
        df_cleaned = df[(df[column] >= lower_bound) & (df[column] <= upper_bound)]
        removed_rows = original_rows - len(df_cleaned)
        
        if removed_rows > 0:
            logger.info(f"{removed_rows} valeurs aberrantes supprimées de la colonne '{column}'.")
            
        return df_cleaned

    def fill_missing_numeric(self, df: pd.DataFrame, strategy: str = 'median') -> pd.DataFrame:
        """
        OBJECTIF : Remplir les valeurs numériques manquantes (NaN) dans un DataFrame.

        PARAMÈTRES :
        - df (pd.DataFrame): Le DataFrame à traiter.
        - strategy (str): La méthode à utiliser ('mean', 'median', ou 'zero').

        RETOURNE :
        - pd.DataFrame: Le DataFrame avec les valeurs manquantes remplies.
        
        LOGIQUE :
        1. Itère sur toutes les colonnes numériques du DataFrame.
        2. Si une colonne contient des valeurs nulles :
           a. Calcule la valeur de remplacement selon la stratégie choisie.
           b. Remplit les valeurs manquantes avec cette valeur.
        """
        df_filled = df.copy()
        for col in df_filled.select_dtypes(include=['number']).columns:
            if df_filled[col].isnull().any():
                if strategy == 'mean':
                    fill_value = df_filled[col].mean()
                elif strategy == 'median':
                    fill_value = df_filled[col].median()
                else: # 'zero'
                    fill_value = 0
                
                df_filled[col] = df_filled[col].fillna(fill_value)
                logger.info(f"Valeurs manquantes dans '{col}' remplies avec la {strategy} ({fill_value:.2f}).")
                
        return df_filled

    def standardize_data_types(self, df: pd.DataFrame, type_mapping: dict) -> pd.DataFrame:
        """
        OBJECTIF : Assurer que chaque colonne d'un DataFrame a le type de données correct.

        PARAMÈTRES :
        - df (pd.DataFrame): Le DataFrame à standardiser.
        - type_mapping (dict): Dictionnaire mappant les noms de colonnes à leur type désiré.

        RETOURNE :
        - pd.DataFrame: Le DataFrame avec les types de données corrigés.
        
        LOGIQUE :
        1. Itère sur le dictionnaire de mapping (colonne -> type).
        2. Pour chaque colonne, tente de la convertir au type spécifié.
        3. Gère les erreurs si la conversion est impossible.
        """
        df_standardized = df.copy()
        for column, dtype in type_mapping.items():
            if column in df_standardized.columns:
                try:
                    df_standardized[column] = df_standardized[column].astype(dtype)
                except (ValueError, TypeError) as e:
                    logger.error(f"Impossible de convertir la colonne '{column}' en type '{dtype}': {e}")
        return df_standardized 