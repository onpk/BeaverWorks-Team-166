import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QTextEdit, QVBoxLayout, QWidget, QLabel, QStackedWidget, QComboBox
from PyQt5.QtGui import QFont, QColor, QPalette
from PyQt5.QtCore import Qt, QThread, pyqtSignal
import speech_recognition as sr
import openai
import threading
import time
from gtts import gTTS
import os
import requests
from re import sub
from random import choice
import os

output_file_path = "conversation.json"

# Set up OpenAI API key
openai.api_key = "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"

# Define scenarios
scenarios = [
    """You're in the cafeteria during lunch break when 
    a classmate from your science class, walks over. He asks if he can sit with you and mentions he's curious about your opinion on the latest physics 
    experiment""",
    """ You're studying in the library when an art enthusiast approaches. She asks if the seat next to you is taken and mentions 
    she's been experimenting with watercolor techniques lately and would love to share her progress.""",
    # Add more scenarios as needed
]

# Initialize user with a default value
user = ""
assistant = ""
name = ""
intromessage = """You are an AI friend who is interacting with autistic children.
            Your goal is to engage them in a friendly and supportive conversation, incorporating role-playing scenarios to encourage social interaction. 
           Create a positive and inclusive environment, adapt to their preferences, and guide them through imaginative scenarios that foster communication and social skills. 
           Remember to be patient, understanding, and encouraging throughout the interaction."""
#user = [{"role": "user", "content": user_input}]
intromessage += """Your role-playing scenario is this: """ + choice(scenarios) + ". Please make your responses and messages based around this scenario."

# Load existing conversation from JSON file
if os.path.exists(output_file_path) and os.path.getsize(output_file_path) > 0:
    # print("aye")
    with open(output_file_path, 'r') as json_file:
        chat = json.load(json_file)
    for c in range(2, len(chat)):
        if chat[c]["role"] == "user":
            if "python -u" in chat[c]["content"]:
                pass
            else:
                user += chat[c]["content"]
        elif chat[c]["role"] == "assistant":
            assistant += chat[c]["content"]
        else:
            cont = chat[c]["content"]
            temp = cont.split()
            for i in temp:
                if i == "I'm":
                    name = sub(r'\W+', '', temp[temp.index(i) + 1])
            if ("apologize" or "sorry") in cont:
                pass
            else:
                assistant += cont

    intromessage += "These are previous messages you sent. Remember them as you write your responses. " + assistant + " These are the messages that the user sent. Remember these as well when you write your responses. " + user
    system = [{"role": "system", "content": intromessage}]
    user = [{"role": "user", "content": "Reintroduce yourself as " + name + ". Start a conversation with the user."}]
    chat = []

else:
    # If the JSON file is empty or doesn't exist, initialize the conversation with general questions
    # print("nay")
    system = [{"role": "assistant", "content": intromessage.strip()}]

    user = [{"role": "user", "content": "Introduce yourself with a name. Ask the user their age and tailor your responses appropriately."}]
    chat = []

class SpeechRecognitionThread(QThread):
    speech_detected = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()
        self.is_running = True

    def stop_recording(self):
        self.is_running = False

    def run(self):
        with self.microphone as source:
            self.recognizer.adjust_for_ambient_noise(source)
            while self.is_running:
                audio = self.recognizer.listen(source, phrase_time_limit=20)
                try:
                    response = self.recognizer.recognize_google(audio)
                    self.speech_detected.emit(response)
                except sr.UnknownValueError:
                    pass
                except sr.RequestError as e:
                    print(f"Could not request results from Google Speech Recognition service; {e}")

class SocialScenarioApp(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Social Scenario Practice")
        self.setGeometry(100, 100, 800, 600)

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        self.layout = QVBoxLayout()
        self.central_widget.setLayout(self.layout)

        # Add title label
        self.title_label = QLabel("Social Scenario Practice")
        self.title_label.setFont(QFont('Arial', 20))
        self.layout.addWidget(self.title_label, alignment=Qt.AlignCenter)

        # Add buttons
        self.button_layout = QVBoxLayout()
        self.layout.addLayout(self.button_layout)

        self.category_label = QLabel("Select Category:")
        self.button_layout.addWidget(self.category_label)

        self.category_combo = QComboBox()
        self.category_combo.addItem("School")
        self.category_combo.addItem("Friends")
        # Add more categories as needed
        self.button_layout.addWidget(self.category_combo)

        self.start_session_button = QPushButton("Start Session")
        self.start_session_button.clicked.connect(self.start_session)
        self.button_layout.addWidget(self.start_session_button)

        self.quit_button = QPushButton("Quit")
        self.quit_button.clicked.connect(self.close)
        self.button_layout.addWidget(self.quit_button)

        # Stacked widget for multiple pages
        self.stacked_widget = QStackedWidget()
        self.layout.addWidget(self.stacked_widget)

        # Add main page
        self.main_page_widget = QWidget()
        self.stacked_widget.addWidget(self.main_page_widget)

        # Add recording page
        self.recording_page_widget = QWidget()
        self.recording_page_layout = QVBoxLayout()
        self.recording_page_widget.setLayout(self.recording_page_layout)
        self.stacked_widget.addWidget(self.recording_page_widget)

        # Initialize speech recognition thread
        self.speech_thread = SpeechRecognitionThread()
        self.speech_thread.speech_detected.connect(self.process_input)

        # Initialize variables
        self.is_recording = False
        self.recorded_audio = ""
        self.last_audio_time = time.time()

        # Text edit for displaying conversation
        self.text_edit = QTextEdit()
        self.recording_page_layout.addWidget(self.text_edit)

    def start_session(self):
        # Switch to recording page
        self.stacked_widget.setCurrentWidget(self.recording_page_widget)
        self.text_edit.clear()  # Clear text_edit
        self.recorded_audio = ""
        self.is_recording = True
        self.speech_thread.start()

        # Get selected category
        selected_category = self.category_combo.currentText()

        # Provide social scenario based on the selected category
        scenario = self.get_social_scenario(selected_category)
        self.text_edit.append(f"<font color='blue'><b>AI:</b></font> {scenario}")

        # Speak the scenario
        tts = gTTS(text=scenario, lang='en')
        tts.save("scenario.mp3")
        os.system("mpg123 scenario.mp3")

    def process_input(self, response):
        self.recorded_audio += response + " "
        self.text_edit.append(f"<font color='blue'><b>User (Recorded):</b></font> {response}")

        if time.time() - self.last_audio_time > 20:
            self.speech_thread.stop_recording()
            self.is_recording = False
            self.last_audio_time = time.time()
            self.get_ai_response()

    def get_ai_response(self):
        # Call OpenAI API with recorded audio
        response = openai.Completion.create(
            engine="text-davinci-002",
            prompt=self.recorded_audio,
            temperature=0.7,
            max_tokens=50
        )

        # Speak AI response
        ai_response = response.choices[0].text.strip()
        self.text_edit.append(f"<font color='green'><b>AI:</b></font> {ai_response}")
        tts = gTTS(text=ai_response, lang='en')
        tts.save("ai_response.mp3")
        os.system("mpg123 ai_response.mp3")

        # Reset variables
        self.recorded_audio = ""
        self.last_audio_time = time.time()

    def get_social_scenario(self, category):
        try:
            # Define the prompt based on the selected category
            prompt = f"Generate a social scenario for {category}."

            # Call OpenAI API to generate the scenario
            response = openai.Completion.create(
                engine="text-davinci-002",
                prompt=prompt,
                temperature=0.7,
                max_tokens=200
            )

            # Extract the scenario from the response
            scenario = response.choices[0].text.strip()
            return scenario

        except Exception as e:
            print(f"Failed to fetch scenario from API: {e}")
            return "This is a sample social scenario for the selected category."

    def closeEvent(self, event):
        if self.speech_thread.isRunning():
            self.speech_thread.stop_recording()
            self.speech_thread.wait()
        event.accept()

if __name__ == "__main__":
    app = QApplication(sys.argv)

    # Set application palette
    palette = app.palette()
    palette.setColor(QPalette.Window, QColor(240, 240, 240))
    palette.setColor(QPalette.WindowText, QColor(40, 40, 40))
    app.setPalette(palette)

    window = SocialScenarioApp()
    window.show()
    sys.exit(app.exec_())
