
NEW_TASK = {
        "id":0,
        "name":'',
        "status":"",
        "priority":"none",
        "createAt":"",
        "due":"",
        "upFor":[], #For plasing this task up to tasks from array
        "downFor":[],
        "remindOn":"", #TODO: Do reminde sys for task
        "repitOn":"", #TODO: Do remind sys
        }

COMMANDS={
    "main":[
    'ct', #For create task by id
    'cr', #For create task by id
    'to', #For create task by id
    'на', #For create task by id
    'nt', #For new taskthe same as ct
    'dn', #For marking done task
    'D', #For marking done task
    'un', #For undu task
    'qu', #For questiuon task
    'et', #For edit task by id
    'ed', #For edit task by id
    'dt', #For delete task by id
    'dd', #For delete task by id
    'dts', #For delete task by id
    'mt', #For move task by id
    'mv', #For move task by id
    '>', #For move
    'sr', #For sort
    'q',
    'help',
    'vi',
    'се',
    'ве',
    'веы',
    'се',
    'сз',
    'ув',
    'рз',
    'й',
    'до',
    'уд',
    'удн',
    'вен',
    'вз',
    'вп',
    'вт',
    'важ',
    'wr',
    'help',
    'mvb',
    '>>',
    '<<',
    'db',
    'dB',
    'crl',
    'cls',
    'crlist',
    'dls',
    'dell',
    'deL',
    'LL',
    'listL',
    'back',
    'bk',
    'srw',
    'sett',
    'settings',
    'se',
    'serch',
    'search',
    'sch',
    '/',
    'cal',
    'dd',
    'utt',
    '',
    '',
    '',
    '',
    '',
    ],
    "middle_commands":[
        'due', #For due date or day
        'p',#For priority
        'cr', #Create date
        ],
    "last_commans":[],
}


NEW_LIST={
        "hight":[],
        "medium":[],
        "low":[],
        "none":[],
        "done":[],
        "archived":[],
        }

NEW_TASK_FILE={
        "tasks":{
            "hight":[],
            "medium":[],
            "low":[],
            "none":[],
            "done":[],
            "archived":[],
            },
        "cash":{
            "repeat":[]
            },
        "week":{
            "hight":[],
            "medium":[],
            "low":[],
            "none":[],
            "done":[],
            "archived":[],
            },
        "Mon":{
            "hight":[],
            "medium":[],
            "low":[],
            "none":[],
            "done":[],
            "archived":[],
            },
        "Tue":{
            "hight":[],
            "medium":[],
            "low":[],
            "none":[],
            "done":[],
            "archived":[],
            },
        "Wed":{
            "hight":[],
            "medium":[],
            "low":[],
            "none":[],
            "done":[],
            "archived":[],
            },
        "Thu":{
            "hight":[],
            "medium":[],
            "low":[],
            "none":[],
            "done":[],
            "archived":[],
            },
        "Fri":{
            "hight":[],
            "medium":[],
            "low":[],
            "none":[],
            "done":[],
            "archived":[],
            },
        "Sat":{
            "hight":[],
            "medium":[],
            "low":[],
            "none":[],
            "done":[],
            "archived":[],
            },
        "Sun":{
            "hight":[],
            "medium":[],
            "low":[],
            "none":[],
            "done":[],
            "archived":[],
            },
        'lastId':0,
        "tommorow":{
            "hight":[],
            "medium":[],
            "low":[],
            "none":[],
            "done":[],
            "archived":[],
            },
        "today":{
            "hight":[],
            "medium":[],
            "low":[],
            "none":[],
            "done":[],
            "archived":[],
            },
        "yesterday":{
            "hight":[],
            "medium":[],
            "low":[],
            "none":[],
            "done":[],
            "archived":[],
            },
        }
HELP_BOX='''
1)cr [name] - create task 
2)dn [letter of task] - make task done
3)un [letter of task] - make task undone
4)ed [letter of task] - edit task params
5)dt [letter of task] - delete task
5)dts [letters of tasks] - delete many tasks
6)qu [letter of task] - make question mark task
7)wr [letter of task] - make important mark to task
8)mv or > [letter of task] move task to another list
9)mvb >> - to move all of one block to another
10)db or dB or << - to delete choosed block
11)cls - create list
12)dls dell deL - delete list
13)sr - for sort tasks
14)srw - for sort tasks without smth
15)Many lines /
16)sett settings block
17)dd - delete done tasks from list's
18)utt - update today's tasks date

'''

COMMANDS_DESCR={
        "cr":'''
cr test
cr test due (td,tm,ye,mon,tue,wed,thu,fri,sat,sun,wee) p (h,m,l)
        ''',
        "dn":'''
dn a - done task a
        ''',
        "un":'''
un a - undone task a
        ''',
        "ed":'''
Works with any of (st p name) in any combinations
ed a st - status (t-todo d-done wr- important q-question) p (h,m,l) name new_name
        ''',
        "dt":'''
dt a - delete task a
dts a b c - delete tasks a b c
        ''',
        "qu":'''
qu a - make a task question
        ''',
        "wr":'''
wr a - make a task important
        ''',
        "mv":'''
mv or > a (td,tm,ye,mon,tue,wed,thu,fri,sat,sun,wee) - move task a to any of lists
> a b c td - will move a b c tasks to today
        ''',
        "mvb":'''
mvb or >> tm td - move tommorrow tasks to today
        ''',
        "db":'''
db/dB/<< td - delete all today tasks
        ''',
        "cls":'''
cls name - create list
        ''',
        "dls":'''
dls dell deL name - delete list
        ''',
        "sr":'''
sr A           - Show all tasks 
sr td/tm...    - Show tasks from chosed list
sr td... h/m/l - Show task from list with prior
        ''',
        "LL":'''
LL listL - List of listts
        ''',
        "srw":'''
srw
    params
    D/due
    tt - task type
    p - prioryty
Example:
    srw D dev - don't show dev block
    srw tt done - don't show donetasks
    srw !D dev show only dev block
    srw D dev tt qu !p h - don't show dev and ? type tasks 
        and show only hight priority tasks
    srw D test,test1,test2 - wont show this bloks and the same to others params tt and p 
        ''',
        "sett":'''
sett - open settings block
0 option needs to set default sort mode to sort tasks with opening program
1 option needs to creare short commands to comands you often use
        ''',
        "utt":'''
utt - Update today tasks date
        '''
        }

DEF_SETTINGS = {
        "sort":"",
        "commands":[], # For short comands
        "week_day":1,
        "ignore":{
            "date":0
            }

        }

DEF_TASK_TYPES = {
	"todo":{
		"shortNames":["td","todo","T","tommo"],
		"style":"[white]|[/]",
		"symbol":"[ ]",
		"symbol_style":"[yellow]|[/]"

	},
	"done":{
		"shortNames":["d","done","don"],
		"style":"[bright_green]|[/]",
		"symbol":"[+]",
		"symbol_style":"[bright_green]|[/]"

	},
	"archived":{
		"shortNames":["arch","ar","arh","archived"],
		"style":"[strike bright_red]|[/]",
		"symbol":"[D]",
		"symbol_style":"[bright_red]|[/]"

	},
	"quest":{
		"shortNames":["q","qu","quest"],
		"style":"[deep_sky_blue1]|[/]",
		"symbol":"[?]",
		"symbol_style":"[deep_sky_blue1]|[/]"

	},
	"wrong":{
		"shortNames":["wr","wron","wrong"],
		"style":"[red]|[/]",
		"symbol":"[!]",
		"symbol_style":"[red]|[/]"

	},
	"moved":{
		"shortNames":["mv","move"],
		"style":"[blue]|[/]",
		"symbol":"[>>]",
		"symbol_style":"[deep_sky_blue1]|[/]"

	},
	"dr":{
		"shortNames":["dr"],
		"style":"[yellow]|[/]",
		"symbol":"[!D!]",
		"symbol_style":"[gold1]|[/]"

	},
}
