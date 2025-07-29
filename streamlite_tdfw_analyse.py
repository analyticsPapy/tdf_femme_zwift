import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from math import pi
import json
import os

# Données des coureuses
coureuses = {
    'Lorena Wiebes': [9.5, 5.5, 2.5, 8.5],
    'Marianne Vos': [8.5, 7.5, 4.0, 9.0],
    'Kasia Niewiadoma': [5.0, 8.5, 9.0, 9.0],
    'Demi Vollering': [4.5, 8.0, 9.5, 6.5],
    'Pauline Ferrand-Prevot': [6.0, 7.5, 8.0, 8.5],
    'Mavi Garcia': [4.0, 6.5, 7.5, 7.5],
    'Emilie Morier': [7.0, 7.5, 6.0, 8.0]
}

labels = ['Sprint', 'Vallonnée', 'Montagne', 'Forme 2025']

# Fichier mémoire pondérations
memory_file = "poids_historique.json"
historique_pond = {}
if os.path.exists(memory_file):
    try:
        with open(memory_file, 'r') as f:
            contenu = f.read().strip()
            if contenu:
                historique_pond = json.loads(contenu)
    except json.JSONDecodeError:
        historique_pond = {}

# Prédiction scores par étape (initial)
etapes = historique_pond if historique_pond else {
    'Etape 5 - Vallonnée': {'Sprint': 0.2, 'Vallonnée': 0.5, 'Montagne': 0.1, 'Forme 2025': 0.2},
    'Etape 6 - Montagne Moyenne': {'Sprint': 0.1, 'Vallonnée': 0.3, 'Montagne': 0.4, 'Forme 2025': 0.2},
    'Etape 7 - Vallonnée Longue': {'Sprint': 0.15, 'Vallonnée': 0.55, 'Montagne': 0.1, 'Forme 2025': 0.2},
    'Etape 8 - Haute Montagne': {'Sprint': 0.0, 'Vallonnée': 0.1, 'Montagne': 0.65, 'Forme 2025': 0.25},
    'Etape 9 - Haute Montagne (Joux Plane)': {'Sprint': 0.0, 'Vallonnée': 0.05, 'Montagne': 0.7, 'Forme 2025': 0.25}
}

# App
st.title("Tour de France Femmes 2025 – Dashboard Analytique")
tabs = st.tabs(["Radar coureuse", "Scores prédictifs", "Saisie résultats journaliers", "Historique pondérations"])

# Onglet Radar
with tabs[0]:
    st.subheader("Visualisation radar par coureuse")
    selected_rider = st.selectbox("Choisissez une coureuse :", list(coureuses.keys()))

    def radar_plot(values, title):
        values = [v / 10 for v in values]
        values += values[:1]
        angles = [n / float(len(labels)) * 2 * pi for n in range(len(labels))]
        angles += angles[:1]

        fig, ax = plt.subplots(figsize=(5, 5), subplot_kw=dict(polar=True))
        ax.plot(angles, values, linewidth=2)
        ax.fill(angles, values, alpha=0.3)
        ax.set_xticks(angles[:-1])
        ax.set_xticklabels(labels)
        ax.set_yticklabels(["0", "2", "4", "6", "8", "10"], color="grey", size=7)
        ax.set_title(title, size=12, pad=20)
        st.pyplot(fig)

    radar_plot(coureuses[selected_rider], f"Profil de {selected_rider}")

# Onglet Scores prédictifs
with tabs[1]:
    st.subheader("Prédiction des vainqueures par étape")

    df_scores = []
    for etape, weights in etapes.items():
        etape_scores = {}
        for rider, values in coureuses.items():
            score = (
                values[0]*weights.get('Sprint', 0) +
                values[1]*weights.get('Vallonnée', 0) +
                values[2]*weights.get('Montagne', 0) +
                values[3]*weights.get('Forme 2025', 0)
            )
            etape_scores[rider] = round(score, 2)
        df_scores.append(pd.DataFrame.from_dict(etape_scores, orient='index', columns=[etape]))

    df_final = pd.concat(df_scores, axis=1)
    st.dataframe(df_final.style.highlight_max(axis=0, color='lightgreen'))

# Onglet Saisie résultats journaliers
with tabs[2]:
    st.subheader("Entrer les résultats journaliers")

    password = st.text_input("Mot de passe requis :", type="password")
    if password != st.secrets["admin_password"]:
        st.warning("Accès restreint – veuillez entrer un mot de passe valide.")
        st.stop()

    etape_sel = st.selectbox("Choisir une étape :", list(etapes.keys()))
    classement = {}
    for rider in coureuses.keys():
        rang = st.number_input(f"Classement de {rider} pour {etape_sel} (laisser vide si non classé)", min_value=1, max_value=100, step=1, key=f"{etape_sel}_{rider}")
        classement[rider] = rang if rang else None

    if st.button("Enregistrer les résultats"):
        classement_valide = {k: v for k, v in classement.items() if v is not None}
        if classement_valide:
            poids_auto = {}
            for rider, val in classement_valide.items():
                if rider in coureuses:
                    sprint, vallonnee, montagne, forme = coureuses[rider]
                    total = sprint + vallonnee + montagne + forme
                    if total > 0:
                        poids_auto['Sprint'] = poids_auto.get('Sprint', 0) + sprint / total * (1/val)
                        poids_auto['Vallonnée'] = poids_auto.get('Vallonnée', 0) + vallonnee / total * (1/val)
                        poids_auto['Montagne'] = poids_auto.get('Montagne', 0) + montagne / total * (1/val)
                        poids_auto['Forme 2025'] = poids_auto.get('Forme 2025', 0) + forme / total * (1/val)

            somme = sum(poids_auto.values())
            if somme > 0:
                poids_final = {k: round(v / somme, 2) for k, v in poids_auto.items()}
                etapes[etape_sel] = poids_final
                historique_pond[etape_sel] = poids_final
                with open(memory_file, 'w') as f:
                    json.dump(historique_pond, f)
                st.success(f"Pondérations mises à jour pour {etape_sel} : {poids_final}")
        else:
            st.warning("Veuillez entrer au moins un classement valide.")

# Onglet historique des pondérations
with tabs[3]:
    st.subheader("Évolution des pondérations par étape")
    if historique_pond:
        df_hist = pd.DataFrame(historique_pond).T
        st.dataframe(df_hist.style.format("{:.2f}"))

        # Graphe d'évolution des pondérations
        st.line_chart(df_hist)
    else:
        st.info("Aucune donnée enregistrée encore.")
