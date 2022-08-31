import datetime
import TimeFormatConverter as TFC
import LogFile

root = "D:/UAV-Befliegungen/02_logs/"

# Instanziierung des LogFile-Objekts
log_file = LogFile(root + "00000052.log")

# Festlegung des Kommandos durch das das Relais geschaltet
# und damit die Videoaufnahme gestartet wird.
startcmd = "Mission: 7 RepeatRelay"
stopcmd  = "Reached command #12"

# Abfrage der Systemzeit seit Boot (TimeUS)
# beim Starten und Stoppen der Videoaufnahme (Rückgabetyp: Tupel).
timeUS_of_video_start_and_stop = \
log_file.get_timeUS_of_video_start_and_stop(startcmd, stopcmd)

# Systemzeit beim Starten der Videoaufnahme (tvs = tsd1 + Δt).
vid_start_time = timeUS_of_video_start_and_stop[0]
# print(vid_start_time)

# Systemzeit beim Stoppen der Videoaufnahme (tve = tsd2 + Δt).
vid_stop_time  = timeUS_of_video_start_and_stop[1]
# print(vid_stop_time)

# Abfrage der Dictionary mit den GPS-Zeitstempeln (GPS-Sekunden)
# als Schlüssel und den TimeUS-Zeitstempeln als Wert.
map_gpstime_to_timeUS = log_file.map_gpstime_to_timeUS()
# print(map_gpstime_to_timeUS)

# Dateiname der Quell-CSV-Datei.
csv_file_read  = root + "00000052.csv"
# Dateiname der Ziel-CSV-Datei.
csv_file_write = root + "00000052_2.csv"

# new_header = \
# "Date;Time;latitude(deg);longitude(deg);height(m);Q;ns;" + \
# "sdn(m);sde(m);sdu(m);sdne(m);sdeu(m);sdun(m);age(s);ratio;" + \
# "videotime;videotime(sec)\n" # "videotime;videotime(sec)" wird ergänzt

new_header = \
"Date;Time;latitude(deg);longitude(deg);height(m);Q;ns;" + \
"sdn(m);sde(m);sdu(m);sdne(m);sdeu(m);sdun(m);age(s);ratio;" + \
"videotime;videotime(sec);alt_agl(m)\n" # "videotime;videotime(sec)" wird ergänzt

def closest_value(valueset, searchvalue):
    dictio = {}
    for value in valueset:
        diff = abs(searchvalue - int(value))
        dictio[diff] = int(value)
    x = min(list(dictio.keys()))
    # print(dictio[x])
    return dictio[x]

# Öffnen der Ziel-CSV-Datei,
# die eine Erweiterung der Quell-CSV-Datei um die Videolaufzeiten darstellt.
with open(csv_file_write, "w") as csv_file_write_opened:
    # Einfügen einer neuen Kopfzeile in die Ziel-CSV-Datei.
    csv_file_write_opened.write(new_header)
    # Öffnen der Quell-CSV-Datei.
    with open(csv_file_read, "r") as csv_file_read_opened:
        # Schleife durch die Zeilen der Quell-CSV-Datei,
        # außer der Kopfzeile.
        for row in csv_file_read_opened.readlines()[1:]:
            # Zeileninhalt (Datum, Zeit, Koordinaten etc.) werden
            # vereinzelt und als separate Elemente in einer Liste
            # gespeichert.
            row_splitted = row.split(";")
            # Das 1. Listenelement, das Datum (z. B. "2021/09/10")
            # wird in seine Teilkomponenten Jahr, Monat und Tag zerlegt
            # und als Liste gespeichert.
            date  = row_splitted[0].split("/")
            year  = int(date[0])
            month = int(date[1])
            day   = int(date[2])
            # Das 2. Listenelement, der Zeitpunkt (z. B. "06:58:43.800")
            # wird in seine Teilkomponenten Stunde, Minute und Sekunde
            # zerlegt und als Liste gespeichert.
            time        = row_splitted[1].split(":")
            hour        = int(time[0])
            minute      = int(time[1])
            sec_float   = time[2].split(".")
            sec_int     = int(sec_float[0])
            microsec    = int(sec_float[1])

            # Umrechnung der obigen Zeitgrößen in die GPS-Zeitgrößen
            # GPS-Woche und GPS-Sekunden (Beispiel 2174, 457126.59)
            gps_weeks_and_microseconds = TFC.utc_to_week_and_seconds(\
            year, month, day, hour, minute, sec_int, microsec)
            # Zugriff auf die soeben berechneten GPS-Sekunden.
            gpsmicroseconds = gps_weeks_and_microseconds[1]

            try:
                # Abfrage des TimeUS-Zeitstempels
                # der dem GPS-Zeitstempel zugeordnet ist.
                timeUS = map_gpstime_to_timeUS[gpsmicroseconds]
                print("success: matching gps-record found")
                print("timeUS: " + str(timeUS))

                # Berechnung des Zeitpunks im Video,
                # an dem die GPS-Koordinate gemessen wurde (tgps - tvs).
                timeVideo = timeUS - vid_start_time
                print("timeVideo: " + str(timeVideo))
                # Umrechnung des Videozeitpunkts (Mikrosekunden)
                # in ein Tupel aus Minuten, Sekunden und Millisekunden.
                timeVideoUTC =  TFC.microseconds_to_clocktime(timeVideo)
                print("timeVideoUTC: " + str(timeVideoUTC) + "\n")
                timeVid_min  = timeVideoUTC[0]
                timeVid_sec  = timeVideoUTC[1]
                timeVid_msec = timeVideoUTC[2]
                # Umrechnung Mikrosekunden in Dezimalsekunden
                # mit 3 Nachkommastellen
                dsec = round(timeVideo/1000000, 3)
                # Schreiben der Quell-Zeile zzgl. der neuen Zeitangaben
                # in die Ziel-CSV-Datei.
                csv_file_write_opened.write(row.strip("\n") + ";" + \
                str(timeVid_min) + "," + str(timeVid_sec) + "," + \
                # str(timeVid_msec) + ";" + str(dsec) + "\n")
                str(timeVid_msec) + ";" + str(dsec)+ ";" + str(BARO) + "\n")

            except:
                # Falls einer Positionslösung kein GPS-Wert in der
                # Log-Datei zugeordnet werden kann.
                # print("failure: no matching gps-record found")
                csv_file_write_opened.write(row.strip("\n") + \
                ";NULL;NULL;NULL\n")
