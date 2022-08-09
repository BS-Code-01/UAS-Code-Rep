import sys
newpath = r"C:\software\QGIS_3_16\apps\qgis-ltr\.\python"
sys.path.append(newpath)

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

def get_angle(bbox_angle, bbox_width, bbox_height):
    if bbox_height > bbox_width:
        return 90 - bbox_angle
    else:
        return bbox_angle

def get_line(bbox_width, bbox_height):
    if bbox_height > bbox_width:
        return bbox_height
    else:
        return bbox_width

def get_line_count(line_spacing, bbox_width, bbox_height):
    if bbox_height > bbox_width:
        return (int(bbox_width/line_spacing)+2) * 2
    else:
        return (int(bbox_height/line_spacing)+2) * 2

def get_WP1(angle, bbox, height_agl):
    WP = QgsPointXY()
    x_oriented = True
    if x_oriented:
        pt_list = []
        for vertex in bbox.vertices():
            x = vertex.x()
            y = vertex.y()
            pt_list.append([y, x])
        wp_coords = min(pt_list)
        WP.setX(wp_coords[1])
        WP.setY(wp_coords[0])
    else:
        pt_list = []
        for vertex in bbox1.vertices():
            x = vertex.x()
            y = vertex.y()
            pt_list.append([x, y])
        wp_coords = min(pt_list)
        WP.setX(wp_coords[0])
        WP.setY(wp_coords[1])
    return WP

def calculate_wp(WP1, angle, line, line_spacing, line_count, height_agl, writer):
    wp_dictio = {}

    x =  WP1.x()
    y =  WP1.y()

    crsSrc  = QgsCoordinateReferenceSystem(25832)
    crsDest = QgsCoordinateReferenceSystem(4326)
    xform   = QgsCoordinateTransform(crsSrc, crsDest, QgsProject.instance())

    WP1 = xform.transform(WP1, QgsCoordinateTransform.ForwardTransform)
    wp_dictio["WP1"] = [WP1.x(), WP1.y()]

    wp_counter = 2

    while wp_counter <= line_count:
        if wp_counter % 2 == 0:
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
        WP.setX(x)
        WP.setY(y)
        # WP_f = QgsFeature()
        # WP_f.setGeometry(WP)
        # writer.addFeature(WP_f)

        WP_Nr = "WP" + str(wp_counter)
        pt1 = xform.transform(QgsPointXY(x,y))


        wp_dictio[WP_Nr] = [pt1.x(), pt1.y()]

        wp_counter += 1

    return wp_dictio

# Supply path to qgis install location
QgsApplication.setPrefixPath('C:/software/QGIS_3_16/apps/qgis-ltr', True)

# second argument to False disables the GUI.
qgs = QgsApplication([], False)

# Load providers
qgs.initQgis()

line_spacing = 10
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

path        = "D:/GIS/Missions/shp/Unrechteck.shp"
baseName    = "Unrechteck"
providerLib = "ogr"
AOI         = QgsVectorLayer(path, baseName, providerLib)
features    = AOI.getFeatures()

for feature in features:
    geom = feature.geometry()

    bbox1        = geom.orientedMinimumBoundingBox()[0]
    bbox1_area   = geom.orientedMinimumBoundingBox()[1]
    bbox1_angle  = geom.orientedMinimumBoundingBox()[2]
    bbox1_width  = geom.orientedMinimumBoundingBox()[3]
    bbox1_height = geom.orientedMinimumBoundingBox()[4]

    angle      = get_angle(bbox1_angle, bbox1_width, bbox1_height)
    line       = get_line(bbox1_width, bbox1_height)
    line_count = get_line_count(line_spacing, bbox1_width, bbox1_height)

    WP1 =  get_WP1(bbox1_angle, bbox1, height_agl)
    WP1_f = QgsFeature()
    WP1_f.setGeometry(QgsGeometry.fromQPointF(WP1.toQPointF()))
    writer.addFeature(WP1_f)

    wps1 = calculate_wp(WP1, angle, line, line_spacing, line_count, height_agl, writer)

    geom2    = bbox1
    geom2.rotate(-25, geom2.centroid().asPoint())

    bbox2        = geom2.orientedMinimumBoundingBox()[0]
    bbox2_area   = geom2.orientedMinimumBoundingBox()[1]
    bbox2_angle  = geom2.orientedMinimumBoundingBox()[2]
    bbox2_width  = geom2.orientedMinimumBoundingBox()[3]
    bbox2_height = geom2.orientedMinimumBoundingBox()[4]

    angle      = get_angle(bbox2_angle, bbox2_width, bbox2_height)
    line       = get_line(bbox2_width, bbox2_height)
    line_count = get_line_count(line_spacing, bbox2_width, bbox2_height)

    WP2 =  get_WP1(bbox2_angle, bbox2, height_agl)
    WP2_f = QgsFeature()
    WP2_f.setGeometry(QgsGeometry.fromQPointF(WP1.toQPointF()))
    writer.addFeature(WP2_f)

    wps2 = calculate_wp(WP2, angle, line, line_spacing, line_count, height_agl, writer)

del writer
features.close()

print(wps1)
print(wps2)

qgs.exitQgis()

################################################################################
py_file = open("D:/temp00_Masterarbeit/py_2/03_EXEC_CMD_SEQ_1.py", "w")

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
s += "mavutil.mavlink.MAV_CMD_NAV_TAKEOFF, 0, 0, 0, 0, 0, 0, 0, 0, {}))\n".format(height_agl)
s += "cmds.add(Command(0, 0, 0, mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT, "
s += "mavutil.mavlink.MAV_CMD_DO_REPEAT_RELAY, 0, 0, 0, 1, 3, 0,  0, 0, 0))\n"
s += "cmds.add(Command(0, 0, 0, mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT, "
s += "mavutil.mavlink.MAV_CMD_DO_SET_SERVO, 0, 0, 7, 1987, 0, 0,  0, 0, 0))\n"

counter = 1
for wp in wps1.values():
    print(wp)
    if counter == 2:
        s += "cmds.add(Command(0, 0, 0, mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT, " + \
        "mavutil.mavlink.MAV_CMD_DO_REPEAT_RELAY, 0, 0,  1, 1, 1, 0,  0, 0, 0))\n"
        s += "cmds.add(Command(0, 0, 0, mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT, " + \
        "mavutil.mavlink.MAV_CMD_NAV_WAYPOINT, 0, 0, 0, 0, 0, 0, {},  {}, {}))\n".format(wp[1], wp[0], height_agl)
    else:
        s += "cmds.add(Command(0, 0, 0, mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT, " + \
        "mavutil.mavlink.MAV_CMD_NAV_WAYPOINT, 0, 0, 0, 0, 0, 0, {},  {}, {}))\n".format(wp[1], wp[0], height_agl)
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
py_file = open("D:/temp00_Masterarbeit/py_2/03_EXEC_CMD_SEQ_2.py", "w")

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
s += "mavutil.mavlink.MAV_CMD_NAV_TAKEOFF, 0, 0, 0, 0, 0, 0, 0, 0, {}))\n".format(height_agl)
s += "cmds.add(Command(0, 0, 0, mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT, "
s += "mavutil.mavlink.MAV_CMD_DO_REPEAT_RELAY, 0, 0, 0, 1, 3, 0,  0, 0, 0))\n"
s += "cmds.add(Command(0, 0, 0, mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT, "
s += "mavutil.mavlink.MAV_CMD_DO_SET_SERVO, 0, 0, 7, 1987, 0, 0,  0, 0, 0))\n"

counter = 1
for wp in wps2.values():
    print(wp)
    if counter == 2:
        s += "cmds.add(Command(0, 0, 0, mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT, " + \
        "mavutil.mavlink.MAV_CMD_DO_REPEAT_RELAY, 0, 0,  1, 1, 1, 0,  0, 0, 0))\n"
        s += "cmds.add(Command(0, 0, 0, mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT, " + \
        "mavutil.mavlink.MAV_CMD_NAV_WAYPOINT, 0, 0, 0, 0, 0, 0, {},  {}, {}))\n".format(wp[1], wp[0], height_agl)
    else:
        s += "cmds.add(Command(0, 0, 0, mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT, " + \
        "mavutil.mavlink.MAV_CMD_NAV_WAYPOINT, 0, 0, 0, 0, 0, 0, {},  {}, {}))\n".format(wp[1], wp[0], height_agl)
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
