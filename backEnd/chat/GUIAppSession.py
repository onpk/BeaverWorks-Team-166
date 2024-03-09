import sys
import json
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QTextEdit, QVBoxLayout, QWidget, QLabel, \
    QStackedWidget, QComboBox
from PyQt5.QtGui import QFont, QColor, QPalette
from PyQt5.QtCore import Qt, QThread, pyqtSignal
import speech_recognition as sr
from transformers import GPT2LMHeadModel, GPT2Tokenizer
import torch
import time
from gtts import gTTS
import os
from random import choice

#category = sys.argv[1]     CATEGORY!

# Define the scenarios list
scenarios = [
    """During lunchtime at school, a group of friends are sitting together at a table in the cafeteria. They are discussing their plans for an upcoming school project and trying to figure out who will be responsible for which tasks. One friend suggests that they should all work together on the project to make it easier and more fun. Another friend disagrees and thinks they should divide the tasks evenly to ensure a fair distribution of workload. As the debate continues, other students at nearby tables start to take notice and offer their opinions on the best approach. The group of friends ultimately come to a compromise and decide to divide the tasks fairly while also working collaboratively on the project. This scenario highlights the importance of communication and teamwork in a school setting."""
]


class SpeechRecognitionThread(QThread):
    speech_detected = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()

        # Adjust the recognizer sensitivity
        self.recognizer.energy_threshold = 1000  # You may need to adjust this value based on your environment
        self.is_running = True

    def stop_recording(self):
        self.is_running = False

    def run(self):
        with self.microphone as source:
            self.recognizer.adjust_for_ambient_noise(source)

            # Adjust phrase time limit for real-time processing
            while self.is_running:
                audio = self.recognizer.listen(source, phrase_time_limit=3)  # Adjust as needed
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

        self.title_label = QLabel("Social Scenario Practice")
        self.title_label.setFont(QFont('Arial', 20))
        self.layout.addWidget(self.title_label, alignment=Qt.AlignCenter)

        self.button_layout = QVBoxLayout()
        self.layout.addLayout(self.button_layout)

        self.start_session_button = QPushButton("Start Session")
        self.start_session_button.clicked.connect(self.start_session)
        self.button_layout.addWidget(self.start_session_button)

        self.quit_button = QPushButton("Quit")
        self.quit_button.clicked.connect(self.close)
        self.button_layout.addWidget(self.quit_button)

        self.stacked_widget = QStackedWidget()
        self.layout.addWidget(self.stacked_widget)

        self.main_page_widget = QWidget()
        self.stacked_widget.addWidget(self.main_page_widget)

        self.recording_page_widget = QWidget()
        self.recording_page_layout = QVBoxLayout()
        self.recording_page_widget.setLayout(self.recording_page_layout)
        self.stacked_widget.addWidget(self.recording_page_widget)

        self.speech_thread = SpeechRecognitionThread()
        self.speech_thread.speech_detected.connect(self.process_input)

        self.is_recording = False
        self.recorded_audio = ""
        self.last_audio_time = time.time()

        self.text_edit = QTextEdit()
        self.recording_page_layout.addWidget(self.text_edit)

        self.current_scenario = None

        # Initialize GPT-2 model and tokenizer
        self.tokenizer = GPT2Tokenizer.from_pretrained("gpt2")
        self.model = GPT2LMHeadModel.from_pretrained("gpt2")

    def start_session(self):
        self.stacked_widget.setCurrentWidget(self.recording_page_widget)
        self.text_edit.clear()
        self.recorded_audio = ""
        self.is_recording = True
        self.speech_thread.start()

        selected_scenario = choice(scenarios)
        self.text_edit.append(f"<font color='blue'><b>Scenario:</b></font> {selected_scenario}")

        # Extracting a dialogue from the scenario
        dialogue = "One friend suggests that they should all work together on the project to make it easier and more fun."
        self.text_edit.append(f"<font color='green'><b>AI:</b></font> {dialogue}")

        tts = gTTS(text=dialogue, lang='en')
        tts.save("dialogue.mp3")
        os.system("mpg123 dialogue.mp3")

    def process_input(self, response):
        self.recorded_audio += response + " "
        self.text_edit.append(f"<font color='blue'><b>User (Recorded):</b></font> {response}")

        if time.time() - self.last_audio_time > 10:
            self.speech_thread.stop_recording()
            self.is_recording = False
            self.last_audio_time = time.time()
            self.get_ai_response()  # Trigger AI response immediately after user response

    def generate_response(self, input_text):
        input_ids = self.tokenizer.encode(input_text, return_tensors="pt")
        output = self.model.generate(input_ids, max_length=1000, num_return_sequences=1)
        generated_text = self.tokenizer.decode(output[0], skip_special_tokens=True)
        return generated_text

    def get_ai_response(self):
        # Get the user's input prompt from the text edit widget
        user_input = self.text_edit.toPlainText()

        # Generate AI response
        ai_response = self.generate_response(user_input)

        # Save AI response as an audio file
        tts = gTTS(text=ai_response, lang='en')
        tts.save("ai_response.mp3")

        # Play the AI response immediately after generating it
        os.system("mpg123 ai_response.mp3")

        self.recorded_audio = ""
        self.last_audio_time = time.time()

    def closeEvent(self, event):
        if self.speech_thread.isRunning():
            self.speech_thread.stop_recording()
            self.speech_thread.wait()
        event.accept()


if __name__ == "__main__":
    app = QApplication(sys.argv)

    palette = app.palette()
    palette.setColor(QPalette.Window, QColor(240, 240, 240))
    palette.setColor(QPalette.WindowText, QColor(40, 40, 40))
    app.setPalette(palette)

    window = SocialScenarioApp()
    window.show()
    sys.exit(app.exec_())
