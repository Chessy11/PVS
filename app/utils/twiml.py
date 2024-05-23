from utils.ngrok_config import get_ngrok_url
import xml.etree.ElementTree as ET

def generate_twiml_response(speech_result: str) -> str:
    root = ET.Element("Response")
    if speech_result:
        say = ET.SubElement(root, "Say")
        say.text = "Thanks for using TechBurst."
    else:
        say = ET.SubElement(root, "Say")
        say.text = "We did not receive any input or encountered an issue. Goodbye!"
    hangup = ET.SubElement(root, "Hangup")
    
    return ET.tostring(root, encoding='unicode', method='xml')



digit_mapping = {
    '0': 'zero',
    '1': 'one',
    '2': 'two',
    '3': 'three',
    '4': 'four',
    '5': 'five',
    '6': 'six',
    '7': 'seven',
    '8': 'eight',
    '9': 'nine'
}

def generate_twiml(code: str, attempt: int = 1) -> str:
    root = ET.Element("Response")
    say_code = ET.SubElement(root, "Say")
    say_code.text = "Please say your verification code after the tone."
    ET.SubElement(root, "Pause", length="1")
    
    play_beep = ET.SubElement(root, "Play")
    ngrok_url = get_ngrok_url()
    play_beep.text = f"{ngrok_url}//static/beep1.mp3" 
    
    gather = ET.SubElement(root, "Gather", input="speech", action=f"{ngrok_url}/process_speech/{attempt}", timeout="5")
    
    # Iterate over each digit in the code and replace it with spoken representation
    for digit in code:
        if digit.isdigit():
            say_digit = digit_mapping.get(digit, digit)  # Get spoken representation or use digit itself if not found
            say_repeat = ET.SubElement(gather, "Say")
            say_repeat.text = say_digit
    
    ET.SubElement(root, "Pause", length="5")
    no_input = ET.SubElement(root, "Say")
    no_input.text = "We did not receive any input or encountered an issue. Goodbye!"
    ET.SubElement(root, "Hangup")
    
    print("Verification code", code)
    return ET.tostring(root, encoding='unicode', method='xml')