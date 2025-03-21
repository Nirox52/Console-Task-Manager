from rich.console import Console
from jsonLib import JsonLoad


class HabbTrak:
    def __init__(self) -> None:
        self.JSLoad = JsonLoad(path='./data/Habbit.json')
        self.cons = Console()
        try:
            self.habits = self.JSLoad.loadFile()
        except Exception as err:
            self.JSLoad.SaveFile(data={"habbits":{}})

    def addHabbit(self):
        name = self.cons.input('Habbit name [green]>>[/]')
        self.habits[name]=[]
        self.JSLoad.SaveFile()
            




if __name__ == "__main__":
    HT = HabbTrak()
