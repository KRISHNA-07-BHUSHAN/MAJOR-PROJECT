import webbrowser
import geocoder
import speech_recognition as sr
import urllib.request
import json

def get_current_location():
    # Use geocoder to get the current location based on the IP address
    g = geocoder.ip('me')  # This fetches location based on the public IP address
    if g.ok:
        latitude, longitude = g.latlng
        print(f"Current Coordinates from IP: Latitude: {latitude}, Longitude: {longitude}")
        return latitude, longitude
    else:
        print("Error: Could not fetch location.")
        return None, None

def get_address_from_coordinates(latitude, longitude):
    # Use urllib to get address from coordinates using OpenCage API (via reverse geocoding)
    api_key = 'c327f83f7f2c4451bc01c7eb1118ab58'  # Replace with your OpenCage API key
    url = f'https://api.opencagedata.com/geocode/v1/json?q={latitude},{longitude}&key={api_key}'
    with urllib.request.urlopen(url) as response:
        data = json.load(response)
        if data['results']:
            address = data['results'][0]['formatted']
            print(f"Address: {address}")
        else:
            address = "Address not available"
    return address

def navigate_to(destination):
    latitude, longitude = get_current_location()
    if latitude is not None and longitude is not None:
        # Get the address from the coordinates
        source_address = get_address_from_coordinates(latitude, longitude)

        # Format the URL for Google Maps navigation
        maps_url = f"https://www.google.com/maps/dir/{latitude},{longitude}/{destination.replace(' ', '+')}/"
        print(f"Navigating from {source_address} to {destination}")
        webbrowser.open(maps_url)
    else:
        print("Could not determine current location for navigation.")

# Function to listen for navigation commands via voice input
def listen_for_navigation_command():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening for navigation command... Please say 'navigate to [destination]'.")
        while True:
            try:
                # Listen to the audio from the microphone
                audio = recognizer.listen(source)
                command = recognizer.recognize_google(audio).lower()
                print(f"Command: {command}")
                
                if "navigate to" in command:
                    destination = command.split("navigate to")[1].strip()  # Extracting the destination
                    print(f"Destination: {destination}")
                    navigate_to(destination)
                else:
                    print("Command not recognized. Please say it in the format 'navigate to [destination]'.")

            except sr.UnknownValueError:
                # In case the speech was not understood
                pass
            except sr.RequestError as e:
                print(f"Could not request results from Google Speech Recognition service; {e}")
                break

# Start listening for voice commands to navigate
listen_for_navigation_command()
