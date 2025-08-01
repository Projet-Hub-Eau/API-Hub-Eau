import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
from hub_o.HubEauClass import EtatPiscicoleAPI, QualiteCoursEauAPI
import os
import zipfile

# Initialisation des APIs
api_poissons = EtatPiscicoleAPI()
api_eau = QualiteCoursEauAPI()

st.set_page_config(layout="wide")
st.title("Exploration des données Hub'Eau")
st.markdown("Sélectionner un fleuve pour visualiser les stations piscicoles et choisir celles à étudier.")

# --- Initialisation session state ---
if "validated" not in st.session_state:
    st.session_state.validated = False

if "stations_summary" not in st.session_state:
    st.session_state.stations_summary = None

# --- Sélection du fleuve ---
fleuve = st.text_input("Nom du fleuve", "seine")
if st.button("Rechercher les stations"):
    stations = api_poissons.fetch_all_data("etat_piscicole/stations", params={"libelle_entite_hydrographique": fleuve})

    if stations.empty:
        st.warning("Aucune station trouvée pour ce fleuve.")
        st.stop()

    codes_station = stations["code_station"].tolist()
    operations = api_poissons.fetch_all_data("etat_piscicole/operations", params={"code_station": codes_station})
    observations = api_poissons.fetch_all_data("etat_piscicole/observations", params={"code_station": codes_station})

    ops_count = operations.groupby("code_station")["code_operation"].nunique().reset_index(name="nombre_operations")
    obs_count = observations.groupby("code_station").size().reset_index(name="nombre_observations")

    stations_summary = stations.merge(ops_count, on="code_station", how="left")
    stations_summary = stations_summary.merge(obs_count, on="code_station", how="left")
    stations_summary[["nombre_operations", "nombre_observations"]] = stations_summary[["nombre_operations", "nombre_observations"]].fillna(0).astype(int)

    st.session_state.stations_summary = stations_summary
    st.session_state.validated = False

# --- Affichage de la carte si stations disponibles ---
if st.session_state.stations_summary is not None:
    stations_summary = st.session_state.stations_summary

    st.subheader("Carte interactive des stations")
    mean_lat = stations_summary["latitude"].mean()
    mean_lon = stations_summary["longitude"].mean()

    m = folium.Map(location=[mean_lat, mean_lon], zoom_start=8)

    min_ops = stations_summary["nombre_operations"].min()
    max_ops = stations_summary["nombre_operations"].max()
    min_obs = stations_summary["nombre_observations"].min()
    max_obs = stations_summary["nombre_observations"].max()

    def color_scale(obs):
        ratio = (obs - min_obs) / (max_obs - min_obs) if max_obs > min_obs else 0.5
        r = int(255 * ratio)
        g = int(255 * (1 - ratio))
        return f"#{r:02x}{g:02x}00"

    def size_scale(ops):
        return 5 + 15 * ((ops - min_ops) / (max_ops - min_ops)) if max_ops > min_ops else 10

    for _, row in stations_summary.iterrows():
        folium.CircleMarker(
            location=[row["latitude"], row["longitude"]],
            radius=size_scale(row["nombre_operations"]),
            color=color_scale(row["nombre_observations"]),
            fill=True,
            fill_opacity=0.7,
            popup=f"{row['libelle_entite_hydrographique']}<br>Opérations: {row['nombre_operations']}<br>Observations: {row['nombre_observations']}"
        ).add_to(m)

    st_folium(m, width=700, height=500)

    st.subheader("Sélection des stations à étudier")
    stations_a_etudier = st.multiselect(
        "Choisissez les stations :",
        options=stations_summary["libelle_entite_hydrographique"].tolist(),
        default=[]
    )

    stations_utiles = stations_summary[stations_summary["libelle_entite_hydrographique"].isin(stations_a_etudier)]
    st.session_state.codes_station_utiles = stations_utiles["code_station"].tolist()

    if st.button("Valider la sélection"):
        st.session_state.validated = True

# --- Traitement des données si validé ---
if st.session_state.validated:
    st.success("Début de la collecte des données...")

    # Poissons : toutes les stations du fleuve
    poissons_stations = api_poissons.fetch_all_data("etat_piscicole/stations", params={"libelle_entite_hydrographique": fleuve})
    codes_station_fleuve = poissons_stations["code_station"].tolist()
    poissons_observations = api_poissons.fetch_all_data("etat_piscicole/observations", params={"code_station": codes_station_fleuve})
    poissons_operations = api_poissons.fetch_all_data("etat_piscicole/operations", params={"code_station": codes_station_fleuve})
    poissons_indicateurs = api_poissons.fetch_all_data("etat_piscicole/indicateurs", params={"code_station": codes_station_fleuve})

    # Qualité de l'eau : uniquement les stations sélectionnées
    codes_station_utiles = st.session_state.codes_station_utiles
    params_qualite = {"code_station": codes_station_utiles}
    qualite_eau_station_pc = api_eau.fetch_all_data("qualite_rivieres/station_pc", params=params_qualite)
    qualite_eau_analyse_pc = api_eau.fetch_all_data_by_year_range(api_eau.endpoint_analyse_pc, params=params_qualite)
    qualite_eau_condition_env_pc = api_eau.fetch_all_data("qualite_rivieres/condition_environnementale_pc", params=params_qualite)
    qualite_eau_operation_pc = api_eau.fetch_all_data("qualite_rivieres/operation_pc", params=params_qualite)

    dataset = {
        "poissons_stations": poissons_stations,
        "poissons_observations": poissons_observations,
        "poissons_operations": poissons_operations,
        "poissons_indicateurs": poissons_indicateurs,
        "qualite_eau_station_pc": qualite_eau_station_pc,
        "qualite_eau_analyse_pc": qualite_eau_analyse_pc,
        "qualite_eau_condition_env_pc": qualite_eau_condition_env_pc,
        "qualite_eau_operation_pc": qualite_eau_operation_pc
    }

    st.subheader("Tailles des jeux de données")
    for key, df in dataset.items():
        st.write(f"**{key}** : {df.shape[0]} lignes, {df.shape[1]} colonnes")

    # Sauvegarde
    dossier_racine = fleuve.capitalize()
    dossier_poissons = os.path.join(dossier_racine, "Poissons")
    dossier_eau = os.path.join(dossier_racine, "Qualite des Cours d'Eau")

    os.makedirs(dossier_poissons, exist_ok=True)
    os.makedirs(dossier_eau, exist_ok=True)

    for k, df in dataset.items():
        if k.startswith("poissons"):
            df.to_csv(os.path.join(dossier_poissons, k + ".csv"), index=False)
        else:
            df.to_csv(os.path.join(dossier_eau, k + ".csv"), index=False)

    zip_path = f"{dossier_racine}_donnees.zip"
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for folder in [dossier_poissons, dossier_eau]:
            for file in os.listdir(folder):
                full_path = os.path.join(folder, file)
                arcname = os.path.relpath(full_path, start=dossier_racine)
                zipf.write(full_path, arcname=arcname)

    with open(zip_path, "rb") as f:
        st.download_button("💾 Télécharger les données compressées (.zip)", f, file_name=zip_path)

    st.success("Extraction terminée et données sauvegardées avec succès.")
