"""Diese Datei errechnet den Stromertrag im Jahr mit Hilfe von 304 Variablen.


Scheaffler:
    flat_roof_area_scheffler
        Parameter: building_area

    gable_roof_area_scheffler
        Parameter: building_area, tilt_angle

    pitched_roof_area_scheffler
        Parameter: building_area, reduction_factor, tilt_angle

        
TUM:
    flat_roof_area_tum
        Parameter: building_area    

    gable_roof_area_tum
        Parameter: building_area, reduction_factor, tilt_angle

    pitched_roof_area_tum
        Parameter: building_area, reduction_factor, tilt_angle  

 
Relativer Ertragspotential:
    get_relative_yield
        Parameter: orientation, tilt


Jährlicher Stromertrag:
    annual_solar_yield
        Parameter: roof_area, solar_irradiation, module_efficiency, relative_yield
"""

import json
import os
import sys
import numpy as np

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
from formulas.relative_yield_potential import (
    get_relative_yield,
    orientations,
)

tilt_angles = [i for i in range(20, 51, 10)]  # 20, 30, 40, 50
wirkungsgrad_liste = list(np.arange(0.18, 0.24, 0.01))


def erstelle_daten() -> list:
    """Diese Funktion liest die Grundfläche ein und gibt sie als Liste zurück.

    Returns:
        float: Grundfläche
    """
    if not os.path.exists("data/grundflaeche.csv"):
        sys.exit("Fehler: Datei grundflaeche.csv nicht gefunden")

    daten = []
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

            daten.append(
                {
                    "building": inhalte[0],
                    "building_area": float(
                        inhalte[1].replace(".", "").replace(",", ".")
                    ),
                    "roof_type": roof_type,
                    "orientation": inhalte[3],
                }
            )

    return daten


def calulate_roof_area(daten: list[dict]) -> list[dict]:
    """Diese Funktion berechnet die Dachfläche.

    Args:
        daten (list[dict]): Liste mit den Gebäudedaten.

    Returns:
        list[dict]: Liste mit den Gebäudedaten und der Dachfläche.
    """
    for gebaeude in daten:
        building_area = gebaeude.get("building_area")
        roof_type = gebaeude.get("roof_type")

        if roof_type == "flat":
            gebaeude["roof_area_schaeffler_flat"] = flat_roof_area_scheffler(
                building_area=building_area
            )
            gebaeude["roof_area_tum_flat"] = flat_roof_area_tum(
                building_area=building_area
            )

        elif roof_type == "gable":
            for i in tilt_angles:
                gebaeude[f"roof_area_schaeffler_gable_with_tilt_angle_{i}"] = (
                    gable_roof_area_scheffler(building_area=building_area, tilt_angle=i)
                )
                gebaeude[f"roof_area_tum_gable_with_tilt_angle_{i}"] = (
                    gable_roof_area_tum(
                        building_area=building_area, reduction_factor=0.8, tilt_angle=i
                    )
                )

        elif roof_type == "pitched":
            for i in tilt_angles:
                gebaeude[f"roof_area_schaeffler_pitched_with_tilt_angle_{i}"] = (
                    pitched_roof_area_scheffler(
                        building_area=building_area, reduction_factor=0.8, tilt_angle=i
                    )
                )
                gebaeude[f"roof_area_tum_pitched_with_tilt_angle_{i}"] = (
                    pitched_roof_area_tum(
                        building_area=building_area, reduction_factor=0.8, tilt_angle=i
                    )
                )

        elif roof_type == "mixed":
            gebaeude["roof_area_schaeffler_flat"] = flat_roof_area_scheffler(
                building_area=building_area
            )
            gebaeude["roof_area_tum_flat"] = flat_roof_area_tum(
                building_area=building_area
            )

            for i in tilt_angles:
                gebaeude[f"roof_area_schaeffler_gable_with_tilt_angle_{i}"] = (
                    gable_roof_area_scheffler(building_area=building_area, tilt_angle=i)
                )
                gebaeude[f"roof_area_tum_gable_with_tilt_angle_{i}"] = (
                    gable_roof_area_tum(
                        building_area=building_area, reduction_factor=0.8, tilt_angle=i
                    )
                )

                gebaeude[f"roof_area_schaeffler_pitched_with_tilt_angle_{i}"] = (
                    pitched_roof_area_scheffler(
                        building_area=building_area, reduction_factor=0.8, tilt_angle=i
                    )
                )
                gebaeude[f"roof_area_tum_pitched_with_tilt_angle_{i}"] = (
                    pitched_roof_area_tum(
                        building_area=building_area, reduction_factor=0.8, tilt_angle=i
                    )
                )

        else:
            sys.exit("Fehler: Dachtyp nicht bekannt: " + roof_type)

    return daten


def calculate_relative_yield(daten: list[dict]) -> list[dict]:
    """Diese Funktion berechnet den jährlichen Stromertrag.

    Args:
        daten (list[dict]): Liste mit den Gebäudedaten.

    Returns:
        list[dict]: Liste mit den Gebäudedaten und dem jährlichen Stromertrag.
    """
    for gebauede in daten:
        orientation = gebauede.get("orientation")
        roof_type = gebauede.get("roof_type")

        if roof_type == "flat":
            gebauede["relative_yield"] = get_relative_yield(
                orientation=int(orientation), tilt=0
            )

        elif roof_type in ["gable", "pitched", "mixed"]:
            if orientation == "variabel":
                for i in orientations:
                    for j in tilt_angles:
                        if roof_type == "mixed":
                            # notwendig, damit Feld relative_yield vorhanden ist bei mixed
                            gebauede[f"relative_yield"] = get_relative_yield(
                                orientation=i, tilt=0
                            )

                        gebauede[f"relative_yield_with_orientation_{i}_tilt_{j}"] = (
                            get_relative_yield(orientation=i, tilt=j)
                        )
            else:
                for i in tilt_angles:
                    if roof_type == "mixed":
                        # notwendig, damit Feld relative_yield vorhanden ist bei mixed
                        gebauede[f"relative_yield"] = get_relative_yield(
                            orientation=int(orientation), tilt=0
                        )

                    gebauede[
                        f"relative_yield_with_orientation_{orientation}_tilt_{i}"
                    ] = get_relative_yield(orientation=int(orientation), tilt=i)

        else:
            sys.exit("Fehler: Dachtyp nicht bekannt: " + roof_type)

    return daten


def calculate_globalstrahlung_pro_stunde(daten: list[dict]) -> list[dict]:
    """Diese Funktion berechnet die Globalstrahlung pro Stunde.

    Args:
        daten (list[dict]): Liste mit den Gebäudedaten.

    Returns:
        list[dict]: Liste mit den Gebäudedaten und der Globalstrahlung.
    """
    if not os.path.exists("data/globalstrahlung_stuendlich_mistelbach.csv"):
        sys.exit(
            "Fehler: Datei data/globalstrahlung_stuendlich_mistelbach.csv nicht gefunden"
        )

    globalstrahlungs_werte: list[dict] = []
    with open(
        "data/globalstrahlung_stuendlich_mistelbach.csv", "r", encoding="utf-8"
    ) as file:
        for zeile in file:
            zeitstempel, wert = zeile.strip().split(";")

            if not isinstance(zeitstempel, str) or not isinstance(wert, str):
                sys.exit("Fehler: Datei hat nicht das richtige Format")

            globalstrahlungs_werte.append(
                {
                    "zeitstempel": zeitstempel,
                    "wert": float(wert.replace(",", ".")),
                }
            )

    for gebaeude in daten:
        roof_type = gebaeude.get("roof_type")

        if roof_type == "flat":
            # Wenn "flat", dann hat gebaude folgende Felder:
            #
            # Roof Area:
            #   roof_area_schaeffler_flat
            #   roof_area_tum_flat
            #
            # Relative Yield:
            #   relative_yield

            relative_yield = gebaeude.get("relative_yield")
            assert relative_yield is not None

            for wirkungsgrad in wirkungsgrad_liste:
                for globalstrahlung in globalstrahlungs_werte:

                    globalstrahlungs_wert = globalstrahlung.get("wert")
                    assert globalstrahlungs_wert is not None

                    globalstrahlung_zeitstempel = globalstrahlung.get("zeitstempel")
                    assert globalstrahlung_zeitstempel is not None

                    roof_area_schaeffler_flat = float(
                        gebaeude.get("roof_area_schaeffler_flat")
                    )
                    assert roof_area_schaeffler_flat is not None

                    roof_area_tum_flat = float(gebaeude.get("roof_area_tum_flat"))
                    assert roof_area_tum_flat is not None

                    gebaeude[
                        f"leistung_scheaffler_flat_relative_yield_{relative_yield}_wirkungsgrad_{wirkungsgrad}_globalstrahlung_{globalstrahlungs_wert}_zeitstempel_{globalstrahlung_zeitstempel}"
                    ] = (
                        roof_area_schaeffler_flat
                        * relative_yield
                        * wirkungsgrad
                        * globalstrahlungs_wert
                    )
                    gebaeude[
                        f"leistung_tum_flat_relative_yield_{relative_yield}_wirkungsgrad_{wirkungsgrad}_globalstrahlung_{globalstrahlungs_wert}_zeitstempel_{globalstrahlung_zeitstempel}"
                    ] = (
                        roof_area_tum_flat
                        * relative_yield
                        * wirkungsgrad
                        * globalstrahlungs_wert
                    )

                    print(
                        f"Berechnung für {gebaeude.get('building')} mit Flachdach abgeschlossen"
                    )

        elif roof_type == "gable":
            # Wenn "gable", dann hat gebaude folgende Felder:
            #
            # Roof Area:
            #   roof_area_schaeffler_gable_with_tilt_angle_{i} für i in range(20, 51, 1)
            #   roof_area_tum_gable_with_tilt_angle_{i} für i in range(20, 51, 1)
            #
            # Relative Yield:
            #   relative_yield_with_orientation_{i}_tilt_{j}
            #       für i in orientations und j in tilt_angles wenn orientation == "variabel"
            #       für j in tilt_angles wenn orientation != "variabel"

            orientation = gebaeude.get("orientation")
            assert orientation is not None

            if orientation == "variabel":
                for i in orientations:
                    for j in tilt_angles:
                        for wirkungsgrad in wirkungsgrad_liste:
                            for globalstrahlung in globalstrahlungs_werte:

                                globalstrahlungs_wert = globalstrahlung.get("wert")
                                assert globalstrahlungs_wert is not None

                                globalstrahlung_zeitstempel = globalstrahlung.get(
                                    "zeitstempel"
                                )
                                assert globalstrahlung_zeitstempel is not None

                                roof_area_schaeffler_gable = float(
                                    gebaeude.get(
                                        f"roof_area_schaeffler_gable_with_tilt_angle_{j}"
                                    )
                                )
                                assert roof_area_schaeffler_gable is not None

                                roof_area_tum_gable = float(
                                    gebaeude.get(
                                        f"roof_area_tum_gable_with_tilt_angle_{j}"
                                    )
                                )
                                assert roof_area_tum_gable is not None

                                relative_yield = gebaeude.get(
                                    f"relative_yield_with_orientation_{i}_tilt_{j}"
                                )
                                assert relative_yield is not None

                                gebaeude[
                                    f"leistung_scheaffler_gable_with_orientation_{i}_tilt_{j}_wirkungsgrad_{wirkungsgrad}_globalstrahlung_{globalstrahlungs_wert}_zeitstempel_{globalstrahlung_zeitstempel}"
                                ] = (
                                    roof_area_schaeffler_gable
                                    * relative_yield
                                    * wirkungsgrad
                                    * globalstrahlungs_wert
                                )
                                gebaeude[
                                    f"leistung_tum_gable_with_orientation_{i}_tilt_{j}_wirkungsgrad_{wirkungsgrad}_globalstrahlung_{globalstrahlungs_wert}_zeitstempel_{globalstrahlung_zeitstempel}"
                                ] = (
                                    roof_area_tum_gable
                                    * relative_yield
                                    * wirkungsgrad
                                    * globalstrahlungs_wert
                                )

                                print(
                                    f"Berechnung für {gebaeude.get('building')} mit Satteldach und variabler Orientierung abgeschlossen"
                                )

            else:
                for i in tilt_angles:
                    for wirkungsgrad in wirkungsgrad_liste:
                        for globalstrahlung in globalstrahlungs_werte:

                            globalstrahlungs_wert = globalstrahlung.get("wert")
                            assert globalstrahlungs_wert is not None

                            globalstrahlung_zeitstempel = globalstrahlung.get(
                                "zeitstempel"
                            )
                            assert globalstrahlung_zeitstempel is not None

                            roof_area_schaeffler_gable = float(
                                gebaeude.get(
                                    f"roof_area_schaeffler_gable_with_tilt_angle_{i}"
                                )
                            )
                            assert roof_area_schaeffler_gable is not None

                            roof_area_tum_gable = float(
                                gebaeude.get(f"roof_area_tum_gable_with_tilt_angle_{i}")
                            )
                            assert roof_area_tum_gable is not None

                            relative_yield = gebaeude.get(
                                f"relative_yield_with_orientation_{orientation}_tilt_{i}"
                            )
                            assert relative_yield is not None

                            gebaeude[
                                f"leistung_scheaffler_gable_with_orientation_{orientation}_tilt_{i}_wirkungsgrad_{wirkungsgrad}_globalstrahlung_{globalstrahlungs_wert}_zeitstempel_{globalstrahlung_zeitstempel}"
                            ] = (
                                roof_area_schaeffler_gable
                                * relative_yield
                                * wirkungsgrad
                                * globalstrahlungs_wert
                            )
                            gebaeude[
                                f"leistung_tum_gable_with_orientation_{orientation}_tilt_{i}_wirkungsgrad_{wirkungsgrad}_globalstrahlung_{globalstrahlungs_wert}_zeitstempel_{globalstrahlung_zeitstempel}"
                            ] = (
                                roof_area_tum_gable
                                * relative_yield
                                * wirkungsgrad
                                * globalstrahlungs_wert
                            )

                            print(
                                f"Berechnung für {gebaeude.get('building')} mit Satteldach und fixer Orientierung abgeschlossen für tilt_angle {i}"
                            )

        elif roof_type == "pitched":
            # Wenn "pitched", dann hat gebaude folgende Felder:
            #
            # Roof Area:
            #   roof_area_schaeffler_pitched_with_tilt_angle_{i} für i in range(20, 51, 1)
            #   roof_area_tum_pitched_with_tilt_angle_{i} für i in range(20, 51, 1)
            #
            # Relative Yield:
            #   relative_yield_with_orientation_{i}_tilt_{j}
            #       für i in orientations und j in tilt_angles wenn orientation == "variabel"
            #       für j in tilt_angles wenn orientation != "variabel"
            orientation = gebaeude.get("orientation")
            assert orientation is not None

            if orientation == "variabel":
                for i in orientations:
                    for j in tilt_angles:
                        for wirkungsgrad in wirkungsgrad_liste:
                            for globalstrahlung in globalstrahlungs_werte:

                                globalstrahlungs_wert = globalstrahlung.get("wert")
                                assert globalstrahlungs_wert is not None

                                globalstrahlung_zeitstempel = globalstrahlung.get(
                                    "zeitstempel"
                                )
                                assert globalstrahlung_zeitstempel is not None

                                roof_area_schaeffler_pitched = float(
                                    gebaeude.get(
                                        f"roof_area_schaeffler_pitched_with_tilt_angle_{j}"
                                    )
                                )
                                assert roof_area_schaeffler_pitched is not None

                                roof_area_tum_pitched = float(
                                    gebaeude.get(
                                        f"roof_area_tum_pitched_with_tilt_angle_{j}"
                                    )
                                )
                                assert roof_area_tum_pitched is not None

                                relative_yield = gebaeude.get(
                                    f"relative_yield_with_orientation_{i}_tilt_{j}"
                                )
                                assert relative_yield is not None

                                gebaeude[
                                    f"leistung_scheaffler_pitched_with_orientation_{i}_tilt_{j}_wirkungsgrad_{wirkungsgrad}_globalstrahlung_{globalstrahlungs_wert}_zeitstempel_{globalstrahlung_zeitstempel}"
                                ] = (
                                    roof_area_schaeffler_pitched
                                    * relative_yield
                                    * wirkungsgrad
                                    * globalstrahlungs_wert
                                )
                                gebaeude[
                                    f"leistung_tum_pitched_with_orientation_{i}_tilt_{j}_wirkungsgrad_{wirkungsgrad}_globalstrahlung_{globalstrahlungs_wert}_zeitstempel_{globalstrahlung_zeitstempel}"
                                ] = (
                                    roof_area_tum_pitched
                                    * relative_yield
                                    * wirkungsgrad
                                    * globalstrahlungs_wert
                                )

                                print(
                                    f"Berechnung für {gebaeude.get('building')} mit Schrägdach und variabler Orientierung abgeschlossen"
                                )

            else:
                for i in tilt_angles:
                    for wirkungsgrad in wirkungsgrad_liste:
                        for globalstrahlung in globalstrahlungs_werte:

                            globalstrahlungs_wert = globalstrahlung.get("wert")
                            assert globalstrahlungs_wert is not None

                            globalstrahlung_zeitstempel = globalstrahlung.get(
                                "zeitstempel"
                            )
                            assert globalstrahlung_zeitstempel is not None

                            roof_area_schaeffler_pitched = float(
                                gebaeude.get(
                                    f"roof_area_schaeffler_pitched_with_tilt_angle_{i}"
                                )
                            )
                            assert roof_area_schaeffler_pitched is not None

                            roof_area_tum_pitched = float(
                                gebaeude.get(
                                    f"roof_area_tum_pitched_with_tilt_angle_{i}"
                                )
                            )
                            assert roof_area_tum_pitched is not None

                            relative_yield = gebaeude.get(
                                f"relative_yield_with_orientation_{orientation}_tilt_{i}"
                            )
                            assert relative_yield is not None

                            gebaeude[
                                f"leistung_scheaffler_pitched_with_orientation_{orientation}_tilt_{i}_wirkungsgrad_{wirkungsgrad}_globalstrahlung_{globalstrahlungs_wert}_zeitstempel_{globalstrahlung_zeitstempel}"
                            ] = (
                                roof_area_schaeffler_pitched
                                * relative_yield
                                * wirkungsgrad
                                * globalstrahlungs_wert
                            )
                            gebaeude[
                                f"leistung_tum_pitched_with_orientation_{orientation}_tilt_{i}_wirkungsgrad_{wirkungsgrad}_globalstrahlung_{globalstrahlungs_wert}_zeitstempel_{globalstrahlung_zeitstempel}"
                            ] = (
                                roof_area_tum_pitched
                                * relative_yield
                                * wirkungsgrad
                                * globalstrahlungs_wert
                            )

                            print(
                                f"Berechnung für {gebaeude.get('building')} mit Schrägdach und fixer Orientierung abgeschlossen für tilt_angle {i}"
                            )

        elif roof_type == "mixed":
            # Wenn "mixed", dann hat gebaude folgende Felder:
            #
            # Roof Area:
            #   roof_area_schaeffler_flat
            #   roof_area_tum_flat
            #   roof_area_schaeffler_gable_with_tilt_angle_{i} für i in range(20, 51, 1)
            #   roof_area_tum_gable_with_tilt_angle_{i} für i in range(20, 51, 1)
            #   roof_area_schaeffler_pitched_with_tilt_angle_{i} für i in range(20, 51, 1)
            #   roof_area_tum_pitched_with_tilt_angle_{i} für i in range(20, 51, 1)
            #
            # Relative Yield:
            #   relative_yield
            #   relative_yield_with_orientation_{i}_tilt_{j}
            #       für i in orientations und j in tilt_angles wenn orientation == "variabel"
            #       für j in tilt_angles wenn orientation != "variabel"

            ### FLAT ###
            relative_yield = gebaeude.get("relative_yield")
            print("HER")
            print(gebaeude.get("building"))
            assert relative_yield is not None

            for wirkungsgrad in wirkungsgrad_liste:
                for globalstrahlung in globalstrahlungs_werte:

                    globalstrahlungs_wert = globalstrahlung.get("wert")
                    assert globalstrahlungs_wert is not None

                    globalstrahlung_zeitstempel = globalstrahlung.get("zeitstempel")
                    assert globalstrahlung_zeitstempel is not None

                    roof_area_schaeffler_flat = float(
                        gebaeude.get("roof_area_schaeffler_flat")
                    )
                    assert roof_area_schaeffler_flat is not None

                    roof_area_tum_flat = float(gebaeude.get("roof_area_tum_flat"))
                    assert roof_area_tum_flat is not None

                    gebaeude[
                        f"leistung_scheaffler_flat_relative_yield_{relative_yield}_wirkungsgrad_{wirkungsgrad}_globalstrahlung_{globalstrahlungs_wert}_zeitstempel_{globalstrahlung_zeitstempel}"
                    ] = (
                        roof_area_schaeffler_flat
                        * relative_yield
                        * wirkungsgrad
                        * globalstrahlungs_wert
                    )
                    gebaeude[
                        f"leistung_tum_flat_relative_yield_{relative_yield}_wirkungsgrad_{wirkungsgrad}_globalstrahlung_{globalstrahlungs_wert}_zeitstempel_{globalstrahlung_zeitstempel}"
                    ] = (
                        roof_area_tum_flat
                        * relative_yield
                        * wirkungsgrad
                        * globalstrahlungs_wert
                    )

                    print(
                        f"Berechnung für {gebaeude.get('building')} mit Flachdach abgeschlossen für den Mixed Typ"
                    )

            ### GABLE ###
            orientation = gebaeude.get("orientation")
            assert orientation is not None

            if orientation == "variabel":
                for i in orientations:
                    for j in tilt_angles:
                        for wirkungsgrad in wirkungsgrad_liste:
                            for globalstrahlung in globalstrahlungs_werte:

                                globalstrahlungs_wert = globalstrahlung.get("wert")
                                assert globalstrahlungs_wert is not None

                                globalstrahlung_zeitstempel = globalstrahlung.get(
                                    "zeitstempel"
                                )
                                assert globalstrahlung_zeitstempel is not None

                                roof_area_schaeffler_gable = float(
                                    gebaeude.get(
                                        f"roof_area_schaeffler_gable_with_tilt_angle_{j}"
                                    )
                                )
                                assert roof_area_schaeffler_gable is not None

                                roof_area_tum_gable = float(
                                    gebaeude.get(
                                        f"roof_area_tum_gable_with_tilt_angle_{j}"
                                    )
                                )
                                assert roof_area_tum_gable is not None

                                relative_yield = gebaeude.get(
                                    f"relative_yield_with_orientation_{i}_tilt_{j}"
                                )
                                assert relative_yield is not None

                                gebaeude[
                                    f"leistung_scheaffler_gable_with_orientation_{i}_tilt_{j}_wirkungsgrad_{wirkungsgrad}_globalstrahlung_{globalstrahlungs_wert}_zeitstempel_{globalstrahlung_zeitstempel}"
                                ] = (
                                    roof_area_schaeffler_gable
                                    * relative_yield
                                    * wirkungsgrad
                                    * globalstrahlungs_wert
                                )
                                gebaeude[
                                    f"leistung_tum_gable_with_orientation_{i}_tilt_{j}_wirkungsgrad_{wirkungsgrad}_globalstrahlung_{globalstrahlungs_wert}_zeitstempel_{globalstrahlung_zeitstempel}"
                                ] = (
                                    roof_area_tum_gable
                                    * relative_yield
                                    * wirkungsgrad
                                    * globalstrahlungs_wert
                                )

                                print(
                                    f"Berechnung für {gebaeude.get('building')} mit Satteldach und variabler Orientierung abgeschlossen für den Mixed Typ"
                                )

            else:
                for i in tilt_angles:
                    for wirkungsgrad in wirkungsgrad_liste:
                        for globalstrahlung in globalstrahlungs_werte:

                            globalstrahlungs_wert = globalstrahlung.get("wert")
                            assert globalstrahlungs_wert is not None

                            globalstrahlung_zeitstempel = globalstrahlung.get(
                                "zeitstempel"
                            )
                            assert globalstrahlung_zeitstempel is not None

                            roof_area_schaeffler_gable = float(
                                gebaeude.get(
                                    f"roof_area_schaeffler_gable_with_tilt_angle_{i}"
                                )
                            )
                            assert roof_area_schaeffler_gable is not None

                            roof_area_tum_gable = float(
                                gebaeude.get(f"roof_area_tum_gable_with_tilt_angle_{i}")
                            )
                            assert roof_area_tum_gable is not None

                            relative_yield = gebaeude.get(
                                f"relative_yield_with_orientation_{orientation}_tilt_{i}"
                            )
                            assert relative_yield is not None

                            gebaeude[
                                f"leistung_scheaffler_gable_with_orientation_{orientation}_tilt_{i}_wirkungsgrad_{wirkungsgrad}_{wirkungsgrad}_globalstrahlung_{globalstrahlungs_wert}_zeitstempel_{globalstrahlung_zeitstempel}"
                            ] = (
                                roof_area_schaeffler_gable
                                * relative_yield
                                * wirkungsgrad
                                * globalstrahlungs_wert
                            )
                            gebaeude[
                                f"leistung_tum_gable_with_orientation_{orientation}_tilt_{i}_wirkungsgrad_{wirkungsgrad}_{wirkungsgrad}_globalstrahlung_{globalstrahlungs_wert}_zeitstempel_{globalstrahlung_zeitstempel}"
                            ] = (
                                roof_area_tum_gable
                                * relative_yield
                                * wirkungsgrad
                                * globalstrahlungs_wert
                            )

                            print(
                                f"Berechnung für {gebaeude.get('building')} mit Satteldach und fixer Orientierung abgeschlossen für den Mixed Typ für tilt_angle {i} für den Mixed Typ"
                            )

            ### PITCHED ###
            orientation = gebaeude.get("orientation")
            assert orientation is not None

            if orientation == "variabel":
                for i in orientations:
                    for j in tilt_angles:
                        for wirkungsgrad in wirkungsgrad_liste:
                            for globalstrahlung in globalstrahlungs_werte:

                                globalstrahlungs_wert = globalstrahlung.get("wert")
                                assert globalstrahlungs_wert is not None

                                globalstrahlung_zeitstempel = globalstrahlung.get(
                                    "zeitstempel"
                                )
                                assert globalstrahlung_zeitstempel is not None

                                roof_area_schaeffler_pitched = float(
                                    gebaeude.get(
                                        f"roof_area_schaeffler_pitched_with_tilt_angle_{j}"
                                    )
                                )
                                assert roof_area_schaeffler_pitched is not None

                                roof_area_tum_pitched = float(
                                    gebaeude.get(
                                        f"roof_area_tum_pitched_with_tilt_angle_{j}"
                                    )
                                )
                                assert roof_area_tum_pitched is not None

                                relative_yield = gebaeude.get(
                                    f"relative_yield_with_orientation_{i}_tilt_{j}"
                                )
                                assert relative_yield is not None

                                gebaeude[
                                    f"leistung_scheaffler_pitched_with_orientation_{i}_tilt_{j}_wirkungsgrad_{wirkungsgrad}_globalstrahlung_{globalstrahlungs_wert}_zeitstempel_{globalstrahlung_zeitstempel}"
                                ] = (
                                    roof_area_schaeffler_pitched
                                    * relative_yield
                                    * wirkungsgrad
                                    * globalstrahlungs_wert
                                )
                                gebaeude[
                                    f"leistung_tum_pitched_with_orientation_{i}_tilt_{j}_wirkungsgrad_{wirkungsgrad}_globalstrahlung_{globalstrahlungs_wert}_zeitstempel_{globalstrahlung_zeitstempel}"
                                ] = (
                                    roof_area_tum_pitched
                                    * relative_yield
                                    * wirkungsgrad
                                    * globalstrahlungs_wert
                                )

                                print(
                                    f"Berechnung für {gebaeude.get('building')} mit Schrägdach und variabler Orientierung abgeschlossen für den Mixed Typ"
                                )

            else:
                for i in tilt_angles:
                    for wirkungsgrad in wirkungsgrad_liste:
                        for globalstrahlung in globalstrahlungs_werte:

                            globalstrahlungs_wert = globalstrahlung.get("wert")
                            assert globalstrahlungs_wert is not None

                            globalstrahlung_zeitstempel = globalstrahlung.get(
                                "zeitstempel"
                            )
                            assert globalstrahlung_zeitstempel is not None

                            roof_area_schaeffler_pitched = float(
                                gebaeude.get(
                                    f"roof_area_schaeffler_pitched_with_tilt_angle_{i}"
                                )
                            )
                            assert roof_area_schaeffler_pitched is not None

                            roof_area_tum_pitched = float(
                                gebaeude.get(
                                    f"roof_area_tum_pitched_with_tilt_angle_{i}"
                                )
                            )
                            assert roof_area_tum_pitched is not None

                            relative_yield = gebaeude.get(
                                f"relative_yield_with_orientation_{orientation}_tilt_{i}"
                            )
                            assert relative_yield is not None

                            gebaeude[
                                f"leistung_scheaffler_pitched_with_orientation_{orientation}_tilt_{i}_wirkungsgrad_{wirkungsgrad}_globalstrahlung_{globalstrahlungs_wert}_zeitstempel_{globalstrahlung_zeitstempel}"
                            ] = (
                                roof_area_schaeffler_pitched
                                * relative_yield
                                * wirkungsgrad
                                * globalstrahlungs_wert
                            )
                            gebaeude[
                                f"leistung_tum_pitched_with_orientation_{orientation}_tilt_{i}_wirkungsgrad_{wirkungsgrad}_globalstrahlung_{globalstrahlungs_wert}_zeitstempel_{globalstrahlung_zeitstempel}"
                            ] = (
                                roof_area_tum_pitched
                                * relative_yield
                                * wirkungsgrad
                                * globalstrahlungs_wert
                            )

                            print(
                                f"Berechnung für {gebaeude.get('building')} mit Schrägdach und fixer Orientierung abgeschlossen für den Mixed Typ für tilt_angle {i} für den Mixed Typ"
                            )

        else:
            sys.exit("Fehler: Dachtyp nicht bekannt: " + roof_type)

    return daten


def speichere_daten_als_json(daten: list[dict]) -> None:
    """Diese Funktion speichert die Daten als JSON-Datei.

    Args:
        daten (list[dict]): Liste mit den Gebäudedaten.
    """
    with open("data/daten_mit_dachflaeche.json", "w", encoding="utf-8") as file:
        json.dump(daten, file, indent=4)


if __name__ == "__main__":
    daten = erstelle_daten()
    daten = calulate_roof_area(daten)
    daten = calculate_relative_yield(daten)
    daten = calculate_globalstrahlung_pro_stunde(daten)
    speichere_daten_als_json(daten)
