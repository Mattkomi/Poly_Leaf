from machine import ADC, Pin
import time

xAxis = ADC(Pin(26, Pin.IN))  # Créer un objet ADC agissant sur une broche
xAxis.atten(xAxis.ATTN_11DB)
yAxis = ADC(Pin(25, Pin.IN))  # Créer un objet ADC agissant sur une broche
yAxis.atten(yAxis.ATTN_11DB)
button = Pin(27, Pin.IN, Pin.PULL_UP)

# Seuils pour déterminer les mouvements
SEUIL_HAUT = 1000
SEUIL_BAS = 3000
SEUIL_GAUCHE = 1000
SEUIL_DROITE = 3000

while True:
    xValue = xAxis.read()  # Lire une valeur analogique brute dans la plage 0-4095
    yValue = yAxis.read()  # Lire une valeur analogique brute dans la plage 0-4095
    btnValue = button.value()

    # Direction selon les mouvements de l'axe X
    if xValue < SEUIL_GAUCHE:
        directionX = "Gauche"
    elif xValue > SEUIL_DROITE:
        directionX = "Droite"
    else:
        directionX = "Centre"

    # Direction selon les mouvements de l'axe Y
    if yValue < SEUIL_HAUT:
        directionY = "Haut"
    elif yValue > SEUIL_BAS:
        directionY = "Bas"
    else:
        directionY = "Centre"

    print(f"X: {directionX}, Y: {directionY}, Button: {btnValue}")

    time.sleep(0.1)

