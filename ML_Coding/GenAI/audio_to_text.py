__author__ = "Vivek"
__author_email__ = "vivekltp120@gmail.com"
import whisper

# Load the Whisper model
model = whisper.load_model("large")


# Transcribe audio
result = model.transcribe("path_to_audio_file.wav")
# print(result["text"])