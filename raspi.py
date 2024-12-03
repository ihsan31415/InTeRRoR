import asyncio
from telegram import Update
from telegram.ext import Application, MessageHandler, filters, CallbackContext
import google.generativeai as genai
import subprocess

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
  - Library: Adafruit_HMC5883_Unified

MPU6050:
  - SDA: A4
  - SCL: A5
  - Library: MPU6050

BUZZER:
  - Positive: 9
"""

genai.configure(api_key="")
model = genai.GenerativeModel("gemini-1.5-flash")

def make_code(instruksi):
    instruksi = (
        "Generate an Arduino code based on the following objective: " + instruksi +
        " Only use the necessary components from the list below:\n\n" + components +
        "\nEnsure the code is concise, includes only required libraries, and outputs only the Arduino code without explanations."
    )
    model = genai.GenerativeModel(
        model_name='gemini-1.5-flash',
        system_instruction=(
            "You are a C++ Arduino programmer. Use only the libraries and components relevant to the task specified in the instruction. "
            "Exclude unused components, avoid comments, and output only the final code."
        )
    )
    response = model.generate_content(instruksi)
    kode = response.text.strip()  # Remove extra whitespace
    return kode




def compile_with_arduino_cli(kode):
    """Compile the provided Arduino code using the Arduino CLI to check for errors."""
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

def verify_and_correct_code(kode):
    max_attempts = 5  # Limit to prevent infinite loops
    attempts = 0

    model = genai.GenerativeModel(
        model_name='gemini-1.5-flash',
        tools='code_execution',
        system_instruction=(
            "You are an Arduino C++ code verifier and corrector. "
            "You will be provided with an Arduino code. Your task is to check if it is valid and compile-ready. "
            "If it is valid, return the code unchanged. If it is invalid, correct the code and return only the corrected Arduino code, "
            "without any explanations, comments, or additional text. Do not include any non-required libraries or components. "
            "Only output the corrected code, nothing else."
        )
    )

    while attempts < max_attempts:
        # Verify the code with Arduino CLI first
        is_valid, error_message = compile_with_arduino_cli(kode)

        if is_valid:
            print("Code is valid and ready for compilation.")
            break

        # If there are compilation errors, send the code to Gemini for correction
        print(f"Compilation failed with errors: {error_message}. Correcting the code...")
        
        # Send the code to Gemini for correction
        verification_prompt = f"""
        The following Arduino code is invalid and failed to compile:

        ```cpp
        {kode}
        ```

        Please correct it. Only output the corrected code, without any additional explanations or text.
        """
        
        response = model.generate_content(verification_prompt)
        corrected_code = response.text.strip()

        # Update the code with the corrected version and try again
        kode = corrected_code
        attempts += 1

    if attempts == max_attempts:
        print("Maximum correction attempts reached. Please review the last corrected version.")

    return kode  # Return only the final corrected code


def upload_to_arduino(kode, port="/dev/ttyACM0"):
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
    text_received = update.message.text
    await update.message.reply_text(f'{"excuting..."}')
    await update.message.reply_text(f'{"genrating code..."}')
    kode = make_code(text_received)
    
    await update.message.reply_text(f'{"verifying code..."}')

    verif = verify_and_correct_code(kode)
    await update.message.reply_text(f'{verif}')

    
    is_valid, compile_message = compile_with_arduino_cli(corrected_code)
    if is_valid:
        print("Code compiled successfully.")
        upload_success, upload_message = upload_to_arduino(corrected_code, port)
        if upload_success:
            print(upload_message)  # Successful upload message
        else:
            print(f"Upload failed: {upload_message}")  # Error message from upload attempt
    else:
        print(f"Compilation failed: {compile_message}")  # Compilation error message








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