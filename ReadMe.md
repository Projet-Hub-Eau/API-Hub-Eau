# 🐟📊 Application Streamlit : Analyse des données Hub'Eau

Cette application permet d'explorer et de télécharger les données de différentes stations de mesures piscicoles et de qualité des eaux en France à partir des APIs publiques Hub'Eau : [https://hubeau.eaufrance.fr/](https://hubeau.eaufrance.fr/).

## 🚀 Fonctionnalités

- Recherche de stations piscicoles par nom de fleuve
- Affichage des stations sur une carte interactive
- Sélection manuelle des stations à étudier
- Téléchargement des données associées : poissons, qualité des rivières, opérations, indicateurs, etc.

---

## 🧰 Prérequis

- Python 3.9 ou plus récent
- Git (facultatif si vous téléchargez manuellement les fichiers)
- Visual Studio Code (VS Code) ou Anaconda
- Une connexion Internet (pour accéder aux APIs Hub'Eau)

---

## 🛠️ Installation étape par étape avec VS Code

### 1. Cloner ce dépôt

```bash
git clone https://github.com/fernand-f/API-Hub-Eau.git
cd API-Hub-Eau
```

### 2. Créer un environnement python

```bash
python -m venv .venv
```
#### Activer l'environnement sous Windows
```bash
.venv\Scripts\activate
```
#### Activer l'environnement sous macOS/Linux
```bash
source .venv/bin/activate
```
### 3. Installer les dépendances
Avec pip : 
```bash
pip install -r requirements.txt
```
Avec conda : 
```bash
conda create -n hubeau-env python=3.10
conda activate hubeau-env
pip install -r requirements.txt
```
## Lancer l'application depuis le bash
```bash
streamlit run app.py
```
## Structure du projet 
```bash
API-Hub-Eau/
│
├── app.py                  # Application principale Streamlit
├── setup.py                # Script d'installation du module `hub_o`
├── requirements.txt        # Dépendances Python
├── README.md               # Ce fichier
├── .gitignore              # Fichiers à ignorer par Git
├── LICENSE                 # Licence MIT
├── hub_o/
│   └── HubEauClass.py      # Classe d’accès aux APIs Hub’Eau
└── hub_o.egg-info/         # (généré automatiquement si module installé)
```

## 🔧 Installer le module hub_o localement

En mode développement (recommandé):
```bash
pip install -e .
```
Ou en mode standard : 
```bash
pip install .
```


