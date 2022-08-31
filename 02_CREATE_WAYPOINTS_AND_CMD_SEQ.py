from qgis.core import QgsApplication
from qgis.core import QgsCoordinateReferenceSystem
from qgis.core import QgsCoordinateTransform
from qgis.core import QgsCoordinateTransformContext
from qgis.core import QgsFeature
from qgis.core import QgsFields
from qgis.core import QgsGeometry
from qgis.core import QgsPointXY
from qgis.core import QgsProject
from qgis.core import QgsVectorFileWriter
from qgis.core import QgsVectorLayer
from qgis.core import QgsWkbTypes
import math

# Verdrehwinkel der Flugachsen, wird zurückgegeben.
def get_angle(bbox_angle, bbox_width, bbox_height):
    if bbox_height > bbox_width:
        return 90 - bbox_angle
    else:
        return bbox_angle

# Längere Rechteckseite (=1. Flugachse), wird zurückgegeben.
def get_line(bbox_width, bbox_height):
    if bbox_height > bbox_width:
        return bbox_height
    else:
        return bbox_width

# Anzahl anzulegender Flugachsen, wird zurückgegeben.
def get_line_count(line_spacing, bbox_width, bbox_height):
    if bbox_height > bbox_width:
        return (int(bbox_width/line_spacing)+2) * 2
    else:
        return (int(bbox_height/line_spacing)+2) * 2

# Koordinaten von WP1, werden zurückgegeben.
def get_WP1(angle, bbox, height_agl):
    WP = QgsPointXY()
    # Festsetzung, ob Rechteck-Längsseite näher an der x-Koordinatenachse (=True)
    # oder y-Koordinatenachse (=False) ausgerichtet ist.
    x_oriented = True
    if x_oriented:
        # Liste zur Speicherung der Geometriestützpunkte.
        pt_list = []
        #Schleife durch die Geometriestützpunkte.
        for vertex in bbox.vertices():
            x = vertex.x() # X-Koordinate von Stützpunkt.
            y = vertex.y() # Y-Koordinate von Stützpunkt.
            pt_list.append([y, x])
        # Punkt mit kleinster Y-Koordinate wird abgerufen.
        wp_coords = min(pt_list)
        WP.setX(wp_coords[1])
        WP.setY(wp_coords[0])
    else:
        # Liste zur Speicherung der Geometriestützpunkte.
        pt_list = []
        for vertex in bbox1.vertices():
            x = vertex.x() # X-Koordinate von Stützpunkt.
            y = vertex.y() # Y-Koordinate von Stützpunkt.
            pt_list.append([x, y])
        # Punkt mit kleinster X-Koordinate wird abgerufen.
        wp_coords = min(pt_list)
        WP.setX(wp_coords[0]) # X-Koordinate von WP1 wird gesetzt.
        WP.setY(wp_coords[1]) # Y-Koordinate von WP1 wird gesetzt.
    return WP

def calculate_wp(WP1, angle, line, line_spacing, line_count, height_agl, writer):
    # Dicitionary zur Speicherung der Wegpunkte
    # (Schlüssel: Bezeichner (z. B. "WP1"), Wert: WGS84-Koordinaten)
    wp_dictio = {}

    x =  WP1.x() # X-Koordinate von Wegpunkt 1.
    y =  WP1.y() # Y-Koordinate von Wegpunkt 1.

    crsSrc  = QgsCoordinateReferenceSystem(25832) # Quell-Koordinatensystem.
    crsDest = QgsCoordinateReferenceSystem(4326)  # Ziel-Koordinatensystem.
    xform   = QgsCoordinateTransform(crsSrc, crsDest, QgsProject.instance())

    # Koordinatentransformation von EPSG 25832 nach EPSG 4326 (WGS84)
    WP1 = xform.transform(WP1, QgsCoordinateTransform.ForwardTransform)
    # Wegpunkt 1 wird in Dicitionary gespeichert.
    wp_dictio["WP1"] = [WP1.x(), WP1.y()]

    wp_counter = 2

    while wp_counter <= line_count:
        # Falls WP Ende einer langen Flugachse bildet.
        if wp_counter % 2 == 0:
            # Falls WP Ende einer antiparall verlaufenden Flugachse bildet.
            if wp_counter % 4 == 0:
                x -= math.cos(math.radians(angle)) * line
                y -= math.sin(math.radians(angle)) * line
            else:
                x += math.cos(math.radians(angle)) * line
                y += math.sin(math.radians(angle)) * line
        else:
            x -= math.sin(math.radians(angle)) * line_spacing
            y += math.cos(math.radians(angle)) * line_spacing

        WP = QgsPointXY()
        WP.setX(x) # X-Koordinate von Wegpunkt n wird gesetzt.
        WP.setY(y) # Y-Koordinate von Wegpunkt n wird gesetzt.
        WP_f = QgsFeature()
        WP_f.setGeometry(WP) # Punkt-Vektorgeometrie von WP n wird erstellt.
        writer.addFeature(WP_f)

        WP_Nr = "WP" + str(wp_counter)
        # Koordinatentransformation von EPSG 25832
        # nach EPSG 4326 (WGS84)
        pt1 = xform.transform(QgsPointXY(x,y))

        # Wegpunkt n wird in Dicitionary gespeichert.
        wp_dictio[WP_Nr] = [pt1.x(), pt1.y()]

        wp_counter += 1

    return wp_dictio

# Pfad zum qgis-Installationsort wird angeben.
QgsApplication.setPrefixPath('C:/software/QGIS_3_16/apps/qgis-ltr', True)

# Ausschalten der QGIS-GUI.
qgs = QgsApplication([], False)

# QGIS-Ressourcen werden geladen.
qgs.initQgis()

# Angabe Flugachsenabstand (A) in m
line_spacing = 10

# Angabe Flughöhe über Grund (h) in m
height_agl   = 25

save_options = QgsVectorFileWriter.SaveVectorOptions()
save_options.driverName   = "ESRI Shapefile"
save_options.fileEncoding = "UTF-8"

writer = QgsVectorFileWriter.create(
    "D:/GIS/Missions/shp/points.shp",
    QgsFields(),
    QgsWkbTypes.Point,
    QgsCoordinateReferenceSystem("EPSG:25832"),
    QgsCoordinateTransformContext(),
    save_options
)

# AOI (zu überfliegender Bereich) wird als Vektorgeometrie-Layer geladen.
path        = "D:/GIS/Missions/shp/Unrechteck.shp"
baseName    = "Unrechteck"
providerLib = "ogr"
AOI         = QgsVectorLayer(path, baseName, providerLib)

# AOI wird als Objekt der Klasse QgsFeature instanziiert.
features    = AOI.getFeatures()

for feature in features:
    # AOI-Geometrie wird als Objekt der Klasse QgsGeometry abgefragt.
    geom = feature.geometry()

    # Abfrage des nach Flächeninhalt kleinsten minimal umgebenden Rechtecks
    # um die AOI-Geometrie (Fläche, die in Flugmission 1 überflogen wird).
    bbox1        = geom.orientedMinimumBoundingBox()[0] # Rechteckgeometrie
    bbox1_area   = geom.orientedMinimumBoundingBox()[1] # Rechteckfläche
    bbox1_angle  = geom.orientedMinimumBoundingBox()[2] # Verdrehwinkel
    bbox1_width  = geom.orientedMinimumBoundingBox()[3] # Rechteckweite
    bbox1_height = geom.orientedMinimumBoundingBox()[4] # Rechteckhöhe

    # Verdrehwinkel der Flugachsen.
    angle      = get_angle(bbox1_angle, bbox1_width, bbox1_height)
    # Längere Rechteckseite (=1. Flugachse).
    line       = get_line(bbox1_width, bbox1_height)
    # Anzahl anzulegender Flugachsen.
    line_count = get_line_count(line_spacing, bbox1_width, bbox1_height)

    WP1 =  get_WP1(bbox1_angle, bbox1, height_agl)
    WP1_f = QgsFeature()
    # Punkt-Vektorgeometrie von WP 1 wird erstellt.
    WP1_f.setGeometry(QgsGeometry.fromQPointF(WP1.toQPointF()))
    writer.addFeature(WP1_f)

    # Alle weiteren Wegpunkte von Flugmission 1 werden berechnet
    # und in einer Dictionary (wps1) gespeichert.
    wps1 = calculate_wp(WP1, angle, line, line_spacing, line_count, height_agl, writer)

    # Rotation der BoundingBox um 25°.
    geom2    = bbox1
    geom2.rotate(-25, geom2.centroid().asPoint())

    # Abfrage des nach Flächeninhalt kleinsten minimal umgebenden Rechtecks
    # um die verdrehte AOI-Geometrie (Fläche, die in Flugmission 2 überflogen wird)
    bbox2        = geom2.orientedMinimumBoundingBox()[0] # Rechteckgeometrie
    bbox2_area   = geom2.orientedMinimumBoundingBox()[1] # Rechteckfläche
    bbox2_angle  = geom2.orientedMinimumBoundingBox()[2] # Verdrehwinkel
    bbox2_width  = geom2.orientedMinimumBoundingBox()[3] # Rechteckweite
    bbox2_height = geom2.orientedMinimumBoundingBox()[4] # Rechteckhöhe

    # Verdrehwinkel der Flugachsen.
    angle      = get_angle(bbox2_angle, bbox2_width, bbox2_height)
    # Längere Rechteckseite (=1. Flugachse).
    line       = get_line(bbox2_width, bbox2_height)
    # Anzahl anzulegender Flugachsen.
    line_count = get_line_count(line_spacing, bbox2_width, bbox2_height)

    WP2 =  get_WP1(bbox2_angle, bbox2, height_agl)
    WP2_f = QgsFeature()
    # Punkt-Vektorgeometrie von WP 2 wird erstellt.
    WP2_f.setGeometry(QgsGeometry.fromQPointF(WP1.toQPointF()))
    writer.addFeature(WP2_f)

    # Alle weiteren Wegpunkte von Flugmission 2 werden berechnet
    # und in einer Dictionary (wps1) gespeichert.
    wps2 = calculate_wp(WP2, angle, line, line_spacing, line_count, \
    height_agl, writer)

del writer
features.close()

print(wps1)
print(wps2)

# Provider- und Layer-Registrierungen werden aus Arbeitsspeicher gelöscht.
qgs.exitQgis()

################################################################################
py_file = open("D:/py/03_EXEC_CMD_SEQ_1.py", "w")

s = ""

s += "import dronekit\n"
s += "from dronekit import connect\n"
s += "from pymavlink import mavutil\n\n"

s += "vehicle = dronekit.connect('com3', baud=57600, wait_ready=True)\n"
s += "print('vehicle connected')\n\n"

s += "cmds = vehicle.commands\n"
s += "cmds.clear()\n"
s += "cmds.wait_ready()\n"
s += "print('old commands cleared')\n\n"

s += "cmds.add(Command(0, 0, 0, mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT, "
s += "mavutil.mavlink.MAV_CMD_DO_CHANGE_SPEED, 0, 0, 0, 2, 0, 0,  0, 0, 0))\n"
s += "cmds.add(Command(0, 0, 0, mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT, "
s += "mavutil.mavlink.MAV_CMD_NAV_TAKEOFF, \n"
s += "0, 0, 0, 0, 0, 0, 0, 0, {}))\n".format(height_agl)
s += "cmds.add(Command(0, 0, 0, mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT, "
s += "mavutil.mavlink.MAV_CMD_DO_REPEAT_RELAY, 0, 0, 0, 1, 3, 0,  0, 0, 0))\n"
s += "cmds.add(Command(0, 0, 0, mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT, "
s += "mavutil.mavlink.MAV_CMD_DO_SET_SERVO, 0, 0, 7, 1987, 0, 0,  0, 0, 0))\n"

counter = 1
for wp in wps1.values():
    print(wp)
    if counter == 2:
        s += "cmds.add(Command(0, 0, 0, " + \
        "mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT, " + \
        "mavutil.mavlink.MAV_CMD_DO_REPEAT_RELAY, 0, 0,  1, 1, 1, 0,  0, 0, 0))\n"
        s += "cmds.add(Command(0, 0, 0, " + \
        "mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT, " + \
        "mavutil.mavlink.MAV_CMD_NAV_WAYPOINT, "
        "0, 0, 0, 0, 0, 0, {},  {}, {}))\n".format(wp[1], wp[0], height_agl)
    else:
        s += "cmds.add(Command(0, 0, 0, " + \
        "mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT, " + \
        "mavutil.mavlink.MAV_CMD_NAV_WAYPOINT, "
        "0, 0, 0, 0, 0, 0, {},  {}, {}))\n".format(wp[1], wp[0], height_agl))
    counter += 1

s += "cmds.add(Command(0, 0, 0, mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT, "
s += "mavutil.mavlink.MAV_CMD_DO_REPEAT_RELAY, 0, 0, 1, 1, 1, 0,  0, 0, 0))\n"
s += "cmds.add(Command(0, 0, 0, mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT, "
s += "mavutil.mavlink.MAV_CMD_CONDITION_DELAY, 0, 0, 4, 0, 0, 0,  0, 0, 0))\n"
s += "cmds.add(Command(0, 0, 0, mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT, "
s += "mavutil.mavlink.MAV_CMD_DO_REPEAT_RELAY, 0, 0, 0, 1, 3, 0,  0, 0, 0))\n"
s += "cmds.add(Command(0, 0, 0, mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT, "
s += "mavutil.mavlink.MAV_CMD_DO_SET_SERVO, 0, 0,  7, 1507, 0, 0,  0, 0, 0))\n"
s += "cmds.add(Command(0, 0, 0, mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT, "
s += "mavutil.mavlink.MAV_CMD_NAV_RETURN_TO_LAUNCH, 0, 0,  0, 0, 0, 0, 0, 0, 0))\n"
s += "cmds.add(Command(0, 0, 0, mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT, "
s += "mavutil.mavlink.MAV_CMD_NAV_LAND, 0, 0,  0, 0, 0, 0, 0, 0, 0))\n\n"

s += "cmds.upload()\n"
s += "print('commands uploaded')\n\n"

s += "vehicle.flush()\n"
s += "vehicle.close()\n"
s += "print('vehicle disconnected')"

py_file.write(s)
py_file.close()

################################################################################
py_file = open("D:/py/03_EXEC_CMD_SEQ_2.py", "w")

s = ""

s += "import dronekit\n"
s += "from dronekit import Command\n"
s += "from pymavlink import mavutil\n\n"

s += "vehicle = dronekit.connect('com3', baud=57600, wait_ready=True)\n"
s += "print('vehicle connected')\n\n"

s += "cmds = vehicle.commands\n"
s += "cmds.clear()\n"
s += "cmds.wait_ready()\n"
s += "print('old commands cleared')\n\n"

s += "cmds.add(Command(0, 0, 0, mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT, "
s += "mavutil.mavlink.MAV_CMD_DO_CHANGE_SPEED, 0, 0, 0, 2, 0, 0,  0, 0, 0))\n"
s += "cmds.add(Command(0, 0, 0, mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT, "
s += "mavutil.mavlink.MAV_CMD_NAV_TAKEOFF, \n"
s += "0, 0, 0, 0, 0, 0, 0, 0, {}))\n".format(height_agl)
s += "cmds.add(Command(0, 0, 0, mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT, "
s += "mavutil.mavlink.MAV_CMD_DO_REPEAT_RELAY, 0, 0, 0, 1, 3, 0,  0, 0, 0))\n"
s += "cmds.add(Command(0, 0, 0, mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT, "
s += "mavutil.mavlink.MAV_CMD_DO_SET_SERVO, 0, 0, 7, 1987, 0, 0,  0, 0, 0))\n"

counter = 1
for wp in wps2.values():
    print(wp)
    if counter == 2:
        s += "cmds.add(Command(0, 0, 0, " + \
        "mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT, " + \
        "mavutil.mavlink.MAV_CMD_DO_REPEAT_RELAY, 0, 0,  1, 1, 1, 0,  0, 0, 0))\n"
        s += "cmds.add(Command(0, 0, 0, " + \
        "mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT, " + \
        "mavutil.mavlink.MAV_CMD_NAV_WAYPOINT, "
        "0, 0, 0, 0, 0, 0, {},  {}, {}))\n".format(wp[1], wp[0], height_agl)
    else:
        s += "cmds.add(Command(0, 0, 0, " + \
        "mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT, " + \
        "mavutil.mavlink.MAV_CMD_NAV_WAYPOINT, "
        "0, 0, 0, 0, 0, 0, {},  {}, {}))\n".format(wp[1], wp[0], height_agl))
    counter += 1

s += "cmds.add(Command(0, 0, 0, mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT, "
s += "mavutil.mavlink.MAV_CMD_DO_REPEAT_RELAY, 0, 0, 1, 1, 1, 0,  0, 0, 0))\n"
s += "cmds.add(Command(0, 0, 0, mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT, "
s += "mavutil.mavlink.MAV_CMD_CONDITION_DELAY, 0, 0, 4, 0, 0, 0,  0, 0, 0))\n"
s += "cmds.add(Command(0, 0, 0, mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT, "
s += "mavutil.mavlink.MAV_CMD_DO_REPEAT_RELAY, 0, 0, 0, 1, 3, 0,  0, 0, 0))\n"
s += "cmds.add(Command(0, 0, 0, mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT, "
s += "mavutil.mavlink.MAV_CMD_DO_SET_SERVO, 0, 0,  7, 1507, 0, 0,  0, 0, 0))\n"
s += "cmds.add(Command(0, 0, 0, mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT, "
s += "mavutil.mavlink.MAV_CMD_NAV_RETURN_TO_LAUNCH, 0, 0,  0, 0, 0, 0, 0, 0, 0))\n"
s += "cmds.add(Command(0, 0, 0, mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT, "
s += "mavutil.mavlink.MAV_CMD_NAV_LAND, 0, 0,  0, 0, 0, 0, 0, 0, 0))\n\n"

s += "cmds.upload()\n"
s += "print('commands uploaded')\n\n"

s += "vehicle.flush()\n"
s += "vehicle.close()\n"
s += "print('vehicle disconnected')"

py_file.write(s)
py_file.close()
