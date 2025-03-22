"""Dieses File dient zur Auswertung der Daten aus der ergebnisse.json.

Relevante Felder der ergebnisse.json:

if roof_type == "flat":
    - leistung_scheaffler_flat_relative_yield_{relative_yield_wert}_wirkungsgrad_{wirkungsgrad_wert}_globalstrahlung_{globalstrahlung_wert}_zeitstempel_{zeitstempel}
    - leistung_tum_flat_relative_yield_{relative_yield_wert}_wirkungsgrad_{wirkungsgrad_wert}_globalstrahlung_{globalstrahlung_wert}_zeitstempel_{zeitstempel}

if roof_type == "pitched":
    - leistung_scheaffler_pitched_with_orientation_{orientation_wert}_tilt_{tilt_wert}_wirkungsgrad_{wirkungsgrad_wert}_globalstrahlung_{globalstrahlung_wert}_zeitstempel_{zeitstempel}
    - leistung_tum_pitched_with_orientation_{orientation_wert}_tilt_{tilt_wert}_wirkungsgrad_{wirkungsgrad_wert}_globalstrahlung_{globalstrahlung_wert}_zeitstempel_{zeitstempel}

if roof_type == "gable":
    - leistung_scheaffler_gable_with_orientation_{orientation_wert}_tilt_{tilt_wert}_wirkungsgrad_{wirkungsgrad_wert}_globalstrahlung_{globalstrahlung_wert}_zeitstempel_{zeitstempel}
    - leistung_tum_gable_with_orientation_{orientation_wert}_tilt_{tilt_wert}_wirkungsgrad_{wirkungsgrad_wert}_globalstrahlung_{globalstrahlung_wert}_zeitstempel_{zeitstempel}

if roof_type == "mixed": 
    - Alle Felder von flat, pitched und gable

Berechnet werden soll für jedes berechnungsart (getrennt nach TUM und Scheaffler), für jedes Building und
für jede Stunde des Tages:
- Die maximale Leistung
- Die durchschnittliche Leistung
- Die minimale Leistung

Danach wird das Ergebnis graphisch dargestellt, die aggregierten Werte in eine Excel-Datei geschrieben und die Plots als PNG gespeichert.
"""

import ijson
import matplotlib.pyplot as plt
from datetime import datetime
import pandas as pd
import os


def _remove_leistung_prefix(key: str) -> tuple:
    """Entfernt das 'leistung_'-Präfix vom Key.

    Args:
        key (str): Der Key, von dem das Präfix entfernt werden soll.

    Returns:
        tuple: (Restlicher Key, bool ob Präfix vorhanden war)
    """
    if key.startswith("leistung_"):
        return key[len("leistung_") :], True
    return key, False


def _get_berechnungsart(key: str) -> str:
    """Extrahiert die berechnungsart aus dem Key (erstes Token)."""
    parts = key.split("_")
    return parts[0] if parts else None


def _get_roof_type(key: str) -> str:
    """Extrahiert den roof_type aus dem Key (zweites Token)."""
    parts = key.split("_")
    return parts[1] if len(parts) >= 2 else None


def _get_relative_yield(key: str) -> float:
    """Extrahiert den relative yield als Float aus dem Key."""
    parts = key.split("_relative_yield_")
    if len(parts) != 2:
        return None
    value_str = parts[1].split("_")[0]
    try:
        return float(value_str)
    except Exception:
        print("Fehler beim Parsen des Relative Yield:", value_str)
        return None


def get_orientation(key: str) -> float:
    """Extrahiert die Orientation als Float aus dem Key."""
    parts = key.split("_with_orientation_")
    if len(parts) != 2:
        return None
    value_str = parts[1].split("_")[0]
    try:
        return float(value_str)
    except Exception:
        print("Fehler beim Parsen der Orientation:", value_str)
        return None


def _get_tilt(key: str) -> float:
    """Extrahiert den Tilt als Float aus dem Key."""
    parts = key.split("_tilt_")
    if len(parts) != 2:
        return None
    value_str = parts[1].split("_")[0]
    try:
        return float(value_str)
    except Exception:
        print("Fehler beim Parsen des Tilt:", value_str)
        return None


def _get_wirkungsgrad(key: str) -> float:
    """Extrahiert den Wirkungsgrad als Float aus dem Key."""
    parts = key.split("_wirkungsgrad_")
    if len(parts) != 2:
        return None
    value_str = parts[1].split("_")[0]
    try:
        return float(value_str)
    except Exception:
        print("Fehler beim Parsen des Wirkungsgrads:", value_str)
        return None


def _get_globalstrahlung(key: str) -> float:
    """Extrahiert die Globalstrahlung als Float aus dem Key."""
    parts = key.split("_globalstrahlung_")
    if len(parts) != 2:
        return None
    value_str = parts[1].split("_")[0]
    try:
        return float(value_str)
    except Exception:
        print("Fehler beim Parsen der Globalstrahlung:", value_str)
        return None


def _get_zeitstempel(key: str) -> datetime:
    """Extrahiert den Zeitstempel aus dem Key und gibt ein datetime-Objekt zurück."""
    parts = key.split("_zeitstempel_")
    if len(parts) != 2:
        return None
    timestamp_str = parts[1].replace("\ufeff", "").strip()
    try:
        return datetime.strptime(timestamp_str, "%d.%m.%Y %H:%M")
    except Exception:
        print("Fehler beim Parsen des Zeitstempels:", timestamp_str)
        return None


def safe_filename(name: str) -> str:
    """Erstellt einen dateisicheren Dateinamen, indem unerwünschte Zeichen ersetzt werden."""
    return "".join(c if c.isalnum() or c in "._-" else "_" for c in name)


def auswertung():
    """Hauptfunktion zur Auswertung der Daten aus der ergebnisse.json."""

    data_rows = []
    with open("data/ergebnisse.json", "rb") as f:
        for building_obj in ijson.items(f, "item"):
            building_name = building_obj.get("building")
            if not building_name:
                print(
                    "Fehlendes 'building' in Objekt:",
                    building_obj,
                )
                continue

            for key, value in building_obj.items():
                key_without_prefix, valid_key = _remove_leistung_prefix(key)
                if not valid_key:
                    print("Ungültiger Key (fehlender Prefix 'leistung_'):", key)
                    continue

                key_berechnungsart = _get_berechnungsart(key_without_prefix)
                if key_berechnungsart not in ["scheaffler", "tum"]:
                    print("Ungültige Berechnungsart in Key:", key_berechnungsart)
                    continue

                roof_type_key = _get_roof_type(key_without_prefix)
                if roof_type_key not in ["flat", "pitched", "gable"]:
                    print("Ungültiger Roof Type in Key:", roof_type_key)
                    continue

                if roof_type_key == "flat":
                    relative_yield = _get_relative_yield(key_without_prefix)
                    if relative_yield is None:
                        print("Ungültiger Relative Yield in Key:", key_without_prefix)
                        continue

                elif roof_type_key in ["pitched", "gable"]:
                    orientation = get_orientation(key_without_prefix)
                    if orientation is None:
                        print("Ungültige Orientation in Key:", key_without_prefix)
                        continue

                    tilt = _get_tilt(key_without_prefix)
                    if tilt is None:
                        print("Ungültiger Tilt in Key:", key_without_prefix)
                        continue

                else:
                    print("Ungültiger Roof Type in Key:", roof_type_key)
                    continue

                wirkungsgrad = _get_wirkungsgrad(key_without_prefix)
                if wirkungsgrad is None:
                    print("Ungültiger Wirkungsgrad in Key:", key_without_prefix)
                    continue

                globalstrahlung = _get_globalstrahlung(key_without_prefix)
                if globalstrahlung is None:
                    print("Ungültige Globalstrahlung in Key:", key_without_prefix)
                    continue

                zeitstempel = _get_zeitstempel(key_without_prefix)
                if zeitstempel is None:
                    print("Ungültiger Zeitstempel in Key:", key_without_prefix)
                    continue
                datum = zeitstempel.date()

                data_rows.append(
                    {
                        "building": building_name,
                        "berechnungsart": key_berechnungsart,
                        "roof_type": roof_type_key,
                        "wirkungsgrad": wirkungsgrad,
                        "globalstrahlung": globalstrahlung,
                        "datum": datum,
                        "leistung": value,
                    }
                )

                if roof_type_key == "flat":
                    data_rows[-1]["relative_yield"] = relative_yield

                elif roof_type_key in ["pitched", "gable"]:
                    data_rows[-1]["orientation"] = orientation
                    data_rows[-1]["tilt"] = tilt

    df = pd.DataFrame(data_rows)

    aggregated = (
        df.groupby(["building", "berechnungsart", "datum"])["leistung"]
        .agg(min_leistung="min", avg_leistung="mean", max_leistung="max")
        .reset_index()
    )

    excel_filename = "aggregierte_ergebnisse.xlsx"
    aggregated.to_excel(excel_filename, index=False)
    print(f"Aggregierte Ergebnisse wurden in '{excel_filename}' gespeichert.")

    plot_dir = "plot"
    if not os.path.exists(plot_dir):
        os.makedirs(plot_dir)

    for (building, berechnungsart), group in aggregated.groupby(
        ["building", "berechnungsart"]
    ):
        plt.figure()
        plt.plot(group["datum"], group["min_leistung"], marker="o", label="Min")
        plt.plot(
            group["datum"], group["avg_leistung"], marker="o", label="Durchschnitt"
        )
        plt.plot(group["datum"], group["max_leistung"], marker="o", label="Max")
        plt.xlabel("Datum")
        plt.ylabel("Leistung")
        plt.title(f"Aggregierte Leistung für {building} ({berechnungsart})")
        plt.legend()
        png_filename = os.path.join(
            plot_dir, safe_filename(f"plot_{building}_{berechnungsart}.png")
        )
        plt.savefig(png_filename)
        plt.close()
        print(
            f"Plot für {building} ({berechnungsart}) wurde in '{png_filename}' gespeichert."
        )


if __name__ == "__main__":
    auswertung()
