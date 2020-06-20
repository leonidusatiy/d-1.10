import sys 
import requests    
base_url = "https://api.trello.com/1/{}"
# заполните своими значениями
auth_params = {    
    'key': "",    
    'token': "", }
# board_id должен быть в длинном формате (пример: 5eea4899da0a291412269890)
board_id = ""    
    
def read():      
    # Получим данные всех колонок на доске:      
    column_data = requests.get(base_url.format('boards') + '/' + board_id + '/lists', params=auth_params).json()     

    # Теперь выведем название каждой колонки и всех заданий, которые к ней относятся:      
    for column in column_data:      
        # Получим данные всех задач в колонке и перечислим все названия      
        task_data = requests.get(base_url.format('lists') + '/' + column['id'] + '/cards', params=auth_params).json()
        print(column['name'] + " (" + str(len(task_data)) + ")")
        if not task_data:      
            print('\t' + 'Нет задач!')      
            continue      
        for task in task_data:      
            print('\t' + task['name'])    
    
def create(name, column_name):      
    # Получим данные всех колонок на доске      
    column_data = requests.get(base_url.format('boards') + '/' + board_id + '/lists', params=auth_params).json()      
      
    # Переберём данные обо всех колонках, пока не найдём ту колонку, которая нам нужна      
    for column in column_data:      
        if column['name'] == column_name:
            # Создадим задачу с именем _name_ в найденной колонке      
            requests.post(base_url.format('cards'), data={'name': name, 'idList': column['id'], **auth_params})      
            break
    
def move(name, column_name):    
    # Получим данные всех колонок на доске    
    column_data = requests.get(base_url.format('boards') + '/' + board_id + '/lists', params=auth_params).json()
        
    # Среди всех колонок ищем задачи с запрошенным именем   
    tasks = []
    for column in column_data:    
        column_tasks = requests.get(base_url.format('lists') + '/' + column['id'] + '/cards', params=auth_params).json()    
        for task in column_tasks:    
            if task['name'] == name:    
                tasks.append(task)

    task_id = None
    if len(tasks) == 0:
        print("Задачи " + name + " не найдено!")
        return
    # если задача одна, сразу получаем ее id
    elif len(tasks) == 1:
        task_id = tasks[0]['id']
    # если задач с таким именем больше одной, выводим их все
    else:
        print(f"Найдено несколько задач с названием {task['name']}:")
        for index, task in enumerate(tasks):
            colname = requests.get(base_url.format('lists') + '/' + task['idList'], params=auth_params).json()['name']
            print(f"{index + 1}. {task['id']} - {colname} - {task['dateLastActivity']}")
        task_num = int(input("Введите номер задачи, которую будем перемещать: "))

        # если ввели невалидное значение, выходим
        if task_num > len(tasks):
            print("Введено неправильное значение!")
            return
        # получаем id выбранной задачи
        else:
            task_id = tasks[task_num - 1]['id']

    # Теперь, когда у нас есть id задачи, которую мы хотим переместить    
    # Переберём данные обо всех колонках, пока не найдём ту, в которую мы будем перемещать задачу    
    for column in column_data:    
        if column['name'] == column_name:    
            # И выполним запрос к API для перемещения задачи в нужную колонку    
            requests.put(base_url.format('cards') + '/' + task_id + '/idList', data={'value': column['id'], **auth_params})    
            break    

def addList(name):
    # запрос на добавление колонки к нашей доске
    requests.post(base_url.format('lists'), data={'name': name, 'idBoard': board_id, **auth_params})

def help():
    print("Возможные команды:")
    print("create - создание новой карточки в определенном списке. Пример: python trello-d1.py create \"TaskName\" \"ListName\"")
    print("move - перемещение карточки в определенный список. Пример: python trello-d1.py move \"TaskName\" \"ListName\"")
    print("addlist - создание нового списка. Пример: python trello-d1.py addlist \"ListName\"")

def checkAuth():
    if len(auth_params['key']) < 1 or len(auth_params['token']) < 1 or len(board_id) < 1:
        return False
    else:
        return True

if __name__ == "__main__":
    if checkAuth():
        if len(sys.argv) < 2:    
            read()
        elif sys.argv[1] == 'help':
            help()    
        elif sys.argv[1] == 'create':    
            create(sys.argv[2], sys.argv[3])    
        elif sys.argv[1] == 'move':    
            move(sys.argv[2], sys.argv[3])
        elif sys.argv[1] == 'addlist':
            addList(sys.argv[2])
        else:
            print("Неизвестная команда!")
    else:
        print("Заполните авторизационные данные и ссылку на доску")