import speech_recognition as sr
import pygame
import threading
import signal
from gtts import gTTS
import sys
from openai import OpenAI
import re
from pathlib import Path
from assistants import assistant
import os
import time
from transformers import pipeline, AutoTokenizer, AutoModelForCausalLM

print("Downloading AI model")
#nlp = pipeline("conversational", model="microsoft/DialoGPT-medium")
os.environ["TOKENIZERS_PARALLELISM"] = "true"
tokenizer = AutoTokenizer.from_pretrained("microsoft/DialoGPT-medium")
model = AutoModelForCausalLM.from_pretrained("microsoft/DialoGPT-medium")
print("done")

go_to_sleep = False

openAiClient = OpenAI(
    # This is the default and can be omitted
    #api_key=os.getenv('chatgptkey')
)

screen = None
current_sound = None
#screen_width, screen_height = 640, 480
screen_width, screen_height = 480, 320

def init_pygame():
    global screen
    # Initialize Pygame for facial animation
    if not screen:
        pygame.init()
        
        screen = pygame.display.set_mode((screen_width, screen_height), pygame.DOUBLEBUF)
        #screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
        pygame.display.set_caption('Smart Kiosk')

def close_pygame():
    global screen
    global current_sound
    if current_sound:
        current_sound.stop()

    if screen:
        screen.fill((0, 0, 0))  # Fill screen with black
        pygame.display.flip()
    pygame.quit()
    screen = None
    

    # Load face images (ensure these images exist in the correct directory)
face_image = pygame.image.load('images/face.png')
face_image = pygame.transform.scale(face_image, (screen_width, screen_height))
mouth_open_image = pygame.image.load('images/mouth_open.png')
mouth_open_image = pygame.transform.scale(mouth_open_image, (screen_width, screen_height))
mouth_closed_image = pygame.image.load('images/mouth_closed.png')
mouth_closed_image = pygame.transform.scale(mouth_closed_image, (screen_width, screen_height))

response_sound_file = "sounds/response.mp3"
is_talking = False

# Function to display facial animations
def display_face(talking=False, startup=True):
    global screen
    if (screen is not None):
        screen_width, screen_height = screen.get_size()
        face_image_width, face_image_height = face_image.get_size()

        # Calculate the position to center the face image
        x = (screen_width - face_image_width) // 2
        y = (screen_height - face_image_height) // 2

        #if screen is not None:
        screen.fill((255, 255, 255))  # Clear screen with white background
        screen.blit(face_image, (x, y))  # Display face image at (0, 0)
        
        if talking:
            screen.blit(mouth_open_image, (x, y))  # Display open mouth image (adjust position as needed)
        elif not startup:
            screen.blit(mouth_closed_image, (x, y))  # Display closed mouth image (adjust position as needed)
        
        pygame.display.flip()  # Update display to show changes

# Global event to control background listening thread
#listening_event = threading.Event()
#listening_event.set()  # Initialize event as set (listening)

# Flag to indicate if the application should exit
exit_flag = threading.Event()
exit_flag.clear()  # Initially clear the flag

# Initialize speech recognizer and microphone
recognizer = sr.Recognizer()
microphone = sr.Microphone()

# Background thread for continuous speech recognition
def background_listen():
    global exit_flag
    global last_activity_time
    while not exit_flag.is_set():
        text = recognize_speech()
        if text and is_greeting(text):
            #response = "You said: " + text
            #response = text
            last_activity_time = time.time()
            # if not go_to_sleep:
            #     respond_with_audio("Uno momento")
            #     display_face(startup=True)
            response =  ask_gpt(text)
            respond_with_audio(response)
        else:
            print("command is not for us")

# Function to handle speech recognition
def recognize_speech():
    global exit_flag
    while not exit_flag.is_set():
        with microphone as source:
            recognizer.adjust_for_ambient_noise(source)
            print("Listening...")
            try:
                # Listen for audio with a timeout of 1 second
                audio = recognizer.listen(source, timeout=1)
            except sr.WaitTimeoutError:
                continue  # Continue if timeout occurs
        
        if exit_flag.is_set():
            break  # Exit the loop if exit flag is set

        try:
            print("Analyzing speach...")
            recognized_text = recognizer.recognize_google(audio)
            print(f"You said: {recognized_text}")
            return recognized_text.lower()
        except sr.UnknownValueError:
            print("Sorry, I did not understand that.")
            return ""
        except sr.RequestError:
            print("Could not request results; check your network connection.")
            return ""
        
    return ""

# Function to respond using speech synthesis (with pygame.mixer.Sound)
def respond_with_audio(text, startup=False):
        global last_activity_time  
        global current_sound

        pygame.mixer.init()
        pygame.mixer.music.set_endevent(pygame.constants.USEREVENT)  # Event for when music finishes

        assistant.conert_to_audio(text, response_sound_file)

        # Load the response audio file
        current_sound = pygame.mixer.Sound(response_sound_file)
        
        # Play the audio
        current_sound.play()

        # Calculate the duration of the audio to sync with animation
        audio_length_ms = int(current_sound.get_length() * 1000)

        # Animate the mouth while the audio is playing
        #animate_mouth(audio_length_ms)

   

def is_greeting(text):
    greetings = r"^(hi|hello|hey) assistant\b"
    return re.search(greetings, text.lower())

def animate_mouth(audio_length_ms):
    global last_activity_time   
    global is_talking
    global screen

    start_time = pygame.time.get_ticks()
    current_time = start_time

    last_activity_time = time.time()
    is_talking = True

    while screen is not None and current_time - start_time < audio_length_ms:
        # Calculate whether the mouth should be open or closed based on time
        if (current_time - start_time) % 1000 < 300:
            display_face(talking=True)
        else:
            display_face(talking=False)

        # Calculate elapsed time for smooth animation
        elapsed_time = current_time - start_time
        current_time = pygame.time.get_ticks()

        # Adjust the animation speed dynamically
        pygame.time.delay(10)  # Adjust this delay to control animation smoothness

    # Ensure mouth is closed at the end
    display_face(talking=False)
    last_activity_time = time.time()
    is_talking = False

def ask_gpt(query):
    try:
        print("Calling AI...")
        
        # conversation = Conversation(query)
        # response = nlp(conversation)
        # response = response.generated_responses[-1]
        #response = assistant.handle_prompt(query)
        # Tokenize the input query
        print("start tokenizer encoding...")
        input_ids = tokenizer.encode(query + tokenizer.eos_token, return_tensors='pt')

        attention_mask = input_ids.ne(tokenizer.pad_token_id).long()
        
        # Generate a response from the model
        print("start model generate")
        output_ids = model.generate(input_ids, attention_mask=attention_mask, max_length=1000, pad_token_id=tokenizer.eos_token_id)

        # Decode the generated response into a readable string
        print("start decoding")
        response = tokenizer.decode(output_ids[:, input_ids.shape[-1]:][0], skip_special_tokens=True)
        
        print("finished")
        return response
    
    except Exception as e:
        print(f"Error: {e}")
        

# Signal handler for Ctrl+C
def signal_handler(sig, frame):
    global exit_flag
    print("Ctrl+C pressed. Exiting...")
    exit_flag.set()  # Set the flag to stop background listening
    sys.exit(0)  # Exit the program

# Set up signal handler for Ctrl+C
signal.signal(signal.SIGINT, signal_handler)

def game_loop(first_run=False):
    global running
    global last_activity_time
    global is_talking
    global go_to_sleep

    if first_run:
        #respond_with_audio("Welcome to our beautiful hotel. How can I assist you today?", True)
        respond_with_audio("Hello", True)
        display_face(startup=True) 
    # else:
    #     init_pygame()
    #     respond_with_audio("Uno momento")
    #     display_face(startup=True)
    #     time.sleep(0.5)
    #     #display_face(startup=True)
        

    while running: 
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # Check if inactive for more than X seconds
        if go_to_sleep and not is_talking and time.time() - last_activity_time > 30:
            print("No activity detected. Closing the game.")
            running = False

    close_pygame()


# Main loop (for handling Pygame events, not directly related to speech synthesis)
try:
    init_pygame()
    running = True
    last_activity_time = time.time()

    # Start background listening thread
    listening_thread = threading.Thread(target=background_listen)
    listening_thread.daemon = True 
    listening_thread.start()

    first_run = True
    while True:
        if exit_flag.is_set():
            running = False
            break
        
        if running:
            game_loop(first_run)
            first_run = False            
        elif not go_to_sleep:
            break

        while go_to_sleep and not running:
            #print("Current time: " + time.ctime(time.time()) + " Last activity: " + time.ctime(last_activity_time))
            if time.time() - last_activity_time <= 5:
                running = True
                print("restore game")
                break
            time.sleep(1)

finally:
    # Clean up resources on program exit
    exit_flag.set()  
    #listening_event.clear()  # Stop background listening thread
    listening_thread.join()  # Wait for the thread to terminate
    #pygame.quit()  # Quit Pygame
    close_pygame()
