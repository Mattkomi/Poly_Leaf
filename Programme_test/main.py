from machine import Pin, ADC, UART, SoftI2C
import ssd1306
import time

# ======================== Définition des broches ========================= #
TX_PIN = 1  # Broche TX pour communication série
SELECTOR_PIN = Pin(4, Pin.OUT)  # Sélection lecture/écriture

# Joystick
axeX = ADC(Pin(26))  # Axe X joystick
axeY = ADC(Pin(25))  # Axe Y joystick
joystick_button = Pin(27, Pin.IN, Pin.PULL_UP)  # Bouton joystick

# Matrice de boutons (zoom)
rows = [Pin(32, Pin.IN, Pin.PULL_DOWN), Pin(33, Pin.IN, Pin.PULL_DOWN), Pin(16, Pin.IN, Pin.PULL_DOWN)]
cols = [Pin(18, Pin.OUT), Pin(19, Pin.OUT), Pin(23, Pin.OUT)]
for col in cols:
    col.value(0)

# Switch HDMI/USB
switch_son = Pin(14, Pin.IN)
output_son = Pin(5, Pin.OUT)
switch_hdmi = Pin(15, Pin.IN)
hdmi_pin1 = Pin(12, Pin.OUT)
hdmi_pin2 = Pin(13, Pin.OUT)

# OLED configuration
i2c = SoftI2C(scl=Pin(22), sda=Pin(21))
oled = ssd1306.SSD1306_I2C(128, 64, i2c)

# Communication série
mySerial = UART(1, baudrate=9600, tx=Pin(TX_PIN))

# ======================== Commandes VISCA =============================== #
VISCA_BROADCAST_up = bytearray([0x81, 0x01, 0x06, 0x01, 0x0C, 0x0A, 0x03, 0x01, 0xFF])
VISCA_BROADCAST_down = bytearray([0x81, 0x01, 0x06, 0x01, 0x0C, 0x0A, 0x03, 0x02, 0xFF])
VISCA_BROADCAST_left = bytearray([0x81, 0x01, 0x06, 0x01, 0x0C, 0x0A, 0x01, 0x03, 0xFF])
VISCA_BROADCAST_right = bytearray([0x81, 0x01, 0x06, 0x01, 0x0C, 0x0A, 0x02, 0x03, 0xFF])
VISCA_BROADCAST_stop = bytearray([0x81, 0x01, 0x06, 0x01, 0x00, 0x00, 0x03, 0x03, 0xFF])
VISCA_BROADCAST_zoomIn = bytearray([0x81, 0x01, 0x04, 0x07, 0x02, 0xFF])
VISCA_BROADCAST_zoomOut = bytearray([0x81, 0x01, 0x04, 0x07, 0x03, 0xFF])
VISCA_BROADCAST_zoomOff = bytearray([0x81, 0x01, 0x04, 0x07, 0x00, 0xFF])
VISCA_BROADCAST_upleft = bytearray([0x81, 0x01, 0x06, 0x01, 0x0C, 0x0A, 0x02, 0x02, 0xFF])
VISCA_BROADCAST_upright = bytearray([0x81, 0x01, 0x06, 0x01, 0x0C, 0x0A, 0x01, 0x02, 0xFF])
VISCA_BROADCAST_downleft = bytearray([0x81, 0x01, 0x06, 0x01, 0x0C, 0x0A, 0x02, 0x01, 0xFF])
VISCA_BROADCAST_downright = bytearray([0x81, 0x01, 0x06, 0x01, 0x0C, 0x0A, 0x01, 0x01, 0xFF])

VISCA_BROADCAST_brightIn = bytearray([0x81, 0x01, 0x04, 0x0D, 0x02, 0xFF])
VISCA_BROADCAST_brightOut = bytearray([0x81, 0x01, 0x04, 0x0D, 0x03, 0xFF])
VISCA_BROADCAST_gainIn = bytearray([0x81, 0x01, 0x04, 0x0C, 0x02, 0xFF])
VISCA_BROADCAST_gainOut = bytearray([0x81, 0x01, 0x04, 0x0C, 0x03, 0xFF])
VISCA_BROADCAST_freezeIn = bytearray([0x81, 0x01, 0x04, 0x62, 0x02, 0xFF])
VISCA_BROADCAST_freezeOut = bytearray([0x81, 0x01, 0x04, 0x62, 0x03, 0xFF])
VISCA_BROADCAST_setHome = bytearray([0x81, 0x01, 0x06, 0x04,0xFF])



# ======================== Variables globales ============================ #
lastMovementTime = 0
cameraActive = True
isMoving = False
joystickNeutralX = 2048
joystickNeutralY = 2048
threshold = 500
timeoutDuration = 5000  # Timeout in ms
zooming = False  # État actuel du zoom
brighting = False # État actuel du focus
freezing = False
gaining = False

# ======================== Fonctions utilitaires ========================= #
def sendVISCACommand(command):
    SELECTOR_PIN.value(1)
    time.sleep(0.01)
    mySerial.write(command)
    mySerial.flush()
    time.sleep(0.01)
    SELECTOR_PIN.value(0)

def check_son():
    state_son = switch_son.value()
    output_son.value(state_son)
    return state_son

def check_hdmi():
    state_hdmi = switch_hdmi.value()
    hdmi_pin1.value(state_hdmi)
    hdmi_pin2.value(state_hdmi)
    return state_hdmi

def display_oled(son_state, hdmi_state, joystick_status, zoom_status, brightness_status):
    oled.fill(0)
    oled.text("Switch Test", 0, 0)
    oled.text(f"SON: {'Prof' if son_state else 'EXT'}", 0, 20)
    oled.text(f"HDMI: {'PROF' if hdmi_state else 'EXT'}", 0, 30)
    oled.text(f"Joystick: {joystick_status}", 0, 40)
    oled.text(f"Zoom: {zoom_status}", 0, 50)
    oled.text(f"Zoom: {brightness_status}", 0, 60)
    oled.show()

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

# ======================== Programme principal =========================== #
def main():
    global lastMovementTime, cameraActive, isMoving, zooming, brighting, gaining

    axeX.atten(ADC.ATTN_11DB)
    axeY.atten(ADC.ATTN_11DB)

    while True:
        # Lecture du joystick
        valX = axeX.read()
        valY = axeY.read()
        btnJoystick = joystick_button.value()

        # Lecture des boutons pour le zoom via la matrice
        buttons = scan_matrix()
        zoomIn = any(button == (0, 1) for button in buttons)  # Si le premier bouton est pressé
        zoomOut = any(button == (0, 0) for button in buttons)  # Si le deuxième bouton est pressé
        gainIn= any(button == (1, 2) for button in buttons)  
        gainOut= any(button == (1, 1) for button in buttons)
        setHome = any(button == (1, 0) for button in buttons)
        #setTableau = any(button == (2, 2) for button in buttons)
        #freeze = any(button == (2, 2) for button in buttons)
        brightIn = any(button == (2, 2) for button in buttons)
        brightOut = any(button == (2, 1) for button in buttons)

        # Lecture des switches
        son_state = check_son()
        hdmi_state = check_hdmi()

        # Gestion zoom
        if zoomIn and not zooming:
            sendVISCACommand(VISCA_BROADCAST_zoomIn)
            zooming = True
        elif zoomOut and not zooming:
            sendVISCACommand(VISCA_BROADCAST_zoomOut)
            zooming = True
        elif not zoomIn and not zoomOut and zooming:
            sendVISCACommand(VISCA_BROADCAST_zoomOff)
            zooming = False
        
        #Gestion Brightness
        if brightIn and not brighting :
            sendVISCACommand(VISCA_BROADCAST_brightIn)
            brighting = True
        elif brightOut and not brighting :
            sendVISCACommand(VISCA_BROADCAST_brightOut)
            brighting = True
        elif not brightIn and not brightOut and brighting:
            brighting = False
        
        #Gestion Brightness
        if gainIn and not gaining :
            sendVISCACommand(VISCA_BROADCAST_gainIn)
            gaining = True
        elif gainOut and not gaining :
            sendVISCACommand(VISCA_BROADCAST_gainOut)
            gaining = True
        elif not gainIn and not gainOut and gaining:
            gaining = False
            
        #Gestion setHome
        if setHome :
            sendVISCACommand(VISCA_BROADCAST_setHome)
            
        
        
            
        # Gestion caméra (mouvement)
        if btnJoystick == 0:
            cameraActive = True
            lastMovementTime = time.ticks_ms()

        if cameraActive:
            adjustedX = valX - joystickNeutralX
            adjustedY = valY - joystickNeutralY
            moved = False

            # Détection des mouvements diagonaux
            if adjustedX < -threshold and adjustedY < -threshold:
                sendVISCACommand(VISCA_BROADCAST_downright)
                moved = True
            elif adjustedX > threshold and adjustedY < -threshold:
                sendVISCACommand(VISCA_BROADCAST_downleft)
                moved = True
            elif adjustedX < -threshold and adjustedY > threshold:
                sendVISCACommand(VISCA_BROADCAST_upright)
                moved = True
            elif adjustedX > threshold and adjustedY > threshold:
                sendVISCACommand(VISCA_BROADCAST_upleft)
                moved = True
            elif adjustedX < -threshold:
                sendVISCACommand(VISCA_BROADCAST_left)
                moved = True
            elif adjustedX > threshold:
                sendVISCACommand(VISCA_BROADCAST_right)
                moved = True
            elif adjustedY < -threshold:
                sendVISCACommand(VISCA_BROADCAST_up)
                moved = True
            elif adjustedY > threshold:
                sendVISCACommand(VISCA_BROADCAST_down)
                moved = True

            # Arrêt si le joystick est neutre
            if not moved and isMoving:
                sendVISCACommand(VISCA_BROADCAST_stop)
                isMoving = False

            if moved:
                lastMovementTime = time.ticks_ms()
                isMoving = True

            if time.ticks_ms() - lastMovementTime > timeoutDuration:
                cameraActive = False
                sendVISCACommand(VISCA_BROADCAST_stop)

        # Mise à jour de l'affichage OLED
        joystick_status = "Active" if isMoving else "Inactive"
        zoom_status = "In" if zoomIn else "Out" if zoomOut else "Off"
        brightness_status = "+" if brightIn else "-" if brightOut else "Off"
        display_oled(son_state, hdmi_state, joystick_status, zoom_status,brightness_status)

        time.sleep(0.1)

# ======================== Exécution du programme ======================== #
if __name__ == "__main__":
    main()

