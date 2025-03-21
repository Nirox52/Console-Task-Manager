from CONSTS import *


class Command:
    def __init__(self,command) -> None:
        self.command= command

    def analyze(self):
        return self.command
