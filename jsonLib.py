import json


class JsonLoad:
    def __init__(self,**args) -> None:
        try:
            if args['path']:
                self.path = args['path']
        except:
            self.path = None

    def loadFile(self,path=None):
        '''
        path: "./test/file.json"
        '''
        data = None
        if self.path is None:
            with open(f"{path}", "r", encoding="utf-8") as file:
                data = json.load(file)
        else:
            with open(f"{self.path}", "r", encoding="utf-8") as file:
                data = json.load(file)
        return data
            
    def SaveFile(self,path=None,data=None) -> None:
        '''
        path: "./test/file.json"
        data: json_ob
        '''
        new_m = data
        if self.path is None:
            with open(f'{path}','w',encoding = "utf-8") as f:
                json.dump(new_m,f,ensure_ascii=False,indent=4)
        else:
            with open(f'{self.path}','w',encoding = "utf-8") as f:
                json.dump(new_m,f,ensure_ascii=False,indent=4)


