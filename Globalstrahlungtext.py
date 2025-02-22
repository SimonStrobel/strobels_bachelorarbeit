import sys
import pandas as pd


def erstelle_daten_bayreuth():
    """Diese Funktion liest die stündlichen Werte von UniBayreuth ein und gibt sie als Liste zurück.

    Note:
        zeitstempel_hourly ist eine Liste von 8760 Stunden
        (e.g. ['2023-01-01 00:00:00', '2023-01-01 01:00:00', ...] )

    Returns:
        list: Liste mit stündlichen Werten von UniBayreuth
    """
    zeitstempel_hourly = pd.date_range(
        start="2023-01-01 00:00:00", end="2023-12-31 23:00:00", freq="1h"
    )
    daten_bayreuth = []
    with open("GlobalstrahlungMessungUni.txt", "r") as file:
        for zeile in file:
            daten_bayreuth.append(float(zeile))

    if len(daten_bayreuth) < len(zeitstempel_hourly):
        sys.exit("Fehler: Nicht genügend Werte in UniBayreuth.txt")

    return pd.DataFrame(
        daten_bayreuth, index=zeitstempel_hourly, columns=["Globalstrahlung_Stündlich"]
    )


def erstelle_daten_mistelbach():
    """Diese Funktion liest die täglichen Werte von Mistelbach ein und gibt sie als Liste zurück.

    Note:
        zeitstempel_daily ist eine Liste von 365 Tagen
        (e.g. ['2023-01-01', '2023-01-02', ...] )

    Returns:
        list: Liste mit täglichen Werten von Mistelbach
    """
    zeitstempel_daily = pd.date_range(start="2023-01-01", end="2023-12-31", freq="1D")
    daten_mistelbach_daily = []
    with open("GlobalstrahlungMessungMistelbach.txt", "r") as file:
        for zeile in file:
            daten_mistelbach_daily.append(float(zeile))

    if len(daten_mistelbach_daily) < len(zeitstempel_daily):
        sys.exit("Fehler: Nicht genügend Werte in Mistelbach.txt")

    return pd.DataFrame(
        daten_mistelbach_daily,
        index=zeitstempel_daily,
        columns=["Globalstrahlung_Täglich"],
    )


def stunde_elf_und_zwoelf_anpassen(
    daten_bayreuth: pd.DataFrame, daten_mistelbach: pd.DataFrame
) -> pd.DataFrame:
    """Diese Funktion passt die Stunden-Werte von UniBayreuth an,
    wenn die Summe der stündlichen Werte eines Tages nicht mit dem täglichen Wert von Mistelbach übereinstimmt.
    Es passt hier nur die Werte für 11:00 und 12:00 Uhr an.

    Args:
        daten_bayreuth (pd.DataFrame): Stündliche Werte von UniBayreuth
        daten_mistelbach (pd.DataFrame): Tägliche Werte von Mistelbach

    Returns:
        pd.DataFrame: Angepasste stündliche Werte von UniBayreuth
    """
    df_gs_bayreuth_hourly = daten_bayreuth.copy()
    df_gs_mistelbach_daily = daten_mistelbach.copy()

    globalstrahlung_angepasst = []

    for zaehler in range(0, len(df_gs_mistelbach_daily)):
        taeglicher_wert_mistelbach = df_gs_mistelbach_daily.loc[
            df_gs_mistelbach_daily.index[zaehler], "Globalstrahlung_Täglich"
        ]
        summe_24_stundenwerte_bayreuth = df_gs_bayreuth_hourly.loc[
            df_gs_bayreuth_hourly.index[zaehler * 24 : zaehler * 24 + 24],
            "Globalstrahlung_Stündlich",
        ].sum()

        if taeglicher_wert_mistelbach == summe_24_stundenwerte_bayreuth:
            # Wenn die Werte übereinstimmen, dann füge diesen Wert in die neue Liste ein
            globalstrahlung_angepasst.extend(
                df_gs_bayreuth_hourly.loc[
                    df_gs_bayreuth_hourly.index[zaehler * 24 : zaehler * 24 + 24],
                    "Globalstrahlung_Stündlich",
                ]
            )
            continue

        # Wenn die Werte nicht übereinstimmen, dann berechne die Differenz
        halbe_differenz = (
            taeglicher_wert_mistelbach - summe_24_stundenwerte_bayreuth
        ) / 2

        elf_uhr_wert_bayreuth = df_gs_bayreuth_hourly.loc[
            df_gs_bayreuth_hourly.index[zaehler * 24 + 11], "Globalstrahlung_Stündlich"
        ]
        zwoelf_uhr_wert_bayreuth = df_gs_bayreuth_hourly.loc[
            df_gs_bayreuth_hourly.index[zaehler * 24 + 12], "Globalstrahlung_Stündlich"
        ]

        neuer_elf_uhr_wert = elf_uhr_wert_bayreuth + halbe_differenz
        neuer_zwoelf_uhr_wert = zwoelf_uhr_wert_bayreuth + halbe_differenz

        globalstrahlung_angepasst.extend(
            df_gs_bayreuth_hourly.loc[
                df_gs_bayreuth_hourly.index[zaehler * 24 : zaehler * 24 + 11],
                "Globalstrahlung_Stündlich",
            ]
        )
        globalstrahlung_angepasst.append(neuer_elf_uhr_wert)
        globalstrahlung_angepasst.append(neuer_zwoelf_uhr_wert)
        globalstrahlung_angepasst.extend(
            df_gs_bayreuth_hourly.loc[
                df_gs_bayreuth_hourly.index[zaehler * 24 + 13 : zaehler * 24 + 24],
                "Globalstrahlung_Stündlich",
            ]
        )

    if len(globalstrahlung_angepasst) != len(df_gs_bayreuth_hourly):
        raise sys.exit(
            f"Mismatch in number of rows: expected {len(df_gs_bayreuth_hourly)}, got {len(globalstrahlung_angepasst)}."
        )

    # Erstelle ein neues DataFrame mit den angepassten Werten und Zeitstempeln
    df_gs_bayreuth_hourly["Globalstrahlung_Stündlich"] = globalstrahlung_angepasst

    with pd.ExcelWriter(
        "Globalstrahlung_Angepasst.xlsx", engine="xlsxwriter"
    ) as writer:
        df_gs_bayreuth_hourly.to_excel(writer, index=True, header=True)
        worksheet = writer.sheets["Sheet1"]
        worksheet.set_column("A:B", 20)

    df_gs_bayreuth_hourly.to_excel(
        "Globalstrahlung_Angepasst.xlsx", index=True, header=True
    )
    print("Angepasste Datei gespeichert: Globalstrahlung_Angepasst.xlsx")


# führt den Code nur aus, wenn das Skript direkt ausgeführt wird
if __name__ == "__main__":
    daten_bayreuth = erstelle_daten_bayreuth()
    daten_mistelbach = erstelle_daten_mistelbach()
    stunde_elf_und_zwoelf_anpassen(daten_bayreuth, daten_mistelbach)
