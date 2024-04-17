import json
import sys
import os
import time
from random import choice
from re import sub
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QTextEdit, QVBoxLayout, QWidget, QLabel, \
    QStackedWidget, QComboBox
from PyQt5.QtGui import QFont, QColor, QPalette
from PyQt5.QtCore import Qt, QThread, pyqtSignal
import speech_recognition as sr
import openai
import time
from gtts import gTTS

import os
from random import choice
from secretkey import keyval
from vtt import VTT
from re import sub

# Set up OpenAI API key
openai.api_key = keyval

# Define the scenarios list
scenarios = [
    "During lunchtime at school, a group of friends are sitting together at a table in the cafeteria. They are "
    "discussing their plans for an upcoming school project and trying to figure out who will be responsible for which "
    "tasks. One friend suggests that they should all work together on the project to make it easier and more fun. "
    "Another friend disagrees and thinks they should divide the tasks evenly to ensure a fair distribution of "
    "workload. As the debate continues, other students at nearby tables start to take notice and offer their opinions "
    "on the best approach. The group of friends ultimately come to a compromise and decide to divide the tasks fairly "
    "while also working collaboratively on the project."
]

intromessage = "You are an AI friend who is interacting with autistic children. Your goal is to engage them in a " \
               "friendly and supportive conversation, incorporating role-playing scenarios to encourage social " \
               "interaction. Create a positive and inclusive environment, adapt to their preferences, and guide them " \
               "through imaginative scenarios that foster communication and social skills. Remember to be patient, " \
               "understanding, and encouraging throughout the interaction."

# Define the default category if no command line arguments are provided
default_category = "Default Category"

# Load existing conversation from JSON file
output_file_path = "conversation.json"
if os.path.exists(output_file_path) and os.path.getsize(output_file_path) > 0:
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
    system = [{"role": "assistant", "content": intromessage.strip()}]

    user = [{"role": "user",
             "content": "Introduce yourself with a name. Ask the user their age and tailor your responses "
                        "appropriately."}]
    chat = []


class SpeechRecognitionThread(QThread, VTT):
    speech_detected = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()
        self.is_running = True

    def stop_recording(self):
        self.stopspeak()

    def run(self):
        aresponse = self.speak()
        self.speech_detected.emit(aresponse)


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

        self.category_label = QLabel("Select Category:")
        self.button_layout.addWidget(self.category_label)

        self.category_combo = QComboBox()

        # Check if command line arguments are provided
        if len(sys.argv) > 1:
            self.category_combo.addItem(sys.argv[1])
        else:
            self.category_combo.addItem(default_category)

        self.button_layout.addWidget(self.category_combo)

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
        self.chat = []

    def start_session(self):
        self.stacked_widget.setCurrentWidget(self.recording_page_widget)
        self.text_edit.clear()
        self.recorded_audio = ""
        self.is_recording = True
        self.speech_thread.start()

        selected_category = self.category_combo.currentText()

        # Extracting a dialogue from the scenario dynamically using OpenAI
        dialogue = self.chat_with_openai(
            "I want actual dialogue. Don't give too much dialogue for the entire scnerio as I need oppurutnity for me to speak as well.")
        self.text_edit.append(f"<font color='green'><b>AI:</b></font> {dialogue}")

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
            self.get_ai_response()  # Trigger AI response immediately after user response

    def getprev(self):
        user = ""
        assistant = ""
        with open("conversation.json", 'r') as json_file:
            self.chat = json.load(json_file)
        for c in range(2, len(self.chat)):
            if self.chat[c]["role"] == "user":
                if "python -u" in self.chat[c]["content"]:
                    pass
                else:
                    user += self.chat[c]["content"]
            elif self.chat[c]["role"] == "assistant":
                assistant += self.chat[c]["content"]
            else:
                cont = self.chat[c]["content"]
                temp = cont.split()
                for i in temp:
                    if i == "I'm":
                        name = sub(r'\W+', '', temp[temp.index(i) + 1])
                if ("apologize" or "sorry") in cont:
                    pass
                else:
                    assistant += cont
        return [user, assistant]

    import os
    import json
    from random import choice

    def setupchat(self):
        # Check if the conversation file exists
        if not os.path.exists("conversation.json"):
            # If it doesn't exist, create it with default content
            with open("conversation.json", 'w') as json_file:
                json_file.write("[]")  # Writing an empty list as default content

        # Load existing conversation from JSON file
        with open("conversation.json", 'r') as json_file:
            self.chat = json.load(json_file)

        # Define scenarios list
        scenarios = ["Your list of scenarios here..."]

        # Define intro message
        intromessage = "Your intro message here..."

        # Add previous messages to the intro message if the conversation file is not empty
        if self.chat:
            user, assistant = self.getprev()
            intromessage += f"These are previous messages you sent. Remember them as you write your responses. {assistant} These are the messages that the user sent. Remember these as well when you write your responses. {user}"

        return intromessage

    import os
    import json
    from random import choice

    def setupchat(self):
        # Check if the conversation file exists
        if not os.path.exists("conversation.json"):
            # If it doesn't exist, create it with default content
            with open("conversation.json", 'w') as json_file:
                json_file.write("[]")  # Writing an empty list as default content

        # Load existing conversation from JSON file
        with open("conversation.json", 'r') as json_file:
            self.chat = json.load(json_file)

        # Define scenarios list
        scenarios = [
            "You're in the cafeteria during lunch break when a classmate from your science class walks over. He asks if he can sit with you and mentions he's curious about your opinion on the latest physics experiment.",
            "You're studying in the library when an art enthusiast approaches. She asks if the seat next to you is taken and mentions she's been experimenting with watercolor techniques lately and would love to share her progress.",
            "You're working on a group project in the classroom when Alex, a classmate known for their musical talents, comes over. They ask if they can join your group and suggest incorporating music into the presentation since they recently composed a piece inspired by the topic.",
            # Add more scenarios as needed
        ]

        # Define intro message
        intromessage = "Welcome to the chat application! This is an introduction message. Here, you can engage in friendly conversations with our AI assistant. Please select a scenario from the dropdown menu to get started."

        # Add previous messages to the intro message if the conversation file is not empty
        if self.chat:
            user, assistant = self.getprev()
            intromessage += f"\n\nThese are previous messages you sent. Remember them as you write your responses. {assistant} These are the messages that the user sent. Remember these as well when you write your responses. {user}"

        return intromessage

    def setupchat(self):
        # Check if the conversation file exists
        if not os.path.exists("conversation.json"):
            # If it doesn't exist, create it with default content
            with open("conversation.json", 'w') as json_file:
                json_file.write("[]")  # Writing an empty list as default content

        # Load existing conversation from JSON file
        with open("conversation.json", 'r') as json_file:
            self.chat = json.load(json_file)

        # Define scenarios list
        scenarios = [
            "You're in the cafeteria during lunch break when a classmate from your science class walks over. He asks if he can sit with you and mentions he's curious about your opinion on the latest physics experiment.",
            "You're studying in the library when an art enthusiast approaches. She asks if the seat next to you is taken and mentions she's been experimenting with watercolor techniques lately and would love to share her progress.",
            "You're working on a group project in the classroom when Alex, a classmate known for their musical talents, comes over. They ask if they can join your group and suggest incorporating music into the presentation since they recently composed a piece inspired by the topic.",
            # Add more scenarios as needed
        ]

        # Define intro message
        intromessage = "Welcome to the chat application! This is an introduction message. Here, you can engage in friendly conversations with our AI assistant. Please select a scenario from the dropdown menu to get started."

        # Add previous messages to the intro message if the conversation file is not empty
        if self.chat:
            user, assistant = self.getprev()
            intromessage += f"\n\nThese are previous messages you sent. Remember them as you write your responses. {assistant} These are the messages that the user sent. Remember these as well when you write your responses. {user}"

        return intromessage

    def getprev(self):
        user = ""
        assistant = ""
        for c in range(2, len(self.chat)):
            if self.chat[c]["role"] == "user":
                if "python -u" in self.chat[c]["content"]:
                    pass
                else:
                    user += self.chat[c]["content"]
            elif self.chat[c]["role"] == "assistant":
                assistant += self.chat[c]["content"]
            else:
                cont = self.chat[c]["content"]
                temp = cont.split()
                for i in temp:
                    if i == "I'm":
                        name = sub(r'\W+', '', temp[temp.index(i) + 1])
                if ("apologize" or "sorry") in cont:
                    pass
                else:
                    assistant += cont
        return user, assistant

    def getprev(self):
        user = ""
        assistant = ""
        for c in range(2, len(self.chat)):
            if self.chat[c]["role"] == "user":
                if "python -u" in self.chat[c]["content"]:
                    pass
                else:
                    user += self.chat[c]["content"]
            elif self.chat[c]["role"] == "assistant":
                assistant += self.chat[c]["content"]
            else:
                cont = self.chat[c]["content"]
                temp = cont.split()
                for i in temp:
                    if i == "I'm":
                        name = sub(r'\W+', '', temp[temp.index(i) + 1])
                if ("apologize" or "sorry") in cont:
                    pass
                else:
                    assistant += cont
        return user, assistant

    def chat_with_openai(self, prompt):
        """
        Sends the prompt to OpenAI API using the chat interface and gets the model's response.
        """
        intromessage = self.setupchat()
        system = [{"role": "system", "content": intromessage.strip()}]
        user = [{"role": "user", "content": prompt}]

        client = openai.OpenAI(api_key=keyval)

        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=system + user,
        )

        # Extract the chatbot's message from the response.
        # Assuming there's at least one response and taking the last one as the chatbot's reply.
        print(response)
        chatbot_response = response.choices[0].message.content
        return chatbot_response.strip()

    def get_ai_response(self):
        # Prepare the conversation history
        message_log = [{"role": "system", "content": intromessage}]
        message_log.extend(user)
        message_log.extend(assistant)
        # Get the user's input prompt from the text edit widget
        user_input = self.text_edit.toPlainText()
        self.chat.append({"role": "user", "content": user_input})

        # Call the chat_with_openai function to interact with OpenAI API
        ai_response = self.chat_with_openai(user_input)
        self.chat.append({"role": "assistant", "content": ai_response})

        # Find the first response from the chatbot that has text in it (some responses may not have text)
        for choice in response.choices:
            if "text" in choice:
                ai_response = choice.text
                break
        else:
            # If no response with text is found, return an empty string
            ai_response = ""

        # Display the AI's response
        self.text_edit.append(f"<font color='green'><b>AI:</b></font> {ai_response}")

        # Convert the AI's response to speech
        tts = gTTS(text=ai_response, lang='en')
        tts.save("ai_response.mp3")
        os.system("mpg123 ai_response.mp3")

        # Reset the recorded audio and time
        self.recorded_audio = ""
        self.last_audio_time = time.time()

    def get_social_scenario(self, category):
        return choice(scenarios)

    def closeEvent(self, event):

        if self.speech_thread.isRunning():
            self.speech_thread.stop_recording()
            self.speech_thread.wait()
        event.accept()
        with open("conversation.json", 'w') as json_file:
            json.dump(self.chat, json_file, indent=2)


if __name__ == "__main__":
    app = QApplication(sys.argv)

    palette = app.palette()
    palette.setColor(QPalette.Window, QColor(240, 240, 240))
    palette.setColor(QPalette.WindowText, QColor(40, 40, 40))
    app.setPalette(palette)

    window = SocialScenarioApp()
    window.show()
    sys.exit(app.exec_())
