import RPi.GPIO as GPIO
from time import sleep

__BUZZER_PIN = 23

def intermittent_beep(beep_duration_in_seconds: float = 0.5, seconds_between_beeps: float = 0.5, times: int = 2):
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(__BUZZER_PIN, GPIO.OUT)

    for _ in range(times):
        GPIO.output(__BUZZER_PIN, GPIO.HIGH)
        sleep(beep_duration_in_seconds) 
        GPIO.output(__BUZZER_PIN, GPIO.LOW)
        sleep(seconds_between_beeps)



