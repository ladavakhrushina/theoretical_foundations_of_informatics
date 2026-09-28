valid_status = ['новый', 'в обработке', 'выполнен', 'отменён']




def load_orders(file):
    orders = []
    errors = []
    used_ids = set()

    try:
        with open(file, encoding='utf-8') as f:
            for line_number, line in enumerate(f, start = 1):
                line = line.strip().split(';')

                if not line:
                    continue

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
                    errors.append(f'Строка {line_number}: повторяющийся номер заказа {id}')
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
    return order["price"]*order["quantity"]


def cost_category(cost):

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
    categories = {order["category"] for order in orders}
    return sorted(categories)


def sort_by_cost(orders):
    sorted_orders = sorted(orders, key = lambda p: (-full_cost(p), p["id"]))
    return sorted_orders


def sort_by_category(orders):
    sorted_orders = sorted(orders, key = lambda p: (p["category"], p["name"]))
    return sorted_orders


def find_by_status(orders, status):
    status = status.strip().casefold()
    return [order for order in orders if status in order["status"]]


def find_by_category(orders, category):
    category = category.strip().casefold()
    return [order for order in orders if category in order["category"]]


def find_by_name(orders, name):
    name = name.strip().casefold()
    return [order for order in orders if name in order["name"]]

orders, errors = load_orders('orders.txt')

def large_orders(orders):
    return [order for order in orders if cost_category(full_cost(order)) == 'Крупный']


def category_statistics(orders):
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
            "complleted_cost": completed_cost,
            "average_cost": average_cost
        }
    return result


def status_statistics(orders):
    result = {}

    for status in valid_status:
        count = len([order for order in orders if order["status"] == status])
        result[status] = count

    return result


def overall_statistics(orders):

    completed_orders = [order for order in orders if order["status"] == "выполнен"]

    cancelled_orders = len([order for order in orders if order["status"] == "отменён"])

    total_cost = sum([full_cost(order) for order in orders])

    revenue = sum([full_cost(order) for order in orders if order["status"] == "выполнен"])

    if orders:
        average_cost = (total_cost/len(orders))
        most_expensive = max(orders, key=full_cost)

    else:
        average_cost = 0
        most_expensive = "отсутствует"

    buyers = {}
    for order in completed_orders:
        name = order["name"]
        if name not in buyers:
            buyers[name] = full_cost(order)
        else:
            buyers[name] += full_cost(order)

    if order:
        total = max(buyers.values())
        top_buyers = sorted([buyer for buyer, revenue in buyers.items() if revenue == total])
    else:
        top_buyers = "отсутствует"
        total = 0

    result = {
        "total_orders": len(orders),
        "completed_orders": len(completed_orders),
        "cancelled_orders": cancelled_orders,
        "total_cost": total_cost,
        "revenue": revenue,
        "average_cost": average_cost,
        "most_expensive": most_expensive,
        "top_buyers": top_buyers,
        "top_buyers_cost": total
    }
    return result



