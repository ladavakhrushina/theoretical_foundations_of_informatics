def load_orders(file):
    '''читает файл, возвращает корректные заказы и список ошибок'''
    valid_status = ['новый', 'в обработке', 'выполнен', 'отменён']
    orders = []
    errors = []

    used_ids = set()

    try:
        with open(file, encoding='utf-8') as f:
            for line_number, line in enumerate(f, start = 1):
                line = line.strip()

                if not line:
                    continue
                line = line.split(';')

                if len(line) != 6:
                    errors.append(f'Строка {line_number}: неверное количество полей')
                    continue

                try:
                    id = int(line[0])
                    name = str(line[1])
                    category = str(line[2])
                    quantity = int(line[3])
                    price = float(line[4])
                    status = str(line[5])

                except ValueError:
                    errors.append(f'Строка {line_number}: неверно указано числовое значение')
                    continue

                if id <= 0:
                    errors.append(f'Строка {line_number}: номер заказа должен быть положительным')
                    continue

                if not name:
                    errors.append(f'Строка {line_number}: имя покупателя не должно быть пустым полем')
                    continue

                if not category:
                    errors.append(f'Строка {line_number}: категория товара не должна быть пустым полем')
                    continue
                
                if quantity <= 0:
                    errors.append(f'Строка {line_number}: количество товара должно быть положительным')
                    continue

                if price <= 0:
                    errors.append(f'Строка {line_number}: цена товара должна быть положительной')
                    continue

                if status.casefold() not in valid_status:
                    errors.append(f'Строка {line_number}: неизвестный статус товара - "{status}"')
                    continue

                if id in used_ids:
                    errors.append(f'Строка {line_number}: повторяющийся номер заказа - {id}')
                    continue
                used_ids.add(id)

                orders.append({
                    "id": id,
                    "name": name,
                    "category": category,
                    "quantity": quantity,
                    "price": price,
                    "status": status.casefold()
                })

    except FileNotFoundError:
        errors.append(f"Файл '{file}' не найден")

    if len(orders) == 0:
        errors.append('Не найдено корректных заказов')

    return orders, errors


def full_cost(order):
    '''возвращает полную стоимость заказа'''
    return order["price"] * order["quantity"]


def cost_category(cost):
    '''возвращает категорию заказа'''
    if cost < 1000:
        return "Малый"
    
    elif cost < 5000:
        return "Средний"

    else:
        return "Крупный"

assert cost_category(999.99) == "Малый"
assert cost_category(1000) == "Средний"
assert cost_category(4999.99) == "Средний"
assert cost_category(5000) == "Крупный"


def all_categories(orders):
    '''возвращает список уникальных категорий'''
    categories = {order["category"] for order in orders}
    return sorted(categories)


def sort_by_cost(orders):
    '''сортирует заказы по цене'''
    sorted_orders = sorted(orders, key = lambda p: (-full_cost(p), p["id"]))
    return sorted_orders


def sort_by_category(orders):
    '''сортирует заказы по категории'''
    sorted_orders = sorted(orders, key = lambda p: (p["category"], p["name"]))
    return sorted_orders


def find_by_status(orders, status):
    '''возвращает заказы указанного статуса'''
    status = status.strip().casefold()
    return [order for order in orders if status in order["status"].casefold()]


def find_by_category(orders, category):
    '''возвращает заказы нужной категории'''
    category = category.strip().casefold()
    return [order for order in orders if category in order["category"].casefold()]


def find_by_name(orders, name):
    '''возвращает заказы по имени покупателя'''
    name = name.strip().casefold()
    return [order for order in orders if name in order["name"].casefold()]


def large_orders(orders):
    '''возвращает крупные заказы'''
    return [order for order in orders if cost_category(full_cost(order)) == 'Крупный']


def category_statistics(orders):
    '''возвращает статистику заказов по категориям'''
    result = {}

    for category in all_categories(orders):
        count_of_orders = len([order for order in orders if order["category"] == category])

        count_of_units = sum([order["quantity"] for order in orders if order["category"] == category])

        total_cost = sum([full_cost(order) for order in orders if order["category"] == category])

        completed_cost = sum([full_cost(order) for order in orders 
                              if order["category"] == category and order["status"] == "выполнен"])
        
        if count_of_orders:
            average_cost = (total_cost/count_of_orders)
        else:
            average_cost = 0

        result[category] = {
            "orders_count": count_of_orders,
            "units_count": count_of_units,
            "total_cost": total_cost,
            "completed_cost": completed_cost,
            "average_cost": average_cost
        }
    return result


def status_statistics(orders):
    '''возвращает статистику заказов по статусам'''
    result = {}
    valid_status = ['новый', 'в обработке', 'выполнен', 'отменён']

    for status in valid_status:
        count = len([order for order in orders if order["status"] == status])
        result[status] = count

    return result


def overall_statistics(orders):
    '''возвращает общую статистику по заказам'''

    completed_orders = [order for order in orders if order["status"] == "выполнен"]

    cancelled_orders = len([order for order in orders if order["status"] == "отменён"])

    total_cost = sum([full_cost(order) for order in orders])

    revenue = sum([full_cost(order) for order in orders if order["status"] == "выполнен"])

    if orders:
        average_cost = (total_cost/len(orders))
        most_expensive = full_cost(max(orders, key=full_cost))

    else:
        average_cost = 0
        most_expensive = "Заказ не найден"

    buyers = {}
    for order in completed_orders:
        name = order["name"]
        if name not in buyers:
            buyers[name] = full_cost(order)
        else:
            buyers[name] += full_cost(order)

    if buyers:
        total = max(buyers.values())
        top_buyers = sorted([buyer for buyer, revenue in buyers.items() if revenue == total])
    else:
        total = "Заказ не найден"
        top_buyers = "Покупатель не найден"

    if buyers:
        result = {
                "total_orders": len(orders),
                "completed_orders": len(completed_orders),
                "cancelled_orders": cancelled_orders,
                "total_cost": total_cost,
                "revenue": revenue,
                "average_cost": average_cost,
                "most_expensive": most_expensive,
                "top_buyers": ', '.join(top_buyers)
                }
    else:
        result = {
                "total_orders": len(orders),
                "completed_orders": len(completed_orders),
                "cancelled_orders": cancelled_orders,
                "total_cost": total_cost,
                "revenue": revenue,
                "average_cost": average_cost,
                "most_expensive": most_expensive,
                "top_buyers": top_buyers
                }

    return result


def print_orders(orders):
    '''печатает список заказов'''
    if orders:
        print('\nномер    покупатель         категория     сумма     статус\n')
        for order in orders:
            print(f'№{order["id"]:<5}| {order["name"]:<17}| {order["category"]:<12}| {full_cost(order):<8}| {order["status"]}')
    else:
        print('Заказы не найдены')

def save_report(orders, errors):
    '''выгружает отчёт по заказам в файл'''
    with open('orders_report.txt', 'a', encoding='utf-8') as f:
        if orders:
            f.write(f'\n        ОТЧЁТ ПО АНАЛИЗУ ЗАКАЗОВ\n')
            f.write(f'\nКоличество корректных записей: {len(orders)}')
            f.write(f'\nКоличество некорректных записей: {len(errors)}')
            f.write(f'\nУникальные категории: {', '.join(all_categories(orders))}')

            f.write('\n\n       ЗАКАЗЫ ПО УБЫВАНИЮ СТОИМОСТИ\n')
            f.write('\nномер    покупатель        сумма      статус\n')
            for num, order in enumerate(sort_by_cost(orders), start=1):
                f.write(f'\n№{order["id"]:<5}| {order["name"]:<17}| {full_cost(order):<8}| {order["status"]}')

            f.write('\n\n       КРУПНЫЕ ЗАКАЗЫ\n')
            if large_orders(orders):
                f.write('\nномер    покупатель        сумма      статус\n')
                num = 0
                for order in orders:
                    if cost_category(full_cost(order)) == 'Крупный':
                        num += 1
                        f.write(f'\n№{order["id"]:<5}| {order["name"]:<17}| {full_cost(order):<8}| {order["status"]}')
            else:
                f.write('Крупные заказы не найдены')

            f.write('\n\n       ОБЩИЕ ПОКАЗАТЕЛИ\n')
            f.write(f'\nОбщее количество заказов: {overall_statistics(orders)["total_orders"]}')
            f.write(f'\nКоличество выполненных заказов: {overall_statistics(orders)["completed_orders"]}')
            f.write(f'\nКоличество отменённых заказов: {overall_statistics(orders)["cancelled_orders"]}')
            f.write(f'\nОбщая стоимость заказов: {overall_statistics(orders)["total_cost"]}')
            f.write(f'\nВыручка по выполненным заказам: {overall_statistics(orders)["revenue"]}')
            f.write(f'\nСредняя стоимость заказа: {overall_statistics(orders)["average_cost"]:.2f}')
            f.write(f'\nСамый дорогой заказ: {overall_statistics(orders)["most_expensive"]}')
            f.write(f'\nПокупатели с наибольшей суммой заказа: {overall_statistics(orders)["top_buyers"]}')

            f.write('\n\n       СТАТИСТИКА ПО КАТЕГОРИЯМ\n')
            for category in category_statistics(orders):
                f.write(f'\n    {category}:')
                f.write(f'\nКоличество заказов: {category_statistics(orders)[category]["orders_count"]}')
                f.write(f'\nКоличество заказанных единиц товара: {category_statistics(orders)[category]["units_count"]}')
                f.write(f'\nОбщая стоимость всех заказов: {category_statistics(orders)[category]["total_cost"]}')
                f.write(f'\nСтоимость выполненных заказов: {category_statistics(orders)[category]["completed_cost"]}')
                f.write(f'\nСреднаяя стоимость одного заказа: {category_statistics(orders)[category]["average_cost"]:.2f}\n')

            f.write('\n\n       СТАТИСТИКА ПО СТАТУСАМ\n')
            for status in status_statistics(orders):
                f.write(f'\n{status.capitalize()}: {status_statistics(orders)[status]} заказов')

            f.write('\n\n       ОШИБКИ ВХОДНЫХ ДАННЫХ\n\n')
            if errors:
                f.write('\n'.join(errors))
            else:
                f.write('Ошибок не найдено')

        else:
            f.write('\nЗАКАЗЫ НЕ НАЙДЕНЫ')
            f.write('\n\n       ОШИБКИ ВХОДНЫХ ДАННЫХ\n\n')
            f.write('\n'.join(errors))


def main_programm():
    orders, errors = load_orders('orders.txt')

    while True:
        print("""
\n         \033[33mМЕНЮ\033[0m\n
\033[35m1. Показать все заказы
2. Показать заказы по убыванию стоимости
3. Показать заказы по категориям
4. Найти заказы по статусу
5. Найти заказы по категории
6. Найти заказы покупателя
7. Показать крупные заказы
8. Показать статистику
9. Сохранить отчёт
0. Завершить программу\033[0m\n""")
        choice = input('\033[36mВыберите пункт: \033[0m').strip().casefold()

        if choice == '1':
            print_orders(orders)

        elif choice == '2':
            print_orders(sort_by_cost(orders))

        elif choice == '3':
            print_orders(sort_by_category(orders))

        elif choice == '4':
            status = input('\033[36mВведите статус: \033[0m').strip().casefold()
            print_orders(find_by_status(orders, status))

        elif choice == '5':
            category = input('\033[36mВведите категорию: \033[0m').strip().casefold()
            print_orders(find_by_category(orders, category))

        elif choice == '6':
            name = input('\033[36mВведите имя покупателя: \033[0m').strip().casefold()
            print_orders(find_by_name(orders, name))

        elif choice == '7':
            if large_orders(orders):
                print('\nномер    покупатель        сумма      статус\n')
                for order in orders:
                            if cost_category(full_cost(order)) == 'Крупный':
                                print(f'№{order["id"]:<5}| {order["name"]:<17}| {full_cost(order):<8}| {order["status"]}')
            else:
                print('Заказы не найдены')

        elif choice == '8':
            if orders:
                print(f'\nОбщее количество заказов: {overall_statistics(orders)["total_orders"]}')
                print(f'Количество выполненных заказов: {overall_statistics(orders)["completed_orders"]}')
                print(f'Количество отменённых заказов: {overall_statistics(orders)["cancelled_orders"]}')
                print(f'Общая стоимость заказов: {overall_statistics(orders)["total_cost"]}')
                print(f'Выручка по выполненным заказам: {overall_statistics(orders)["revenue"]}')
                print(f'Средняя стоимость заказа: {overall_statistics(orders)["average_cost"]:.2f}')
                print(f'Самый дорогой заказ: {overall_statistics(orders)["most_expensive"]}')
                print(f'Покупатели с наибольшей суммой заказа: {overall_statistics(orders)["top_buyers"]}')
            else:
                print('Заказы не найдены')
            

        elif choice == '9':
            save_report(orders, errors)
            print('\033[31mЗОтчёт сохранён\033[0m\n')

        elif choice == '0':
            print('\n\033[31mПрограмма завершена\033[0m\n')
            break

        else:
            print('Неизвестный пункт меню. Попробуйте еще раз')
        

main_programm()