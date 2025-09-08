Django Todo App

For your assessment, you will create a single Django application to manage a simple to-do list. This project will demonstrate your understanding of fundamental Django concepts, including virtual environments, models, migrations, and basic CRUD (Create, Read, Update, Delete) operations through views and templates.
Here are the specific requirements:
Virtual Environment: 
Set up a dedicated Python virtual environment for your project.
Django Project and App: 
Create a new Django project and a single Django application within it for your to-do list functionality.
To-Do List Model: 
Design a Django model for a Task that includes:
- A field for the task description (e.g., title or description).
- A field to indicate the status of the task (e.g., completed as a boolean, or status with choices like "Pending" and "Completed").
- (Optional but recommended) A field for creation date/time.
Database Migration: 
After defining your model, perform the necessary database migrations to create the corresponding table in your database.
CRUD Operations: 
Implement the following functionalities through Django views and corresponding HTML templates:
- View To-Do Lists: 
A page that displays all tasks in the to-do list.
- Add New Task: 
A form to allow users to add a new task to the list.
- Update Task Status:
Functionality to change the status of a task (e.g., mark as completed or pending). This could be a link/button next to each task.
- Delete Task: 
Functionality to remove a task from the list. This could be a link/button next to each task.

Features

- Add new tasks
- Mark tasks as complete/incomplete
- Delete tasks
- View task statistics (Total, Completed, Pending)
- Responsive UI with Bootstrap and dark mode styling

Tech Stack

- Python 3
- Django 4.x
- Bootstrap 5 (for UI)

Setup Instructions

1. Clone the Repository

Terminal
git clone https://github.com/Joelwick147/REF_MAY_COHORT_2025.git
cd django-todo-app

2. Create Virtual Environment

Terminal
python -m venv venv
source venv/Scripts/activate  # Windows


3. Install Dependencies

Terminal
pip install -r requirements.txt

4. Apply Migrations

Terminal
python manage.py makemigrations
python manage.py migrate

5. Run the Server

Terminal
python manage.py runserver

6. Access the App

Visit "http://127.0.0.1:8000/" in your browser.

Folder Structure
- crud_project
--crud
-----todo
