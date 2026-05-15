# Database Normalization

## Overview

The database for this project management app is in Third Normal Form, also called 3NF.

The final database has three main tables:

- `users`
- `projects`
- `tasks`

Each table stores one main type of information. This helps reduce repeated data and avoids common database problems.

## Original Functional Dependencies

Before normalization, the data could have been stored in one large table like this:

```text
user_id, full_name, email,
project_id, project_name, project_status, start_date, due_date,
task_id, task_name, priority, task_status, estimated_hours, actual_hours,
created_date, task_due_date
```

The main functional dependencies are:

```text
user_id -> full_name, email
project_id -> project_name, project_status, start_date, due_date, user_id
task_id -> task_name, priority, task_status, estimated_hours, actual_hours, created_date, task_due_date, project_id, assigned_user_id
```

There are also relationships:

```text
One user can own many projects.
One project can have many tasks.
One user can be assigned many tasks.
```

## Anomaly Identification

If all data was stored in one large table, there would be problems.

### Insert Anomaly

A new user could not be added unless they already had a project or task.

### Update Anomaly

If a user's email appeared in many rows, changing the email would require updating many rows. If one row was missed, the data would become inconsistent.

### Delete Anomaly

If the only task for a project was deleted, the project information might also be lost.

## Decomposition Steps

The large table was separated into smaller tables.

### Step 1: Create Users Table

User information was moved into the `users` table.

```text
users(user_id, full_name, email, created_at, updated_at)
```

### Step 2: Create Projects Table

Project information was moved into the `projects` table. The `user_id` field connects each project to its owner.

```text
projects(project_id, user_id, project_name, status, start_date, due_date, created_at, updated_at)
```

### Step 3: Create Tasks Table

Task information was moved into the `tasks` table. The `project_id` field connects the task to a project. The `assigned_user_id` field connects the task to the user assigned to it.

```text
tasks(task_id, project_id, assigned_user_id, task_name, priority, status, estimated_hours, actual_hours, created_date, due_date, created_at, updated_at)
```

## Final Relational Schema

```text
users
-----
user_id PK
full_name
email
created_at
updated_at

projects
--------
project_id PK
user_id FK -> users.user_id
project_name
status
start_date
due_date
created_at
updated_at

tasks
-----
task_id PK
project_id FK -> projects.project_id
assigned_user_id FK -> users.user_id
task_name
priority
status
estimated_hours
actual_hours
created_date
due_date
created_at
updated_at
```

## Why The Users Table Is In 3NF

The primary key is `user_id`.

All other fields depend only on `user_id`:

```text
user_id -> full_name, email, created_at, updated_at
```

There are no non-key fields depending on other non-key fields. This means the `users` table is in 3NF.

## Why The Projects Table Is In 3NF

The primary key is `project_id`.

All project fields depend only on `project_id`:

```text
project_id -> user_id, project_name, status, start_date, due_date, created_at, updated_at
```

The project owner is stored using `user_id`, not by repeating the user's name and email. This avoids repeated user data.

There are no transitive dependencies, so the `projects` table is in 3NF.

## Why The Tasks Table Is In 3NF

The primary key is `task_id`.

All task fields depend only on `task_id`:

```text
task_id -> project_id, assigned_user_id, task_name, priority, status, estimated_hours, actual_hours, created_date, due_date, created_at, updated_at
```

The task stores `project_id` instead of repeating project details. It also stores `assigned_user_id` instead of repeating user details.

There are no non-key fields depending on other non-key fields, so the `tasks` table is in 3NF.

## Conclusion

The database is in 3NF because:

- Each table has a primary key.
- Each field depends on the whole primary key.
- No table stores repeated groups of data.
- No non-key field depends on another non-key field.
- Foreign keys are used to connect related tables.

This design helps prevent insert, update, and delete anomalies.
