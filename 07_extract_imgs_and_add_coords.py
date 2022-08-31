import cv2
import datetime
import math
import numpy as np
import piexif
import TimeFormatConverter as TFC
from PIL import Image

# Ordnet einem Videozeitstempel den nächsten GPS-Wert zu.
def find_nearest(array, a0):
    nearest_val = array[abs(array-a0)==abs(array-a0).min()]
    result = np.where(array == nearest_val[0])
    index = result[0]
    return array[index]

# Wandelt einen dezimalen Gradwert in Grad, Minuten und Sekunden um.
def degToDmsRational(degFloat):
    minFloat = degFloat % 1 * 60
    secFloat = minFloat % 1 * 60
    deg = math.floor(degFloat)
    min = math.floor(minFloat)
    sec = int(secFloat * 100)
    return ((deg, 1), (min, 1), (sec, 100))

# Liefert 'N' (Nordhalbkugel) zurück, wenn Breitengrad >= 0°,
# sonst 'S' (Südhalbkugel).
def ChooseLatRef(degree):
    if degree >= 0:
        return 'N'
    else:
        return 'S'

# Liefert 'E' (Osten) zurück, wenn Längengrad >= 0°, sonst 'W' (Westen).
def ChooseLonRef(degree):
    if degree >= 0:
        return 'E'
    else:
        return 'W'

# Log-Datei wird geöffnet.
log_file = "D:/UAV-Befliegungen/210904/02_logs/00000052.log"
# Numpy-Array zur Speicherung der GNSS-Koordinaten
# und der synchronen Systemlaufzeit
arr = np.empty([0,4])

with open(log_file, "r") as log_file_open:
    lock = True
    # Schleife über die Zeilen der Log-Datei.
    for line in log_file_open.readlines():
    	# Falls Zeile mit MSG-Parameter
        if line[:3] == 'MSG':
            items = line.split(", ")
            # Wenn Kommando mit dem das Video gestartet wird enthalten.
            if "Mission: 7 RepeatRelay" in items[2]:
                # Systemlaufzeit abfragen.
                starttime = items[1]
                lock = False
            # Wenn Kommando mit dem das Video gestoppt wird enthalten.
            if "Reached command #12" in items[2]:
                # Systemlaufzeit abfragen.
                starttime = items[1]
                lock = True

        if not lock:
            # Falls Zeile mit GPS-Parameter
            if line[:3] == 'GPS':
                items = line.split(", ")
                # Umrechnung Mikrosekunden Dezimalsekunden
                time = round(((int(items[1]) - int(starttime))/1000000),9)
                print(time)
                lat  = items[7] #Abfrage X-Koordinate
                lon  = items[8] #Abfrage Y-Koordinate
                alt  = items[9] #Abfrage Z-Koordinate
                secs, lat, lon, alt = \
                float(time), float(lat), float(lon), float(alt)
                # Synchrone Systemlaufzeit und GNSS-Koordinaten
                # werden in Array gespeichert.
                arr = np.append(arr, [[secs, lat, lon, alt]], axis=0)

# Video-Datei wird geöffnet.
vc = cv2.VideoCapture('D:/UAV-Befliegungen/03_videos/MOVI0026.mov')

fps     = vc.get(cv2.CAP_PROP_FPS)
frames  = int(vc.get(cv2.CAP_PROP_FRAME_COUNT))
seconds = frames/fps
width   = vc.get(cv2.CAP_PROP_FRAME_WIDTH)
height  = vc.get(cv2.CAP_PROP_FRAME_HEIGHT)

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

while rval:
    # s. oben
    rval, frame = vc.read()
    # Zählvariable wird um 1 erhöht.
    counter += 1
    # Kommandos nach Verzweigung werden nur bei jedem 10. Bild ausgeführt.
    # if counter % 10 == 0:
    if counter % 10 == 0:
        # Der Zeitstempel des Bilds wird aus der Division
        # von Bildnummer und Bildrate errechnet.
        timestamp = round(counter/fps, 3)
        print("time stamp current frame: ", timestamp)

        # Anhand des Zeitstempels werden aus dem Numpy-Array
        # die nächstliegenden GNSS-Positionen abgefragt.
        tuple = find_nearest(arr, timestamp)
        lat  = tuple[0][1]
        lon  = tuple[0][2]
        alt  = tuple[0][3]

        print(lat)
        print(lon)
        print(alt)

        # Festlegung der Exif-Kameraparameter.
        zeroth_ifd = {
        piexif.ImageIFD.Make: u"Renkforce",
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

        filename = 'D:/UAV-Befliegungen/04_ODM/images/' \
        + str(timestamp).replace(".", "_") + '.jpg'
        # Speichern des Einzelbilds als jpg-Datei.
        cv2.imwrite(filename, frame)

        # Öffnen der soeben gespeicherten jpg-Datei mit Pillow.
        im = Image.open(filename)
        # Erneutes Speichern jpg-Datei unter Anfügung der Exif-Daten.
        im.save(filename, exif=exif_bytes)

    else:
        pass

# Schließt die Video-Datei.
vc.release()
