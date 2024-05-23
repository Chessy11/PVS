import random
import string

def generate_verification_code():
    # letter = random.choice(string.ascii_uppercase) 
    digits = random.randint(100, 999)
    print(f"Code: {digits}")
    return f"{digits}"
