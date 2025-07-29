## 🟡 Tour de France Femmes 2025 – Dashboard Analytique

Ce projet est une application **Streamlit** permettant de suivre, prédire et analyser les performances des coureuses du Tour de France Femmes 2025.

### 🔧 Fonctionnalités

* **Radar comparatif par coureuse** (Sprint, Vallonnée, Montagne, Forme 2025)
* **Tableau de prédictions des vainqueures par étape**, basé sur un modèle pondéré
* **Saisie manuelle des résultats journaliers**
* **Réajustement automatique des pondérations** selon les résultats
* **Historique & visualisation graphique** de l’évolution des pondérations

### 📁 Fichiers

* `app.py` – Code principal du dashboard
* `poids_historique.json` – Historique des pondérations par étape
* `README.md` – Documentation

### ▶️ Lancer le projet

```bash
streamlit run app.py
```

### 🧠 Modèle de prédiction

Chaque score est calculé par la formule pondérée suivante :

```text
Score = Sprint × w1 + Vallonnée × w2 + Montagne × w3 + Forme × w4
```

Les pondérations `w1–w4` sont ajustées automatiquement en fonction des classements journaliers saisis.
