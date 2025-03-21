import datetime
import calendar
from io import StringIO
import re
import sys
from rich.console import Console
from rich.table import Table
from rich.tree import Tree
from rich.live import Live
from rich.panel import Panel
from rich import print, style
import keyboard
from itertools import product
from os import listdir, stat, walk, system
import time
import json
import shutil
from datetime import datetime, timedelta


from CONSTS import *
from Command import Command
from Tasks import Task

cons = Console()

cursor_row=0
LIVE_RUN=False
TABLE_ROWS=0
DONT_CLEAR_MESS=[]




class ToDoConsole:
    def __init__(self) -> None:
        #Styles
        ERROR_STYLE = "bold white on red"
        
        #Consols
        self.mainConsole=Console() #console for main opertions
        self.errorConsole = Console(style=ERROR_STYLE)
        self.tasklistUpdate=True
        files = self.getFilesInDir('./data') 
        self.SORTMODE=False
        self.SORT_FILTER=''
        self.SHORT_COMMANDS=[]
        self.TODAY = datetime.today()
        self.letters='abcdefghijklmnopqrstuvwxyz'
        self.__loadTaskTypes()
        self.__loadSetting()
        if len(files)==0:
            self.createMonth('./data/Tasks.json')
            DONT_CLEAR_MESS.append('''
            [yellow underline]Hello in my ToDoConsole[/]

Try to create your first task with command 
[bold green]cr[/] task_name
Or try [bold yellow]help[/] command to know more about all commands.
                [blue underline]Have fun!!!![/]
''')
            system('cls')
            self.mainConsole.print(DONT_CLEAR_MESS[0])
            DONT_CLEAR_MESS.clear()
        else:
            checked_data = self.__checkArchTasks(self.loadMonthData("./data/Tasks.json"))
            if not checked_data is None:
                self.createMonth("./data/Tasks.json",checked_data)

            checked_data= self.__checkTaskDates(checked_data)
            self.displayTasks()

    def show_calendar(self):
        # Получаем текущую дату
        today = datetime.today()
        year, month, day = today.year, today.month, today.day

        # Создаем календарь
        cal = calendar.TextCalendar(calendar.MONDAY)

        # Функция для выделения текущего дня
        def highlight_day(month_str, day):
            return month_str.replace(f' {day} ', f'[{day}]')

        # Генерируем календарь для текущего месяца
        month_str = cal.formatmonth(year, month)
        highlighted_month = highlight_day(month_str, day)
        DONT_CLEAR_MESS.append(highlighted_month)

    def __loadTaskTypes(self):
        try:
            self.taskTypes = self.loadMonthData('./TaskTypes.json')
        except:
            self.createMonth("./TaskTypes.json",DEF_TASK_TYPES)
    
    def __loadSetting(self):
        try:
            self.SETTING = self.loadMonthData('./data/Setting.json')
            try:
                if len(self.SETTING["sort"])>0:
                    self.SORTMODE=True
                    self.SORT_FILTER= self.SETTING['sort']
            except:
                pass
            try:
                if self.SETTING["commands"]:
                    self.SHORT_COMMANDS = self.SETTING["commands"] 
            except:
                pass
            try:
                if self.SETTING['ignore']['date']==0:
                    self.SETTING['ignore']['date']=self.TODAY.strftime("%Y-%m-%d")
                elif self.SETTING['ignore']['date']!=self.TODAY.strftime("%Y-%m-%d"):
                    tod = self.TODAY.strftime("%Y-%m-%d").split('-')[2]
                    day =  self.SETTING['ignore']['date'].split('-')[2] 
                    day_dif = int(tod) - int(day)
                    self.SETTING['week_day'] = (int(self.SETTING['week_day'])+day_dif) % 7
                    self.SETTING['ignore']['date']=self.TODAY.strftime("%Y-%m-%d")
                self.createMonth("./data/Setting.json",self.SETTING)

            except:
                pass
        except:
            self.createMonth("./data/Setting.json",DEF_SETTINGS)
            self.SETTING = self.loadMonthData('./data/Setting.json')

    def __getTaskType(self,task,unickCode,text,date=''):
        # task_str = f'{unique_combination}|[yellow]        [ ] [/yellow] {task['name']}'
        for tp in list(self.taskTypes.keys()):
            if task in self.taskTypes[tp]['shortNames']:
                symb = self.taskTypes[tp]['symbol']
                symb_style=self.taskTypes[tp]['symbol_style'].replace('|',f"        { symb }")
                st=self.taskTypes[tp]['style'].replace("|",text)
                if date!='':
                    task_str= f"{unickCode}|{symb_style} {st}|{date}"
                else:
                    task_str= f"{unickCode}|{symb_style} {st}"
                return task_str


    def __convertTaskType(self,taskStat):
        for tp in list(self.taskTypes.keys()):
            if taskStat in self.taskTypes[tp]['shortNames']:
                return tp

    def __del_tasks_by_ids(self,ids:list,task_list:list):
        i=0
        for d in ids:
            del task_list[d-i]
            i+=1
        return task_list


    def __checkTaskDates(self,data):
        for category in data:  # Перебираем все ключи верхнего уровня
            if category != 'lastId'and category!='today' and category != 'tommorow' and category != 'yesterday':
                for priority in data[category]:  # Перебираем уровни приоритетов
                    task_ids_to_del =[]
                    for i,task in enumerate(data[category][priority]):  # Перебираем задачи
                        if task['createAt']!="":
                            if task['createAt'] == self.TODAY.strftime("%Y-%m-%d") and priority!='today':
                                # del data[category][priority][i]
                                task_ids_to_del.append(i)
                                task['due'] = 'today'
                                data['today'][priority].append(task)
                                DONT_CLEAR_MESS.append(f'Задача [gold1]{task["name"]}[/] истеккает сегодня')
                            elif task['createAt'] == ( self.TODAY+timedelta(days=1) ).strftime("%Y-%m-%d") and priority!="tommorow":
                                # del data[category][priority][i]
                                task_ids_to_del.append(i)
                                task['due'] = 'tommorow'
                                data['tommorow'][priority].append(task)
                                DONT_CLEAR_MESS.append(f'Задача [blue]{task["name"]}[/] истеккает завтра')
                            elif task['createAt'] == ( self.TODAY-timedelta(days=1) ).strftime("%Y-%m-%d") and priority!="yesterday":
                                # del data[category][priority][i]
                                task_ids_to_del.append(i)
                                task['due'] = 'yesterday'
                                data['yesterday'][priority].append(task)
                                DONT_CLEAR_MESS.append(f'Задача [red]{task["name"]}[/] истекла вчера')
                        if task['repitOn'] !="":
                            pass
                    if task_ids_to_del:
                        data[category][priority] =self.__del_tasks_by_ids(task_ids_to_del,data[category][priority]) 


        self.createMonth('./data/Tasks.json',data)
        return data




    def __checkIfPartIsInCommandArray(self,command_part,commandArr):
        if command_part in commandArr:
            return True
        else:
            return False

    def __checkArchTasks(self,data):
        chnged =False
        for category in data:  # Перебираем все ключи верхнего уровня
                print(category)
                if category!='lastId' or category!="cash":
                    print(category)
                    try:
                        # task_ids_for_del = []
                        # for i,task in enumerate(data[category]["archived"]):  # Перебираем задачи
                        #     DONT_CLEAR_MESS.append(f'[red]Task {task["name"]} was deleted[/]')
                        #     task_ids_for_del.append(i)
                        #     del data[category]['archived'][i]
                        #     chnged=True
                        if len(data[category]['archived'])>0:
                            for tasks in data[category]['archived']:
                                DONT_CLEAR_MESS.append(f'[red]DELETED TASK >>[/]{ tasks['name'] }')
                        data[category]['archived']=[]
                        chnged=True
                    except:
                        continue
        if chnged:
            return data 
        return None

    def __getTaskById(self,data,id):
        for category in data:  # Перебираем все ключи верхнего уровня
            try:
                if category != 'lastId':
                    for priority in data[category]:  # Перебираем уровни приоритетов
                        for i,task in enumerate(data[category][priority]):  # Перебираем задачи
                            if task["id"] == id:
                                get_task = data[category][priority][i]
                                return get_task
            except:
                return None

    
    def __cange_task_by_id(self,data, task_id,**params):
        for category in data:  # Перебираем все ключи верхнего уровня
            try:
                for priority in data[category]:  # Перебираем уровни приоритетов
                    for i,task in enumerate(data[category][priority]):  # Перебираем задачи
                        if task["id"] == task_id:
                            get_task = data[category][priority][i]
                            try:
                                if params['status']:
                                    if params['status']=="d":
                                        if get_task['status']!='dr' and not get_task['remindOn']:
                                            get_task['status'] = 'done'
                                        else:
                                            get_task['status'] = 'dr'
                                    elif params['status']=='t' or params['status']=='td':
                                        get_task['status'] = 'todo'
                                    elif params['status']=='wr' or params['status']=='wrong':
                                        get_task['status'] = 'wrong'
                                    else:
                                        if get_task['status']!='dr':
                                            if not get_task['remindOn']:
                                                get_task['status'] = params['status']
                                        else:
                                            get_task['status'] = 'dr'


                                    del data[category][priority][i]
                                    if params['status']=="d" or params['status']=="done" or params['status']=="dn":
                                        if self.__convertTaskType(get_task['status'])=='dr':
                                            get_task['createAt'] = (self.TODAY+timedelta(days=365)).strftime("%Y-%m-%d")
                                            data['tasks']['hight'].append(get_task)
                                        else:
                                            if get_task['remindOn']:
                                                get_task['createAt'] = (self.TODAY+timedelta(days=int(get_task['remindOn']))).strftime("%Y-%m-%d")
                                                data['tasks']['none'].append(get_task)
                                            else:
                                                data[category]['done'].append(get_task)
                                    elif params['status']=='w' or params['status']=='wr' or params['status']=='wrong':
                                        data[category]['hight'].insert(0,get_task)
                                    else:
                                        data[category]['none'].append(get_task)
                            except:
                                pass
                            try:
                                if params['prios']:
                                    get_task['priority'] = params['prios']
                                    del data[category][priority][i]
                                    if params['prios']=="h":
                                        data[category]['hight'].append(get_task)
                                    elif params['prios']=="m":
                                        data[category]['medium'].append(get_task)
                                    elif params['prios']=="l":
                                        data[category]['low'].append(get_task)  
                                    elif params['prios']=="n":
                                        data[category]['none'].append(get_task) 
                                    else:
                                        data[category]['none'].append(get_task)
                            except:
                                pass

                            try:
                                if params['name']:
                                    # get_task['name'] = params['name']
                                    data[category][priority][i]['name'] = params['name']
                            except:
                                pass

                            
                            return data  # Если нашли, возвращаем задачу
            except:
                pass
        
        return None  # Если не нашли, возвращаем None


    def __move_task_by_id(self,data, task_id,to):
        for category in data:  # Перебираем все ключи верхнего уровня
            try:
                for priority in data[category]:  # Перебираем уровни приоритетов
                    for i,task in enumerate(data[category][priority]):  # Перебираем задачи
                        if task["id"] == task_id:
                            try:
                                if task['createAt'] and to =='tommorow':
                                    task['createAt']= (self.TODAY+timedelta(days=1)).strftime("%Y-%m-%d")
                            except:
                                pass
                            task = data[category][priority][i]
                            del data[category][priority][i]
                            data[to][priority].append(task)
                            return data  # Если нашли, возвращаем задачу
            except:
                pass
        
        return None  # Если не нашли, возвращаем None
    
    def __del_task_by_id(self,data, task_id):
        for category in data:  # Перебираем все ключи верхнего уровня
            try:
                for priority in data[category]:  # Перебираем уровни приоритетов
                    for i,task in enumerate(data[category][priority]):  # Перебираем задачи
                        if task["id"] == task_id:
                            del data[category][priority][i]
                            task['status']='archived'
                            data[category]["archived"].append(task)
                            return data  # Если нашли, возвращаем задачу
            except Exception as err:
                self.errorConsole.print(err)
                pass
        
        return None  # Если не нашли, возвращаем None

    def __getDue(self,due):
        task_data = self.loadMonthData('./data/Tasks.json')
        match due:
            case "td"|"today"|"T"|"С"|"сег":
                return 'today'
                
            case "tm"|"tom"|"tommorow"|"tommorrow"|"З"|"зав":
                return 'tommorow'
                
            case "ye"|"ys"|"yes"|"yesterday"|"ВЧ"|"вч"|"вчер":
                return 'yesterday'
                
            case "Mon"|"M"|"mon"|"monday"|"Monday"|"П"|"пон"|"пн"|"Пон":
                return "Mon"
                
            case "tu"|"tue"|"Tu"|"Tuesday"|"вт"|"Вт"|"В"|"Втор"|"втор":
                return 'Tue'
                
            case "we"|"We"|"W"|"Wed"|"wed"|"С"|"Ср"|"ср"|"Сред"|"сред":
                return "Wed"
                
            case "th"|"thu"|"Thu"|"Thursday"|"Ч"|"чет"|"Чет":
                return "Thu"
                
            case "fr"|"Fr"|"F"|"fri"|"Fri"|"П"|"пят"|"Пят":
                return "Fri"
                
            case "St"|"st"|"sat"|'Sat'|"С"|"Суб"|"суб":
                return "Sat"
                
            case "Su"|"su"|"sun"|"Sun"|"Вос"|"вос"|"вс":
                return "Sun"
            case "wee"|'weeek'|"нед":
                return "week"
            case "tsk"|'tk'|"task"|"tas":
                return "tasks"
                
            case _:
                try:
                    if task_data[due]:
                        return due
                except:
                    pass

    
    def get_day_difference(self, input_day):
        diff = (input_day - int(self.SETTING['week_day'])) % 7
        return diff if diff >= 0 else diff + 7
    
    def __analyseCommand(self,command:str) -> None:
        self.tasklistUpdate = True
        DUE =False
        for com in self.SHORT_COMMANDS:
            if com.split('|')[0]==command:
                command = com.split('|')[1]

        task_data = self.loadMonthData('./data/Tasks.json')
        command_parts = command.split(' ')
        if command_parts[0] == "SET": #Delete setting commad mark
            command_parts = command_parts[1:]
        # self.mainConsole.print(command_parts)
        if self.__checkIfPartIsInCommandArray(command_parts[0],COMMANDS['main']):
            # self.mainConsole.print(command_parts[0])
            match command_parts[0]:
                case "ct"|"cr"|"се"|"сз":
                    if len(command_parts)==1:
                        DONT_CLEAR_MESS.append('[red]No argumentsd check [/] [green]help[/] [red]command to know more[/]')
                        self.createMonth('./data/Tasks.json',task_data)
                        self.displayTasks()
                        return
                    task_text=True
                    task_status = False
                    cr = False
                    rp = False
                    self.mainConsole.print(f'Create task: {command_parts[1]}')
                    tast = Task(command_parts[1],task_data['lastId'])
                    task_data['lastId']+=1
                    i=2
                    for comand in command_parts[2:]:
                        if i >= len(command_parts):
                            i=len(command_parts)-1
                        match comand:
                            case "due"|"to"|"d"|"вгу"|"до"|"на":
                                task_text=False
                                tast.due=command_parts[i+1]
                                DUE = True
                            case "p"|'п'|'з':
                                task_text=False
                                tast.priority = command_parts[i+1]
                            case "st"|"ст":
                                task_text=False
                                task_status = True
                                task_status_str= command_parts[i+1]
                                # task_from_data = self.__cange_task_by_id(task_data,task['id'],status=status)
                            case "rp": #TODO: complete repeat part
                                task_text = False
                                remindOn = command_parts[i+1]
                                rp=True
                                try:
                                    int(remindOn)
                                    tast.remindOn=remindOn
                                except:
                                    DONT_CLEAR_MESS.append('[red]Bad rp arg[/]')
                                # rem1 = remindOn[0]
                                # rem2 = remindOn[1:]
                                # if rem2 == "ds":
                                #     tast.repitOn = (self.TODAY + timedelta(days=int(rem1))).strftime("%Y-%m-%d")
                                # else:
                                #     DONT_CLEAR_MESS.append('[red]Bad rp arg[/]')

                            case "cr": #FIXME:week days
                                task_text=False
                                cr = True
                                date = command_parts[i+1]
                                match date:
                                    case "td":  # Сегодня
                                        tast.createAt =  self.TODAY.strftime("%Y-%m-%d")
                                    case "tm":  # Завтра
                                        tast.createAt = (self.TODAY + timedelta(days=1)).strftime("%Y-%m-%d")
                                    case "mon":
                                        days = self.get_day_difference(1)
                                        tast.createAt = (self.TODAY + timedelta(days=days)).strftime("%Y-%m-%d")
                                    case "tue":
                                        days = self.get_day_difference(2)
                                        tast.createAt = (self.TODAY + timedelta(days=days)).strftime("%Y-%m-%d")
                                    case "wed":
                                        days = self.get_day_difference(3)
                                        tast.createAt = (self.TODAY + timedelta(days=days)).strftime("%Y-%m-%d")
                                    case "thu":
                                        days = self.get_day_difference(4)
                                        tast.createAt = (self.TODAY + timedelta(days=days)).strftime("%Y-%m-%d")
                                    case "fri":
                                        days = self.get_day_difference(5)
                                        tast.createAt = (self.TODAY + timedelta(days=days)).strftime("%Y-%m-%d")
                                    case "sat":
                                        days = self.get_day_difference(6)
                                        tast.createAt = (self.TODAY + timedelta(days=days)).strftime("%Y-%m-%d")
                                    case "sun":
                                        days = self.get_day_difference(7)
                                        tast.createAt = (self.TODAY + timedelta(days=days)).strftime("%Y-%m-%d")
                                    case _:
                                        tast.createAt = date

                            case _:
                                # self.errorConsole.print(f'Неизвесный аргуиент:{comand}')
                                if task_text:
                                    if '\\'in comand:
                                        comand = comand.replace('\\','\n')
                                        tast.name+=" "+comand+'             '
                                    else:
                                        tast.name+=" "+comand
                        i+=1

                    js_task = tast.createTast('./data/Tasks.json')
                    if DUE:
                        due = self.__getDue(js_task['due'])
                        task_data[due][js_task['priority']].append(js_task)

                    else:
                        task_data['tasks'][js_task['priority']].append(js_task)

                    if cr:
                        js_task['createAt'] = tast.createAt
                    if rp:
                        js_task['remindOn'] = tast.remindOn

                    if task_status:
                        # self.__cange_task_by_id(task_data,js_task['id'],stat=task_status_str)
                        task_from_data = self.__cange_task_by_id(task_data,js_task['id'],status=task_status_str)

                case "dt"|"уд"|"ве":
                    if len(command_parts)==1:
                        DONT_CLEAR_MESS.append('[red]No argumentsd check [/] [green]help[/] [red]command to know more[/]')
                        self.createMonth('./data/Tasks.json',task_data)
                        self.displayTasks()
                        return
                    try:
                        task = self.combination_dict[command_parts[1]]
                        task_from_data = self.__del_task_by_id(task_data,task['id'])
                        task_data = task_from_data
                    except Exception as err:
                        self.errorConsole.print(err)
                
                case "dts"|"удн"|"веы":
                    tasks = command_parts[1::]
                    start=False
                    tasks_to_del=[]
                    task_from_data=None
                    if '-' in tasks[0]:
                        fr = tasks[0].split('-')[0]
                        to = tasks[0].split('-')[1]
                        for l in self.letters:
                            if l==fr:
                                start=True
                            if start:
                                task = self.combination_dict[l]
                                task_from_data = self.__del_task_by_id(task_data,task['id'])
                                task_data=task_from_data

                            if l == to:
                                start=False
                        task_data=task_from_data
                    else:
                        for t in tasks:
                            try:
                                task = self.combination_dict[t]
                                task_from_data = self.__del_task_by_id(task_data,task['id'])
                                task_data = task_from_data
                            except Exception as err:
                                self.errorConsole.print(err)

                case "dd":
                    lists = command_parts[1:]
                    if len(lists)==1:
                        categ = self.__getDue(lists[0])
                        task_data[categ]['done']=[]
                        self.createMonth('./data/Tasks.json',task_data)
                        self.displayTasks()
                    else:
                        for l in lists:
                            categ = self.__getDue(l)
                            task_data[categ]['done']=[]
                        self.createMonth('./data/Tasks.json',task_data)
                        self.displayTasks()


                case "cal":
                    self.show_calendar()


                case "dn"|"D"|"вз"|"вт"|"С":
                    if len(command_parts)==1:
                        DONT_CLEAR_MESS.append('[red]No argumentsd check [/] [green]help[/] [red]command to know more[/]')
                        self.createMonth('./data/Tasks.json',task_data)
                        self.displayTasks()
                        return
                    try:
                        task = self.combination_dict[command_parts[1]]
                        task_from_data = self.__cange_task_by_id(task_data,task['id'],status='done')
                        task_data = task_from_data
                    except Exception as err:
                        self.errorConsole.print(err)

                case "un"|"гт":
                    if len(command_parts)==1:
                        DONT_CLEAR_MESS.append('[red]No argumentsd check [/] [green]help[/] [red]command to know more[/]')
                        self.createMonth('./data/Tasks.json',task_data)
                        self.displayTasks()
                        return
                    try:
                        task = self.combination_dict[command_parts[1]]
                        task_from_data = self.__cange_task_by_id(task_data,task['id'],status='todo')
                        task_data = task_from_data
                    except Exception as err:
                        self.errorConsole.print(err)

                case "qu"|"вп":
                    if len(command_parts)==1:
                        DONT_CLEAR_MESS.append('[red]No argumentsd check [/] [green]help[/] [red]command to know more[/]')
                        return
                    try:
                        task = self.combination_dict[command_parts[1]]
                        task_from_data = self.__cange_task_by_id(task_data,task['id'],status='q')
                        task_data = task_from_data
                    except Exception as err:
                        self.errorConsole.print(err)

                case "wr"|"важ":
                    if len(command_parts)==1:
                        DONT_CLEAR_MESS.append('[red]No argumentsd check [/] [green]help[/] [red]command to know more[/]')
                        self.createMonth('./data/Tasks.json',task_data)
                        self.displayTasks()
                        return
                    try:
                        task = self.combination_dict[command_parts[1]]
                        task_from_data = self.__cange_task_by_id(task_data,task['id'],status='wrong')
                        task_data = task_from_data
                    except Exception as err:
                        self.errorConsole.print(err)

                case "LL"|"listL":
                    DONT_CLEAR_MESS.append("[green]List of lists[/]")
                    for k in list(task_data.keys()):
                        DONT_CLEAR_MESS.append(f"[deep_sky_blue1]|  {k}[/]")

                case "sett"|"settings":
                    self.__openSettings()
                
                case "ed"|"et"|"ув"|"рз":
                    if len(command_parts)==1:
                        DONT_CLEAR_MESS.append('[red]No argumentsd check [/] [green]help[/] [red]command to know more[/]')
                        self.createMonth('./data/Tasks.json',task_data)
                        self.displayTasks()
                        return
                    try:
                        task = self.combination_dict[command_parts[1]]
                        if task is None:
                            DONT_CLEAR_MESS.append('[red]Wrong task id[/]')
                            return
                        task = self.__getTaskById(task_data,task['id'])
                        params = command_parts[1::]
                        for i,p in enumerate(params):    
                            if 'st' == p:
                                status = params[i+1]
                                task_from_data = self.__cange_task_by_id(task_data,task['id'],status=status)
                            if 'pr' == p or 'p' == p:
                                prior = params[i+1]
                                task_from_data = self.__cange_task_by_id(task_data,task['id'],prios=prior)
                            if 'due'==p or 'du'==p:
                                due = self.__getDue(params[i+1]) 
                                prior = self.__getPrior(task['priority'])
                                task['due']=due
                                task['priority']=prior
                                status = task['status']
                                self.__del_task_by_id(task_data,task['id'])
                                task['status'] = status
                                for d in list(task_data.keys()):
                                    if d != "lastId" and d == due:
                                        for p in list(task_data[d]):
                                            if p == prior:
                                                task_data[d][p].append(task)


                            if 'n'==p or 'name' ==p:
                                part_name = params[i+1:]
                                name = ''
                                for n in part_name:
                                    if n == "p" or n == 'st':
                                        break
                                    name+=n+' '
                                task_from_data = self.__cange_task_by_id(task_data,task['id'],name=name)


                        task_data = task_from_data
                    except Exception as err:
                        self.errorConsole.print(err)

                case "help":
                    if len(command_parts)==1:
                        if self.SETTING['commands']:
                            for com in self.SETTING['commands']:
                                HELP_BOX+f'\n{com}'
                        print(Panel(HELP_BOX, title="Help"))
                    else:
                        com = command_parts[1]
                        try:
                            print(Panel(COMMANDS_DESCR[com], title=f"Help command {com}"))
                        except:
                            self.errorConsole.print(f'Wrong command {com}')
                    self.tasklistUpdate = False

                case "back"|"bk":
                    shutil.copy('./data/Tasks.json','./data/back/Tasks.json')


                case "se"|"sch"|"search"|"serch"|'/':
                    if len(command_parts)==1:
                        DONT_CLEAR_MESS.append('[red]No argumentsd check [/] [green]help[/] [red]command to know more[/]')
                        self.createMonth('./data/Tasks.json',task_data)
                        self.displayTasks()
                        return
                    self.SORTMODE = True
                    self.SORT_FILTER=command
                    serched = 0
                    search = command_parts[1]
                    self.createMonth('./data/Tasks.json',task_data)
                    filtr=task_data
                    for d in list(filtr.keys()):
                        if d != "lastId" :
                            for p in list(filtr[d]):
                                for ti,t in enumerate(filtr[d][p]):
                                    if search in t['name']:
                                        serched+=1
                                        tname = t['name']
                                        rname = tname.replace(search,f'[black on yellow underline]{search}[/]')
                                        filtr[d][p][ti]['name']=rname


                    if serched==0:
                        DONT_CLEAR_MESS.append(f'[red]Not Found any {search}[/]')
                    else:
                        DONT_CLEAR_MESS.append(f'[yellow]Found {serched} of {search}[/]')

                    self.displayTasks(True,mode='due',filtr=filtr)
                    return



                case "srw":
                    if len(command_parts)==1:
                        DONT_CLEAR_MESS.append('[red]No argumentsd check [/] [green]help[/] [red]command to know more[/]')
                        self.createMonth('./data/Tasks.json',task_data)
                        self.displayTasks()
                        return
                    self.SORTMODE = True
                    self.SORT_FILTER = command
                    by = command_parts[1:]
                    self.createMonth('./data/Tasks.json',task_data)
                    filtr=task_data
                        
                    for comId,com in enumerate(by):
                        match com:
                            case "tt"|"!tt": #Task type
                                tts = by[comId+1].split(',')
                                ttsF=[]
                                for t in tts:
                                    ttsF.append(self.__convertTaskType(t))
                                for t in tts:
                                    for k in list(task_data.keys()):
                                        if k !="lastId":
                                            for p in list(task_data[k].keys()):
                                                for task_id,task in enumerate(task_data[k][p]):
                                                    taskT=self.__convertTaskType(task['status'])
                                                    getT = self.__convertTaskType(t)
                                                    if not "!" in com:
                                                        if taskT==getT:
                                                            del filtr[k][p][task_id]
                                                    else:
                                                        if not taskT in ttsF:
                                                            if taskT!=getT:
                                                                del filtr[k][p][task_id]

                            case "D"|"du"|"due"|"!D"|"!du"|"!due":
                                dues = by[comId+1].split(',')
                                duesF=[]
                                for du in dues:
                                    duesF.append(self.__getDue(du))
                                for t in dues:
                                    for k in list(task_data.keys()):
                                        if k !="lastId":
                                            getT = self.__getDue(t)
                                            if not "!" in com:
                                                if getT == k:
                                                    del filtr[k]
                                            else:
                                                if not self.__getDue(k) in duesF:
                                                    if getT != k:
                                                        del filtr[k]
                            
                            case "se"|"sch"|"search"|"serch"|'/':
                                search = by[comId+1]
                                serched=0
                                for d in list(filtr.keys()):
                                    if d != "lastId" :
                                        for p in list(filtr[d]):
                                            for ti,t in enumerate(filtr[d][p]):
                                                if search in t['name']:
                                                    serched+=1
                                                    tname = t['name']
                                                    rname = tname.replace(search,f'[black on yellow underline]{search}[/]')
                                                    filtr[d][p][ti]['name']=rname
                                if serched==0:
                                    DONT_CLEAR_MESS.append(f'[red]Not Found any {search}[/]')
                                else:
                                    DONT_CLEAR_MESS.append(f'[yellow]Found {serched} of {search}[/]')
                                                    
                            case "p"|"!p":
                                pr = by[comId+1].split(',')
                                prF = []
                                for p in pr:
                                    prF.append(self.__getPrior(p))
                                for t in pr:
                                    match t:
                                        case "h":
                                            t="hight"
                                        case "m":
                                            t="medium"
                                        case "l":
                                            t="low"
                                        case "n":
                                            t="none"

                                    for k in list(task_data.keys()):
                                        if k !="lastId":
                                            for p in list(task_data[k].keys()):
                                                if not "!"in com:
                                                    if p==t:
                                                        del filtr[k][p]
                                                else:
                                                    if not self.__getPrior(p) in prF:
                                                        if p!=t:
                                                            del filtr[k][p]


                    self.displayTasks(True,mode='due',filtr=filtr)
                    return



                case "sr":
                    if len(command_parts)==1:
                        DONT_CLEAR_MESS.append('[red]No argumentsd check [/] [green]help[/] [red]command to know more[/]')
                        self.createMonth('./data/Tasks.json',task_data)
                        self.displayTasks()
                        return
                    # self.tasklistUpdate=False
                    by = command_parts[1:]
                    if by[0]!='A'and by[0]!='all':
                        self.SORTMODE=True
                        self.SORT_FILTER=command
                    else:
                        self.SORTMODE=False
                        self.SORT_FILTER=''

                    byDue=None
                    byPr = None
                    byQuer = None
                    if len(by)==1:
                        byDue = self.__getDue(by[0])
                        byPr = by[0] if byDue is None and by[0] in ['h','m','l'] else None
                        if byPr is None and byDue is None and not by[0]=="A": #TASK TYPE SORT
                            statuses = ["hight", "medium", "low", "none", "done", "archived"]
                            filtr={}
                            byType = by[0]
                            try:
                                for tp in list(self.taskTypes.keys()):
                                    if byType in self.taskTypes[tp]['shortNames']:
                                        for k in list(task_data.keys()):
                                            if k == 'lastId':
                                                continue
                                            filtr[k] = {status: [] for status in statuses}
                                            for p in list(task_data[k]):
                                                for t in task_data[k][p]:
                                                    if t['status'] in self.taskTypes[tp]['shortNames']:
                                                        filtr[k][p].append(t)
                                
                                self.createMonth('./data/Tasks.json',task_data)
                                self.displayTasks(True,mode='due',filtr=filtr)
                                return
                            except Exception as err:
                                self.errorConsole.print(err)

                                                    
                    else:
                        byDue =self.__getDue(by[0]) 
                        byPr = by[1] if by[1] in ['h','m','l'] else None
                        match byPr:
                            case 'h':
                                byPr='hight'
                            case 'm':
                                byPr='medium'
                            case 'l':
                                byPr='low'
                        filtr={}
                        # filtr[byDue] = task_data[byDue]
                        try:
                            for k in list(task_data.keys()):
                                for p in list(task_data[k]):
                                    if k==byDue and p==byPr:
                                        if isinstance(task_data.get(k), dict) and byPr in task_data[k]:
                                            filtr[k] = {byPr: task_data[k][p]}
                                        else:
                                            pass  # Или другое значение по умолчанию
                        except Exception as err:
                            self.errorConsole.print(err)

                        self.createMonth('./data/Tasks.json',task_data)
                        self.displayTasks(True,mode='due',filtr=filtr)
                        return

                    if not byDue is None or by[0]=='all' or by[0]=='A': #If by due
                        if by[0] == "A" or by[0]=='all':
                            self.createMonth('./data/Tasks.json',task_data)
                            self.displayTasks()
                            return
                        else:
                            filtr={}
                            filtr[byDue] = task_data[byDue]

                            self.createMonth('./data/Tasks.json',task_data)
                            self.displayTasks(True,mode='due',filtr=filtr)
                            return
                    elif not byPr is None: #PRIORITY SORT
                        match byPr:
                            case 'h':
                                byPr='hight'
                            case 'm':
                                byPr='medium'
                            case 'l':
                                byPr='low'
                        filtr={}
                        try:
                            for k in list(task_data.keys()):
                                # filtr[k] = {byPr: task_data[k][byPr]}
                                # filtr[k] = {byPr: task_data[k].get(byPr)} if isinstance(task_data.get(k), dict) else {}
                                if isinstance(task_data.get(k), dict) and byPr in task_data[k]:
                                    filtr[k] = {byPr: task_data[k][byPr]}
                                else:
                                    pass  # Или другое значение по умолчанию


                            self.createMonth('./data/Tasks.json',task_data)
                            self.displayTasks(True,mode='due',filtr=filtr)
                            return
                        except Exception as err:
                            self.errorConsole.print(err)
                        

                    else:
                        pass
                    #TODO: Create sort sys

                case "mv"|">"|'mt':
                    if len(command_parts)==1:
                        DONT_CLEAR_MESS.append('[red]No argumentsd check [/] [green]help[/] [red]command to know more[/]')
                        self.createMonth('./data/Tasks.json',task_data)
                        self.displayTasks()
                        return
                    task_id = command_parts[1:]
                    to =''
                    for t in task_id:
                        to = self.__getDue(t)
                        if to:
                            break
                    # to = self.__getDue( command_parts[2] )
                    try:
                        for t in task_id:
                            task = self.combination_dict[t]
                            task_from_data = self.__move_task_by_id(task_data,task['id'],to)
                            task_data = task_from_data
                    except Exception as err:
                        self.errorConsole.print(err)

                case 'mvb'|">>":
                    if len(command_parts)==1:
                        DONT_CLEAR_MESS.append('[red]No argumentsd check [/] [green]help[/] [red]command to know more[/]')
                        self.createMonth('./data/Tasks.json',task_data)
                        self.displayTasks()
                        return
                    fr = self.__getDue( command_parts[1] )
                    to = self.__getDue( command_parts[2] )    
                    try:
                        for key in task_data[fr]:
                            task_data[to][key].extend(task_data[fr][key])

                        # Очистка `tasks` после переноса
                        for key in task_data[fr]:
                            task_data[fr][key] = []
                    except Exception as err:
                        self.errorConsole.print(err)

                case "db"|"dB"|"<<":
                    if len(command_parts)==1:
                        DONT_CLEAR_MESS.append('[red]No argumentsd check [/] [green]help[/] [red]command to know more[/]')
                        self.createMonth('./data/Tasks.json',task_data)
                        self.displayTasks()
                        return
                    fr = self.__getDue( command_parts[1] )
                    try:
                        for key in task_data[fr]:
                            task_data[fr][key] = []
                    except:
                        pass

                case "crl"|"crlist"|'cls':
                    if len(command_parts)==1:
                        DONT_CLEAR_MESS.append('[red]No argumentsd check [/] [green]help[/] [red]command to know more[/]')
                        self.createMonth('./data/Tasks.json',task_data)
                        self.displayTasks()
                        return
                    name = command_parts[1]
                    new_data = {}
                    for d in list(task_data.keys()):
                        if d != "today" and d != "yesterday" and d!= "tommorow":
                            new_data[d] = task_data[d]
                        else:
                            break
                    new_data[name] = NEW_LIST
                    new_data['tommorow']=task_data['tommorow']
                    new_data['today']=task_data['today']
                    new_data['yesterday']=task_data['yesterday']
                    task_data = new_data

                    # task_data[name]=NEW_LIST
                    DONT_CLEAR_MESS.append(f"[blue]List[/] - {name} [green]created[/]")

                case "dls"|"dell"|'deL':
                    if len(command_parts)==1:
                        DONT_CLEAR_MESS.append('[red]No argumentsd check [/] [green]help[/] [red]command to know more[/]')
                        self.createMonth('./data/Tasks.json',task_data)
                        self.displayTasks()
                        return
                    list_to_del = command_parts[1]
                    try:
                        del task_data[list_to_del]
                    except:
                        self.errorConsole.print('Delete error')
                    DONT_CLEAR_MESS.append(f'[red]List {list_to_del} deleted[/]')


                # case "vi":
                #     mode = command_parts[1]
                #     match mode:
                #         case "lv"|'live':
                #             self.displayTasks("live")


                case "q"|"й":
                    exit()

                    
            self.createMonth('./data/Tasks.json',task_data)
            self.displayTasks()
        else:
            self.errorConsole.print("Неправильная команда")
            
    def __getPrior(self,prior):
        for pr in list( self.taskTypes.keys() ):
            if prior in self.taskTypes[pr]['shortNames']:
                return pr


    def __openSettings(self):
        settings_table = Table(show_header=False)  # Отключаем заголовки колонок
        settings_table.add_column("№", justify="right", style="bold cyan")
        settings_table.add_column("Settings", style="green")
        settings_table.add_column("Value", style="blue")
        settings_options=list(self.SETTING.keys())
        for settId,sett in enumerate(settings_options):
            if type(self.SETTING[sett]) == list:
                settings_table.add_row(f"{settId}",sett,str( self.SETTING[sett] ))
            else: 
                settings_table.add_row(f"{settId}",sett,str(self.SETTING[sett]) if len(str(self.SETTING[sett]))>0 and type(self.SETTING[sett]) != list else "[gold1]None[/]")

        if settings_table.rows:
            system('cls')
            self.mainConsole.print(settings_table)
        else:
            self.errorConsole.print("No settings in file")

        while True:
            userInput = self.mainConsole.input('Input option number [green]>>[/]')
            match userInput:
                case "q":
                    self.createMonth('./data/Setting.json',self.SETTING)
                    self.__loadSetting()
                    return
            intUserInput = int(userInput)
            settKey = settings_options[intUserInput]
            match settKey:
                case "sort":
                    new_sort = self.mainConsole.input("Input sort query to set it default [green]>>[/]")
                    self.SETTING[settKey] = "SET "+new_sort

                case "commands":
                    self.mainConsole.print('1)Create short command\n2)Delete short command\n3)List all short command')
                    userInput=self.mainConsole.input('[green]>>[/]')
                    match userInput:
                        case "1":
                            self.mainConsole.print('Type commands, when finish type [red]q[/]')
                            while True:
                                command = self.mainConsole.input('type short_commad|command [green]>>[/]')
                                if command != 'q':
                                    self.SETTING['commands'].append(command)
                                else:
                                    self.createMonth('./data/Setting.json',self.SETTING)
                                    self.__loadSetting()
                                    return
                        case "2":
                            for comId,com in enumerate(self.SETTING['commands']):
                                self.mainConsole.print(f'[deep_sky_blue1]{comId} - {com}[/]')
                            delCom = self.mainConsole.input("Delete commadn by id [red]>>[/]")
                            del self.SETTING['commands'][int(delCom)]
                        case "3":
                            for com in self.SETTING['commands']:
                                self.mainConsole.print(f'[deep_sky_blue1]{com}[/]')
                        case "q":
                            return
                case "week_day":
                    week_day_input = self.mainConsole.input("Week day num (1-7) [green]>>[/]")
                    self.SETTING['week_day'] = week_day_input
                    self.mainConsole.print('[green]Changed completed[/]')




    def generate_unique_combinationsv2(self):
        letters = self.letters
        
        # Генерация одиночных букв
        for letter in letters:
            yield letter
        
        # Генерация комбинаций из двух букв
        for combination in product(letters, repeat=2):
            yield ''.join(combination)


    def __formTableFromArr(self,Arr):
        global TABLE_ROWS
        table = Table(show_header=False)  # Отключаем заголовки колонок
        table.add_column("№", justify="right", style="bold cyan")
        table.add_column("Задача", style="green")
        table.add_column("Дата", style="green")
        tasks=[]

        # combinations_gen = self.generate_unique_combinations()  # Генератор уникальных комбинаций
        combinations_gen = self.generate_unique_combinationsv2()  # Генератор уникальных комбинаций
        self.combination_dict = {}

        for taskKey in list( Arr.keys() ):
            if taskKey=='cash' or taskKey=='lastId':
                continue
            try:
                if any(Arr[taskKey].values()):
                    tasks.append(f'[bold bright_magenta]{taskKey}[/bold bright_magenta]')
                for priorKey in list( Arr[taskKey].keys() ):
                    if len(Arr[taskKey][priorKey])>0:
                        match priorKey:
                            case "hight":
                               tasks.append(f'[bold red]   {priorKey}[/bold red]')
                            case "medium":
                                tasks.append(f'[bold yellow]   {priorKey}[/bold yellow]')
                            case "low":
                                tasks.append(f'[bold blue]   {priorKey}[/bold blue]')
                            case "none":
                                tasks.append(f'[bold white]   {priorKey}[/bold white]')
                            case 'done':
                                tasks.append(f'[bold bright_green]   {priorKey}[/bold bright_green]')
                            #INFO: Display deleted tasks
                            case "archived":
                                tasks.append(f'[bold bright_red]   {priorKey}[/bold bright_red]')

                        for task in Arr[taskKey][priorKey]:
                            unique_combination = next(combinations_gen)
                            # Добавляем в словарь комбинация:строка
                            self.combination_dict[unique_combination] = {"id":task['id'],"task":task['name']}
                            try:
                                if task['createAt']:
                                    task_str=self.__getTaskType(task['status'],unique_combination,task['name'],task['createAt'])
                                else:
                                    task_str=self.__getTaskType(task['status'],unique_combination,task['name'])
                            except:
                                task_str=self.__getTaskType(task['status'],unique_combination,task['name'])
                            try:
                                if task['remindOn']:
                                    task_str=self.__getTaskType(task['status'],unique_combination,task['name'],f'{task["createAt"]}--{task["remindOn"]}')
                                elif task['createAt']:
                                    task_str=self.__getTaskType(task['status'],unique_combination,task['name'],task['createAt'])
                                else:
                                    task_str=self.__getTaskType(task['status'],unique_combination,task['name'])
                            except:
                                task_str=self.__getTaskType(task['status'],unique_combination,task['name'])
                                

                            if not task_str is None:
                                tasks.append(task_str)
                            

            except Exception as err:
                pass

                                

        for i, task in enumerate(tasks, 1):
            try:
                parts =task.split('|')
                if len(parts)>1:
                    if len(parts)==2:
                        table.add_row(str(parts[0]), parts[1])
                    else:
                        table.add_row(str(parts[0]), parts[1],parts[2])

                elif cursor_row == i:
                    table.add_row("",f'[bold on green]{task}[/]')
                else:
                    table.add_row("", f'{task}')
            except:
                pass


        self.TABLE=table
        TABLE_ROWS = len(tasks)
        match self.SETTING['week_day']:
            case '1'|1:
                day= 'Mon'
            case '2'|2:
                day= 'Tue'
            case '3'|3:
                day= 'Wed'
            case '4'|4:
                day= 'Thu'
            case '5'|5:
                day= 'Fri'
            case '6'|6:
                day= 'Sat'
            case '7'|7:
                day= 'Sun'
            case _:
                day= ''
        if table.columns:
            self.mainConsole.print(table)
        else:
            self.mainConsole.print("[red]No tasks[/]")

        self.mainConsole.print(f'{self.TODAY.strftime("%Y-%m-%d")} - {day}')
    


    def __getTask(self,mode="normal",filtr = None):
        global cursor_row
        global LIVE_RUN
        LIVE_RUN=True
        task_data = self.loadMonthData("./data/Tasks.json")
        if mode == 'normal':
            if filtr == None:
                self.__formTableFromArr(task_data)
        elif mode == "due":
            self.__formTableFromArr(filtr)
        elif mode == "live":
            keyboard.on_press(self.update_cursor)  # Подключаем обработчик клавиш

            with Live(self.__formTableFromArr(task_data), refresh_per_second=10) as live:
                while LIVE_RUN:
                    live.update(self.__formTableFromArr(task_data))  # Обновляем отображение
                    time.sleep(0.3)  # Небольшая пауза
                    # system('cls')

            # while LIVE_RUN:
            #     self.__formTableFromArr(task_data)  # Обновляем отображение
            #     time.sleep(0.1)  # Небольшая пауза
            # pass



    def displayTasks(self,sort=False,mode='normal',filtr = None):
        if self.tasklistUpdate:
            system('cls') 
            if self.SORTMODE and not sort or "SET" in self.SORT_FILTER and not sort:
                self.__analyseCommand(self.SORT_FILTER)
                return

            self.__getTask(mode,filtr)
        if len(DONT_CLEAR_MESS)>0:
            # print(mess for mess in DONT_CLEAR_MESS)
            for mess in DONT_CLEAR_MESS:
                self.mainConsole.print(mess)
        DONT_CLEAR_MESS.clear()
        self.tasklistUpdate = True

    def getFilesInDir(self,path):
        filenames = next(walk(path), (None, None, []))[2]  # [] if no file
        return filenames

    def commadInput(self) ->None:
        command = self.mainConsole.input('[bold green]>>[/bold green]')
        self.__analyseCommand(command)

    def loadMonthData(self,path):
        with open(f"{path}", "r", encoding="utf-8") as file:
            data = json.load(file)
        return data
            
    def createMonth(self,path,data=NEW_TASK_FILE) -> None:
        new_m = data
        with open(f'{path}','w',encoding = "utf-8") as f:
            json.dump(new_m,f,ensure_ascii=False,indent=4)






if __name__ == "__main__":
    ToDo = ToDoConsole()
    while True:
        ToDo.commadInput()
