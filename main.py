import network
import urequests
from machine import ADC, Pin, I2C 
from time import sleep
from imu import MPU6050 #vibration detection
import sh1106 #Oled

#Wi-Fi credentials
ssid = "YOUR_WIFI_SSID"
password = "YOUR_WIFI_PASSWORD"

#Connect to Wi-Fi
wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect(ssid, password)

#check connectivity of wifi
while not wlan.isconnected():
    print("Connecting to WiFi...")
    sleep(1)
print("Connected:", wlan.ifconfig())

#I2C setup
#MPU6050 setup
i2c = I2C(0, scl=Pin(1), sda=Pin(0))
imu = MPU6050(i2c)

#oled setup
i2c1 = I2C(1, scl=Pin(3), sda=Pin(2))
oled = sh1106.SH1106_I2C(128,64, i2c1)

#sound sensor
sound = ADC(Pin(26))  # A0 to GP26

#buzzer
buzzer = Pin(15, Pin.OUT)
#light
alert = Pin(16, Pin.OUT)

#Telegram
TOKEN = "YOUR_TELEGRAM_BOT_TOKEN"
CHAT_ID = "YOUR_CHAT_ID"
MESSAGE1 = "🚨 Abnormal vibration detected!"
MESSAGE2 = "🚨 Abnormal Noise detected!"

#ThingSpeak setup
THINGSPEAK_API_KEY = "YOUR_THINGSPEAK_API_KEY"
THINGSPEAK_URL = "https://api.thingspeak.com/update"

#Thresholds
ACCEL_THRESHOLD = 1.4
GYRO_THRESHOLD = 100

while True:
    ax = round(imu.accel.x, 2)
    ay = round(imu.accel.y, 2)
    az = round(imu.accel.z, 2)
    gx = round(imu.gyro.x)
    gy = round(imu.gyro.y)
    gz = round(imu.gyro.z)
    #combine all the accleraion and gyro parameter
    vibration = round((ax**2 + ay**2 + az**2 + gx**2 + gy**2 + gz**2)**0.5, 2) 
    # sound sensor
    level = sound.read_u16()
    #error status
    status=0
    #buzzer
    buzzer.value(1)
    #light
    alert.value(0)
    #default oled display
    oled.fill(0)
    oled.text("NVH Monitoring", 0, 0)
    oled.text("Normal", 0, 16)
    oled.show()
    #seial monitor
    print("Normal :","Vibration Value", vibration,"Noise Value", level,"Status of alert", status)
    
    #Send data to thingspeak
    try:
        response = urequests.get(
            f"{THINGSPEAK_URL}?api_key={THINGSPEAK_API_KEY}"
            f"&field1={vibration}&field2={level}&field3={status}"
        )
        print("Data sent:", response.status_code)
        response.close()
    except:
        print("Failed to send data to Thingspeak")

    # Alert Condition
    # Vibration alert
    if (abs(ax) > ACCEL_THRESHOLD or abs(ay) > ACCEL_THRESHOLD or abs(az) > ACCEL_THRESHOLD or
        abs(gx) > GYRO_THRESHOLD or abs(gy) > GYRO_THRESHOLD or abs(gz) > GYRO_THRESHOLD):
        #serial monitor
        print("🚨 Abnormal vibration detected!")
        #oled display
        oled.fill(0)
        oled.text("NVH monitoring", 0, 0)
        oled.text("Abnrml Vibration", 0, 16)
        oled.show()
        #error status
        status=1
        #buzzer
        buzzer.value(0)
        #light
        alert.value(1)
        #seial monitor
        print("Normal :","Vibration Value", vibration,"Noise Value", level,"Status of alert", status)
    #telegram alert
    if (abs(ax) > ACCEL_THRESHOLD or abs(ay) > ACCEL_THRESHOLD or abs(az) > ACCEL_THRESHOLD or
        abs(gx) > GYRO_THRESHOLD or abs(gy) > GYRO_THRESHOLD or abs(gz) > GYRO_THRESHOLD):
        try:
            response = urequests.get(
                f"https://api.telegram.org/bot{TOKEN}/sendMessage?chat_id={CHAT_ID}&text={MESSAGE1}"
            )
            print("Telegram alert sent")
            response.close()
        except:
            print("Failed to send Telegram alert")
        try:
            response = urequests.get(
                f"{THINGSPEAK_URL}?api_key={THINGSPEAK_API_KEY}"
                f"&field1={vibration}&field2={level}&field3={1}"
            )
            print("Data sent:", response.status_code)
            response.close()
        except:
            print("Failed to send data to Thingspeak")
    
    #Noise alert
    if level >4500:  # Set  threshold to 29db
        #serial monitor
        print("Loud sound detected!")
        #oled display
        oled.fill(0)
        oled.text("NVH Monitoring", 0, 0)
        oled.text("Abnormal Noise", 0, 32)
        oled.show()
        #error status
        status=1
        #buzzer
        buzzer.value(1)
        #light
        alert.value(1)
        #seial monitor
        print("Normal :","Vibration Value", vibration,"Noise Value", level,"Status of alert", status)
        #telegram alert
        if level >4500:
            try:
                response = urequests.get(
                    f"https://api.telegram.org/bot{TOKEN}/sendMessage?chat_id={CHAT_ID}&text={MESSAGE2}"
                )
                print("Telegram alert sent")
                response.close()
            except:
                print("Failed to send Telegram alert")
            try:
                response = urequests.get(
                    f"{THINGSPEAK_URL}?api_key={THINGSPEAK_API_KEY}"
                    f"&field1={vibration}&field2={level}&field3={1}"
                )
                print("Data sent:", response.status_code)
                response.close()
            except:
                print("Failed to send data to Thingspeak")

    sleep(1)
