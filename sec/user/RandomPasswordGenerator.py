import random
import string


class RandomPasswordGenerator:
    @staticmethod
    def generate(num_characters: int):
        character_set = string.ascii_uppercase + string.ascii_lowercase + string.digits + "!\"#$%&/()=?"
        random_password = ''.join(random.choices(character_set, k=num_characters))
        return random_password
