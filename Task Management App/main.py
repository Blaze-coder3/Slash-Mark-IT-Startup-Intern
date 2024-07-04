import pandas as pd
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import make_pipeline
import random
import joblib

# Initialize an empty task list
tasks = pd.DataFrame(columns=['description', 'priority', 'completed'])

# Load pre-existing tasks from a CSV file (if any)
try:
    tasks = pd.read_csv('tasks.csv')
except FileNotFoundError:
    pass

# Function to save tasks to a CSV file
def save_tasks():
    tasks.to_csv('tasks.csv', index=False)

# Load or train the task priority classifier
try:
    model = joblib.load('task_model.pkl')
except FileNotFoundError:
    vectorizer = CountVectorizer()
    clf = MultinomialNB()
    model = make_pipeline(vectorizer, clf)
    if not tasks.empty:
        model.fit(tasks['description'], tasks['priority'])

# Function to add a task to the list
def add_task(description, priority):
    global tasks  # Declare tasks as a global variable
    if priority not in ['Low', 'Medium', 'High']:
        print("Invalid priority. Please enter Low, Medium, or High.")
        return
    new_task = pd.DataFrame({'description': [description], 'priority': [priority], 'completed': [False]})
    tasks = pd.concat([tasks, new_task], ignore_index=True)
    model.fit(tasks['description'], tasks['priority'])
    joblib.dump(model, 'task_model.pkl')
    save_tasks()
    print("Task added successfully.")

# Function to remove a task by description
def remove_task(description):
    global tasks
    if description not in tasks['description'].values:
        print("Task not found.")
        return
    tasks = tasks[tasks['description'] != description]
    save_tasks()
    print("Task removed successfully.")

# Function to list all tasks
def list_tasks(show_completed=True):
    if tasks.empty:
        print("No tasks available.")
    else:
        if show_completed:
            print(tasks)
        else:
            print(tasks[tasks['completed'] == False])

# Function to recommend a task based on machine learning
def recommend_task():
    if not tasks.empty:
        high_priority_tasks = tasks[(tasks['priority'] == 'High') & (tasks['completed'] == False)]
        if not high_priority_tasks.empty:
            random_task = random.choice(high_priority_tasks['description'].values)
            print(f"Recommended task: {random_task} - Priority: High")
        else:
            print("No high-priority tasks available for recommendation.")
    else:
        print("No tasks available for recommendations.")

# Function to edit a task's description or priority
def edit_task(description, new_description=None, new_priority=None):
    global tasks
    if description not in tasks['description'].values:
        print("Task not found.")
        return
    if new_description:
        tasks.loc[tasks['description'] == description, 'description'] = new_description
    if new_priority:
        if new_priority not in ['Low', 'Medium', 'High']:
            print("Invalid priority. Please enter Low, Medium, or High.")
            return
        tasks.loc[tasks['description'] == description, 'priority'] = new_priority
    model.fit(tasks['description'], tasks['priority'])
    joblib.dump(model, 'task_model.pkl')
    save_tasks()
    print("Task edited successfully.")

# Function to mark a task as completed
def complete_task(description):
    global tasks
    if description not in tasks['description'].values:
        print("Task not found.")
        return
    tasks.loc[tasks['description'] == description, 'completed'] = True
    save_tasks()
    print("Task marked as completed.")

# Main menu
while True:
    print("\nTask Management App")
    print("1. Add Task")
    print("2. Remove Task")
    print("3. List Tasks")
    print("4. Recommend Task")
    print("5. Edit Task")
    print("6. Complete Task")
    print("7. Exit")

    choice = input("Select an option: ")

    if choice == "1":
        description = input("Enter task description: ")
        priority = input("Enter task priority (Low/Medium/High): ").capitalize()
        add_task(description, priority)

    elif choice == "2":
        description = input("Enter task description to remove: ")
        remove_task(description)

    elif choice == "3":
        show_completed = input("Show completed tasks? (yes/no): ").lower() == 'yes'
        list_tasks(show_completed)

    elif choice == "4":
        recommend_task()

    elif choice == "5":
        description = input("Enter task description to edit: ")
        new_description = input("Enter new task description (or leave blank to keep the same): ")
        new_priority = input("Enter new task priority (Low/Medium/High) (or leave blank to keep the same): ").capitalize()
        edit_task(description, new_description if new_description else None, new_priority if new_priority else None)

    elif choice == "6":
        description = input("Enter task description to mark as completed: ")
        complete_task(description)

    elif choice == "7":
        print("Goodbye!")
        break

    else:
        print("Invalid option. Please select a valid option.")
