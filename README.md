# InTeRRoR: Integrating LLM Output for Robotics Input through Local Wired Compiling (First Attempt)
an llm controlled robot through live local wired (USB) C++ compilation for ESP32/Arduino 
Project Overview

InTeRRoR is an innovative project that leverages the power of Large Language Models (LLMs) to generate, compile, and upload C++ code to an Arduino-based 2-wheeled robot. The process involves using the Gemini API to generate the code based on user instructions, compiling the code locally using arduino-cli, and uploading it to the Arduino through a USB connection. This project aims to simplify the process of programming robotics by using natural language instructions to control the robot's behavior.
# How It Works?

    User Input: The user provides instructions through a Telegram bot.
    |
    V
    Code Generation: The Gemini API generates Arduino C++ code based on the provided instructions.
    |
    V
    Code Compilation: The generated code is compiled locally using arduino-cli.
    |   |
    |   V
    |   Code Correction: If there are any compilation errors, the code is corrected and recompiled.
    |   |
    V   V
    Code Upload: Once the code is successfully compiled, it is uploaded to the Arduino via USB.
    |
    V
    Execution: The robot executes the uploaded code to perform the desired actions.

# Quickstart Guide

Getting Your API Key

We use the Gemini API since it's free to use.
  Go to Gemini API Key.
  Click `Get API Key` and copy your API key.\
  Replace the `YOUR_API_KEY` variable in the Python code with your API key.

Follow these steps to set up and run the InTeRRoR project: \
Prerequisites

    Arduino board (e.g., Arduino Uno)
    Required components (L298N motor driver, HCSR04 ultrasonic sensor, gy273_HMC5883L, MPU6050, buzzer)
    Raspberry Pi with Raspberry Pi OS Lite
    FreeCAD or TinkerCAD for 3D modeling (optional)
    Telegram bot setup (follow Telegram Bot API)

Steps
1. Clone the Repository 

        git clone https://github.com/ihsan31415/InTeRRoR.git
        cd InTeRRoR
2. Install Dependencies

Make sure you have `arduino-cli` and required Python packages installed.


Python libraries 

    pip install python-telegram-bot google-generativeai nest-asyncio

3. Configuring the Code
Open ras.py and replace the following placeholders with your actual credentials:
    
        YOUR_MODEL = <your_model>
        YOUR_API_KEY = <your_api_key>
        YOUR_TELE_TOKEN = <your_telegrambot_token>

Run the Bo`
 
Run the Python script to start the Telegram bot.

    python ras.py

    Interact with the Bot

    Send instructions to the Telegram bot to generate and upload code to the Arduino.

Source

    Gemini LLM : https://aistudio.google.com/app/apikey \
    Raspberry Pi Zero 2 W : https://datasheets.raspberrypi.com/rpizero2/raspberry-pi-zero-2-w-product-brief.pdf \
    FreeCAD : https://wiki.freecad.org/download \
    TinkerCAD : https://www.tinkercad.com \
    Telegram Bot API : https://core.telegram.org/bots/api \
    Arduino : https://docs.arduino.cc/resources/datasheets/A000066-datasheet.pdf

  
