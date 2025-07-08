import subprocess
import sys
import os
from pathlib import Path

def setup_environment():
    # Création de l'environnement virtuel
    subprocess.check_call([sys.executable, '-m', 'venv', 'ds'])
    
    # Détermination du chemin d'activation selon le système d'exploitation
    if sys.platform == "win32":
        activate_script = Path('ds/Scripts/activate')
    else:
        activate_script = Path('ds/bin/activate')
    
    print(f"Environnement virtuel créé dans le dossier 'ds'")
    print(f"Pour activer l'environnement:")
    if sys.platform == "win32":
        print("ds\\Scripts\\activate")
    else:
        print("source ds/bin/activate")
    
    print("\nPour installer les dépendances après activation:")
    print("pip install -r requirements.txt")

if __name__ == "__main__":
    setup_environment()

