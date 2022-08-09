from moduls.calculate_flight_path import CalculateFlightPath

c   = 8     #focal_length width (mm)
ImW = 3840  #image width (Pixel)
SW  = 6.16  #sensor_width (mm)
GSD = 5     #ground sampling distance (cm/Pixel)

# Klassenkonstruktor mit SW, ImW, c als Pflichtparameter
cfg = CalculateFlightPath(SW, ImW, c)

# Flughöhe über Grund h
h = cfg.calculate_flight_altitude(GSD)     #Flughöhe über Grund (m)
print(h)

# Querüberdeckung q
q = 75

# Kameraöffnungswinkel γ
gamma = 120

# Flugachsenabstand A
A = cfg.calculate_line_spacing(h, q, gamma) #Flugachsenabstand (m)
print(A)
