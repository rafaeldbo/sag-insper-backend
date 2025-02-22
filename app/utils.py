import string, random

CHARACTERS = string.ascii_letters + string.digits

def generate_random_alphanumeric(length: int) -> str:
    random.seed(4)
    return ''.join(random.choices(CHARACTERS, k=length))
