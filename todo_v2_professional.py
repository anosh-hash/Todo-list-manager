
import tkinter as tk
from tkinter import ttk, messagebox
from tkcalendar import DateEntry
import sqlite3
from datetime import datetime

DB_NAME = "tasks.db"

conn = sqlite3.connect(DB_NAME)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS tasks(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    priority TEXT,
    due_date TEXT,
    completed INTEGER DEFAULT 0
)
""")
conn.commit()

BG = "#1e1e1e"
CARD = "#2d2d30"
ACCENT = "#00BFFF"

def check_due_today():
    today = datetime.now().strftime("%d-%m-%Y")

    cursor.execute(
        "SELECT name FROM tasks WHERE due_date=? AND completed=0",
        (today,)
    )

    tasks_due = cursor.fetchall()

    if tasks_due:
        names = "\n".join(task[0] for task in tasks_due)
        messagebox.showinfo(
            "Reminder",
            f"Tasks Due Today:\n\n{names}"
        )

def refresh_table():
    for row in tree.get_children():
        tree.delete(row)

    cursor.execute("SELECT * FROM tasks")
    rows = cursor.fetchall()

    total = len(rows)
    completed = 0
    pending = 0

    for row in rows:
        status = "Completed" if row[4] else "Pending"

        if row[4]:
            completed += 1
        else:
            pending += 1

        tree.insert(
            "",
            "end",
            iid=row[0],
            values=(row[1], row[2], row[3], status)
        )

    total_card.config(text=f"📊 Total\n{total}")
    completed_card.config(text=f"✅ Completed\n{completed}")
    pending_card.config(text=f"⌛ Pending\n{pending}")
    count_label.config(text=f"Total Tasks : {total}")

def add_task():
    name = task_entry.get().strip()

    if not name:
        messagebox.showwarning("Warning", "Enter Task Name")
        return

    cursor.execute(
        "INSERT INTO tasks(name,priority,due_date,completed) VALUES(?,?,?,0)",
        (name, priority_var.get(), due_entry.get())
    )

    conn.commit()

    task_entry.delete(0, tk.END)

    refresh_table()

def delete_task():
    selected = tree.selection()

    if not selected:
        messagebox.showwarning("Warning", "Select a Task")
        return

    task_id = int(selected[0])

    cursor.execute(
        "DELETE FROM tasks WHERE id=?",
        (task_id,)
    )

    conn.commit()

    refresh_table()

def mark_completed():
    selected = tree.selection()

    if not selected:
        messagebox.showwarning("Warning", "Select a Task")
        return

    task_id = int(selected[0])

    cursor.execute(
        "UPDATE tasks SET completed=1 WHERE id=?",
        (task_id,)
    )

    conn.commit()

    refresh_table()

def edit_task():
    selected = tree.selection()

    if not selected:
        messagebox.showwarning("Warning", "Select a Task")
        return

    task_id = int(selected[0])

    cursor.execute(
        "SELECT * FROM tasks WHERE id=?",
        (task_id,)
    )

    task = cursor.fetchone()

    win = tk.Toplevel(root)
    win.title("Edit Task")
    win.geometry("400x300")

    tk.Label(win, text="Task Name").pack(pady=5)

    name_entry = tk.Entry(win, width=35)
    name_entry.pack()
    name_entry.insert(0, task[1])

    tk.Label(win, text="Priority").pack(pady=5)

    pvar = tk.StringVar(value=task[2])

    tk.OptionMenu(
        win,
        pvar,
        "High",
        "Medium",
        "Low"
    ).pack()

    tk.Label(win, text="Due Date").pack(pady=5)

    date_entry = DateEntry(
        win,
        date_pattern="dd-mm-yyyy"
    )
    date_entry.pack()

    def save_changes():
        cursor.execute(
            """
            UPDATE tasks
            SET name=?, priority=?, due_date=?
            WHERE id=?
            """,
            (
                name_entry.get(),
                pvar.get(),
                date_entry.get(),
                task_id
            )
        )

        conn.commit()

        refresh_table()

        win.destroy()

    tk.Button(
        win,
        text="Save Changes",
        command=save_changes
    ).pack(pady=10)

def search_task():
    keyword = search_entry.get().lower()

    for row in tree.get_children():
        tree.delete(row)

    cursor.execute(
        "SELECT * FROM tasks WHERE LOWER(name) LIKE ?",
        ('%' + keyword + '%',)
    )

    rows = cursor.fetchall()

    for row in rows:
        status = "Completed" if row[4] else "Pending"

        tree.insert(
            "",
            "end",
            iid=row[0],
            values=(row[1], row[2], row[3], status)
        )

def show_all():
    search_entry.delete(0, tk.END)
    refresh_table()

def sort_priority():
    for row in tree.get_children():
        tree.delete(row)

    cursor.execute("""
    SELECT * FROM tasks
    ORDER BY
    CASE priority
        WHEN 'High' THEN 1
        WHEN 'Medium' THEN 2
        WHEN 'Low' THEN 3
        ELSE 4
    END
    """)

    rows = cursor.fetchall()

    for row in rows:
        status = "Completed" if row[4] else "Pending"

        tree.insert(
            "",
            "end",
            iid=row[0],
            values=(row[1], row[2], row[3], status)
        )

root = tk.Tk()
root.title("Professional Task Manager")
root.geometry("1400x900")
root.configure(bg=BG)

style = ttk.Style()
style.theme_use("clam")

style.configure(
    "Treeview",
    background="#252526",
    foreground="white",
    fieldbackground="#252526",
    rowheight=30,
    font=("Segoe UI", 10)
)

style.configure(
    "Treeview.Heading",
    font=("Segoe UI", 11, "bold")
)

logo = tk.Label(
    root,
    text="📝",
    font=("Segoe UI Emoji", 40),
    bg=BG,
    fg=ACCENT
)
logo.pack()

title = tk.Label(
    root,
    text="📋 TASK MANAGEMENT SYSTEM",
    font=("Segoe UI", 24, "bold"),
    bg=BG,
    fg=ACCENT
)
title.pack()

dashboard = tk.Frame(root, bg=BG)
dashboard.pack(pady=10)

total_card = tk.Label(
    dashboard,
    text="📊 Total\n0",
    width=18,
    height=3,
    bg=CARD,
    fg="white"
)
total_card.pack(side="left", padx=10)

completed_card = tk.Label(
    dashboard,
    text="✅ Completed\n0",
    width=18,
    height=3,
    bg=CARD,
    fg="white"
)
completed_card.pack(side="left", padx=10)

pending_card = tk.Label(
    dashboard,
    text="⌛ Pending\n0",
    width=18,
    height=3,
    bg=CARD,
    fg="white"
)
pending_card.pack(side="left", padx=10)

main = tk.Frame(root, bg=BG)
main.pack(fill="both", expand=True)

left = tk.Frame(main, bg=BG)
left.pack(side="left", padx=20)

tk.Label(left, text="Task Name", bg=BG, fg="white").pack()

task_entry = tk.Entry(left, width=30)
task_entry.pack(pady=5)

tk.Label(left, text="Priority", bg=BG, fg="white").pack()

priority_var = tk.StringVar(value="Medium")

tk.OptionMenu(
    left,
    priority_var,
    "High",
    "Medium",
    "Low"
).pack()

tk.Label(left, text="Due Date", bg=BG, fg="white").pack()

due_entry = DateEntry(
    left,
    date_pattern="dd-mm-yyyy"
)
due_entry.pack(pady=5)

tk.Button(
    left,
    text="➕ Add Task",
    width=20,
    command=add_task
).pack(pady=10)

count_label = tk.Label(
    left,
    text="Total Tasks : 0",
    bg=BG,
    fg="white"
)
count_label.pack()

tk.Label(left, text="Search", bg=BG, fg="white").pack(pady=5)

search_entry = tk.Entry(left, width=30)
search_entry.pack()

tk.Button(
    left,
    text="🔍 Search",
    width=20,
    command=search_task
).pack(pady=2)

tk.Button(
    left,
    text="📋 Show All",
    width=20,
    command=show_all
).pack(pady=2)

right = tk.Frame(main, bg=BG)
right.pack(side="right", fill="both", expand=True)

columns = ("Task", "Priority", "Due Date", "Status")

tree = ttk.Treeview(
    right,
    columns=columns,
    show="headings",
    height=15
)

for col in columns:
    tree.heading(col, text=col)
    tree.column(col, width=180)

tree.pack(fill="both", expand=True)
scrollbar = ttk.Scrollbar(
    right,
    orient="vertical",
    command=tree.yview
)

tree.configure(
    yscrollcommand=scrollbar.set
)

scrollbar.pack(
    side="right",
    fill="y"
)
buttons = tk.Frame(root, bg=BG)
buttons.pack(side="bottom", pady=20)

tk.Button(buttons, text="✅ Complete", width=15, command=mark_completed).grid(row=0,column=0,padx=5)
tk.Button(buttons, text="✏️ Edit", width=15, command=edit_task).grid(row=0,column=1,padx=5)
tk.Button(buttons, text="🗑 Delete", width=15, command=delete_task).grid(row=0,column=2,padx=5)
tk.Button(buttons, text="📌 Sort Priority", width=15, command=sort_priority).grid(row=0,column=3,padx=5)
tk.Button(buttons, text="🚪 Exit", width=15, command=root.destroy).grid(row=0,column=4,padx=5)

footer = tk.Label(
    root,
    text="Developed by Anosh | Python Tkinter + SQLite + Calendar",
    bg=BG,
    fg="gray"
)
footer.pack(pady=5)

refresh_table()
root.after(1000, check_due_today)
root.mainloop()
