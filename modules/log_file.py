class LogFile():

    def __init__ (self, logfile):
        self.log = open(logfile, "r")
        self.log_read = self.log.readlines()
        return

    def __del__(self):
        self.log.close()
        del self.log, self.log_read
        return

    # Ordnet den GPS-Zeitstempeln die System-Zeitstempel
    # seit dem Systemstart zu.
    def map_gpstime_to_timeUS(self):
        gpstime_timeus_map = {}
        for row in self.log_read:
            if row[:3] == "GPS":
                row_content = row.split(", ")
                TimeUS = int(row_content[1])
                gpsmicroseconds = int(row_content[3])
                gpstime_timeus_map[gpsmicroseconds] = TimeUS
        return gpstime_timeus_map

    def extract_GPS_from_log(self):
        dictio_GPS = {}
        # message type
        mess_type_ix = 0
        # time since system startup
        TimeUS_ix = 1
        for row in self.log_read:
            if row[:3] == "GPS":
                row_content = row.strip("\n").split(", ")
                TimeUS = row_content[TimeUS_ix]
                dictio_GPS[TimeUS] = row_content[TimeUS_ix + 1:]
        return dictio_GPS

    def extract_BARO_from_log(self):
        dictio_BARO = {}
        # message type
        mess_type_ix = 0
        # time since system startup
        TimeUS_ix = 1
        for row in self.log_read:
            if row[:4] == "BARO":
                row_content = row.strip("\n").split(", ")
                TimeUS = row_content[TimeUS_ix]
                dictio_BARO[TimeUS] = row_content[TimeUS_ix + 1:]
        return dictio_BARO

    # Ordnet den UBX-RXM-RAWX-Nachrichten die System-Zeitstempel
    # seit dem Systemstart zu.
    def extract_GRXH_and_GRXS_from_logfile(self):
        # Dictionary zur Speicherung von Systemzeiten als Schlüssel
        # und UBX-RXM-RAWX-Nachrichten als zuzuordnende Werte.
        dictio_GRXH_GRXS = {}

        # Index des Attributs "message type" (z. B. "GRXH", "GRXS")
        # in der weiter unten aus der zur Log-File-Zeile gewandelten Liste.
        mess_type_ix = 0
        # Index des Attributs "time since system startup" (Systemlaufzeit
        # seit dem Booten) in der weiter unten aus der zur Log-File-Zeile
        # gewandelten Liste.
        TimeUS_ix = 1

        # Schleife durch die Liste mit den eingelesenen Zeilen der
        # Log-Datei.
        for row in self.log_read:
            # Auftrennung der als Zeichenkette gespeicherten und
            # durch Kommata getrennten Teilparameter der Zeile.
            row_content = row.strip("\n").split(", ")

            # Ist die aktuell aufgerufene Zeile eine Nachricht vom  Typ
            # "GRXH", also eine UBX-RXM-RAWX-Header-Message,
            # ist folgende Bedingung erfüllt.
            if row_content[mess_type_ix] == "GRXH":
                # Abfrage der Systemzeit zu der die
                # UBX-RXM-RAWX-Header-Nachricht
                # abgesetzt wurde und Zuweisung zur Variablen TimeUS.
                TimeUS = row_content[TimeUS_ix]
                # Der Dictionary wird als weiteres Element die Systemzeit
                # als Schlüssel und eine leere Liste als Wert hinzugefügt.
                dictio_GRXH_GRXS[TimeUS] = []
                # Die soeben hinzugefügte leere Liste wird mit den
                # UBX-RXM-RAWX-Header-Komponenten (rcvTow, week, leapS,
                # numMeas, recStat) befüllt.
                dictio_GRXH_GRXS[TimeUS].append(row_content[TimeUS_ix+1:])

            # Ist die aktuell aufgerufene Zeile eine Nachricht vom  Typ
            # "GRXS", also eine UBX-RXM-RAWX-Payload-Message,
            # ist folgende Bedingung erfüllt.
            elif row_content[mess_type_ix] == "GRXS":
                # Abfrage der Systemzeit zu der die
                # UBX-RXM-RAWX-Payload-Nachricht
                # abgesetzt wurde und Zuweisung zur Variablen TimeUS.
                TimeUS = row_content[TimeUS_ix]
                # Dieser GRXS-Nachricht ist eine GRXH-Nachricht
                # vorgeschaltet, für die in der vorigen Verzweigung
                # bereits ein Eintrag (Systemzeit als Schlüssel und Liste
                # als Wert) in der Dictionary angelegt wurde. Der Schlüssel
                # TimeUS ist hier identisch und wird zum Aufruf der
                # zugehörigen Liste verwendet. Die Liste wird dann mit den
                # UBX-RXM-RAWX-Header-Komponenten
                # (rcvTow, week, leapS, numMeas, recStat) befüllt.
                dictio_GRXH_GRXS[TimeUS].append(row_content[TimeUS_ix+1:])

        # Rückgabe der Dictionary mit den Systemzeiten als Schlüssel
        # und Listen mit GRXH und GRXS-Messages als Werte.
        return dictio_GRXH_GRXS

    def get_timeUS_of_video_start_and_stop(self, startcmd, stopcmd):
        # z. B. "Mission: 7 RepeatRelay"
        startcmd = startcmd
        # z. B. "Reached command #12"
        stopcmd  = stopcmd
        # Zeitverzögerung Δt in Mikrosekunden
        delta_t  = 1000000
        for row in self.log_read:
            if row[:3] == 'MSG':
                items = row.split(", ")
                if startcmd in items[2]:
                    starttime = int(items[1]) + delta_t
                if stopcmd in items[2]:
                    stoptime  = int(items[1]) + delta_t

        return starttime, stoptime
