# CLEANUP LOG - Restructuration du Projet

**Date de l'opération :** 2025-07-01

## 1. OBJECTIF DE LA RESTRUCTURATION

L'objectif de cette opération est de réorganiser complètement le projet en appliquant une nouvelle arborescence logique, en nettoyant le code, en supprimant les fichiers obsolètes et en standardisant les conventions de nommage. Cette transformation vise à améliorer la clarté, la maintenabilité et la scalabilité du projet.

## 2. FICHIERS ET DOSSIERS SUPPRIMÉS

La règle "Pas de backup, pas d'archive" a été appliquée. Tous les fichiers et dossiers listés ci-dessous ont été **supprimés définitivement** car ils étaient considérés comme obsolètes, redondants, ou inutiles pour la version actuelle et future du projet.

| Chemin du Fichier/Dossier Supprimé       | Justification de la Suppression                                                                              |
| ---------------------------------------- | ------------------------------------------------------------------------------------------------------------ |
| `scripts/data/`                          | Contenait des fichiers JSON de résultats de tests. Ces artéfacts de tests passés sont obsolètes.             |
| `scripts/simple_wallet_analyzer.py`      | Script initial basé sur des données simulées. Remplacé par une approche de scraping de données réelles.       |
| `scripts/dashboard_test.py`              | Script de test exploratoire. Remplacé par des prototypes plus avancés ou des tests d'intégration formels.      |
| `scripts/multi_wallet_dashboard.py`      | Prototype de dashboard. Le développement se concentre maintenant sur l'API et une webapp dédiée.                  |
| `scripts/test_hyperdash_access.py`       | Script de test initial pour l'accès à Hyperdash. Remplacé par `test_hyperdash_pages.py` qui est plus complet. |
| `scripts/test_specific_user_agent.py`    | Test d'une méthode de scraping qui a échoué. Obsolète depuis l'adoption de `cloudscraper`.                 |
| `scripts/wallet_analyzer.py`             | Version intermédiaire d'un analyseur. La logique a été intégrée et améliorée dans les services de l'API.    |
| `scripts/blockchain_wallet_analyzer.py`  | Script d'analyse spécifique dont la fonctionnalité est maintenant intégrée ou prévue dans l'API.              |
| `requirements_scraping.txt`              | Fichier de dépendances redondant. Toutes les dépendances ont été fusionnées dans `requirements.txt`.         |
| `docs/` (ancien dossier)                 | Le contenu a été migré, renommé et réorganisé dans le nouveau dossier `DOCUMENTATION/guides/`.                 |
| `scripts/` (ancien dossier)              | Dossier fourre-tout. Les scripts utiles ont été déplacés et les autres ont été supprimés.                      |

## 3. ACTIONS DE REFACTORING ET DE DÉPLACEMENT

*   **Code Source** : Le contenu de `src/` est déplacé vers `SRC/` pour une meilleure clarté.
*   **Tests** : Les tests de `tests/` sont déplacés vers `TESTS/` et seront organisés en tests unitaires et d'intégration.
*   **Scripts Utiles** : Les scripts restants ont été renommés et déplacés vers `ADMIN/scripts/` ou `NOTEBOOKS/`.
*   **Dépendances** : `requirements.txt` a été mis à jour et déplacé vers `ADMIN/config/`.
*   **Documentation** : Migrée vers `DOCUMENTATION/` avec des noms de fichiers améliorés.

Cette opération laisse le projet avec une base de code propre, une structure de fichiers logique et une documentation claire pour guider les développements futurs. 