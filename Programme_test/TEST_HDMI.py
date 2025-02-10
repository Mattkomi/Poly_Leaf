from machine import Pin
from time import sleep

# Configuration des pins
hdmi_pin1 = Pin(12, Pin.OUT)  # HDMI pin 12
hdmi_pin2 = Pin(13, Pin.OUT)  # HDMI pin 13
led = Pin(2, Pin.OUT)  # LED intégrée (pin 2)

# État initial des HDMI
hdmi_state = 0

# Boucle principale
while True:
    # Alterne l'état des sorties HDMI
    hdmi_state = 1 if hdmi_state == 0 else 0  # Basculer entre 0 et 1
    hdmi_pin1.value(hdmi_state)
    hdmi_pin2.value(hdmi_state)

    # La LED suit l'état des HDMI (reste allumée)
    led.value(hdmi_state)

    # Pause de 20 secondes avant le prochain changement
    sleep(20)
