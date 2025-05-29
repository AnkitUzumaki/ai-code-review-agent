# src/config.py
class Config:
    def __init__(self, args):
        self.priority = args.priority
        self.exclude = args.exclude
        self.aggressiveness = args.aggressiveness
        self.languages = args.languages
