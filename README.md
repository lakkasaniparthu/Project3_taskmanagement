# Flask Project Management App

## Project Description

This is a simple Flask web app for managing users, projects, and tasks. It was built as a database project using MySQL and SQLAlchemy.

The app lets a user create project records, assign tasks, view summaries, and practice basic database operations through a web interface.

## Who The App Is For

This app is for students, small teams, or beginners who want a simple project management system. It is also useful for learning how Flask connects to a MySQL database.

## Tech Stack

- Python 3
- Flask
- MySQL
- SQLAlchemy
- PyMySQL
- Jinja2 templates
- Bootstrap
- HTML and CSS

## Features

- Home page
- Users CRUD
- Projects CRUD
- Tasks CRUD
- Summary dashboard
- Database aggregate functions using `COUNT`, `AVG`, and `SUM`
- Grouped reports for tasks by status and projects by status
- Create Project With First Task transaction feature
- Clear database error page if MySQL is not connected

## Installation Instructions

First, open PowerShell and go to the project folder:

```powershell
cd "C:\Users\lakka\OneDrive\Documents\database\Project3_taskmanagement"
```

## Virtual Environment Setup

Create a virtual environment:

```powershell
python -m venv venv
```

Activate it:

```powershell
venv\Scripts\Activate.ps1
```

If PowerShell blocks activation, run:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
venv\Scripts\Activate.ps1
```

## Install Requirements

Install the required packages:

```powershell
pip install -r requirements.txt
```

## Database Setup

Install MySQL Community Server if it is not already installed.

Start MySQL:

```powershell
net start MySQL80
```

Create the database tables:

```powershell
cmd /c "mysql -u root -p < schema.sql"
```

Add sample data:

```powershell
cmd /c "mysql -u root -p < seed.sql"
```

If `mysql` is not found, use the full path:

```powershell
cmd /c """C:\Program Files\MySQL\MySQL Server 8.0\bin\mysql.exe"" -u root -p < schema.sql"
cmd /c """C:\Program Files\MySQL\MySQL Server 8.0\bin\mysql.exe"" -u root -p < seed.sql"
```

## Database Connection Settings

The app reads database settings from environment variables.

Example:

```powershell
$env:DB_USER="root"
$env:DB_PASSWORD="your_mysql_password"
$env:DB_HOST="localhost"
$env:DB_PORT="3306"
$env:DB_NAME="project_management"
```

## Run The Flask App

Run the app:

```powershell
python app.py
```

Open this URL in a browser:

```text
http://127.0.0.1:5000
```

## How To Use The Main Features

Use the navigation bar to move around the app.

- `Dashboard`: view totals, averages, sums, and grouped status reports.
- `Users`: add, view, edit, and delete users.
- `Projects`: add, view, edit, and delete projects.
- `Tasks`: add, view, edit, and delete tasks.
- `Create Project With First Task`: create a project and its first task together.

The transaction feature saves the project and task together. If the task insert fails, the project insert is rolled back too.

If MySQL is not running, the app shows a database connection error page instead of crashing.
