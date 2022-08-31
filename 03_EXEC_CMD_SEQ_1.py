import dronekit
from dronekit import Command
from pymavlink import mavutil

# Datenfunkverbindung mittels MAV-Link-Protokoll aufbauen.
vehicle = dronekit.connect('com3', baud=57600, wait_ready=True)
print('vehicle connected')

# Im EEPROM-Speicher des Flugreglers gespeicherte Kommandos  als Liste abrufen.
cmds = vehicle.commands
# Im EEPROM-Speicher des Flugreglers gespeicherte Kommandos löschen.
cmds.clear()
# Warten bis Löschvorgang beendet.
cmds.wait_ready()
print('old commands cleared')

# Festsetzung der horizontalen Geschwindigkeit auf 2 m/s.
cmds.add(Command(0, 0, 0, mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT, \
mavutil.mavlink.MAV_CMD_DO_CHANGE_SPEED, 0, 0, 0, 2, 0, 0,  0, 0, 0))

# Takeoff auf 25 m über Grund.
cmds.add(Command(0, 0, 0, mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT, \
mavutil.mavlink.MAV_CMD_NAV_TAKEOFF, 0, 0, 0, 0, 0, 0, 0, 0, 25))

# Relais 1 für 3s einschalten, damit sich Stromkreis 1 der Kamera schließt
# und damit die Kamera eingeschaltet wird.
cmds.add(Command(0, 0, 0, mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT, \
mavutil.mavlink.MAV_CMD_DO_REPEAT_RELAY, 0, 0, 0, 1, 3, 0,  0, 0, 0))

# Die nach vorne ausgerichtete Kamera wird um 90°
# in Richtung Erdmassenschwerpunkt verdreht.
cmds.add(Command(0, 0, 0, mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT, \
mavutil.mavlink.MAV_CMD_DO_SET_SERVO, 0, 0, 7, 1987, 0, 0,  0, 0, 0))

# Ersten Wegpunkt anfliegen.
cmds.add(Command(0, 0, 0, mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT, \
mavutil.mavlink.MAV_CMD_NAV_WAYPOINT, 0, 0, 0, 0, 0, 0, \
51.573462111887764,  8.52425119274193, 25))

# Relais 2 für 1s einschalten, damit sich Stromkreis 2 an der Kamera schliesst
# und somit die Videoaufnahme gestartet wird.
cmds.add(Command(0, 0, 0, mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT, \
mavutil.mavlink.MAV_CMD_DO_REPEAT_RELAY, 0, 0,  1, 1, 1, 0,  0, 0, 0))

# Restliche Wegpunkte nacheinander anfliegen.
cmds.add(Command(0, 0, 0, mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT, \
mavutil.mavlink.MAV_CMD_NAV_WAYPOINT, 0, 0, 0, 0, 0, 0, \
51.57361421983368,  8.525672915782398, 25))
cmds.add(Command(0, 0, 0, mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT, \
mavutil.mavlink.MAV_CMD_NAV_WAYPOINT, 0, 0, 0, 0, 0, 0, \
51.573702838206344,  8.525648499307819, 25))
cmds.add(Command(0, 0, 0, mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT, \
mavutil.mavlink.MAV_CMD_NAV_WAYPOINT, 0, 0, 0, 0, 0, 0, \
51.57355072996008,  8.524226773588104, 25))
cmds.add(Command(0, 0, 0, mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT, \
mavutil.mavlink.MAV_CMD_NAV_WAYPOINT, 0, 0, 0, 0, 0, 0, \
51.573639348025765,  8.524202354338211, 25))
cmds.add(Command(0, 0, 0, mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT, \
mavutil.mavlink.MAV_CMD_NAV_WAYPOINT, 0, 0, 0, 0, 0, 0, \
51.57379145657235,  8.525624082737185, 25))
cmds.add(Command(0, 0, 0, mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT, \
mavutil.mavlink.MAV_CMD_NAV_WAYPOINT, 0, 0, 0, 0, 0, 0, \
51.573880074931694,  8.52559966607049, 25))
cmds.add(Command(0, 0, 0, mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT, \
mavutil.mavlink.MAV_CMD_NAV_WAYPOINT, 0, 0, 0, 0, 0, 0, \
51.57372796608475,  8.524177934992244, 25))
cmds.add(Command(0, 0, 0, mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT, \
mavutil.mavlink.MAV_CMD_NAV_WAYPOINT, 0, 0, 0, 0, 0, 0, \
51.573816584137106,  8.524153515550204, 25))
cmds.add(Command(0, 0, 0, mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT, \
mavutil.mavlink.MAV_CMD_NAV_WAYPOINT, 0, 0, 0, 0, 0, 0, \
51.57396869328438,  8.525575249307735, 25))
cmds.add(Command(0, 0, 0, mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT, \
mavutil.mavlink.MAV_CMD_NAV_WAYPOINT, 0, 0, 0, 0, 0, 0, \
51.57405731163038,  8.525550832448921, 25))
cmds.add(Command(0, 0, 0, mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT, \
mavutil.mavlink.MAV_CMD_NAV_WAYPOINT, 0, 0, 0, 0, 0, 0, \
51.57390520218277,  8.524129096012091, 25))

# Relais 2 für 1s einschalten, damit sich Stromkreis 2 an der Kamera schließt
# und somit die Videoaufnahme gestoppt wird.
cmds.add(Command(0, 0, 0, mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT, \
mavutil.mavlink.MAV_CMD_DO_REPEAT_RELAY, 0, 0, 1, 1, 1, 0,  0, 0, 0))

# alle folgenden DO-Kommandos erst in 4s ausführen.
cmds.add(Command(0, 0, 0, mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT, \
mavutil.mavlink.MAV_CMD_CONDITION_DELAY, 0, 0, 4, 0, 0, 0,  0, 0, 0))

# Relais 1 für 3s einschalten, damit sich Stromkreis 1 der Kamera schließt
# und damit die Kamera ausgeschaltet wird.
cmds.add(Command(0, 0, 0, mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT, \
mavutil.mavlink.MAV_CMD_DO_REPEAT_RELAY, 0, 0, 0, 1, 3, 0,  0, 0, 0))

# Die mit Objektiv nach unten ausgerichtete Kamera
# wird wieder in Richtung der Flugachse verdreht.
cmds.add(Command(0, 0, 0, mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT, \
mavutil.mavlink.MAV_CMD_DO_SET_SERVO, 0, 0,  7, 1507, 0, 0,  0, 0, 0))

# Rückflug zur Startposition.
cmds.add(Command(0, 0, 0, mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT, \
mavutil.mavlink.MAV_CMD_NAV_RETURN_TO_LAUNCH, 0, 0,  0, 0, 0, 0, 0, 0, 0))

# Landen.
cmds.add(Command(0, 0, 0, mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT, \
mavutil.mavlink.MAV_CMD_NAV_LAND, 0, 0,  0, 0, 0, 0, 0, 0, 0))

# Liste mit den Kommandos wird in den EEPROM-Speicher des Flugreglers geladen
# und dort gespeichert.
cmds.upload()
print('commands uploaded')

# Verbindungsdaten werden gelöscht und die Verbindung beendet.
vehicle.flush()
vehicle.close()
print('vehicle disconnected')
