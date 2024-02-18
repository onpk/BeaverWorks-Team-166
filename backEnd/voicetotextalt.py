import argparse
import os
import numpy as np
import speech_recognition as sr
import whisper
import torch
from datetime import datetime, timedelta
from queue import Queue
from time import sleep
from sys import platform

class VTText():
    def __init__(self):
        self.parser = argparse.ArgumentParser()
        self.parser.add_argument("--model", default="medium", help="Model to use",
                            choices=["tiny", "base", "small", "medium", "large"])
        self.parser.add_argument("--non_english", action='store_true',
                            help="Don't use the english model.")
        self.parser.add_argument("--energy_threshold", default=1000,
                            help="Energy level for mic to detect.", type=int)
        self.parser.add_argument("--record_timeout", default=2,
                            help="How real time the recording is in seconds.", type=float)
        self.parser.add_argument("--phrase_timeout", default=3,
                            help="How much empty space between recordings before we "
                                "consider it a new line in the transcription.", type=float)
        self.parser.add_argument("--output_file", default="transcription.txt",
                            help="File to write the transcription to.")
        self.args = self.parser.parse_args()

        # The last time a recording was retrieved from the queue.
        phrase_time = None
        # Thread safe Queue for passing data from the threaded recording callback.
        data_queue = Queue()
        # We use SpeechRecognizer to record our audio because it has a nice feature where it can detect when speech ends.
        self.recorder = sr.Recognizer()
        self.recorder.energy_threshold = self.args.energy_threshold
        # Definitely do this, dynamic energy compensation lowers the energy threshold dramatically to a point where the SpeechRecognizer never stops recording.
        self.recorder.dynamic_energy_threshold = False

    # Important for linux users.
    # Prevents permanent application hang and crash by using the wrong Microphone
    def record_callback(_, audio: sr.AudioData,self) -> None:
        """
        Threaded callback function to receive audio data when recordings finish.
        audio: An AudioData containing the recorded bytes.
        """
        # Grab the raw bytes and push it into the thread safe queue.
        data = audio.get_raw_data()
        self.data_queue.put(data)
    source = sr.Microphone(sample_rate=16000)
    def speech(self):
        # Load / Download model
        model = self.args.model
        if self.args.model != "large" and not self.args.non_english:
            model = model + ".en"
        audio_model = whisper.load_model(model)

        record_timeout = self.args.record_timeout
        phrase_timeout = self.args.phrase_timeout

        transcription = ['']

        with self.source:
            self.recorder.adjust_for_ambient_noise(self.source)



        # Create a background thread that will pass us raw audio bytes.
        # We could do this manually but SpeechRecognizer provides a nice helper.
        self.recorder.listen_in_background(self.source, self.record_callback, phrase_time_limit=record_timeout)

        # Cue the user that we're ready to go.
        print("Model loaded.\n")

        with open(self.args.output_file, 'w') as file:
            while True:
                try:
                    now = datetime.utcnow()
                    # Pull raw recorded audio from the queue.
                    if not self.data_queue.empty():
                        phrase_complete = False
                        # If enough time has passed between recordings, consider the phrase complete.
                        # Clear the current working audio buffer to start over with the new data.
                        if phrase_time and now - phrase_time > timedelta(seconds=phrase_timeout):
                            phrase_complete = True
                        # This is the last time we received new audio data from the queue.
                        phrase_time = now

                        # Combine audio data from queue
                        audio_data = b''.join(self.data_queue.queue)
                        self.data_queue.queue.clear()

                        # Convert in-ram buffer to something the model can use directly without needing a temp file.
                        # Convert data from 16 bit wide integers to floating point with a width of 32 bits.
                        # Clamp the audio stream frequency to a PCM wavelength compatible default of 32768hz max.
                        audio_np = np.frombuffer(audio_data, dtype=np.int16).astype(np.float32) / 32768.0

                        # Read the transcription.
                        result = audio_model.transcribe(audio_np, fp16=torch.cuda.is_available())
                        text = result['text'].strip()

                        # If we detected a pause between recordings, add a new item to our transcription.
                        # Otherwise edit the existing one.
                        if phrase_complete:
                            transcription.append(text)
                        else:
                            transcription[-1] = text

                        # Write the updated transcription to the file.
                        file.write(text + '\n')

                        # Clear the console to reprint the updated transcription.
                        os.system('cls' if os.name == 'nt' else 'clear')
                        for line in transcription:
                            print(line)
                        # Flush stdout.
                        print('', end='', flush=True)

                        # Infinite loops are bad for processors, must sleep.
                        sleep(0.25)
                except KeyboardInterrupt:
                    break
        print("\n\nTranscription written to", self.args.output_file)

obj=VTText()
obj.speech()
#speech()