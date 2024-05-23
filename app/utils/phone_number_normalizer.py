import phonenumbers

def normalize_phone_number(phone_number):
    parsed_number = phonenumbers.parse(phone_number, None)
    return phonenumbers.format_number(parsed_number, phonenumbers.PhoneNumberFormat.E164)