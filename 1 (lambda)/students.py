import os
import json
from functools import reduce

students_path = os.path.join(os.path.dirname(__file__), "./dict/student_data.json")
average_grades_output_path = os.path.join(os.path.dirname(__file__), "./result/average_grades.json")
filtered_students_output_path = os.path.join(os.path.dirname(__file__), "./result/filtered_students.json")

def read_json_file(file_path):
    with open(file_path, 'r') as f:
        return json.load(f)

def calculate_average_grade(student):
    grades_mean = sum(student["grades"]) / len(student["grades"])
    return {"name": student["name"], "average_grade": grades_mean}



###############################################
## ФИЛЬТР

def filter_students(students):
    return list(filter(lambda student: ((student["age"] < 21) and (student["grades"][0] > 89) and (student["grades"][1] > 96)), students))

###############################################




def calculate_total_average_grade(acc, student):
    return acc + sum(student["grades"]) / len(student["grades"])

def display_results(total_average_grade, student_with_highest_average_grade):
    print(f"Средняя сумма баллов всех студентов: {total_average_grade}")
    print("\n")
    read_and_display_json(average_grades_output_path, "Средняя сумма баллов каждого студента:")
    print("\n")
    print(f"Студент с наивысшим средним баллом: {student_with_highest_average_grade}")
    print("\n")
    read_and_display_json(filtered_students_output_path, "Студенты по фильтру:")

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

def write_to_files(average_grades_per_student, filtered_students):
    with open(average_grades_output_path, 'w') as f:
        json.dump(average_grades_per_student, f)
    with open(filtered_students_output_path, 'w') as f:
        json.dump(filtered_students, f)

students = read_json_file(students_path)
average_grades_per_student = list(map(calculate_average_grade, students))
filtered_students = filter_students(students)
total_average_grade = reduce(calculate_total_average_grade, students, 0) / len(students)
student_with_highest_average_grade = max(students, key=lambda student: sum(student["grades"]) / len(student["grades"]))

display_results(total_average_grade, student_with_highest_average_grade)
write_to_files(average_grades_per_student, filtered_students)
