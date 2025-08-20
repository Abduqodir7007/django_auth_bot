import random


def generate_code():
    return ''.join(str(random.randint(0,100)%10) for i in range(6))