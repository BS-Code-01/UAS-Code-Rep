class TimeFormatConverter():

    def __init__ (self):
        return

    # Rechnet ein Tupel aus Minuten, Sekunden und Millisekunden
    # in Dezimalsekunden um.
    def clocktime_to_decimalseconds(minutes, seconds, microseconds):
        x1 = float(minutes*60)
        x2 = float(seconds)
        x3 = float(microseconds/1000)
        result = round(x1+x2+x3, 3)
        return result

    # Rechnet Mikrosekunden in Tupel
    # aus Minuten, Sekunden und Millisekunden um.
    def microseconds_to_clocktime(microseconds):

        microseconds_1 = microseconds
        microseconds_2 = microseconds_1 % (60 * 1000000)
        microseconds_3 = microseconds_2 % 1000000
        microseconds_4 = microseconds_3 % 1000

        minutes = int((microseconds_1 - microseconds_2) / (60*1000000))
        seconds = int((microseconds_2 - microseconds_3) / 1000000)
        millis  = int((microseconds_3 - microseconds_4) / 1000)

        return [minutes, seconds, millis]

    # Rechnet die GPS-Zeitgrößen GPS-Woche, GPS-Sekunden und Sprungsekunden
    # in die UTC-Zeit um.
    def weeks_and_seconds_to_utc(gpsweek, gpsseconds, leapseconds):
        #TO_DO: Minuten müssen lt. RINEX-Format 2-stellig sein.
        import datetime, calendar
        # Festlegung des Datumsformats
        datetimeformat = "%Y  %m  %d  %H %M %S.%f"
        epoch = datetime.datetime.strptime\
        ("1980  1  6  00 00 00.0",datetimeformat)
        elapsed = datetime.timedelta(\
        days=(gpsweek*7),seconds=(gpsseconds+leapseconds))

        return datetime.datetime.strftime(epoch + elapsed, datetimeformat)\
        .lstrip("0").replace(" 0", " ") + "0"

    # Rechnet Kalenderdatum und UTC-Zeit in die GPS-Zeitgrößen
    # GPS-Woche und GPS-Sekunden um (Beispiel 2174, 457126.59).
    def utc_to_week_and_seconds(\
    year, month, day, hour, minute, second, microsecond):
        import datetime

        utc_gps_origin = datetime.datetime(year=1980, month=1, day=6)
        utc_gps_log = datetime.datetime(year=year, month=month, day=day, \
        hour=hour, minute=minute, second=second, microsecond=microsecond)

        time_delta = utc_gps_log - utc_gps_origin
        gpsweek = time_delta.days // 7
        days_in_gpsweek = time_delta.days - gpsweek * 7
        gpsseconds = (days_in_gpsweek * 24 * 60 * 60) + time_delta.seconds
        gpsmicroseconds = gpsseconds * 1000 + time_delta.microseconds

        return gpsweek, gpsmicroseconds
