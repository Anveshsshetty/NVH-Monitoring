# NVH-Monitoring
Develop an IoT Machinery NVH Monitoring System using Raspberry Pi Pico for real-
time vibration, noise, and harshness analysis of industrial machines. Continuously
measure and record vibration patterns, analyze NVH data, and provide alerts for
abnormal or hazardous conditions
# Setup
## Components
* Raspberry Pi Pico 2 W
* MPU6050 Gyroscope
* Sound Sensor
* SSH1106 Oled display
* Buzzer
* Led
## Pin Connections

| Microcontroller Pin | Connected To | Module/Peripheral | Notes                        |
|---------------------|--------------|-------------------|------------------------------|
| Pin 1               | SDA          | MPU6050 (IMU)     | I2C Data line                |
| Pin 2               | SCL          | MPU6050 (IMU)     | I2C Clock line               |
| Pin 4               | SDA          | SH1106 OLED       | I2C Data line                |
| Pin 5               | SCL          | SH1106 OLED       | I2C Clock line               |
| Pin 20              | OUT          | Buzzer            | Digital output control       |
| Pin 21              | A0           | Sound Sensor      | Analog input                 |
| Pin 31              | Anode        | Red LED           | Requires series resistor     |
| Pin 36              | 3.3V VCC     | Buzzer            | Power supply for buzzer      |
| Pin 38              | GND          | Common Ground     | Shared ground for all modules|
| Pin 40              | 5V VCC       | Power Rail        | Supply for 5V peripherals    |
