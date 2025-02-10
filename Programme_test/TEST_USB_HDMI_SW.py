from machine import Pin, SoftI2C
import ssd1306
from time import sleep

# Configuration des pins
switch_son = Pin(14, Pin.IN)  # Switch pour le son (pin 14)
output_son = Pin(5, Pin.OUT)  # Sortie pour le son (pin 5)
switch_externe = Pin(15, Pin.IN)  # Switch HDMI (pin 15)
hdmi_pin1 = Pin(12, Pin.OUT)  # HDMI pin 12
hdmi_pin2 = Pin(13, Pin.OUT)  # HDMI pin 13

# Configuration de l'I2C pour l'OLED
i2c = SoftI2C(scl=Pin(22), sda=Pin(21))
oled_width = 128
oled_height = 64
oled = ssd1306.SSD1306_I2C(oled_width, oled_height, i2c)

# Fonction pour vérifier l'état du switch son
def check_son():
    state_son = switch_son.value()  # Lecture de l'état du switch son (0 ou 1)
    output_son.value(state_son)  # Applique l'état du switch sur la sortie son
    return state_son

# Fonction pour configurer les pins HDMI en fonction du switch externe (pin 15)
def check_hdmi():
    switch_state = check_switch_externe()  # Lecture de l'état du switch externe
    hdmi_pin1.value(switch_state)  # Applique l'état du switch sur la pin HDMI 12
    hdmi_pin2.value(switch_state)  # Applique l'état du switch sur la pin HDMI 13

    return f"{switch_state}, {switch_state}"

# Fonction pour lire l'état du switch externe (pin 15)
def check_switch_externe():
    return switch_externe.value()  # Retourne l'état du switch externe (0 ou 1)

# Boucle principale pour afficher les résultats
while True:
    oled.fill(0)  # Efface l'écran

    # Lecture des états des switches
    son_state = check_son()
    hdmi_state = check_hdmi()
    switch_state = check_switch_externe()

    # Affichage des résultats
    oled.text("Switch Test", 0, 0)
    oled.text(f"SON: {'ON' if son_state else 'OFF'}", 0, 20)
    oled.text(f"Switch HDMI: {'ON' if switch_state else 'OFF'}", 0, 30)
    oled.text(f"HDMI: {hdmi_state}", 0, 40)
    oled.show()  # Mise à jour de l'écran

    print("Switch Test")
    print(f"SON: {'ON' if son_state else 'OFF'}")
    print(f"Switch HDMI: {'ON' if switch_state else 'OFF'}")
    print(f"HDMI: {hdmi_state}")

    sleep(0.5)  # Pause avant le prochain cycle

