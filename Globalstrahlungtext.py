import pandas as pd

# 🔹 1. Stündlichen Datensatz einlesen (Uni Bayreuth)
start_datum = "2023-01-01 00:00:00"
end_datum = "2023-12-31 23:00:00"
Zeitstempel = pd.date_range(start=start_datum, end=end_datum, freq="1h")

DatenBayreuth = []
with open("GlobalstrahlungMessungUni.txt", "r") as file:
    for zeile in file:
        teile = zeile.split()
        if teile:  
            DatenBayreuth.append(float(teile[0]))  

# ✅ Spaltennamen setzen
df_gs = pd.DataFrame(DatenBayreuth, index=Zeitstempel, columns=["Globalstrahlung_Stündlich"])

# 🔹 2. Täglichen Datensatz einlesen (Mistelbach)
start_datum = "2023-01-01"
end_datum = "2023-12-31"
Zeitstempel_täglich = pd.date_range(start=start_datum, end=end_datum, freq="1D")

DatenBayreuth_täglich = []
with open("GlobalstrahlungMessungMistelbach.txt", "r") as file:
    for zeile in file:
        teile = zeile.split()
        if teile:
            DatenBayreuth_täglich.append(float(teile[0]))

# Fehlende Werte auffüllen
if len(DatenBayreuth_täglich) < len(Zeitstempel_täglich):
    DatenBayreuth_täglich.extend([None] * (len(Zeitstempel_täglich) - len(DatenBayreuth_täglich)))

df_gs_täglich = pd.DataFrame(DatenBayreuth_täglich, index=Zeitstempel_täglich, columns=["Globalstrahlung_Täglich"])

# 🔹 3. Werte für 11:00 und 12:00 Uhr anpassen
for datum in Zeitstempel_täglich:
    # Tageswerte abrufen
    tageswerte = df_gs.loc[df_gs.index.date == datum.date()].astype(float)
    sum_uni = tageswerte.sum().values[0]
    mistelbach_wert = df_gs_täglich.loc[datum, "Globalstrahlung_Täglich"]

    # Falls Werte existieren & unterschiedlich sind, anpassen
    if not pd.isna(sum_uni) and not pd.isna(mistelbach_wert) and sum_uni != mistelbach_wert:
        differenz = mistelbach_wert - sum_uni
        timestamps = [pd.Timestamp(f"{datum.date()} 11:00:00"), pd.Timestamp(f"{datum.date()} 12:00:00")]

        # ✅ Prüfen, ob die Zeitstempel existieren, bevor sie verändert werden
        if all(ts in df_gs.index for ts in timestamps):
            werte_vorher = df_gs.loc[timestamps, "Globalstrahlung_Stündlich"].astype(float).values.flatten()

            if len(werte_vorher) == 2 and werte_vorher.sum() != 0:
                faktor = (werte_vorher.sum() + differenz) / werte_vorher.sum()
                df_gs.loc[timestamps, "Globalstrahlung_Stündlich"] = werte_vorher * faktor

# 🔹 4. Sicherstellen, dass keine Zeitstempel fehlen
full_index = pd.date_range(start="2023-01-01 00:00:00", end="2023-12-31 23:00:00", freq="h")
missing_timestamps = full_index.difference(df_gs.index)

print("⏳ Fehlende Zeitstempel:", missing_timestamps)

# Falls fehlende Zeitstempel existieren → Hinzufügen!
df_gs = df_gs.reindex(full_index).fillna(0)

print("✅ Nach dem Fix: df_gs hat jetzt", len(df_gs), "Zeilen")

# 🔹 5. Ergebnisse speichern
# 🔴 Falls durch Berechnungen die Spalten verloren gehen, nochmal sicherstellen:
df_gs.columns = ["Globalstrahlung_Stündlich"]
df_gs.to_csv("Globalstrahlung_Angepasst.csv", sep=";", index=True, header=True)
print("Angepasste Datei gespeichert: Globalstrahlung_Angepasst.csv")
