'''
import sys
import json
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QTextEdit, QVBoxLayout, QWidget, QLabel, \
    QStackedWidget, QComboBox
from PyQt5.QtGui import QFont, QColor, QPalette
from PyQt5.QtCore import Qt, QThread, pyqtSignal
import speech_recognition as sr
import openai
import time
from gtts import gTTS
import os
from random import randint
from secretkey import keyval
import lipsync
# category = sys.argv[1] (string)

# Set up OpenAI API key
openai.api_key = keyval
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

    def start_session(self):
        self.stacked_widget.setCurrentWidget(self.recording_page_widget)
        self.text_edit.clear()
        self.recorded_audio = ""
        self.is_recording = True
        self.speech_thread.start()

        scenarioChoice = randint(0, len(scenarios)-1)

        selected_scenario = scenarios[scenarioChoice]
        self.text_edit.append(f"<font color='blue'><b>Scenario:</b></font> {selected_scenario}")

        # Extracting a dialogue from the scenario dynamically using OpenAI
        dialogue = self.chat_with_openai("I want actual dialogue. Don't give too much dialogue for the entire scnerio as I need oppurutnity for me to speak as well. Give me a dialogue for a character that is not 'You' in the scenario" + selected_scenario)
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

    def chat_with_openai(self, prompt):
        """
        Sends the prompt to OpenAI API using the chat interface and gets the model's response.
        """
        message = {
            'role': 'user',
            'content': prompt
        }
        client=openai.OpenAI(api_key=keyval)

        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[message], stream=True
        )

        # Extract the chatbot's message from the response.
        # Assuming there's at least one response and taking the last one as the chatbot's reply.
        chatbot_response = response.choices[0].message['content']
        return chatbot_response.strip()

    def get_ai_response(self):
        # Get the user's input prompt from the text edit widget
        user_input = self.text_edit.toPlainText()

        # Call the chat_with_openai function to interact with OpenAI API
        ai_response = self.chat_with_openai(user_input)

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
'''
import sys
import json 
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
import lipsync
import random

try:
    category = sys.argv[1]
except:
    category = ""

print(category)

# Set up OpenAI API key
openai.api_key = keyval
# Define the scenarios list
scenarios=["""You're in the cafeteria during lunch break when 
           a classmate from your science class, walks over. He asks if he can sit with you and mentions he's curious about your opinion on the latest physics 
           experiment""",""" You're studying in the library when an art enthusiast approaches. She asks if the seat next to you is taken and mentions 
           she's been experimenting with watercolor techniques lately and would love to share her progress.""", """You're working on a group project in the classroom when Alex, a classmate known for their musical talents, comes over. They ask if they can join your group and 
           suggest incorporating music into the presentation since they recently composed a piece inspired by the topic.""","""You're waiting for the bus after school when Maya, a student you recognize from the drama club, approaches. She asks if she can sit next to you and mentions 
           she's excited about the upcoming school play auditions and wonders if you plan to try out too.""",""" You're in the game room during free period when Michael, a fellow gamer, walks over. He asks if he can join your game and mentions he's been practicing a new strategy 
           in his favorite game and is eager to test it out.""","""You're at the outdoor hangout spot after school when Sarah, a classmate you've seen around, comes over. She asks if she can sit at your table and mentions she's 
           been feeling stressed lately and could use a friendly chat to unwind.""", """ You're in the gym during your workout session when Daniel, a classmate who's into fitness, approaches. He asks if he can share the equipment with you and mentions he's been following a new 
           exercise routine and wants to know if you have any tips.""", """ You're in the music room practicing piano when Lily, a fellow musician, walks in. She asks if she can use the piano next to you and mentions she's been working on a 
           new song and would love your feedback.""", """You're in the library reading zone when Ethan, a classmate you've seen around, approaches. He asks if he can join you and mentions he's been struggling to find a good book to read 
           and wonders if you have any recommendations. """, """ You're at the art studio working on your project when Sophia, a classmate known for her creativity, comes over. She asks if she can work alongside you and mentions she's been experimenting with a 
           new painting technique and would love to share it with you."""]


class SpeechRecognitionThread(QThread,VTT):
    speech_detected = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()

        # Adjust the recognizer sensitivity
        self.recognizer.energy_threshold = 1000  # You may need to adjust this value based on your environment
        self.is_running = True
    def stop_recording(self):
        self.stopspeak()
    def run(self):
        #aresponse=self.speak()
        #self.speech_detected.emit(aresponse)
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
        self.chat=[]

    def start_session(self):
        self.stacked_widget.setCurrentWidget(self.recording_page_widget)
        self.text_edit.clear()
        #self.recorded_audio = ""
        self.is_recording = True
        self.speech_thread.start()

        selected_scenario = choice(scenarios)
        self.text_edit.append(f"<font color='blue'><b>Scenario:</b></font> {selected_scenario}")

        # Extracting a dialogue from the scenario dynamically using OpenAI
        dialogue = self.chat_with_openai("I want actual dialogue. Don't give too much dialogue for the entire scnerio as I need oppurutnity for me to speak as well." )
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
    def getprev(self):
        #chat=[]
        user=""
        assistant=""
        with open("backEnd/chat/conversation.json", 'r') as json_file:
            self.chat = json.load(json_file)
        for c in range(2,len(self.chat)):
            if self.chat[c]["role"]=="user":
                if "python -u" in self.chat[c]["content"]:
                        pass
                else:
                    user+=self.chat[c]["content"]
            elif self.chat[c]["role"]=="assistant":
                assistant+=self.chat[c]["content"]
            else:
                cont=self.chat[c]["content"]
                temp=cont.split()
                for i in temp:
                    if i=="I'm":
                        name=sub(r'\W+', '',temp[temp.index(i)+1])
                if ("apologize" or "sorry") in  cont:
                        pass
                else:
                    assistant+=cont
        return [user,assistant]
    def setupchat(self):
        scenarios=["""You're in the cafeteria during lunch break when 
           a classmate from your science class, walks over. He asks if he can sit with you and mentions he's curious about your opinion on the latest physics 
           experiment""",""" You're studying in the library when an art enthusiast approaches. She asks if the seat next to you is taken and mentions 
           she's been experimenting with watercolor techniques lately and would love to share her progress.""", """You're working on a group project in the classroom when Alex, a classmate known for their musical talents, comes over. They ask if they can join your group and 
           suggest incorporating music into the presentation since they recently composed a piece inspired by the topic.""","""You're waiting for the bus after school when Maya, a student you recognize from the drama club, approaches. She asks if she can sit next to you and mentions 
           she's excited about the upcoming school play auditions and wonders if you plan to try out too.""",""" You're in the game room during free period when Michael, a fellow gamer, walks over. He asks if he can join your game and mentions he's been practicing a new strategy 
           in his favorite game and is eager to test it out.""","""You're at the outdoor hangout spot after school when Sarah, a classmate you've seen around, comes over. She asks if she can sit at your table and mentions she's 
           been feeling stressed lately and could use a friendly chat to unwind.""", """ You're in the gym during your workout session when Daniel, a classmate who's into fitness, approaches. He asks if he can share the equipment with you and mentions he's been following a new 
           exercise routine and wants to know if you have any tips.""", """ You're in the music room practicing piano when Lily, a fellow musician, walks in. She asks if she can use the piano next to you and mentions she's been working on a 
           new song and would love your feedback.""", """You're in the library reading zone when Ethan, a classmate you've seen around, approaches. He asks if he can join you and mentions he's been struggling to find a good book to read 
           and wonders if you have any recommendations. """, """ You're at the art studio working on your project when Sophia, a classmate known for her creativity, comes over. She asks if she can work alongside you and mentions she's been experimenting with a 
           new painting technique and would love to share it with you."""]
        intromessage="""You are an AI friend who is interacting with autistic children.
                    Your goal is to engage them in a friendly and supportive conversation, incorporating role-playing scenarios to encourage social interaction. 
                Create a positive and inclusive environment, adapt to their preferences, and guide them through imaginative scenarios that foster communication and social skills. 
                Remember to be patient, understanding, and encouraging throughout the interaction."""
        intromessage+="""Your role-playing scenario is this: """+choice(scenarios)+". Please make your responses and messages based around this scenario."
        if(os.path.getsize("backEnd/chat/conversation.json")>0):
            intromessage+="These are previous messages you sent. Remember them as you write your responses. "+self.getprev()[1]+" These are the messages that the user sent. Remember these as well when you write your responses. "+self.getprev()[0]
        return intromessage
    def chat_with_openai(self, prompt):
        """
        Sends the prompt to OpenAI API using the chat interface and gets the model's response.
        """
        intromessage=self.setupchat()
        system = [{"role": "system", "content":intromessage.strip()}]
        user = [{"role": "user", "content": prompt}]
    
        client=openai.OpenAI(api_key=keyval)

        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=system+user,
        )

        # Extract the chatbot's message from the response.
        # Assuming there's at least one response and taking the last one as the chatbot's reply.
        print(response)
        chatbot_response = response.choices[0].message.content
        return chatbot_response.strip()

    def get_ai_response(self):
        # Get the user's input prompt from the text edit widget
        user_input = self.text_edit.toPlainText()
        self.chat.append({"role": "user", "content": user_input})

        # Call the chat_with_openai function to interact with OpenAI API
        ai_response = self.chat_with_openai(user_input)
        self.chat.append({"role": "assistant", "content": ai_response})

        # Save AI response as an audio file
        tts = gTTS(text=ai_response, lang='en')
        tts.save("ai_response.mp3")

        # Play the AI response immediately after generating it
        # os.system("mpg123 ai_response.mp3")

        # Play the video of the AI response after it is generated
        outlink=lipsync.lipsync(random.randint(0, 3), ai_response)
        # print(outlink)

        self.recorded_audio = ""
        self.last_audio_time = time.time()

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