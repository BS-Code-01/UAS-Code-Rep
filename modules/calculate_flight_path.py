class CalculateFlightPath():
    # Festlegung der Kamerakonstanten
    def __init__ (self, sensor_width, image_width, focal_length):
        # Sensorweite (mm)
        self.sensor_width = sensor_width
        # Bildweite (px)
        self.image_width  = image_width
        # Brennweite  (mm)
        self.focal_length = focal_length

    # Gibt die Flughöhe zurück
    def calculate_flight_altitude(self, GSD):
        # Berechnung der Flughöhe, abhängig von der gewählten GSD
        self.flight_altitude = \
        (self.image_width * GSD * self.focal_length)\
         / (self.sensor_width * 1000)
        # Rückgabe der Flughöhe
        return int(round(self.flight_altitude, 0))

    # Gibt den Fluglinienabstand zurück
    def calculate_line_spacing(\
    self, flight_altitude, overlap, angular_aperture):
        import math

		# Flughöhe über Grund (m)
        self.flight_altitude = flight_altitude
        # geplante Querüberlappung (%)
        self.overlap = overlap/100
        # Kamera-Öffnungswinkel (Grad)
        self.angular_aperture = angular_aperture

        # Berechnung der beiden anderen Dreieckswinkel
        self.angle_alpha = (180-self.angular_aperture)/2
        self.angle_beta  = self.angle_alpha

		# Sinus von alpha und beta
        self.sin_alpha = math.sin(math.radians(self.angle_alpha))
        self.sin_beta  = self.sin_alpha
        # Berechnung der langen Dreieckseiten
        self.side_a = self.flight_altitude / self.sin_alpha
        self.side_b = self.side_a
        # Berechnung der Dreiecksbasis und damit der Aufnahmenbreite
        # mit dem Kosinussatz
        self.baseline = math.sqrt((self.side_a*self.side_a)+\
        (self.side_b*self.side_b)\
        -(2*self.side_a*self.side_a*\
        math.cos((math.radians(self.angular_aperture)))))
        print(self.baseline)

        # Berechnung des Flugachsenabstands
        self.line_spacing = self.baseline * (1 - self.overlap)
        print(self.line_spacing)
        # Rückgabe des Flugachsenabstands
        return round(self.line_spacing)
