import whisper

def speech2text(file_path):
    # Load the Whisper model
    model_m = whisper.load_model('medium')

    # Load the audio
    audio = whisper.load_audio(file_path)
    audio = whisper.pad_or_trim(audio)

    # Convert the audio to log-Mel spectrograms
    # mel = whisper.log_mel_spectrogram(audio).to(model_m.device)

    # Detect language (optional step)
    # _, probs = model_m.detect_language(mel)
    # print(f"Detected language: {max(probs, key=probs.get)}")

    result = model_m.transcribe(file_path)
    return result["text"]


file_path = './data/test2.wav'
text = speech2text(file_path)
print(text)
