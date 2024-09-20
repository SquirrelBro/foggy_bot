import random

# Функция для броска 4d6 и суммирования трех наибольших значений
def roll_4d6():
    rolls = [random.randint(1, 6) for _ in range(4)]  # Бросаем 4 кубика
    min_roll = min(rolls)  # Находим минимальное значение
    res = sum(rolls) - min_roll  # Суммируем три наибольших значения
    return f"<b>{res}</b> — ({rolls[0]}, {rolls[1]}, {rolls[2]}, {rolls[3]} - {min_roll})"

# Функция для генерации характеристик персонажа (6 бросков 4d6)
def generate_characteristics():
    characteristics = [roll_4d6() for _ in range(6)]  # Генерируем 6 характеристик
    return '\n'.join(characteristics)  # Возвращаем их в виде строки

# Функция для броска кубиков с различными параметрами
def roll_dice(num=1, dice=20, modifier=0, times=1, adv=False):
    results = []
    for _ in range(times):
        if adv:
            roll1 = random.randint(1 * num, dice * num)  # Броски с преимуществом
            roll2 = random.randint(1 * num, dice * num)
            best_roll = max(0, max(roll1, roll2) + modifier)  # Выбираем лучший результат
            results.append((roll1, roll2, best_roll))
        else:
            roll = random.randint(1 * num, dice * num)  # Обычный бросок
            res_roll = max(0, roll + modifier)  # Применяем модификатор
            results.append((roll, res_roll))
    return results

# Функция для преобразования результата броска в значение для добычи ресурсов
def farm_transform(roll):
    if 0 <= roll <= 4:
        return -random.randint(2, 8)
    if 5 <= roll <= 9:
        return -random.randint(1, 4)
    if 10 <= roll <= 14:
        return 0
    if 15 <= roll <= 19:
        return random.randint(1, 4)
    if 20 <= roll <= 24:
        return random.randint(2, 8)
    if roll >= 25:
        return random.randint(4, 16)
    print("пиздец", roll)
    return -99999999

# Функция для парсинга строки и выполнения бросков
def parse_and_roll(expression):
    parts = expression.split(' ')
    adv = 'adv' in parts  # Проверяем, есть ли преимущество
    farm = 'farm' in parts  # Проверяем, бросок ли это для добычи ресурсов
    dice_part = parts[0]
    dice = 20
    modifier = 0
    if 'd' in dice_part:
        num_dice = int(dice_part.split('d')[0]) if dice_part.split('d')[0] else 1
        dice = int(dice_part.split('d')[1].split('+')[0].split('-')[0])
    if '+' in dice_part:
        modifier = int(dice_part.split('+')[1])
    elif '-' in dice_part:
        modifier = -int(dice_part.split('-')[1])
    
    times = 1
    if len(parts) > 1 and parts[1].isdigit():
        times = int(parts[1])
    
    rolls = roll_dice(num_dice, dice, modifier, times, adv)
    if adv:
        total = sum([r[2] for r in rolls])
    else:
        total = sum([r[1] for r in rolls])

    if modifier > 0:
        str_modifier = f"(<i>+{modifier}</i>)"
    elif modifier < 0:
        str_modifier = f"(<i>{modifier}</i>)"
    else:
        str_modifier = ""

    if adv:
        details = ', '.join([f'[{r[0]}, {r[1]} -> {r[2]}]' for r in rolls])
    else:
        details = ', '.join([f'[{r[0]} -> {r[1]}]' for r in rolls])
    if farm:
        farming = 0
        for i in rolls:
            farming += farm_transform(i[len(i) - 1])
        return f'<b>Общий результат</b>: {total}. \n {details} \n <b>Результат добычи золота/ресурсов</b>: {farming}'
    else:
        return f'<b>Общий результат</b>: {total}. \n {details}'
