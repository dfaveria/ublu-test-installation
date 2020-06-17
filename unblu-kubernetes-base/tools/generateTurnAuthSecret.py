#!/usr/bin/env python3

from base64 import b64encode
from random import SystemRandom
from string import ascii_letters

def generate_turn_auth_secret(length = 36):
    """Generate a Base64 encoded random string to be used as the turn server auth secret"""
    character_set = ascii_letters + '#$%&()*+,-./:;<=>?@[]^_`{|}~'
    random_string = ''.join(SystemRandom().choice(character_set) for _ in range(length))
    # print('secret is: ' + random_string)
    return b64encode(bytes(random_string, 'utf-8')).decode("utf-8") 

print("Generated, random auth secret: " + generate_turn_auth_secret())
