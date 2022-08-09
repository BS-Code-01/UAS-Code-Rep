from moduls.log_file import LogFile
from moduls.RINEX_file import RinexFile

# Verzeichnis in dem die ASCII-Log-Datei gespeichtert ist.
path = "D:/UAV-Befliegungen/temp/"

# Name der Log-Datei mit Dateiformats-Suffix
logfile_name = "00000052.log"

# Ganzer Pfad der Logdatei.
logfile_full_path = path + logfile_name

# Instanziierung des Log-File-Objekts: Einlesen der Log-File-Zeilen
# und Rückgabe der Zeilen in einer Liste
log_file = LogFile(logfile_full_path)

# Ordnet den UBX-RXM-RAWX-Nachrichten in der log_file die System-Zeitstempel
# seit dem Systemstart zu.
GRXH_GRXS_values = log_file.extract_GRXH_and_GRXS_from_logfile()

# Die Ausgabedatei (RINEX-Datei), erhält den gleichen Name wie die Log-Datei
# aber mit dem Dateiformatssuffix ".21o"
RINEX_name = logfile_name.replace(".log", ".21o")

# Ganzer Pfad der Ausgabedatei (RINEX-Datei).
RINEX_full_path = path + RINEX_name

# Es wird eine RINEX-Datei erstellt. Dem Konstruktor wird der Dateiname
# mit vollständigem Pfad und die Dictionary mit den extrahierten
# UBX-RXM-RAWX-Nachrichten übergeben
RINEX = RinexFile(RINEX_full_path, GRXH_GRXS_values)

# Die RINEX-Datei wird in das Dateisystem geschrieben.
RINEX.write_RINEX()

# Objekte werden gelöscht.
del LogFile, RINEX
