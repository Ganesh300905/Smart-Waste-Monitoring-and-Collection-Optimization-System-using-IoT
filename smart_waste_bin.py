import RPi.GPIO as GPIO
import time
import requests
from RPLCD.gpio import CharLCD

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BOARD)

TRIG = 7
ECHO = 11
BUZZER = 19

API_KEY ="FV0MZQKQTPC8AETM"
THINGSPEAK_URL = "https://api.thingspeak.com/update"

GPIO.setup(TRIG, GPIO.OUT)
GPIO.setup(ECHO, GPIO.IN)
GPIO.setup(BUZZER, GPIO.OUT)

lcd = CharLCD(
    numbering_mode=GPIO.BOARD,
    pin_rs=22,
    pin_e=18,
    pins_data=[16, 12, 10, 8],
    cols=20,
    rows=4
)

def get_distance():
    GPIO.output(TRIG, False)
    time.sleep(0.2)

    GPIO.output(TRIG, True)
    time.sleep(0.00001)
    GPIO.output(TRIG, False)

    while GPIO.input(ECHO) == 0:
        pulse_start = time.time()

    while GPIO.input(ECHO) == 1:
        pulse_end = time.time()

    duration = pulse_end - pulse_start
    distance = duration * 17150
    return round(distance, 2)

def send_to_thingspeak(distance, fill):
    data = {
        "api_key": API_KEY,
        "field1": distance,
        "field2": fill
    }

    try:
        r = requests.get(THINGSPEAK_URL, params=data, timeout=5)
        if r.text != "0":
            print("ThingSpeak Updated")
        else:
            print("ThingSpeak Update Failed")
    except:
        print("Internet/ThingSpeak Error")

try:
    while True:
        d = get_distance()

        empty = 30
        full = 5

        fill = ((empty - d) / (empty - full)) * 100
        fill = max(0, min(100, fill))
        fill = round(fill, 1)

        print("Distance:", d, "cm | Fill:", fill, "%")

        lcd.clear()
        lcd.write_string("SMART WASTE BIN")
        lcd.cursor_pos = (1, 0)
        lcd.write_string("Dist: " + str(d) + " cm")
        lcd.cursor_pos = (2, 0)
        lcd.write_string("Fill: " + str(fill) + "%")

        if fill >= 80:
            lcd.cursor_pos = (3, 0)
            lcd.write_string("BIN FULL ALERT")
            GPIO.output(BUZZER, True)
            time.sleep(1)
            GPIO.output(BUZZER, False)
        else:
            lcd.cursor_pos = (3, 0)
            lcd.write_string("Status: NORMAL")
            GPIO.output(BUZZER, False)

        send_to_thingspeak(d, fill)

        time.sleep(0.2)

except KeyboardInterrupt:
    lcd.clear()
    GPIO.output(BUZZER, False)
    GPIO.cleanup()