from flask import Flask, request, jsonify, render_template
import pandas as pd
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import make_pipeline
import random
import joblib

app = Flask(__name__)

# Load pre-existing tasks from a CSV file (if any)
try:
    tasks = pd.read_csv('tasks.csv')
except FileNotFoundError:
    tasks = pd.DataFrame(columns=['description', 'priority', 'completed'])

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

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/tasks', methods=['GET'])
def get_tasks():
    show_completed = request.args.get('show_completed', 'true').lower() == 'true'
    if show_completed:
        return jsonify(tasks.to_dict(orient='records'))
    else:
        return jsonify(tasks[tasks['completed'] == False].to_dict(orient='records'))

@app.route('/add_task', methods=['POST'])
def add_task():
    global tasks
    data = request.get_json()
    description = data['description']
    priority = data['priority']
    if priority not in ['Low', 'Medium', 'High']:
        return jsonify({'error': 'Invalid priority. Please enter Low, Medium, or High.'}), 400
    new_task = pd.DataFrame({'description': [description], 'priority': [priority], 'completed': [False]})
    tasks = pd.concat([tasks, new_task], ignore_index=True)
    model.fit(tasks['description'], tasks['priority'])
    joblib.dump(model, 'task_model.pkl')
    save_tasks()
    return jsonify({'message': 'Task added successfully.'}), 201

@app.route('/remove_task', methods=['POST'])
def remove_task():
    global tasks
    data = request.get_json()
    description = data['description']
    if description not in tasks['description'].values:
        return jsonify({'error': 'Task not found.'}), 404
    tasks = tasks[tasks['description'] != description]
    save_tasks()
    return jsonify({'message': 'Task removed successfully.'})

@app.route('/edit_task', methods=['POST'])
def edit_task():
    global tasks
    data = request.get_json()
    description = data['description']
    new_description = data.get('new_description')
    new_priority = data.get('new_priority')
    if description not in tasks['description'].values:
        return jsonify({'error': 'Task not found.'}), 404
    if new_description:
        tasks.loc[tasks['description'] == description, 'description'] = new_description
    if new_priority:
        if new_priority not in ['Low', 'Medium', 'High']:
            return jsonify({'error': 'Invalid priority. Please enter Low, Medium, or High.'}), 400
        tasks.loc[tasks['description'] == description, 'priority'] = new_priority
    model.fit(tasks['description'], tasks['priority'])
    joblib.dump(model, 'task_model.pkl')
    save_tasks()
    return jsonify({'message': 'Task edited successfully.'})

@app.route('/complete_task', methods=['POST'])
def complete_task():
    global tasks
    data = request.get_json()
    description = data['description']
    if description not in tasks['description'].values:
        return jsonify({'error': 'Task not found.'}), 404
    tasks.loc[tasks['description'] == description, 'completed'] = True
    save_tasks()
    return jsonify({'message': 'Task marked as completed.'})

@app.route('/recommend_task', methods=['GET'])
def recommend_task():
    if not tasks.empty:
        high_priority_tasks = tasks[(tasks['priority'] == 'High') & (tasks['completed'] == False)]
        if not high_priority_tasks.empty:
            random_task = random.choice(high_priority_tasks['description'].values)
            return jsonify({'recommended_task': random_task, 'priority': 'High'})
        else:
            return jsonify({'message': 'No high-priority tasks available for recommendation.'}), 404
    else:
        return jsonify({'message': 'No tasks available for recommendations.'}), 404

if __name__ == '__main__':
    app.run(debug=True)
