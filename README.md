# NVH Monitoring — Raspberry Pi Pico W
  
  An IoT Machinery NVH (Noise, Vibration, Harshness) Monitoring System using Raspberry Pi Pico W.  
  Continuously measures vibration (MPU6050) and noise (analog sound sensor), displays local status on an SH1106 OLED, issues local alerts (buzzer and LED), uploads telemetry to ThingSpeak, and sends Telegram alerts for abnormal events.
  
  ---
  
  ## Problem statement
  
  Develop an IoT Machinery NVH Monitoring System using Raspberry Pi Pico for real‑time vibration, noise, and harshness analysis of industrial machines. Continuously measure and record vibration patterns, analyze NVH data, and provide alerts for abnormal or hazardous conditions.
  
  ---
  
  ## Scope
  
  - Continuous real‑time monitoring of vibration using MPU6050 (accelerometer + gyro) and ambient noise using an analog sound sensor.  
  - Local immediate alerts via buzzer and LED when thresholds are exceeded.  
  - Local status display on SH1106 128×64 I2C OLED.  
  - Cloud telemetry to ThingSpeak for time‑series logging and basic analytics.  
  - Remote alerts via Telegram messages for abnormal vibration or noise.  
  - Deliverables: documented repo, wiring diagram, working MicroPython code, ThingSpeak CSV export and screenshots, and a demo video.
  
  Constraints and assumptions: system designed for Raspberry Pi Pico W (Wi‑Fi enabled). Thresholds are empirical and should be tuned per machine and mounting. This is a prototype-level system, not a certified industrial NVH instrument.
  
  ---
  
  ## Required components
  
  **Hardware**
  - Raspberry Pi Pico W (recommended)  
  - MPU6050 IMU module (accelerometer + gyroscope)  
  - SH1106 128×64 I2C OLED display  
  - Analog sound sensor module (A0 output)  
  - Active piezo buzzer (3.3 V compatible) or buzzer + transistor driver  
  - Red LED 
  - Breadboard, jumper wires, USB power supply (5 V)
  
  **Software and IDE**
  - Thonny IDE   
  - MicroPython firmware for Raspberry Pi Pico W  
  - MicroPython libraries: MPU6050 driver (`imu.py`), SH1106 driver (`sh1106.py`), `urequests`  
  - ThingSpeak account (for telemetry)  
  - Telegram bot token and chat ID (for alerts)
  
  **Tools**
  - Serial console (Thonny) for monitoring and debugging  
  - Screenshot/capture tool for dashboard screenshots  
  - Screen recorder or smartphone for demo video
  
  ---
  
  ## Circuit schematic (textual mapping)
  
  Use the wiring table below to wire your hardware. Verify VCC voltage requirements for each module (3.3 V vs 5 V).
  
  ### Wiring table
  
  | Microcontroller Pin | Connected To | Module / Peripheral | Notes |
  |---------------------|--------------|---------------------|-------|
  | Pin 1               | SDA          | MPU6050             | I2C Data (MPU6050) |
  | Pin 2               | SCL          | MPU6050             | I2C Clock (MPU6050) |
  | Pin 4               | SDA          | SH1106 OLED         | I2C Data (OLED) |
  | Pin 5               | SCL          | SH1106 OLED         | I2C Clock (OLED) |
  | Pin 20              | OUT          | Buzzer              | Digital control (may need transistor) |
  | Pin 21              | A0           | Sound sensor        | Analog input (ADC) |
  | Pin 31              | Anode        | Red LED             | Alert Status |
  | Pin 36              | 3.3V         | Buzzer VCC; Sound VCC | 3.3V power rail |
  | Pin 38              | GND          | Common Ground       | Shared ground for all modules |
  | Pin 40              | 5V           | 5V Power Rail       | If any module requires 5V |
  
  
  **Hardware notes**
  - If MPU6050 or SH1106 modules do not include pull-ups, add 4.7 kΩ pull‑ups on SDA and SCL.  
  - Ensure all grounds are common and avoid powering modules with incompatible voltages directly from Pico I/O pins.
  
  ---
  
  ## Code logic implementation
  
  1. Initialization  
     - Load MicroPython on Pico W. Initialize Wi‑Fi, I2C buses, IMU (MPU6050), OLED (SH1106), ADC (sound sensor), and GPIOs (buzzer, LED).
  
  2. Calibration (optional)  
     - Capture baseline acceleration and gyro offsets; store or apply simple zeroing to reduce bias.
  
  3. Sensor reading  
     - Read accelerometer (ax, ay, az) and gyroscope (gx, gy, gz) values from MPU6050.  
     - Read analog sound level from ADC (16‑bit u16 reading).
  
  4. NVH metric computation  
     - Combine accelerometer and gyro readings into a single magnitude (Euclidean/RMS) to detect abnormal vibration.  
     - Compare noise ADC level against a configured threshold for noise alerts.
  
  5. Alerts and display  
     - If NVH metric or any sensor axis exceeds threshold set `status = 1`. Activate buzzer and LED and update OLED with alert text. Otherwise show "Normal".
  
  6. Cloud and notification  
     - Send telemetry (vibration, noise, status) to ThingSpeak.  
     - On alert, send Telegram message (rate-limit to avoid spamming).
  
  7. Loop and error handling  
     - Run main loop at a defined interval (default 1 s). Wrap network operations in try/except and log errors to serial console.
  
  ---
  
  ## Code for the solution (main.py template)
  
  Place the following as `main.py`. Replace placeholders before use. Do not commit real tokens to a public repo — use a gitignored secrets file.
  
  ```python
  # main.py
  import network
  import urequests
  from machine import ADC, Pin, I2C
  from time import sleep
  from imu import MPU6050
  import sh1106
  
  # -------- Configuration (replace placeholders) --------
  SSID = "YOUR_WIFI_SSID"
  PASSWORD = "YOUR_WIFI_PASSWORD"
  
  TOKEN = "YOUR_TELEGRAM_BOT_TOKEN"
  CHAT_ID = "YOUR_CHAT_ID"
  
  THINGSPEAK_API_KEY = "YOUR_THINGSPEAK_API_KEY"
  THINGSPEAK_URL = "https://api.thingspeak.com/update"
  
  ACCEL_THRESHOLD = 1.4
  GYRO_THRESHOLD = 100
  SOUND_THRESHOLD = 4500  # adjust after calibration
  
  # -------- WiFi connect --------
  wlan = network.WLAN(network.STA_IF)
  wlan.active(True)
  wlan.connect(SSID, PASSWORD)
  while not wlan.isconnected():
      print("Connecting to WiFi...")
      sleep(1)
  print("Connected, IP:", wlan.ifconfig())
  
  # -------- Peripherals init (adjust pins to match wiring) --------
  i2c_imu = I2C(0, scl=Pin(2), sda=Pin(1))
  imu = MPU6050(i2c_imu)
  
  i2c_oled = I2C(1, scl=Pin(3), sda=Pin(2))
  oled = sh1106.SH1106_I2C(128, 64, i2c_oled)
  
  sound = ADC(Pin(26))
  buzzer = Pin(20, Pin.OUT)
  alert_led = Pin(31, Pin.OUT)
  
  def send_thingspeak(vib, level, status):
      try:
          r = urequests.get("{}?api_key={}&field1={}&field2={}&field3={}".format(
              THINGSPEAK_URL, THINGSPEAK_API_KEY, vib, level, status))
          print("ThingSpeak:", r.status_code)
          r.close()
      except Exception as e:
          print("ThingSpeak error:", e)
  
  def send_telegram(msg):
      try:
          r = urequests.get("https://api.telegram.org/bot{}/sendMessage?chat_id={}&text={}".format(
              TOKEN, CHAT_ID, msg))
          print("Telegram:", r.status_code)
          r.close()
      except Exception as e:
          print("Telegram error:", e)
  
  # -------- Main loop --------
  while True:
      ax = round(imu.accel.x, 2)
      ay = round(imu.accel.y, 2)
      az = round(imu.accel.z, 2)
      gx = round(imu.gyro.x)
      gy = round(imu.gyro.y)
      gz = round(imu.gyro.z)
  
      vibration = round((ax**2 + ay**2 + az**2 + gx**2 + gy**2 + gz**2)**0.5, 2)
      noise_level = sound.read_u16()
  
      status = 0
  
      # Default display/state
      buzzer.value(1)      # active-low assumed; invert if needed
      alert_led.value(0)
      oled.fill(0)
      oled.text("NVH Monitoring", 0, 0)
      oled.text("Normal", 0, 16)
      oled.show()
  
      print("Vib:", vibration, "Noise:", noise_level, "Status:", status)
      send_thingspeak(vibration, noise_level, status)
  
      vib_alert = (abs(ax) > ACCEL_THRESHOLD or abs(ay) > ACCEL_THRESHOLD or abs(az) > ACCEL_THRESHOLD or
                   abs(gx) > GYRO_THRESHOLD or abs(gy) > GYRO_THRESHOLD or abs(gz) > GYRO_THRESHOLD)
  
      if vib_alert:
          print("Abnormal vibration")
          oled.fill(0)
          oled.text("NVH Monitoring", 0, 0)
          oled.text("Abnrml Vibration", 0, 16)
          oled.show()
          status = 1
          buzzer.value(0)
          alert_led.value(1)
          send_telegram("🚨 Abnormal vibration detected!")
  
      if noise_level > SOUND_THRESHOLD:
          print("Loud sound detected")
          oled.fill(0)
          oled.text("NVH Monitoring", 0, 0)
          oled.text("Abnormal Noise", 0, 32)
          oled.show()
          status = 1
          buzzer.value(0)
          alert_led.value(1)
          send_telegram("🚨 Abnormal Noise detected!")
  
      sleep(1)
```
## Threshold for acclertion and noise
  Since its an demo we have used low level of vibration and noise
  This can be changed based on the 
# 📢 Telegram Alerts with MicroPython

This project demonstrates how to send alerts from a MicroPython device (Raspberry Pi Pico 2 W) directly to a Telegram chat using a bot.

---

## 🚀 Features
- Real‑time alerts from your IoT device to Telegram
- Simple MicroPython function for sending messages
- Easy setup with BotFather and Telegram API

---

## 🛠️ Setup Instructions
3. Look for `"chat":{"id":...}` in the JSON response.  
That number is your **Chat ID**.

---

### 3. MicroPython Code Example

Add this snippet to your MicroPython project:

```python
import urequests

BOT_TOKEN = "YOUR_BOT_TOKEN"
CHAT_ID = "YOUR_CHAT_ID"

def send_telegram_alert(message):
 url = "https://api.telegram.org/bot{}/sendMessage".format(BOT_TOKEN)
 data = {"chat_id": CHAT_ID, "text": message}
 try:
     response = urequests.post(url, json=data)
     response.close()
 except Exception as e:
     print("Error sending alert:", e)
```
# Example usage
send_telegram_alert("🚨 Alert: Sensor threshold exceeded!")
### 1. Create a Telegram Bot
1. Open Telegram and search for **BotFather**.
2. Start a chat and run the command:
# Team Members
* Anurag Shetty
* Anvesh S Shetty
* Dhanush D Shetty

