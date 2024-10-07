import os
import json
from functools import reduce

users_path = os.path.join(os.path.dirname(__file__), "./dict/users_data.json")
sum_users_output_path = os.path.join(os.path.dirname(__file__), "./result/sum_users.json")
filtered_users_output_path = os.path.join(os.path.dirname(__file__), "./result/filtered_users.json")

def read_json_file(file_path):
    with open(file_path, 'r') as f:
        return json.load(f)
    

#####################################################

def filter_and_calculate_expenses():
    global filtered_users, total_expenses_filtered
    filtered_users = list(filter(lambda user: sum(user['expenses']) < 300, users))
    total_expenses_filtered = reduce(lambda acc, user: acc + sum(user['expenses']), filtered_users, 0)

#####################################################


    
def display_results():
    read_and_display_json(filtered_users_output_path, "Пользователи по фильтру:")
    print("\n")
    read_and_display_json(sum_users_output_path, "Сумма расходов каждого пользователя:")
    print("\n")
    print(f"Общая сумма расходов всех отфильтрованных пользователей: {total_expenses_filtered}")
    
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

def write_to_files():
    with open(filtered_users_output_path, 'w') as f:
        json.dump(filtered_users, f)
    with open(sum_users_output_path, 'w') as f:
        json.dump(total_expenses_per_user, f)
                
filtered_users = []  
users = read_json_file(users_path)
total_expenses_per_user = {user['name']: int(sum(user['expenses'])) for user in users}
total_expenses_filtered = 0      

filter_and_calculate_expenses()
display_results()
write_to_files()