async function addTask() {
    const description = document.getElementById('taskDescription').value;
    const priority = document.getElementById('taskPriority').value;

    const response = await fetch('/add_task', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ description, priority }),
    });

    const data = await response.json();
    alert(data.message);
    getTasks();
}

async function getTasks() {
    const response = await fetch('/tasks?show_completed=true');
    const tasks = await response.json();

    const tasksDiv = document.getElementById('tasks');
    tasksDiv.innerHTML = '';

    tasks.forEach(task => {
        const taskDiv = document.createElement('div');
        taskDiv.classList.add('task');
        taskDiv.innerHTML = `
            <span>${task.description} - ${task.priority}</span>
            <button class="complete-button" onclick="completeTask('${task.description}')">Complete</button>
            <button onclick="removeTask('${task.description}')">Remove</button>
        `;
        tasksDiv.appendChild(taskDiv);
    });
}

async function removeTask(description) {
    const response = await fetch('/remove_task', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ description }),
    });

    const data = await response.json();
    alert(data.message);
    getTasks();
}

async function completeTask(description) {
    const response = await fetch('/complete_task', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ description }),
    });

    const data = await response.json();
    alert(data.message);
    getTasks();
}

async function recommendTask() {
    const response = await fetch('/recommend_task');
    const data = await response.json();

    if (response.ok) {
        alert(`Recommended task: ${data.recommended_task} - Priority: ${data.priority}`);
    } else {
        alert(data.message);
    }
}

document.addEventListener('DOMContentLoaded', getTasks);
