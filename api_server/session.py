import random
import string

def randstr(length):
    letters_set = string.ascii_letters
    random_list = random.sample(letters_set, length)
    return ''.join(random_list)

class Session:
    def __init__(self):
        self.sid = None
        self.uid = None
        self.timeout = None

if __name__ == '__main__':
    print(randstr(40))