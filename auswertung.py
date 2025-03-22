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
from openpyxl import load_workbook
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


def aggregate_group(group: pd.DataFrame) -> pd.DataFrame:
    """Für eine Gruppe (d.h. alle Datensätze eines Gebäudes, einer Berechnungsart und einer Stunde)
    wird:
      - das Record mit minimaler Leistung ermittelt,
      - das Record mit maximaler Leistung ermittelt,
      - und ein "Durchschnittsrecord" erzeugt (numerische Felder werden gemittelt,
        nicht-numerische Felder werden aus dem ersten Datensatz übernommen).
    """
    min_row = group.loc[group["leistung"].idxmin()].copy()
    max_row = group.loc[group["leistung"].idxmax()].copy()

    avg_row = group.iloc[0].copy()
    avg_row["leistung"] = group["leistung"].mean()

    min_row["statistic"] = "min"
    avg_row["statistic"] = "avg"
    max_row["statistic"] = "max"

    return pd.DataFrame([min_row, avg_row, max_row])


def auswertung():
    """Hauptfunktion zur Auswertung der Daten aus der ergebnisse.json."""
    data_rows = []
    with open("data/ergebnisse_2.json", "rb") as f:
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
                    print("Überspringe Key ohne 'leistung_'-Präfix:", key)
                    continue

                key_berechnungsart = _get_berechnungsart(key_without_prefix)
                if key_berechnungsart not in ["scheaffler", "tum"]:
                    print(
                        "Überspringe ungültige Berechnungsart in Key:",
                        key_berechnungsart,
                    )
                    continue

                roof_type_key = _get_roof_type(key_without_prefix)
                if roof_type_key not in ["flat", "pitched", "gable"]:
                    print("Überspringe ungültigen Roof Type in Key:", roof_type_key)
                    continue

                if roof_type_key == "flat":
                    relative_yield = _get_relative_yield(key_without_prefix)
                    if relative_yield is None:
                        print(
                            "Überspringe ungültigen Relative Yield in Key:",
                            key_without_prefix,
                        )
                        continue

                elif roof_type_key in ["pitched", "gable"]:
                    orientation = get_orientation(key_without_prefix)
                    if orientation is None:
                        print(
                            "Überspringe ungültige Orientation in Key:",
                            key_without_prefix,
                        )
                        continue

                    tilt = _get_tilt(key_without_prefix)
                    if tilt is None:
                        print("Überspringe ungültigen Tilt in Key:", key_without_prefix)
                        continue

                else:
                    print("Ubergehe ungültigen Roof Type in Key:", key_without_prefix)
                    continue

                wirkungsgrad = _get_wirkungsgrad(key_without_prefix)
                if wirkungsgrad is None:
                    print(
                        "Überspringe ungültigen Wirkungsgrad in Key:",
                        key_without_prefix,
                    )
                    continue

                globalstrahlung = _get_globalstrahlung(key_without_prefix)
                if globalstrahlung is None:
                    print(
                        "Überspringe ungültige Globalstrahlung in Key:",
                        key_without_prefix,
                    )
                    continue

                zeitstempel = _get_zeitstempel(key_without_prefix)
                if zeitstempel is None:
                    print(
                        "Überspringe ungültigen Zeitstempel in Key:", key_without_prefix
                    )
                    continue

                record = {
                    "building": building_name,
                    "berechnungsart": key_berechnungsart,
                    "roof_type": roof_type_key,
                    "wirkungsgrad": wirkungsgrad,
                    "globalstrahlung": globalstrahlung,
                    "datum": zeitstempel,
                    "leistung": value,
                }

                if roof_type_key == "flat":
                    record["relative_yield"] = relative_yield
                    record["orientation"] = None
                    record["tilt"] = None
                elif roof_type_key in ["pitched", "gable"]:
                    record["relative_yield"] = None
                    record["orientation"] = orientation
                    record["tilt"] = tilt

                data_rows.append(record)

    df = pd.DataFrame(data_rows)
    df["hour"] = df["datum"].dt.floor("h")

    groups = df.groupby(["building", "berechnungsart", "hour"])
    aggregated_list = []
    for _, group in groups:
        agg_group = aggregate_group(group)
        aggregated_list.append(agg_group)
    aggregated = pd.concat(aggregated_list, ignore_index=True)

    stat_order = {"min": 0, "avg": 1, "max": 2}
    aggregated["stat_order"] = aggregated["statistic"].map(stat_order)
    aggregated.sort_values(
        by=["building", "berechnungsart", "hour", "stat_order"], inplace=True
    )
    aggregated.drop(columns=["stat_order"], inplace=True)
    # Da 'datum' und 'hour' identisch sind, entfernen der redundanten Spalte "datum"
    aggregated.drop(columns=["datum"], inplace=True)

    # Speichern in Excel-Datei
    excel_folder = "data"
    if not os.path.exists(excel_folder):
        os.makedirs(excel_folder)
    excel_filename = os.path.join(excel_folder, "aggregated_data.xlsx")
    aggregated.to_excel(excel_filename, index=False)
    print(f"Die aggregierten Daten wurden in '{excel_filename}' gespeichert.")

    wb = load_workbook(excel_filename)
    ws = wb.active
    for column_cells in ws.columns:
        max_length = 0
        column = column_cells[0].column_letter
        for cell in column_cells:
            try:
                cell_length = len(str(cell.value))
                if cell_length > max_length:
                    max_length = cell_length
            except:
                pass
        adjusted_width = max_length + 2
        ws.column_dimensions[column].width = adjusted_width
    wb.save(excel_filename)
    print("Die Spaltenbreiten in der Excel-Datei wurden angepasst.")


if __name__ == "__main__":
    auswertung()
