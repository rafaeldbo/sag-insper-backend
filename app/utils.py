import string, random
from datetime import datetime

CHARACTERS = string.ascii_letters + string.digits

def generate_random_alphanumeric(length: int) -> str:
    return ''.join(random.choices(CHARACTERS, k=length))
