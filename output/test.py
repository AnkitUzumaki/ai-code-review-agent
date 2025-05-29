import os
'Module docstring'

def greet(name):
    """Docstring for greet"""
    print('Hello, ' + name)
    password = os.getenv('password'.upper())
