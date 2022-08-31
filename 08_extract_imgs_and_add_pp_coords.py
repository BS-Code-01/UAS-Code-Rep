import cv2
import datetime
import math
import piexif
import time
from PIL import Image

start = time.time()

timestamps_pos_dictio = {}
timestamps_vid_list = []
timestamps_vid_dictio = {}

# Angabe vom Projektverzeichnis
root = "D:/UAV-Befliegungen/210904/"

# CSV-Datei mit den korrigierten GNSS-Koordinaten
# und den zugehörigen Videozeitpunkten.
csv_file_read = root + "02_logs/00000052_2.csv"

with open(csv_file_read, "r") as csv_file_read_opened:
    # Kopfzeile überspringen
    for row in csv_file_read_opened.readlines()[1:]:
        # Zeileninhalt (Datum, Zeit, Koordinaten etc.) werden vereinzelt
        # und als separate Elemente in einer Liste gespeichert.
        row_content = row.strip("\n").split(";")
        # Der Wert für die Postionslösungsgüte wird
        # zur Ganzzahl umgewandelt.
        Q = int(row_content[5])
        # Nur Positionslösungen mit Q=2 (float) oder Q=1 (fix)
        # werden weiterverarbeitet.
        # TODO: Q=1 (fix) ist anzustreben.
        if Q < 3:
            # Extraktion des der Positionslösung
            # zugeordneten Videozeitpunkts.
            videotime = row_content[-2]
            # Nur Positionslösungen ab Videostartzeitpunkt
            # werden übernommen.
            if videotime != "NULL" and float(videotime) >= 0:
                secs = float(videotime)
                lat  = float(row_content[2])
                lon  = float(row_content[3])
                # alt  = float(row_content[4])
                alt  = float(row_content[-1])

                # Einer Dictionary wird der Videozeitpunkt als Schlüssel
                # und die Koordinaten als Werte hinzugefügt.
                timestamps_pos_dictio[secs] = [lat, lon, alt]

# Konstruktor der OpenCV-Klasse VideoCapture. Öffnet und liest die Video-Datei.
vc = cv2.VideoCapture(root + "03_videos/MOVI0026.mov")

# Abfrage von Videoeigenschaften.
fps     = vc.get(cv2.CAP_PROP_FPS)
frames  = int(vc.get(cv2.CAP_PROP_FRAME_COUNT))
seconds = frames/fps
width   = vc.get(cv2.CAP_PROP_FRAME_WIDTH)
height  = vc.get(cv2.CAP_PROP_FRAME_HEIGHT)

# Zählvariable: Zur Festlegung der Bildexport-Frequenz
counter = 0

# Wenn Video-Datei geöffnet.
if vc.isOpened():
    # Wenn Video-Datei geöffnet ist, wird auf das nächste Bild des Videos
    # zugegriffen. Falls ein Bild zugreifbar ist, wird ein Tupel mit
    # rval(return value)=True und das beteffende Bild (frame)
    # zurückgegeben, andernfalls ein Tupel mit rval=False und frame=False.
	rval, frame = vc.read()
else:
    # Wenn Video-Datei nicht geöffnet ist.
    rval = False # rval(return value)=False
    print("cannot open videofile")

timestamplist_vid = []
# Schleifendurchlauf nur, wenn Bild im Zugriff.
print("1st frame iteration")
while rval:
    # s. oben
    rval, frame = vc.read()
    # Zählvariable wird um 1 erhöht.
    counter += 1
    # Kommandos nach Verzweigung werden nur bei jedem 10. Bild ausgeführt.
    if counter % 10 == 0:
        # Der Zeitstempel des Bilds wird aus der Division
        # von Bildnummer und Bildrate errechnet.
        timestamp = round(counter/fps, 3)
        print("time stamp current frame: ", timestamp)
        # Zeitstempel wird der Liste hinzugefügt.
        timestamps_vid_list.append(timestamp)

# Schließt die Video-Datei.
vc.release()
print("timestamps_vid_list finished")

# print(timestamps_pos_dictio)
# print(timestamps_vid_list)

# Schleife durch die Dictionary mit den Videozeitpunkten als Schlüssel
# und den korrigierten Koordinaten als Werte.
for timestamp_pos in timestamps_pos_dictio:
    # Schleife durch die Liste mit den Zeitstempeln der Standbilder.
    for timestamp_vid in timestamps_vid_list:
        # Berechnung der Differenz (Betrag) des Videozeitpunkts aus der
        # Dictionary (mit zugeordneten GNSS-Koordinaten) und des aktuell
        # iterierten Videozeitpunkts eines Einzelbilds.
        result = abs(timestamp_vid - timestamp_pos)
        # Kommandos nach Verzweigung werden nur ausgeführt, wenn der
        # Differenzbetrag kleiner als ein vorgegebener Schwellenwert ist.
        if result < 0.041:
            print("timestamp_pos: " + str(timestamp_pos))
            print("timestamp_vid: " + str(timestamp_vid))
            print("abs(timestamp_vid - timestamp_pos): " + str(result))
            # Der Dictionary wird als Schlüssel der Videozeitpunkt des
            # aktuell iterierten Einzelbilds und als Wert die Liste
            # mit den korrigierten Koordinaten hinzugefügt.
            timestamps_vid_dictio[timestamp_vid] = \
            timestamps_pos_dictio[timestamp_pos]

# Gibt 'N' (Nordhalbkugel) zurück, wenn Breitengrad >= 0°,
# sonst 'S' (Südhalbkugel).
def ChooseLatRef(degree):
    if degree >= 0:
        return 'N'
    else:
        return 'S'

# Gibt 'E' (Osten) zurück, wenn Längengrad >= 0°, sonst 'W' (Westen).
def ChooseLonRef(degree):
    if degree >= 0:
        return 'E'
    else:
        return 'W'

# Wandelt einen dezimalen Gradwert in Grad, Minuten und Sekunden um.
def degToDmsRational(degFloat):
    minFloat = degFloat % 1 * 60
    secFloat = minFloat % 1 * 60
    deg = math.floor(degFloat)
    min = math.floor(minFloat)
    sec = int(secFloat * 100)
    return ((deg, 1), (min, 1), (sec, 100))

# Konstruktor der OpenCV-Klasse VideoCapture.
# Öffnet und liest die Video-Datei ein 2. Mal.
vc = cv2.VideoCapture(root + "03_videos/MOVI0026.mov")

# Zählvariable: Zur Festlegung der Bildexport-Frequenz
counter = 0

if vc.isOpened():
    # Wenn Video-Datei geöffnet ist, wird auf das nächste Bild des Videos
    # zugegriffen. Falls ein Bild zugreifbar ist, wird ein Tupel mit
    # rval(return value)=True und das beteffende Bild (frame)
    # zurückgegeben, andernfalls ein Tupel mit rval=False und frame=False.
	rval, frame = vc.read()
else:
    # Wenn Video-Datei nicht geöffnet ist.
    rval = False # rval(return value)=False

print("2nd frame iteration")
while rval:
    # s. oben
    rval, frame = vc.read()
    # Zählvariable wird um 1 erhöht.
    counter += 1
    # Kommandos nach Verzweigung werden nur bei jedem 10. Bild ausgeführt.
    if counter % 10 == 0:

        # Der Zeitstempel des Bilds wird aus der Division
        # von Bildnummer und Bildrate errechnet.
        # timestamp = round(counter1/fps, 3)
        timestamp = round(counter/fps, 3)
        print(timestamp)
        # Wenn der Zeitstempel des Bildes in der oben angelegten Dictionay
        # als Schlüssel enthalten ist, werden die Kommandos nach der
        # Verzweigung (die Geokodierung) ausgeführt.
        if timestamp in list(timestamps_vid_dictio.keys()):
            print(timestamp)

            # Abfrage der Koordinaten
            lat  = timestamps_vid_dictio[timestamp][0]
            lon  = timestamps_vid_dictio[timestamp][1]
            alt  = timestamps_vid_dictio[timestamp][2]

            print(lat)
            print(lon)
            print(alt)

            # Festlegung der Exif-Kameraparameter.
            zeroth_ifd = {
            piexif.ImageIFD.Make: u"Renkforce",
            piexif.ImageIFD.XResolution: (3840, 1),
            piexif.ImageIFD.YResolution: (2160, 1),
            piexif.ImageIFD.Software: u"piexif"
            }

            # Festlegung des Exif-Erstell-Datums.
            exif_ifd = {
            piexif.ExifIFD.DateTimeOriginal: \
            str(datetime.datetime.now().strftime("%Y:%m:%d %H:%M:%S")),
            piexif.ExifIFD.LensSpecification: \
            ((1, 1), (1, 1), (1, 1), (1, 1)),
            }

            # Festlegung der Exif-Geokoordinaten.
            gps_ifd = {
            piexif.GPSIFD.GPSLatitudeRef: ChooseLatRef(lat),  # N oder S
            piexif.GPSIFD.GPSLatitude: degToDmsRational(lat), # Breitengrad
            piexif.GPSIFD.GPSLongitudeRef: ChooseLonRef(lon), # E oder W
            piexif.GPSIFD.GPSLongitude: degToDmsRational(lon),# Längengrad
            piexif.GPSIFD.GPSAltitudeRef: 0,
            piexif.GPSIFD.GPSAltitude: (int(abs(alt)*100),100)# Höhe ü. NN
            }

            exif_dict = \
            {"0th":zeroth_ifd, "Exif":exif_ifd, \
            "1st":first_ifd, "GPS":gps_ifd}
            # Wandelt die Exif-Daten in bytes um.
            exif_bytes = piexif.dump(exif_dict)

            # Festlegung des Namens der Ausgabe-jpg-Datei.
            # Der Name entspricht dem Videozeitstempel des Einzelbilds.
            filename = \
            root + '04_ODM/images/' + \
            str(timestamp).replace(".", "_") + '.jpg'
            # Speichern des Einzelbilds als jpg-Datei.
            cv2.imwrite(filename, frame)

            # Öffnen der soeben gespeicherten jpg-Datei mit Pillow.
            im = Image.open(filename)
            # Erneutes Speichern jpg-Datei unter Anfügung der Exif-Daten.
            im.save(filename, exif=exif_bytes)

        else:
            # nur bei jedem 20. Bild
            if counter % 20 == 0:
                # Wenn der Zeitstempel des Bildes in der oben angelegten
                # Dictionay nicht als Schlüssel enthalten ist, wird keine
                # Geokodierung vorgenommen aber trotzdem ohne Exif-Infomation
                # als Standbild exportiert.

                # Festlegung des Namens der Ausgabe-jpg-Datei.
                # Der Name entspricht dem Videozeitstempel des Einzelbilds.
                filename = \
                root + '04_ODM_5/images/' + \
                str(timestamp).replace(".", "_") + '.jpg'
                # Speichern des Einzelbilds als jpg-Datei.
                cv2.imwrite(filename, frame)


# Schließt die Video-Datei.
vc.release()

end = time.time()
print("finished after :", end-start, " seconds")
