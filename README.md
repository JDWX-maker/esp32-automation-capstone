# esp32-automation-capstone
For school final project.
Final Project: The Automation Capstone
Light Reactive ESP32 Automation System
📌 Overview
This project is a complete automation system built using an ESP32 microcontroller, a light sensor (LDR), and two indicator LEDs. The ESP32 reads ambient light levels, processes the data, and communicates with a host Python script running on a PC. The host script logs sensor values and can trigger additional actions based on thresholds.
This project demonstrates full integration between hardware, firmware, serial communication, and host side automation, fulfilling all requirements of the Automation Capstone.
________________________________________
🎯 Features
•	LDR light sensor measures ambient brightness
•	Two LEDs indicate “bright” or “dark” conditions
•	ESP32 firmware written in MicroPython
•	Serial communication sends sensor data to the host PC
•	Host Python script logs readings and reacts to changes
•	Version controlled with Git and fully backed up to GitHub
•	Detailed schematic included in /docs
________________________________________
🛠 Hardware Used
•	ESP32 DevKit (MicroPython firmware)
•	LDR (photoresistor)
•	10 kΩ resistor (voltage divider)
•	Two LEDs (red/green or your choice)
•	Two 220 Ω resistors (LED current limiting)
•	Jumper wires
•	Breadboard
________________________________________
🔌 Circuit Diagram
The full schematic is located in:
/docs/ESP32_schematic.png
It includes:
•	GPIO 4 → Bright LED
•	GPIO 5 → Dark LED
•	GPIO 15 (Pin 1 on your board) → LDR voltage divider
•	3.3 V and GND rails
•	All resistor values and labeled nodes
________________________________________
📟 ESP32 Firmware (MicroPython)
Your firmware performs:
•	ADC sampling of the LDR
•	Threshold comparison
•	LED control
•	Serial output of sensor values
Firmware is located in:
/firmware/main.py
________________________________________
💻 Host Python Script
The host script:
•	Opens a serial connection
•	Reads incoming sensor values
•	Logs them to the console or file
•	Can trigger PC side actions
Located in:
/host/host_script.py
________________________________________
🔗 Communication Protocol
This project uses Serial (UART over USB) to communicate between the ESP32 and the host PC.
Data format example:
LDR: 1830
LDR: 1920
LDR: 2100
________________________________________
📁 Repository Structure
Final project/
│
├── firmware/
│   └── main.py
│
├── host/
│   └── host_script.py
│
├── docs/
│   └── ESP32_schematic.png
│
└── README.md
________________________________________
📹 Demonstration Video
A 5–7 minute demonstration video will show:
•	Hardware setup
•	ESP32 running
•	LEDs reacting to light
•	Host script receiving data
•	Explanation of system behavior
________________________________________
📄 Project Proposal
Your proposal outlines:
•	The problem being solved
•	Hardware components
•	Communication method
•	Expected behavior
Located in:
/docs/proposal.md
________________________________________
🚀 How to Run the Project
1. Flash ESP32 with MicroPython
Follow standard MicroPython flashing instructions.
2. Upload firmware
Use Thonny or ampy:
main.py → ESP32 root directory
3. Run host script
On your PC:
python host_script.py
4. Observe LEDs + serial output
•	Cover the LDR → Dark LED turns on
•	Shine light → Bright LED turns on
•	Host script logs values
________________________________________
✔ Capstone Requirements Checklist
Requirement	Status
Sensor + Actuator	✅ LDR + LEDs
Microcontroller Programming	✅ ESP32 MicroPython
Communication Protocol	✅ Serial
Host Interaction	✅ Python script
Version Control	✅ Git + GitHub
Circuit Diagram	✅ Included
Proposal	✅ Completed

