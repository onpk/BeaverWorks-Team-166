from gtts import gTTS
import os
import pyaudio
import wave

def record_audio(filename, duration):
    CHUNK = 1024
    FORMAT = pyaudio.paInt16
    CHANNELS = 1
    RATE = 44100

    audio = pyaudio.PyAudio()

    stream = audio.open(format=FORMAT, channels=CHANNELS,
                        rate=RATE, input=True,
                        frames_per_buffer=CHUNK)

    print("Recording...")

    frames = []

    for _ in range(0, int(RATE / CHUNK * duration)):
        data = stream.read(CHUNK)
        frames.append(data)

    print("Finished recording.")

    stream.stop_stream()
    stream.close()
    audio.terminate()

    wf = wave.open(filename, 'wb')
    wf.setnchannels(CHANNELS)
    wf.setsampwidth(audio.get_sample_size(FORMAT))
    wf.setframerate(RATE)
    wf.writeframes(b''.join(frames))
    wf.close()

def mimic_voice(text_to_speak, output_file="output.wav", duration=5):
    # Record your voice
    record_audio("my_voice.wav", duration)

    # Convert text to speech using gTTS
    tts = gTTS(text=text_to_speak, lang='en')
    tts.save(output_file)

    # Play the output audio
    os.system(f"afplay {output_file}")

# Example usage
text_to_speak = "Hello, this is a test of mimicking voice using text-to-speech."
output_file = "output.wav"
mimic_voice(text_to_speak, output_file)
