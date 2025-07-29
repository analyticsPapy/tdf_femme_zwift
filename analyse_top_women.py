import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# Création d'une base simplifiée des coureuses avec notes sur différents types d'étapes (0 à 10)
# Hypothétique, basé sur performances passées et style
data = {
    'Coureuse': [
        'Lorena Wiebes', 'Marianne Vos', 'Kasia Niewiadoma',
        'Demi Vollering', 'Pauline Ferrand-Prevot', 'Mavi Garcia'
    ],
    'Sprint': [9.5, 8.5, 5.0, 4.5, 6.0, 4.0],
    'Vallonnée': [5.5, 7.5, 8.5, 8.0, 7.5, 6.5],
    'Montagne': [2.5, 4.0, 9.0, 9.5, 8.0, 7.5],
    'Forme_2025': [8.5, 9.0, 9.0, 6.5, 8.5, 7.5],  # estimation forme 2025 post-étape 3
    'Blessure': [0, 0, 0, 1, 0, 0]  # 1 = impacté par une chute (Vollering)
}

df = pd.DataFrame(data)

# Pondération des critères selon profil d'étape
# Exemple : Étape 4 = Sprint plat
weights_sprint = {'Sprint': 0.6, 'Vallonnée': 0.1, 'Montagne': 0.0, 'Forme_2025': 0.3, 'Blessure': -0.2}

def score(row, weights):
    score_val = 0
    for key, w in weights.items():
        score_val += row[key] * w if key != 'Blessure' else -row[key] * abs(w)
    return score_val

# Calcul score pour Étape 4
df['Score_Etape4'] = df.apply(lambda row: score(row, weights_sprint), axis=1)
df_sorted = df.sort_values(by='Score_Etape4', ascending=False)

# Calcul indice de confiance = std dev normalisée inversée
confidence_index = 1 - (df['Score_Etape4'].std() / df['Score_Etape4'].mean())

import ace_tools as tools; tools.display_dataframe_to_user(name="Prévision Étape 4 - Score par coureuse", dataframe=df_sorted)

confidence_index

# Définir les profils d'étapes restantes
etapes = {
    'Etape 5 - Vallonnée': {'Sprint': 0.2, 'Vallonnée': 0.5, 'Montagne': 0.1, 'Forme_2025': 0.2, 'Blessure': -0.2},
    'Etape 6 - Montagne Moyenne': {'Sprint': 0.1, 'Vallonnée': 0.3, 'Montagne': 0.4, 'Forme_2025': 0.2, 'Blessure': -0.2},
    'Etape 7 - Vallonnée Longue': {'Sprint': 0.15, 'Vallonnée': 0.55, 'Montagne': 0.1, 'Forme_2025': 0.2, 'Blessure': -0.2},
    'Etape 8 - Haute Montagne (Madeleine)': {'Sprint': 0.0, 'Vallonnée': 0.1, 'Montagne': 0.65, 'Forme_2025': 0.25, 'Blessure': -0.2},
    'Etape 9 - Haute Montagne (Joux Plane)': {'Sprint': 0.0, 'Vallonnée': 0.05, 'Montagne': 0.7, 'Forme_2025': 0.25, 'Blessure': -0.2}
}

# Créer un dictionnaire pour stocker tous les scores et indices de confiance
results = {}
confidences = {}

# Calculer les scores pour chaque étape
for etape, weights in etapes.items():
    df[etape] = df.apply(lambda row: score(row, weights), axis=1)
    results[etape] = df[['Coureuse', etape]].sort_values(by=etape, ascending=False)
    std = df[etape].std()
    mean = df[etape].mean()
    confidences[etape] = round(1 - (std / mean), 2)

# Générer un graphique par étape
figs = []
for etape, scores in results.items():
    fig, ax = plt.subplots(figsize=(8, 4))
    ax.bar(scores['Coureuse'], scores[etape], color='skyblue')
    ax.set_title(f"{etape} – Scores prédictifs des coureuses")
    ax.set_ylabel("Score (0-10)")
    ax.set_ylim(0, 10)
    ax.set_xticklabels(scores['Coureuse'], rotation=45, ha='right')
    ax.text(0.95, 0.9, f"Indice de confiance : {confidences[etape]}", transform=ax.transAxes,
            fontsize=10, color='darkgreen', ha='right')
    figs.append(fig)

# Afficher tableau récapitulatif
results_summary = pd.DataFrame({
    'Étape': list(etapes.keys()),
    'Indice de confiance': list(confidences.values())
})

tools.display_dataframe_to_user(name="Indice de confiance par étape", dataframe=results_summary)

from math import pi

# Sélection des colonnes pour radar plot
radar_data = df[['Coureuse', 'Sprint', 'Vallonnée', 'Montagne', 'Forme_2025']]
categories = list(radar_data.columns[1:])
N = len(categories)

# Normaliser les données pour que chaque axe soit de 0 à 10
radar_data_normalized = radar_data.copy()
for col in categories:
    radar_data_normalized[col] = radar_data_normalized[col] / 10  # tout ramener entre 0 et 1

# Configuration du radar plot
angles = [n / float(N) * 2 * pi for n in range(N)]
angles += angles[:1]  # fermeture du cercle

# Initialisation du plot
fig, ax = plt.subplots(figsize=(8, 8), subplot_kw=dict(polar=True))

# Tracer chaque coureuse
for i, row in radar_data_normalized.iterrows():
    values = row.drop('Coureuse').tolist()
    values += values[:1]  # fermeture du polygone
    ax.plot(angles, values, linewidth=1, linestyle='solid', label=row['Coureuse'])
    ax.fill(angles, values, alpha=0.1)

# Ajout des étiquettes
ax.set_xticks(angles[:-1])
ax.set_xticklabels(categories)
ax.set_yticklabels(["0", "2", "4", "6", "8", "10"], color="grey", size=8)
ax.set_title("Comparaison des profils de coureuses – Tour de France Femmes 2025", size=12, pad=20)
ax.legend(loc='upper right', bbox_to_anchor=(1.3, 1.1))

plt.tight_layout()
plt.show()
# Générer un radar plot individuel pour chaque coureuse
figs = []
for i, row in radar_data_normalized.iterrows():
    fig, ax = plt.subplots(figsize=(6, 6), subplot_kw=dict(polar=True))
    
    values = row.drop('Coureuse').tolist()
    values += values[:1]
    
    ax.plot(angles, values, linewidth=2, linestyle='solid')
    ax.fill(angles, values, alpha=0.25)
    
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(categories)
    ax.set_yticklabels(["0", "2", "4", "6", "8", "10"], color="grey", size=7)
    ax.set_title(f"Profil de {row['Coureuse']}", size=13, pad=20)
    
    figs.append(fig)

plt.tight_layout()
plt.show()
