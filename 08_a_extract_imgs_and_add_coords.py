import cv2
import datetime
import math
import numpy as np
import piexif
from moduls.time_format_converter import TimeFormatConverter as TFC
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

# Liefert 'N' (Nordhalbkugel) zurück, wenn Breitengrad >= 0°, sonst 'S' (Südhalbkugel).
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

log_file = "D:/UAV-Befliegungen/210904_zuHauseNebenan/02_logs/00000052.log"
arr = np.empty([0,4])
arr_baro = np.empty([0,2])

with open(log_file, "r") as log_file_open:
    lock = True
    for line in log_file_open.readlines():
        if line[:3] == 'MSG':
            items = line.split(", ")
            if "Mission: 7 RepeatRelay" in items[2]:
                starttime = items[1]
                lock = False
            if "Reached command #12" in items[2]:
                starttime = items[1]
                lock = True

        if not lock:
            if line[:3] == 'GPS':
                items = line.split(", ")
                # time = TFC.microseconds_to_clocktime(int(items[1]) - int(starttime))
                time = round(((int(items[1]) - int(starttime))/1000000),9)
                print(time)
                lat  = items[7]
                lon  = items[8]
                alt  = items[9]
                # secs, lat, lon, alt = float(str(time[1]) + "." + str(time[2])), float(lat), float(lon), float(alt)
                secs, lat, lon, alt = float(time), float(lat), float(lon), float(alt)
                arr = np.append(arr, [[secs, lat, lon, alt]], axis=0)
            # if line[:4] == 'BARO':
            #     items = line.split(", ")
            #     time = TFC.microseconds_to_clocktime(int(items[1]) - int(starttime))
            #     alt  = items[2]
            #     secs, alt = float(str(time[0]) + "." + str(time[1])), float(alt)
            #     arr_baro = np.append(arr_baro, [[secs, alt]], axis=0)

# np.savetxt("D:/UAV-Befliegungen/210904_zuHauseNebenan/04_ODM_no_PP_3/arr2.txt", arr, fmt='%1.9f', delimiter=';')
# np.savetxt("D:/UAV-Befliegungen/210904_zuHauseNebenan/04_ODM_no_PP_3/arr_baro2.txt", arr_baro, fmt='%1.9f', delimiter=';')

vc = cv2.VideoCapture('D:/UAV-Befliegungen/210904_zuHauseNebenan/03_videos/MOVI0026.mov')

fps     = vc.get(cv2.CAP_PROP_FPS)
frames  = int(vc.get(cv2.CAP_PROP_FRAME_COUNT))
seconds = frames/fps
width   = vc.get(cv2.CAP_PROP_FRAME_WIDTH)
height  = vc.get(cv2.CAP_PROP_FRAME_HEIGHT)

counter1 = 0
counter2 = 0

if vc.isOpened():
	rval, frame = vc.read()
else:
    rval = False

# datei = open("D:/UAV-Befliegungen/210904_zuHauseNebenan/04_ODM_no_PP_3/findnearest.txt", "w")
while rval:
    rval, frame = vc.read()
    counter1 += 1
    if counter1 % 10 == 0:

        counter2 += 1
        timestamp = round(counter1/fps, 3)
        print("time stamp current frame: ", timestamp)

        tuple = find_nearest(arr, timestamp)
        # tuple_baro = find_nearest(arr_baro, timestamp)
        lat  = tuple[0][1]
        lon  = tuple[0][2]
        alt  = tuple[0][3]
        # alt  = tuple_baro[0][1]

        print(lat)
        print(lon)
        print(alt)

        # datei.write(str(timestamp) + ";" + str(lat) + ";" + str(lon) + ";" + str(alt) + "\n")

        zeroth_ifd = {
        piexif.ImageIFD.Make: u"Renkforce",
        # piexif.ImageIFD.XResolution: (3840, 1),
        # piexif.ImageIFD.YResolution: (2160, 1),
        piexif.ImageIFD.Software: u"piexif"
        }

        exif_ifd = {
        piexif.ExifIFD.DateTimeOriginal: str(datetime.datetime.now().strftime("%Y:%m:%d %H:%M:%S")),
        # piexif.ExifIFD.LensMake: u"LensMake",
        # piexif.ExifIFD.FocalLength: 2.5,
        # piexif.ExifIFD.Sharpness: 65535,
        piexif.ExifIFD.LensSpecification: ((1, 1), (1, 1), (1, 1), (1, 1)),
        }

        first_ifd = {
        piexif.ImageIFD.Make: u"Renkforce",
        # piexif.ImageIFD.XResolution: (3840, 1),
        # piexif.ImageIFD.YResolution: (2160, 1),
        piexif.ImageIFD.Software: u"piexif"
        # pixeif.ImageIFD.Orientation: ""
        }

        gps_ifd = {
        piexif.GPSIFD.GPSLatitudeRef: ChooseLatRef(lat),
        piexif.GPSIFD.GPSLatitude: degToDmsRational(lat),
        piexif.GPSIFD.GPSLongitudeRef: ChooseLonRef(lon),
        piexif.GPSIFD.GPSLongitude: degToDmsRational(lon),
        piexif.GPSIFD.GPSAltitudeRef: 0,
        piexif.GPSIFD.GPSAltitude: (int(abs(alt)*100),100)
        }

        exif_dict = {"0th":zeroth_ifd, "Exif":exif_ifd, "1st":first_ifd, "GPS":gps_ifd}
        exif_bytes = piexif.dump(exif_dict)

        filename = 'D:/UAV-Befliegungen/210904_zuHauseNebenan/04_ODM_no_PP_3/images/' + str(timestamp).replace(".", "_") + '.jpg'
        cv2.imwrite(filename, frame)

        im = Image.open(filename)
        im.save(filename, exif=exif_bytes)

    else:
        pass

vc.release()
# datei.close()
