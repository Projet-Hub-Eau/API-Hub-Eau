# -*- coding: utf-8 -*-
"""
Created on Fri Jul 11 15:43:26 2025

@authors: fernand fort, felix françois
"""

import json
import requests
import warnings
import pandas as pd
import time
from functools import wraps
from datetime import datetime, timedelta
warnings.filterwarnings('ignore')

class HubEauBaseAPI:
    base_url = "https://hubeau.eaufrance.fr/api"
    version = "v1"

    def __init__(self, base_url=None, version=None):
        self.base_url = base_url or self.base_url
        self.version = version or self.version

    def _build_url(self, endpoint):
        return f"{self.base_url}/{self.version}/{endpoint}"

    def _assert_json_success(self, response):
        try:
            data = response.json()
            if 'status' in data and data['status'] == "error":
                raise ValueError(f"Erreur de l'API : {data}")
            return True
        except json.JSONDecodeError:
            raise ValueError("Réponse non valide (pas du JSON)")

    @staticmethod
    def _timing(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            start = time.time()
            result = func(*args, **kwargs)
            end = time.time()
            print(f"⏱️ {func.__name__} exécutée en {end - start:.2f} s")
            return result
        return wrapper

    @_timing
    def get(self, endpoint, params=None):
        url = self._build_url(endpoint)
        response = requests.get(url, params=params)
        if self._assert_json_success(response):
            data = response.json()
            return pd.DataFrame(data.get("data", []))

    @_timing
    def fetch_all_data(self, endpoint, params=None):
        all_data = []
        page = 1
        size = 5000
    
        while True:
            paged_params = params.copy() if params else {}
            paged_params.update({"page": page, "size": size})
    
            url = self._build_url(endpoint)
            response = requests.get(url, params=paged_params)
            if not self._assert_json_success(response):
                break
    
            data = response.json()
            batch = data.get("data", [])
            if not batch:
                break
    
            all_data.extend(batch)
    
            if len(batch) < size:
                break  # plus de pages
    
            page += 1
            time.sleep(0.1)
    
        return pd.DataFrame(all_data)


    @_timing
    def fetch_all_data_by_year_range(self, endpoint, params=None, start_year=1997, end_year=2024):
        from datetime import datetime, timedelta
    
        def date_to_str(d):
            return d.strftime("%Y-%m-%d")
    
        current_start = datetime(start_year, 1, 1)
        date_fin = datetime(end_year, 12, 31)
    
        full_data = []
        total_rows = 0
    
        while current_start <= date_fin:
            temp_params = params.copy() if params else {}
            current_end = datetime(current_start.year, 12, 31)
            if current_end > date_fin:
                current_end = date_fin
    
            temp_params["date_debut_prelevement"] = date_to_str(current_start)
            temp_params["date_fin_prelevement"] = date_to_str(current_end)
    
            print(f"Récupération des données du {date_to_str(current_start)} au {date_to_str(current_end)}")
            df_part = self.fetch_all_data(endpoint, params=temp_params)
    
            if df_part.empty:
                print(f"⛔ Aucun résultat entre {date_to_str(current_start)} et {date_to_str(current_end)} — arrêt.")
                break
    
            full_data.append(df_part)
            total_rows += len(df_part)
            print(f"📈 {total_rows} lignes récupérées jusqu'à présent.")
    
            current_start = current_end + timedelta(days=1)
    
        if full_data:
            return pd.concat(full_data, ignore_index=True)
        else:
            print("⚠️ Aucun DataFrame à concaténer, retour d'un DataFrame vide.")
            return pd.DataFrame()


class EtatPiscicoleAPI(HubEauBaseAPI):
    def __init__(self):
        super().__init__()
        self.endpoint_observations = "etat_piscicole/observations"
        self.endpoint_stations = "etat_piscicole/stations"
        self.endpoint_operations = "etat_piscicole/operations"
        self.endpoint_indicateurs = "etat_piscicole/indicateurs"

    def get_observations(self, params=None):
        return self.get(self.endpoint_observations, params)

    def get_stations(self, params=None):
        return self.get(self.endpoint_stations, params)

    def get_operations(self, params=None):
        return self.get(self.endpoint_operations, params)

    def get_indicateurs(self, params=None):
        return self.get(self.endpoint_indicateurs, params)

class QualiteCoursEauAPI(HubEauBaseAPI):
    def __init__(self):
        super().__init__(version="v2")
        self.endpoint_station_pc = "qualite_rivieres/station_pc"
        self.endpoint_operation_pc = "qualite_rivieres/operation_pc"
        self.endpoint_condition_env_pc = "qualite_rivieres/condition_environnementale_pc"
        self.endpoint_analyse_pc = "qualite_rivieres/analyse_pc"

    def get_stations_pc(self, params=None):
        return self.get(self.endpoint_station_pc, params)

    def get_operations_pc(self, params=None):
        return self.get(self.endpoint_operation_pc, params)

    def get_conditions_env_pc(self, params=None):
        return self.get(self.endpoint_condition_env_pc, params)

    def get_analyses_pc(self, params=None):
        return self.get(self.endpoint_analyse_pc, params)

class HydrobiologieAPI(HubEauBaseAPI):
    def __init__(self):
        super().__init__(version="v1")
        self.endpoint_indices = "hydrobio/indices"
        self.endpoint_stations_hydrobio = "hydrobio/stations_hydrobio"
        self.endpoint_taxons = "hydrobio/taxons"
    
    def get_indices(self, params=None):
        return self.get(self.endpoint_indices, params)

    def get_stations_hydrobio(self, params=None):
        return self.get(self.endpoint_stations_hydrobio, params)

    def get_taxons(self, params=None):
        return self.get(self.endpoint_taxons, params)
    
class IndicateursServicesAPI(HubEauBaseAPI):
    def __init__(self):
        super().__init__(version="v0")
        self.endpoint_communes = "indicateurs_services/communes"
        self.endpoint_services = "indicateurs_services/services"
        self.endpoint_indicateurs = "indicateurs_services/indicateurs"
    
    def get_communes(self, params=None):
        return self.get(self.endpoint_communes, params)

    def get_services(self, params=None):
        return self.get(self.endpoint_services, params)

    def get_indicateurs(self, params=None):
        return self.get(self.endpoint_indicateurs, params)

class PhytopharmaAPI(HubEauBaseAPI):
    def __init__(self):
        super().__init__(version="v1")
        self.ep_ventes_subst = "vente_achat_phyto/ventes/substances"
        self.ep_achats_subst = "vente_achat_phyto/achats/substances"
        self.ep_ventes_prod = "vente_achat_phyto/ventes/produits"
        self.ep_achats_prod = "vente_achat_phyto/achats/produits"

    def get_ventes_substances(self, params=None):
        return self.get(self.ep_ventes_subst, params)

    def get_achats_substances(self, params=None):
        return self.get(self.ep_achats_subst, params)

    def get_ventes_produits(self, params=None):
        return self.get(self.ep_ventes_prod, params)

    def get_achats_produits(self, params=None):
        return self.get(self.ep_achats_prod, params)

class QualiteEauPotableAPI(HubEauBaseAPI):
    def __init__(self):
        super().__init__(version="v1")
        self.ep_communes_udi = "qualite_eau_potable/communes_udi"
        self.ep_resultats_dis = "qualite_eau_potable/resultats_dis"

    def get_communes_udi(self, params=None):
        return self.get(self.ep_communes_udi, params)

    def get_resultats_dis(self, params=None):
        return self.get(self.ep_resultats_dis, params)

    
        
        
