import os
import json
from functools import reduce

orders_path = os.path.join(os.path.dirname(__file__), "./dict/orders_data.json")
filtered_orders_output_path = os.path.join(os.path.dirname(__file__), "./result/filtered_orders.json")

def read_json_file(file_path):
    with open(file_path, 'r') as f:
        return json.load(f)


##################################################

def filter_orders(order):
    if order["customer_id"] == 105:
        return order["customer_id"] == 105
    else:
        pass

def calculate_order_amounts(acc, order):
    if order["customer_id"] == 105:
        acc += order["amount"]
    return acc

def calculate_order_amounts1(av, order):
    if order["customer_id"] == 105:
        av += 1
    return av

################################################

def display_results(total_amount, average_amount):
    print(f"Общая сумма заказов: {total_amount}")
    print("\n")
    print(f"Средняя сумма заказа: {average_amount}")
    print("\n")

def read_and_display_json(file_path, title):
    print(f"{title}")
    try:
        with open(file_path, 'r') as f:
            data = json.load(f)
            print(json.dumps(data, sort_keys=True, separators=(',', ':')))
    except FileNotFoundError:
        print(f"File {file_path} not found.")
    except json.JSONDecodeError:
        print(f"Error decoding JSON in {file_path}.")

def write_to_files(filtered_orders):
    with open(filtered_orders_output_path, 'w') as f:
        json.dump(filtered_orders, f)


orders = read_json_file(orders_path)
filtered_orders = list(filter(filter_orders, orders))
total_amount = reduce(calculate_order_amounts, orders, 0)
total_amount1 = reduce(calculate_order_amounts1, orders, 0)

average_amount = total_amount / total_amount1 if total_amount1 > 0 else 0

display_results(total_amount, average_amount)
write_to_files(filtered_orders)
read_and_display_json(filtered_orders_output_path, "Заказы по фильтру:")
