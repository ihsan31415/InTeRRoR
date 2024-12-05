import asyncio
from telegram import Update
from telegram.ext import Application, MessageHandler, filters, CallbackContext
import google.generativeai as genai
import subprocess
import re

components =  """
these are the components and the wiring for the pinout of the components to the arduino (we ONLY have that and additional libraries are just that so dont add more lib that that): 
L298N:
  - N1: 10
  - N2: 11
  - N3: 12
  - N4: 13
  - ENA: 5
  - ENB: 6
  - Library: L298N

HCSR04:
  - Trig: 2
  - Echo: 3
  - Library: NewPing

gy273_HMC5883L:
  - SDA: A4
  - SCL: A5
  - Library: Adafruit HMC5883 Unified

MPU6050:
  - SDA: A4
  - SCL: A5
  - Library: MPU6050

BUZZER:
  - Positive: 9
"""

genai.configure(api_key="")
model = genai.GenerativeModel("gemini-exp-1121")

def clean_code(text):
    # Regex to find content between '''cpp and '''
    match = re.search(r"```cpp(.*?)```", text, re.DOTALL)
    
    if match:
        return match.group(1).strip()  # Extract the content and remove surrounding spaces
    else:
        return "No match found."




def make_code(instruksi):
    instruksi = (
        "Generate an Arduino code for 2 wheeled robot based on the following objective: " + instruksi +
        " Only use the necessary components from the list below:\n\n" + components +
        "\nEnsure the code is concise, includes only required libraries, and outputs only the Arduino code without explanations."
    )
    model = genai.GenerativeModel(
        model_name='gemini-exp-1121',
        system_instruction=(
            "You are a C++ Arduino programmer for a 2 wheeled robot" 
            "you will be provided with what the user want the robot do" 
            "Use only the libraries and components relevant to the task specified in the instruction. " 
            + components +
            "Exclude unused components, avoid comments, and output only the final code."
            "the user might use indonesian"
        )
    )
    response = model.generate_content(instruksi)
    kode = response.text.strip()  # Remove extra whitespace
    kode = clean_code(kode)
    return kode




def compile_code(kode):
    #compile dengan arduino cli, jika eeror akan return error messege
    try:
        # Save the code to a temporary file
        with open("temp.ino", "w") as f:
            f.write(kode)

        # Compile the code using arduino-cli
        result = subprocess.run(["arduino-cli", "compile", "--fqbn", "arduino:avr:uno", "temp.ino"], 
                                capture_output=True, text=True)

        # Check if there is any error in the compilation process
        if result.returncode != 0:
            return False, result.stderr.strip()  # Compilation failed, return the error message
        return True, ""  # Compilation succeeded
    except Exception as e:
        return False, str(e)  # Handle any exception during the process


# tugas = membenarkan kode dengan input kode dan error message
def correct_code(kode, error_message,instruksi):
    model = genai.GenerativeModel(
        model_name='gemini-exp-1121',
        tools='code_execution',
        system_instruction=(
            "You are an Arduino C++ code corrector for a 2 wheeled robot that has "  + components +  " . and the objective is " + instruksi + 
            "You will be provided with an Arduino code that has a compilation error. Your task is to correct and make it compile-ready. "
        )
    )
    
    correcting_prompt = f"""
    The following Arduino code is invalid and failed to compile:
    {kode}
    error log/error messege : 
    """
    debug = correcting_prompt + error_message
    response = model.generate_content(debug)
    corrected_code = response.text.strip()
    corrected_code = clean_code(corrected_code)

    return corrected_code  # Return only the final corrected code


def upload_to_arduino(kode):
    port="/dev/ttyACM0"
    """Upload the provided Arduino code to the Arduino device using the Arduino CLI."""
    try:
        # Save the code to a temporary file
        with open("temp.ino", "w") as f:
            f.write(kode)

        # Upload the compiled code to the Arduino device
        upload_result = subprocess.run(
            ["arduino-cli", "upload", "--fqbn", "arduino:avr:uno", "--port", port, "temp.ino"],
            capture_output=True, text=True
        )

        if upload_result.returncode != 0:
            return False, upload_result.stderr.strip()  # Upload failed, return error message

        return True, "Upload successful"  # Successful upload message
    except Exception as e:
        return False, str(e)  # Handle any exception during the process

# Define a function to handle text messages
async def echo(update: Update, context: CallbackContext) -> None:
    # Get the text from the message and send it back to the user
    #menerima teks dari user
    instruksi = update.message.text

    await update.message.reply_text(f'{"excuting..."}')
    await update.message.reply_text(f'{"genrating code..."}')
    
    #gemini mulai membuat kode
    kode = make_code(instruksi)
    
    await update.message.reply_text(f'{"verifying code..."}')
    await update.message.reply_text(f'{kode}')
    #verifikasi dengan compile ke arduino cli
    not_uploaded = True
    while(not_uploaded):
        valid, error_message = compile_code(kode)
        if valid :
            uploaded, error_upload  = upload_to_arduino(kode)
            if uploaded:
                await update.message.reply_text(f'{"code uploaded!"}')
                not_uploaded = False
            else:
                await update.message.reply_text(f'{"failed to upload!"}')
                await update.message.reply_text(f'{"correcting code!"}')
                await update.message.reply_text(f'{kode}')
                await update.message.reply_text(f'{error_upload}')
                kode = correct_code(kode,error_upload, instruksi)
        else :
            await update.message.reply_text(f'{"failed to compile!"}')
            await update.message.reply_text(f'{"correcting code!"}')
            await update.message.reply_text(f'{kode}')
            await update.message.reply_text(f'{error_message}')
            kode = correct_code(kode,error_message,instruksi)


async def main():
    # Replace 'YOUR_TOKEN' with the token you received from BotFather
    application = Application.builder().token("").build()

    # Create a MessageHandler that listens for text messages
    text_handler = MessageHandler(filters.TEXT & ~filters.COMMAND, echo)

    # Add the handler to the application
    application.add_handler(text_handler)

    # Start the bot to receive updates
    await application.run_polling()

# If running in Jupyter, use the following to start the bot
if __name__ == '__main__':
    import nest_asyncio
    
    
    nest_asyncio.apply()  # This allows nested event loops in Jupyter
    asyncio.run(main())  # This runs the main function within the asyncio event loop