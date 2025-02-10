from machine import Pin
from time import sleep

# Configuration des pins
usb_pin1 = Pin(14, Pin.OUT)   # USB pin 14
usb_pin2 = Pin(15, Pin.OUT)   # USB pin 15
led = Pin(2, Pin.OUT)  # LED intégrée (pin 2)

# État initial des USB
usb_state = 0

# Boucle principale
while True:
    # Alterne l'état des sorties USB
    usb_state = 1 if usb_state == 0 else 0  # Basculer entre 0 et 1
    usb_pin1.value(usb_state)
    usb_pin2.value(usb_state)

    # La LED suit l'état des USB : allumée si actifs
    led.value(usb_state)

    # Pause de 20 secondes avant le prochain changement
    sleep(20)
