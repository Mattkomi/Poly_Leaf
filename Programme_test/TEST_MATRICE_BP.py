from machine import Pin, ADC, UART, SoftI2C
import time
import ssd1306

# OLED configuration
i2c = SoftI2C(scl=Pin(22), sda=Pin(21))
oled = ssd1306.SSD1306_I2C(128, 64, i2c)


# Définir les pins des lignes (entrées)
rows = [Pin(32, Pin.IN, Pin.PULL_DOWN), Pin(33, Pin.IN, Pin.PULL_DOWN), Pin(16, Pin.IN, Pin.PULL_DOWN)]  # D32, D33, RX2 (D16)

# Définir les pins des colonnes (sorties)
cols = [Pin(18, Pin.OUT), Pin(19, Pin.OUT), Pin(23, Pin.OUT)]  # D18, D19, D23

# Initialiser les colonnes à LOW
for col in cols:
    col.value(0)

def scan_matrix():
    """Scanne la matrice et retourne les boutons pressés sous forme de liste (ligne, colonne)."""
    pressed_buttons = []
    for j, col in enumerate(cols):
        # Activer une colonne à la fois
        col.value(1)
        for i, row in enumerate(rows):
            if row.value() == 1:  # Si le bouton est pressé
                pressed_buttons.append((i, j))  # Ajouter la position (ligne, colonne)
        col.value(0)  # Désactiver la colonne
    return pressed_buttons

# Boucle principale
try:
    while True:
        buttons = scan_matrix()
        if buttons:
            for button in buttons:
                oled.fill(0)
                oled.text(f"L{button[0]}, C{button[1]}", 0, 0)
                oled.show()
                print(f"Bouton pressé : Ligne {button[0]}, Colonne {button[1]}")
        time.sleep(0.1)  # Petite pause pour éviter les faux contacts
except KeyboardInterrupt:
    print("Programme arrêté")


