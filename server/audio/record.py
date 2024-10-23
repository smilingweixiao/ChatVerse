import pyaudio
import wave
import threading
import chat.event as event
from chat.eventType import EventType
from openai import OpenAI
import os

CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100
WAVE_OUTPUT_FILENAME = "server/audio/output.wav"

recording = False
thread = None

def record():
    p = pyaudio.PyAudio()

    stream = p.open(format=FORMAT,
                    channels=CHANNELS,
                    rate=RATE,
                    input=True,
                    frames_per_buffer=CHUNK)

    print("Recording...")

    frames = []
    while recording:
        data = stream.read(CHUNK)
        frames.append(data)

    print("Done recording")

    stream.stop_stream()
    stream.close()
    p.terminate()

    wf = wave.open(WAVE_OUTPUT_FILENAME, 'wb')
    wf.setnchannels(CHANNELS)
    wf.setsampwidth(p.get_sample_size(FORMAT))
    wf.setframerate(RATE)
    wf.writeframes(b''.join(frames))
    wf.close()

def startRecording():
    global recording, thread
    recording = True
    if thread == None or thread.is_alive() == False:
        thread = threading.Thread(target=record)
        thread.start()

def stopRecording():
    global recording, thread
    recording = False
    thread.join()
    text = transcribe_function(WAVE_OUTPUT_FILENAME)
    print("Whisper output: ", text)
    event.updateChatHistory(text, 'human', True)

# def speech2text(file_path):
#     # Load the Whisper model
#     model_m = whisper.load_model('small').to("cuda")

#     # Load the audio
#     audio = whisper.load_audio(file_path)
#     audio = whisper.pad_or_trim(audio)

#     # Convert the audio to log-Mel spectrograms
#     # mel = whisper.log_mel_spectrogram(audio).to(model_m.device)

#     # Detect language (optional step)
#     # _, probs = model_m.detect_language(mel)
#     # print(f"Detected language: {max(probs, key=probs.get)}")

#     result = model_m.transcribe(file_path)
#     return result["text"]

api_key = os.environ['OPENAI_API_KEY']
client = OpenAI(api_key=api_key)

def transcribe_function(audio_file_path):
    audio_file = open(audio_file_path, "rb")
    transcription = client.audio.transcriptions.create(
        model="whisper-1", 
        file=audio_file
    )
    return transcription.text