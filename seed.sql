USE project_management;

INSERT INTO users (full_name, email) VALUES
('Avery Johnson', 'avery@example.com'),
('Morgan Lee', 'morgan@example.com'),
('Taylor Smith', 'taylor@example.com');

INSERT INTO projects (user_id, project_name, status, start_date, due_date) VALUES
(1, 'Website Redesign', 'In Progress', '2026-05-01', '2026-06-15'),
(1, 'Client Portal', 'Planning', '2026-05-20', '2026-07-10'),
(2, 'Mobile App Launch', 'In Progress', '2026-04-15', '2026-06-30');

INSERT INTO tasks (
    project_id,
    assigned_user_id,
    task_name,
    priority,
    status,
    estimated_hours,
    actual_hours,
    created_date,
    due_date
) VALUES
(1, 1, 'Create homepage wireframe', 'High', 'Done', 6.00, 5.50, '2026-05-02', '2026-05-06'),
(1, 2, 'Build Bootstrap layout', 'High', 'In Progress', 8.00, 3.00, '2026-05-05', '2026-05-14'),
(2, 3, 'Draft project requirements', 'Medium', 'To Do', 4.00, 0.00, '2026-05-10', '2026-05-22'),
(3, 2, 'Prepare launch checklist', 'Medium', 'In Progress', 5.00, 2.00, '2026-05-01', '2026-05-25'),
(3, 3, 'Test login flow', 'High', 'To Do', 7.00, 0.00, '2026-05-08', '2026-05-28');
