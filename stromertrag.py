"""Diese Datei errechnet den Stromertrag im Jahr mit Hilfe von 304 Variablen.


Scheaffler:
    flat_roof_area_scheffler
        Parameter: building_area

    gable_roof_area_scheffler
        Parameter: building_area, roof_pitch

    pitched_roof_area_scheffler
        Parameter: building_area, reduction_factor, roof_pitch

        
TUM:
    flat_roof_area_tum
        Parameter: building_area    

    gable_roof_area_tum
        Parameter: building_area, reduction_factor, roof_pitch

    pitched_roof_area_tum
        Parameter: building_area, reduction_factor, roof_pitch  

 
Relativer Ertragspotential:
    get_relative_yield
        Parameter: orientation, tilt


Jährlicher Stromertrag:
    annual_solar_yield
        Parameter: roof_area, solar_irradiation, module_efficiency, relative_yield
"""

import os
import sys
import pandas as pd

from formulas.roof_areas_scheffler import (
    flat_roof_area_scheffler,
    gable_roof_area_scheffler,
    pitched_roof_area_scheffler,
)
from formulas.roof_areas_tum import (
    flat_roof_area_tum,
    gable_roof_area_tum,
    pitched_roof_area_tum,
)
from formulas.relative_yield_potential import get_relative_yield, orientations
from formulas.annual_solar_yield import annual_solar_yield


def erstelle_daten_grundflaeche() -> list:
    """Diese Funktion liest die Grundfläche ein und gibt sie als Liste zurück.

    Returns:
        float: Grundfläche
    """
    if not os.path.exists("data/grundflaeche.csv"):
        sys.exit("Fehler: Datei grundflaeche.txt nicht gefunden")

    daten_grundflaeche = []
    with open("data/grundflaeche.csv", "r", encoding="utf-8") as file:
        for idx, zeile in enumerate(file):
            inhalte = zeile.strip().split(";")[:4]
            if idx == 0:
                print("INFO: CSV hat folgende Spalten: ", inhalte)
                continue

            if len(inhalte) != 4:
                sys.exit("Fehler: CSV hat nicht die richtige Anzahl an Spalten")

            roof_type = ""
            match inhalte[2].lower():
                case "satteldach":
                    roof_type = "gable"
                case "flachdach":
                    roof_type = "flat"
                case "schrägdach":
                    roof_type = "pitched"
                case "gemischt":
                    roof_type = "mixed"
                case _:
                    sys.exit("Fehler: Dachtyp nicht bekannt: " + inhalte[2])

            daten_grundflaeche.append(
                {
                    "building": inhalte[0],
                    "building_area": float(
                        inhalte[1].replace(".", "").replace(",", ".")
                    ),
                    "roof_type": roof_type,
                    "orientation": inhalte[3],
                }
            )

    return daten_grundflaeche


def calulate_roof_area(daten_grundflaeche: list[dict]) -> list[dict]:
    """Diese Funktion berechnet die Dachfläche.

    Args:
        daten_grundflaeche (list[dict]): Liste mit den Gebäudedaten.

    Returns:
        list[dict]: Liste mit den Gebäudedaten und der Dachfläche.
    """
    roof_pitch_values = [i for i in range(20, 51, 1)]

    for gebauede_dict in daten_grundflaeche:
        building_area = gebauede_dict.get("building_area")
        roof_type = gebauede_dict.get("roof_type")

        if roof_type == "flat":
            gebauede_dict["roof_area_schaeffler_flat"] = flat_roof_area_scheffler(
                building_area=building_area
            )
            gebauede_dict["roof_area_tum_flat"] = flat_roof_area_tum(
                building_area=building_area
            )

        elif roof_type == "gable":
            for i in roof_pitch_values:
                gebauede_dict[f"roof_area_schaeffler_gable_with_roof_pitch_{i}"] = (
                    gable_roof_area_scheffler(building_area=building_area, roof_pitch=i)
                )
                gebauede_dict[f"roof_area_tum_gable_with_roof_pitch_{i}"] = (
                    gable_roof_area_tum(
                        building_area=building_area, reduction_factor=0.8, roof_pitch=i
                    )
                )

        elif roof_type == "pitched":
            for i in roof_pitch_values:
                gebauede_dict[f"roof_area_schaeffler_pitched_with_roof_pitch_{i}"] = (
                    pitched_roof_area_scheffler(
                        building_area=building_area, reduction_factor=0.8, roof_pitch=i
                    )
                )
                gebauede_dict[f"roof_area_tum_pitched_with_roof_pitch_{i}"] = (
                    pitched_roof_area_tum(
                        building_area=building_area, reduction_factor=0.8, roof_pitch=i
                    )
                )

        elif roof_type == "mixed":
            gebauede_dict["roof_area_schaeffler_flat"] = flat_roof_area_scheffler(
                building_area=building_area
            )
            gebauede_dict["roof_area_tum_flat"] = flat_roof_area_tum(
                building_area=building_area
            )

            for i in roof_pitch_values:
                gebauede_dict[f"roof_area_schaeffler_gable_with_roof_pitch_{i}"] = (
                    gable_roof_area_scheffler(building_area=building_area, roof_pitch=i)
                )
                gebauede_dict[f"roof_area_tum_gable_with_roof_pitch_{i}"] = (
                    gable_roof_area_tum(
                        building_area=building_area, reduction_factor=0.8, roof_pitch=i
                    )
                )

                gebauede_dict[f"roof_area_schaeffler_pitched_with_roof_pitch_{i}"] = (
                    pitched_roof_area_scheffler(
                        building_area=building_area, reduction_factor=0.8, roof_pitch=i
                    )
                )
                gebauede_dict[f"roof_area_tum_pitched_with_roof_pitch_{i}"] = (
                    pitched_roof_area_tum(
                        building_area=building_area, reduction_factor=0.8, roof_pitch=i
                    )
                )

        else:
            sys.exit("Fehler: Dachtyp nicht bekannt: " + roof_type)

    return daten_grundflaeche


def calculate_relative_yield(daten_grundflaeche: list[dict]) -> list[dict]:
    """Diese Funktion berechnet den jährlichen Stromertrag.

    Args:
        daten_grundflaeche (list[dict]): Liste mit den Gebäudedaten.

    Returns:
        list[dict]: Liste mit den Gebäudedaten und dem jährlichen Stromertrag.
    """
    for gebauede_dict in daten_grundflaeche:
        orientation = gebauede_dict.get("orientation")
        roof_type = gebauede_dict.get("roof_type")

        if roof_type == "flat":
            gebauede_dict["relative_yield"] = get_relative_yield(
                orientation=int(orientation), tilt=0
            )

        elif roof_type in ["gable", "pitched", "mixed"]:
            tilt_values = [i for i in range(20, 51, 1)]

            if orientation == "variabel":
                for i in orientations:
                    for j in tilt_values:
                        gebauede_dict[
                            f"relative_yield_with_orientation_{i}_tilt_{j}"
                        ] = get_relative_yield(orientation=i, tilt=j)

            for i in tilt_values:
                gebauede_dict[f"relative_yield_with_tilt_{i}"] = get_relative_yield(
                    orientation=int(orientation), tilt=i
                )

        else:
            sys.exit("Fehler: Dachtyp nicht bekannt: " + roof_type)

    return daten_grundflaeche


def calculate_globalstrahlung(daten_grundflaeche: list[dict]) -> list[dict]:
    """Diese Funktion berechnet die Globalstrahlung.

    Args:
        daten_grundflaeche (list[dict]): Liste mit den Gebäudedaten.

    Returns:
        list[dict]: Liste mit den Gebäudedaten und der Globalstrahlung.
    """
    if not os.path.exists("data/globalstrahlung_angepasst.csv"):
        sys.exit("Fehler: Datei globalstrahlung_angepasst.csv nicht gefunden")

    daten_globalstrahlung = []
    with open("data/globalstrahlung_angepasst.csv", "r", encoding="utf-8") as file:
        for idx, zeile in enumerate(file):
            if idx == 0:
                continue

            inhalte = zeile.strip().split(",")[:2]
            if len(inhalte) != 2:
                sys.exit("Fehler: CSV hat nicht die richtige Anzahl an Spalten")

            daten_globalstrahlung.append(
                {
                    "timestamp": inhalte[0],
                    "globalstrahlung": float(inhalte[1]),
                }
            )

    for gebauede_dict in daten_grundflaeche:
        roof_areas = [
            key
            for key in gebauede_dict.keys()
            if key.startswith("roof_area_schaeffler") or key.startswith("roof_area_tum")
        ]

        for roof_area in roof_areas:
            for idx, globalstrahlung in enumerate(daten_globalstrahlung):
                pass


def speicher_daten_als_excel(daten_grundflaeche: list[dict]) -> None:
    """Diese Funktion speichert die Daten als Excel-Datei.

    Args:
        daten_grundflaeche (list[dict]): Liste mit den Gebäudedaten.
    """
    df = pd.DataFrame(daten_grundflaeche)
    df.to_excel("data/daten_mit_dachflaeche.xlsx", index=False)


if __name__ == "__main__":
    daten_grundflaeche = erstelle_daten_grundflaeche()
    daten_grundflaeche = calulate_roof_area(daten_grundflaeche)
    daten_grundflaeche = calculate_relative_yield(daten_grundflaeche)
    daten_grundflaeche = calculate_globalstrahlung(daten_grundflaeche)
    speicher_daten_als_excel(daten_grundflaeche)
