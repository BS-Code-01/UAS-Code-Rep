class RinexFile():

    def __init__ (self, rinexfile, GRXH_GRXS_values):
        self.rinexfile = rinexfile
        self.GRXH_GRXS_values = GRXH_GRXS_values
        return

    def __del__(self):
        del self.rinexfile, self.GRXH_GRXS_values
        return

    def create_RINEX_header(self):
        # header-variables
        RINEX_VERSION =    "3.03"
        FILETYPE =         "OBSERVATION DATA"
        SATELLITE_SYSTEM = "M (MIXED)"
        PGM =              "RINEX_CREATOR_BY_STRATMANN"
        RUN_BY =           "STRATMANN"
        DATE =             "STRATMANN"
        MARKER_NAME =      "UBLOX_M8T_ON_QUADROCOPTER"

        rinex_headerlinestring = \
        "     3.05           OBSERVATION DATA    M (MIXED)           " + \
        "RINEX VERSION / TYPE" + "\n" + \
        "RINEX_CREATOR_BY_STRATMANN  STRATMANN       20210206 134313 " + \
        "LCL PGM / RUN BY / DATE" + "\n" + \
        "UBLOX_M8T_ON_QUADROCOPTER                                   " + \
        "MARKER NAME" + "\n" + \
        "                                                            " + \
        "OBSERVER / AGENCY" + "\n" + \
        "3022589             SEPT POLARX5        5.3.2               " + \
        "REC # / TYPE / VERS" + "\n" + \
        "727178              LEIAR25.R4      LEIT                    " + \
        "ANT # / TYPE" + "\n" + \
        "  3928425.8707   588854.8559  4973725.6959                  " + \
        "APPROX POSITION XYZ" + "\n" + \
        "        0.0000        0.0000        0.0000                  " + \
        "ANTENNA: DELTA H/E/N" + "\n" + \
        "G    4 C1C L1C D1C S1C                                      " + \
        "SYS / # / OBS TYPES" + "\n" + \
        "R    4 C1C L1C D1C S1C                                      " + \
        "SYS / # / OBS TYPES" + "\n" + \
        "DBHZ                                                        " + \
        "SIGNAL STRENGTH UNIT" + "\n" + \
        "     1                                                      " + \
        "INTERVAL" + "\n" + \
        "2021    04    30    12    03   55.0000000     GPS           " + \
        "TIME OF FIRST OBS" + "\n" + \
        "2021    04    30    12    05   36.0000000     GPS           " + \
        "TIME OF LAST OBS" + "\n" + \
        "                                                            " + \
        "GLONASS COD/PHS/BIS" + "\n" + \
        "    18    18  1929     7                                    " + \
        "LEAP SECONDS" + "\n" + \
        "                                                            " + \
        "END OF HEADER" + "\n"

        return rinex_headerlinestring

    def create_RINEX_body(self):
        from moduls.time_format_converter import TimeFormatConverter as TFC

        # Der gesamt Body wird als Zeichenkette gespeichert
        # und besteht am Anfang aus 0 Zeichen.
        rinex_body_linestring = ""

        # Indizes der Elemente der UBX-RXM-RAWX-Header-Nachrichten (GRXH)
        # receiver TimeOfWeek measurement
        rcvTime_ix = 0
        # GPS week
        week_ix = 1
        # GPS leap seconds
        leapS_ix = 2
        # number of space-vehicle measurements to follow
        numMeas_ix = 3
        # receiver tracking status bitfield
        recStat_ix = 4

        # Indizes der Elemente der UBX-RXM-RAWX-Payload-Nachrichten (GRXS)
        # Pseudorange measurement
        prMes_ix = 0
        # Carrier phase measurement
        cpMes_ix = 1
        # Doppler measurement
        doMes_ix = 2
        # GNSS identifier
        gnss_ix = 3
        # Satellite identifier
        sv_ix = 4
        # GLONASS frequency slot
        freq_ix = 5
        # carrier phase locktime counter
        lock_ix = 6
        # carrier-to-noise density ratio
        cno_ix = 7
        # estimated pseudorange measurement standard deviation
        prD_ix = 8
        # estimated carrier phase measurement standard deviation
        cpD_ix = 9
        # estimated Doppler measurement standard deviation
        doD_ix = 10
        # tracking status bitfield
        trk_ix = 11

        gnssId_dictio = {
        0 : "G", # GPS
        1 : "S", # SBAS
        2 : "E", # Galileo
        3 : "C", # BeiDou
        4 : "I", # IRNSS
        5 : "J", # QZSS
        6 : "R"  # GLONASS
        }

        # Schleife durch die Dictionary in der die UBX-RXM-RAWX-Nachrichten
        # den System-Zeitstempeln zugeordnet sind. Es werden die Werte
        # (values), also die Listen mit den GRXH- bzw. GRXS-Nachrichten
        # aufgerufen.
        for value in self.GRXH_GRXS_values.values():

            # Das erste Element der Liste, die einer Systemzeit zugeordnet
            # ist, ist immer die GRXH-message.
            GRXH_message = value[0]

            # Abfrage der GPS-Woche, die in der GRXH-message enthalten ist,
            # und Umwandlung in eine Ganzzahl.
            gpsweek = int(GRXH_message[week_ix])

            # Abfrage der Empfänger-Zeit (Sekunde der GPS-Woche),
            # die in der GRXH-message enthalten ist,
            # und Umwandlung in eine Fließkommazahl.
            gpsseconds = float(GRXH_message[rcvTime_ix])

            # Abfrage des GPS-Schaltsekunden-Werts, der in der GRXH-message
            # enthalten ist, und Umwandlung in eine Ganzzahl.
            # TODO: Klären warum Leapseconds nicht nötig sind
            # leapseconds = int(GRXH_message[leapS_ix])
            leapseconds = 0

            # Abfrage der in der GRXH-message enthaltenen Anzahl der als
            # GRXS-message folgenden Satellitenbeobachtungen
            # und Umwandlung in eine Ganzzahl.
            numMeas = int(GRXH_message[numMeas_ix])

            # Rechnet die GPS-Zeitgrößen GPS-Woche, GPS-Sekunden und
            # Schaltsekunden in die UTC-Zeit (Datum und Uhrzeit in
            # Mikrosekundengenauigkeit) um und wandelt diese
            # in eine Zeichenkette um.
            observation_date_str = \
            TFC.weeks_and_seconds_to_utc(gpsweek, gpsseconds, leapseconds)

            # Verkettung des Record identifiers (">"),
            # der UTC-Zeit (Jahr, Monat, Tag, Stunde, Minute, Sekunde),
            # der Epoch-Flag (0:OK, 1: power failure between previous and
            # current epoch, >1:Special event) und der Anzahl der in der
            # aktuellen Epoche beobachteten Satelliten.
            rinex_body_linestring += "> " + str(observation_date_str) \
            + " 0 " + str(numMeas) + "\n"

            # Das zweite und alle folgenden Elemente der Liste, die einer
            # Systemzeit zugeordnet sind, sind immer GRXS-messages.
            GRXS_messages = value[1:]

            # Sequenzielles Aufrufen aller GRXS-messages
            # in der der Systemzeit zugeordneten Liste.
            for entry in GRXS_messages:

                # Abfrage der gnssid (z. B. 0=G=GPS; 6=R=GLONASS)
                # und Umwandlung in eine Ganzzahl
                gnssId = int(entry[gnss_ix])

                # Abfrage der ID des Satelliten
                # und Umwandlung in eine Ganzzahl um Bedingung zu prüfen.
                if int(entry[sv_ix]) <= 9:
                    # Voranstellen einer führenden 0
                    svId = "0" + entry[sv_ix]
                else:
                    svId = entry[sv_ix]

                # Konstruktion der Satellitennummer durch Verkettung
                # der GNSS-Kennung (z. B. G=GPS; R=GLONASS)
                # und der Satellitenummer (z. B. 27). Beispiel: G27.
                sat_number = gnssId_dictio[gnssId] + svId

                # Abfrage der Pseudorange-Messung aus der GRXS-Nachricht,
                # Umwandlung in eine Fließkommazahl und anschließende
                # Umwandlung in eine Zeichenkette, wobei der
                # Pseudorange-Wert immer genau 14 Zeichenstellen mit
                # 5 Nachkommastellen aufweist. Fehlende Stellen vor dem
                # Komma werden mit Nullen aufgefüllt.
                prMes = "{:.5f}".format(float(entry[prMes_ix])).zfill(14)

                # Abfrage der Trägerphasen-Messung aus der GRXS-Nachricht,
                # Umwandlung in eine Fließkommazahl und anschließende
                # Umwandlung in eine Zeichenkette, wobei der
                # Trägerphasen-Messungs-Wert immer genau 13 Zeichenstellen
                # mit 3 Nachkommastellen aufweist. Fehlende Stellen vor dem
                # Komma werden mit Nullen aufgefüllt.
                cpMes = "{:.3f}".format(float(entry[cpMes_ix])).zfill(13)

                # Abfrage der Doppler-Frequenzverschiebung-Messung aus der
                # GRXS-Nachricht.
                # Umwandlung in eine Fließkommazahl und anschließende
                # Umwandlung in eine Zeichenkette, wobei der Wert
                # immer genau 3 Nachkommastellen aufweist.
                doMes = "{:.3f}".format(float(entry[doMes_ix]))
                # Zur rechtsbündigen Ausrichtung der Werte in der
                # RINEX-Datei werden der Zeichenketten, antiproportional
                # zur Länge, Leerzeichen vorangestellt.
                doMes = ((16-len(doMes)) * " ") + doMes

                # Abfrage des Signal-Rausch-Verhältnisses aus der
                # GRXS-Nachricht,
                # Umwandlung in eine Fließkommazahl und anschließende
                # Umwandlung in eine Zeichenkette, wobei der Wert
                # immer genau 3 Nachkommastellen aufweist.
                cno   = "{:.3f}".format(float(entry[cno_ix]))

                # Verkettung der Satellitennummer, der Pseudorange-Messung,
                # der Trägerphasen-Messung, der Doppler-
                # Frequenzverschiebung und des Signal-Rausch-Verhältnisses
                # zur Beobachtungs-Aufzeichnung.
                rinex_body_linestring += sat_number + "  " + prMes \
                + " " + cpMes + doMes + "          " + cno + "\n"

        return rinex_body_linestring


    def write_RINEX(self):
        rinex = open(self.rinexfile, "w")
        rinex.write(self.create_RINEX_header())
        rinex.write(self.create_RINEX_body())
        rinex.close()
        return
