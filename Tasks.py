from CONSTS import *


class Task:
    def __init__(self,name,id) -> None:
        self.id=id
        self.name = name
        self.priority="none"
        self.createAt=""
        self.due="none"
        self.upFor=""
        self.downFor=""
        self.remindOn=""
        self.repitOn=""

    def createTast(self,file) ->None:
        print(self.name)
        print(self.priority)
        print(self.due)
        js_task = NEW_TASK
        js_task['id'] = self.id
        js_task['name']=self.name
        js_task['due']=self.due
        js_task['status']='todo'
        match self.priority:
            case "H"|"h"|"В"|"в":
                js_task['priority']='hight'
            case "M"|"m"|"С"|"с":
                js_task['priority']='medium'
            case "L"|"l"|"Н"|"н":
                js_task['priority']='low'
            case _:
                js_task['priority']='none'
                
        return js_task
    
