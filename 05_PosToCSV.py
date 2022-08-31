# Dateipfad der pos-Datei
# (Datei mit den nachberechneten Positionen aus dem PPK-Prozess).
pos_file_path = "D:/UAV-Befliegungen/temp/00000052.pos"
# Eingelesener Inhalt der pos-Datei.
pos_file_opened = open(pos_file_path, "r")
# Liste mit den Zeilen der pos-Datei.
pos_file_rows = pos_file_opened.readlines()

# Dateipfad der leeren csv-Datei in die die Positionslösungen übertragen werden.
csv_file_path = "D:/UAV-Befliegungen/temp/00000052.csv"
# Schreibender Zugriff auf die CSV-Datei.
csv_file_opened = open(csv_file_path, "w")

# Sequenzielles Aufrufen der Zeilen der pos-Datei.
for pos_file_row in pos_file_rows:
    # Header Zeilen werden ausgelassen.
    if pos_file_row[0] == "%" and pos_file_row[3:7] != "GPST":
        pass
    else:
        # Die Quell-Elemente der zu erstellenden Kopfzeile sind in
        # der Zeile enthalten, die die folgende Bedingung erfüllt.
        if pos_file_row[3:7] == "GPST":
            # Die Elemente der Quellzeile ab dem 3. Zeichen werden in
            # Einzelelemente zerlegt und dann durch Semikolons getrennt
            # wieder zusammengesetzt.
            new_row = ";".join(pos_file_row[3:].split())
            # Es wird eine Zeichenersetzung in der Kopfzeile vorgenommen.
            new_row = new_row.replace("GPST", "Date;Time")
            print(new_row)
            # Der Kopfzeile wird ein Zeilenumbruch angehängt und danach
            # in die CSV-Datei geschrieben.
            csv_file_opened.write(new_row + "\n")
        else:
            # Die Elemente der Quellzeile werden in Einzelelemente zerlegt
            # und dann durch Semikolons getrennt wieder zusammengesetzt.
            new_row = ";".join(pos_file_row.split())
            print(new_row)
            # Der Zeile wird ein Zeilenumbruch angehängt und danach
            # in die CSV-Datei geschrieben.
            csv_file_opened.write(new_row + "\n")

# Quell-Datei wird geschlossen.
pos_file_opened.close()

# Ziel-Datei wird gespeichert und geschlossen.
csv_file_opened.close()
