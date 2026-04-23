import speech_recognition as sr

# List all available microphones
mic_list = sr.Microphone.list_microphone_names()
for i, mic in enumerate(mic_list):
    print(f"{i}: {mic}")