# import speech_recognition as sr
# import pyttsx3
# import dateparser
# from datetime import datetime
# import threading
# import logging

# # Set up logging
# logging.basicConfig(level=logging.DEBUG)
# logger = logging.getLogger(__name__)

# # Initialize speech recognition and TTS with a lock
# listener = sr.Recognizer()
# engine = pyttsx3.init()
# voices = engine.getProperty('voices')
# engine.setProperty('voice', voices[1].id)  # Female voice
# speech_lock = threading.Lock()

# # Configure speech recognition settings
# listener.dynamic_energy_threshold = True
# listener.energy_threshold = 300
# listener.pause_threshold = 0.8
# listener.phrase_time_limit = 8
# listener.non_speaking_duration = 0.5

# def talk(text):
#     """Speak the given text using text-to-speech."""
#     with speech_lock:
#         logger.debug(f"Speaking: {text}")
#         engine.say(text)
#         engine.runAndWait()

# def take_command(prompt, expected_type="text"):
#     """Capture voice input and convert it to the expected type."""
#     max_attempts = 3  # Limit retry attempts
#     attempts = 0

#     while attempts < max_attempts:
#         talk(prompt)
#         print(prompt)
#         logger.info(f"Prompt: {prompt}")
#         try:
#             with sr.Microphone() as source:
#                 listener.adjust_for_ambient_noise(source, duration=2)
#                 logger.debug("Listening...")
#                 print("Listening...")
#                 voice = listener.listen(source)
#                 command = listener.recognize_google(voice, language='en-US').lower()
#                 logger.info(f"User said: {command}")
#                 print(f"User said: {command}")

#                 if expected_type == "time":
#                     parsed = dateparser.parse(command, settings={'TIMEZONE': 'UTC'})
#                     if parsed:
#                         logger.debug(f"Parsed time: {parsed.time()}")
#                         return parsed.time()
#                     else:
#                         talk("I couldn't understand the time. Please try again.")
#                 elif expected_type == "date":
#                     parsed = dateparser.parse(command, settings={'PREFER_DATES_FROM': 'future'})
#                     if parsed:
#                         logger.debug(f"Parsed date: {parsed.date()}")
#                         return parsed.date()
#                     else:
#                         talk("I couldn't understand the date. Please try again.")
#                 elif expected_type == "text":
#                     logger.debug(f"Text input: {command}")
#                     return command

#         except sr.UnknownValueError:
#             logger.warning("Speech recognition failed: UnknownValueError")
#             talk("Sorry, I didn't catch that. Please repeat.")
#         except sr.RequestError as e:
#             logger.error(f"Speech recognition request failed: {e}")
#             talk("Sorry, there was an issue with the speech service. Please try again.")
#         except Exception as e:
#             logger.error(f"Unexpected error: {e}")
#             talk("An error occurred. Please try again.")

#         attempts += 1
#         if attempts < max_attempts:
#             talk(f"Please try again. Attempt {attempts + 1} of {max_attempts}.")
#         else:
#             logger.warning(f"Max attempts ({max_attempts}) reached for prompt: {prompt}")
#             talk("I couldn't get that after several tries.")
#             return None

# def create_voice_reminder():
#     """Handle the voice-based reminder creation process."""
#     logger.info("Starting voice reminder creation")
    
#     task = take_command("Hey, what's the task?", "text")
#     if task is None:
#         logger.error("Failed to get task")
#         return None, "Failed to get task"

#     task_time = take_command("At what time should I remind you?", "time")
#     if task_time is None:
#         logger.error("Failed to get task time")
#         return None, "Failed to get time"

#     task_date = take_command("On which date should I remind you?", "date")
#     if task_date is None:
#         logger.error("Failed to get task date")
#         return None, "Failed to get date"

#     reminder_type = take_command("Should I remind you once or daily?", "text")
#     if reminder_type is None:
#         logger.error("Failed to get reminder type")
#         return None, "Failed to get reminder type"

#     if not all([task, task_time, task_date, reminder_type]):
#         logger.error("Invalid input received")
#         return None, "Invalid input received"

#     confirmation = f"Reminder set for '{task}' on {task_date.strftime('%B %d')} at {task_time.strftime('%I:%M %p')}, {reminder_type}."
#     talk(confirmation)
#     logger.info(f"Confirmation: {confirmation}")
    
#     return {
#         'task': task,
#         'task_time': task_time,
#         'task_date': task_date,
#         'reminder_type': reminder_type
#     }, confirmation

# # For testing purposes
# if __name__ == "__main__":
#     result, msg = create_voice_reminder()
#     print(f"Result: {result}, Message: {msg}")

















# import speech_recognition as sr
# import pyttsx3
# import dateparser
# from datetime import datetime

# # Initialize speech recognition and text-to-speech engine
# listener = sr.Recognizer()
# engine = pyttsx3.init()
# engine.setProperty('voice', engine.getProperty('voices')[1].id)

# # Configure speech recognition settings for better performance
# listener.dynamic_energy_threshold = True
# listener.energy_threshold = 300  
# listener.pause_threshold = 0.8  
# listener.phrase_time_limit = 8  
# listener.non_speaking_duration = 0.5  

# def talk(text):
#     """Speak out the given text."""
#     engine.say(text)
#     engine.runAndWait()

# def take_command(prompt, expected_type="text"):
#     """
#     Keep asking the user until valid input is received.
#     Optimized for distant voice input with improved noise cancellation.
#     """
#     while True:
#         talk(prompt)
#         print(prompt)
#         command = ""

#         try:
#             with sr.Microphone() as source:
#                 listener.adjust_for_ambient_noise(source, duration=2)
#                 print("Listening...")
#                 voice = listener.listen(source)
#                 command = listener.recognize_google(voice, language='en-US').lower()
#                 print(f"User said: {command}")

#                 # Process input based on expected type
#                 if expected_type == "time":
#                     parsed_time = parse_time(command)
#                     if parsed_time:
#                         return parsed_time
#                 elif expected_type == "date":
#                     parsed_date = parse_date(command)
#                     if parsed_date:
#                         return parsed_date
#                 elif expected_type == "text":
#                     return command

#         except sr.UnknownValueError:
#             talk("Sorry, I didn't catch that. Please repeat.")
#         except sr.RequestError:
#             talk("Could not connect to the speech recognition service. Check your internet.")
#             return None
#         except Exception as e:
#             print(f"Error: {e}")

#         talk("Please try again.")

# def parse_time(command):
#     """Convert spoken time into a datetime.time object using dateparser."""
#     parsed = dateparser.parse(command, settings={'TIMEZONE': 'UTC'})

#     if parsed:
#         return parsed.time()
    
#     talk("I couldn't understand the time. Please say something like '5 PM' or '10:30 AM'.")
#     return None

# def parse_date(command):
#     """Convert spoken date into a datetime.date object using dateparser."""
#     parsed = dateparser.parse(command, settings={'PREFER_DATES_FROM': 'future'})

#     if parsed:
#         return parsed.date()

#     talk("I couldn't understand the date. Please say something like 'March 12', 'next Monday', or 'tomorrow'.")
#     return None

# def run_voice_assistant():
#     """Main function to take inputs and confirm back with correct data types."""
    
#     task = take_command("What should I remind you about?", "text")
#     task_time = take_command("At what time should I remind you?", "time")
#     task_date = take_command("On which date should I remind you?", "date")
#     reminder_type = take_command("Should I remind you once or daily?", "text")

#     confirmation_text = (f"You want me to remind you about '{task}' on {task_date.strftime('%B %d')} "
#                          f"at {task_time.strftime('%I:%M %p')}, and I will remind you {reminder_type}.")
    
#     talk(confirmation_text)
#     print(confirmation_text)

#     return {
#         "task": task,
#         "task_time": task_time.strftime('%H:%M:%S'),
#         "task_date": task_date.strftime('%Y-%m-%d'),
#         "reminder_type": reminder_type
#     }

# # Run the voice assistant when executed as a script
# if __name__ == "__main__":
#     run_voice_assistant()








import speech_recognition as sr
import pyttsx3
from RemindHer_app.models import VoiceResponse, User

# Initialize global objects
listener = sr.Recognizer()
engine = pyttsx3.init()  # Define engine globally
engine.setProperty('voice', engine.getProperty('voices')[1].id)

listener.dynamic_energy_threshold = True
listener.energy_threshold = 300
listener.pause_threshold = 0.8
listener.phrase_time_limit = 8
listener.non_speaking_duration = 0.5

def talk(text):
    global engine  # Declare global at the start
    print(f"Speaking: {text}")
    try:
        engine.say(text)
        engine.runAndWait()
    except RuntimeError as e:
        print(f"RuntimeError in talk: {e}")
        # Reinitialize engine if loop conflict occurs
        engine.stop()  # Stop current loop
        engine = pyttsx3.init()  # Reassign global engine
        engine.setProperty('voice', engine.getProperty('voices')[1].id)
        engine.say(text)
        engine.runAndWait()

def take_command(prompt):
    talk(prompt)
    print(f"Prompt: {prompt}")
    try:
        with sr.Microphone() as source:
            listener.adjust_for_ambient_noise(source, duration=2)
            print("Listening...")
            voice = listener.listen(source)
            command = listener.recognize_google(voice, language='en-US').lower()
            print(f"User said: {command}")
            return command
    except Exception as e:
        print(f"Error in take_command: {e}")
        talk("Sorry, something went wrong. Please try again.")
        return None

def run_questionnaire(user_id):
    print(f"Starting questionnaire for user_id: {user_id}")
    responses = {}
    
    try:
        user = User.objects.get(id=user_id)
        print(f"User found: {user.email}")
    except User.DoesNotExist:
        print(f"User with ID {user_id} not found.")
        return responses

    questions = [
        "What is your name?",
        "How old are you?",
        "What is your favorite color?",
        "Where do you live?",
    ]

    for question in questions:
        response = None
        attempts = 0
        max_attempts = 3
        while response is None and attempts < max_attempts:
            response = take_command(question)
            attempts += 1
            if response is None:
                talk("Let's try that again.")
        response = response if response else "No response after retries"
        VoiceResponse.objects.create(user=user, question=question, response=response)
        responses[question] = response
        print(f"Stored: {question} - {response}")

    confirmation = f"Here’s what {user.name} said: "
    for q, r in responses.items():
        confirmation += f"{q} - {r}. "
    talk(confirmation)
    print(confirmation)
    return responses

if __name__ == "__main__":
    run_questionnaire(user_id=1)