import gspread
from oauth2client.service_account import ServiceAccountCredentials
import html
import re
from datetime import datetime

# Настройка доступа к Google Sheets
cred_file = 'cred_file.json'
scope = ['https://spreadsheets.google.com/feeds','https://www.googleapis.com/auth/drive']
creds = ServiceAccountCredentials.from_json_keyfile_name(cred_file, scope)
client = gspread.authorize(creds)

# Функция для открытия или создания таблицы и листов
def open_or_create_sheet(sheet_name, worksheet_name):
    try:
        # Попытка открыть таблицу
        sheet = client.open(sheet_name)
    except gspread.SpreadsheetNotFound:
        # Создание таблицы, если она не найдена
        sheet = client.create(sheet_name)
    
    try:
        # Попытка открыть лист
        worksheet = sheet.worksheet(worksheet_name)
    except gspread.WorksheetNotFound:
        # Создание листа, если он не найден
        worksheet = sheet.add_worksheet(title=worksheet_name, rows="100", cols="20")
    
    return worksheet

# Открытие или создание таблиц и листов
sheet = open_or_create_sheet("Общие предметы", "Список")
old_sheet = open_or_create_sheet("Общие предметы", "Старое")

def parse_and_sheet(command_text, user): 
    # Парсинг команды, переданной из Telegram
    command_parts = re.findall(r'[^"\s]\S*|".+?"', command_text)

    if not command_parts:
        return "Пожалуйста, введите команду."

    command = command_parts[0].lower()
    args = command_parts[1:]

    # Определение команды и вызов соответствующей функции
    if command in ["show", "список"]:
        return show()
    elif command in ["take", "беру"]:
        if len(args) < 1:
            return "Пожалуйста, укажите ID или название предмета."
        item = args[0]
        if item.isdigit():
            item = int(item)
        else:
            item = item.strip('"')
        count = int(args[1]) if len(args) > 1 else 1
        return take(item, user, count)
    elif command in ["add", "кладу"]:
        name = None
        comment = None
        count = 1
        for i, arg in enumerate(args):
            if arg.startswith('"'):
                if name is None:
                    name = arg.strip('"')
                    if i+1 < len(args) and args[i+1].isdigit():
                        count = int(args[i+1])
                elif comment is None:
                    comment = arg.strip('"')
        if name is None:
            if args[0].isdigit():
                name = int(args[0])
            else:
                return "Пожалуйста, укажите название в кавычках."
        return add(name, user, count, comment)
    elif command in ["del", "удалить"]:
        if len(args) < 1:
            return "Пожалуйста, укажите ID."
        row_index = int(args[0])
        return delete_data(row_index)
    else:
        return "Неизвестная команда. Доступные команды: show, take, add, del."

def show(): 
    # Функция выдачи всех элементов таблицы общих предметов
    records = sheet.get_all_records()

    html_records = ["<b>ID | Название | Количество | Комментарий</b>"]
    for record in records:
        html_record = f"{record['ID']}. {record['Название']} — {record['Количество']} <i>{record['Комментарий']}</i>"
        html_records.append(html_record)

    return "\n".join(html_records)

def take(item, user, count=1): 
    # Функция вычитания нужного элемента из списка с переносом его в таблицу "Удалённых"
    records = sheet.get_all_records()
    for i, record in enumerate(records):
        if str(record['ID']) == str(item) or (isinstance(item, str) and record['Название'].lower() == item.lower()):
            record['Количество'] = str(max(0, int(record['Количество']) - count))

            sheet.update([list(record.values())[:4]], f"A{i+2}:D{i+2}")  # Обновляем только первые 4 элемента списка
            result_text = f"Вы взяли <b>{record['Название']}</b> в количестве {count}. ID: {record['ID']}."

            if record['Количество'] == '0':
                date = datetime.now().strftime("%d.%m.%Y")
                new_id = str(len(old_sheet.get_all_values()))
                old_sheet.append_row([new_id, record['Название'], record['От кого?'], user, date])
                delete_data(i+1, return_string=False)

            return result_text

    return "Предмет не найден."

def add(item, user, count=1, comment=None): 
    # Добавление нового элемента в таблицу
    records = sheet.get_all_records()
    for i, record in enumerate(records):
        if (record['Название'] == item or record['ID'] == item) and (record['Комментарий'] == comment or comment == None):
            record['Количество'] = str(int(record['Количество']) + count)
            if user not in record['От кого?'].split(', '):
                record['От кого?'] += ', ' + user
            sheet.update([list(record.values())[:5]], f"A{i+2}:E{i+2}")
            result_text = f"Добавлен предмет <b>{record['Название']}</b>. ID: {record['ID']}"
            return result_text

    if item.isdigit():
        return "Новый предмет нельзя добавить по ID. Пожалуйста, укажите имя предмета."

    new_id = str(len(sheet.get_all_values()))
    date = datetime.now().strftime("%d.%м.%Y")
    sheet.append_row([new_id, item, user, str(count), date, comment if comment is not None else ''])

    result_text = f"Добавлен предмет <b>{item}</b>. ID: {new_id}."
    return result_text

def delete_data(row_index, return_string=True): 
    # Полное удаление элемента таблицы без переноса его в "Удалённые"
    record = sheet.row_values(row_index+1)
    if return_string:
        result_text = f"Удалён предмет <b>{record[1]}</b>. ID: {record[0]}"

    sheet.delete_rows(row_index+1)

    records = sheet.get_all_records()
    for i, record in enumerate(records, start=1):
        if int(record['ID']) > row_index:
            record['ID'] = str(i)
            sheet.update([[str(i)]], f"A{i+1}")

    if return_string:
        return result_text
