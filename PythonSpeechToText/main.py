import tkinter as tk
from pyannote.audio import Pipeline
from pydub import AudioSegment
import speech_recognition as sr
import tempfile
import os

def transcribe_audio():
    # Instantiating pretrained pipeline
    pipeline = Pipeline.from_pretrained("pyannote/speaker-diarization",
                                        use_auth_token="")

    diarization = pipeline("teste.wav")

    audio_file = "teste.wav"
    audio = AudioSegment.from_wav(audio_file)

    output_file = open("saida.txt", "w")

    for turn, _, speaker in diarization.itertracks(yield_label=True):
        start_time = int(turn.start * 1000)  
        end_time = int(turn.end * 1000) 
        speech = audio[start_time:end_time]

        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp_file:
            speech.export(tmp_file.name, format='wav')

            recognizer = sr.Recognizer()
            with sr.AudioFile(tmp_file.name) as source:
                audio_data = recognizer.record(source)
                try:
                    speech_text = recognizer.recognize_google(audio_data)
                except sr.UnknownValueError:
                    speech_text = "<Transcription not available>"

        output = f"start={turn.start:.1f}s stop={turn.end:.1f}s speaker_{speaker}: {speech_text}\n"
        output_file.write(output)
        print("Escrita feita...")
 
        tmp_file.close()

  
    output_file.close()

def capture_audio():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("Speak now...")
        audio_data = recognizer.record(source)

    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp_file:
        audio_file = sr.AudioFile(tmp_file.name)
        with audio_file as f:
            recognizer.write_to_wav(f, audio_data)

        with open("saida.txt", "a") as output_file:
            try:
                speech_text = recognizer.recognize_google(audio_data)
            except sr.UnknownValueError:
                speech_text = "<Transcription not available>"
            output_file.write(f"captured_audio: {speech_text}\n")

    with open("saida.txt", "r") as output_file:
        content = output_file.read()
        text_output.config(state='normal')
        text_output.delete('1.0', tk.END)
        text_output.insert(tk.END, content)
        text_output.config(state='disabled')

    os.remove(tmp_file.name)

window = tk.Tk()
window.title("Transcription Interface")

transcribe_button = tk.Button(window, text="Transcribe Audio", command=transcribe_audio)
transcribe_button.pack(pady=10)

capture_button = tk.Button(window, text="Capture Audio", command=capture_audio)
capture_button.pack(pady=10)

text_output = tk.Text(window, height=10, width=50)
text_output.pack(pady=10)
text_output.config(state='disabled')

window.mainloop()
