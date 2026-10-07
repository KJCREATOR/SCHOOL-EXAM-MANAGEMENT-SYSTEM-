import os
import sys
import csv
import getpass
import tempfile
from datetime import datetime
import MySQLdb
from prettytable import PrettyTable
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import mm
from PIL import Image
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox, Toplevel
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib.styles import getSampleStyleSheet

# ----------------------- DB CONFIG -----------------------
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'passwd': 'tiger',
    'db': 'exams_tests_db'
}

# ----------------------- DB UTILITIES -----------------------

def get_db_connection():
    try:
        conn = MySQLdb.connect(host=DB_CONFIG['host'], user=DB_CONFIG['user'],
                               passwd=DB_CONFIG['passwd'], db=DB_CONFIG['db'])
        return conn
    except Exception as e:
        print("Error connecting to database:", e)
        messagebox.showerror("Database Error", f"Could not connect to database:\n{e}\n\nExiting.")
        sys.exit(1)


def initialize_database():
    conn_tmp = None
    try:
        conn_tmp = MySQLdb.connect(host=DB_CONFIG['host'], user=DB_CONFIG['user'], passwd=DB_CONFIG['passwd'])
        cur = conn_tmp.cursor()
        cur.execute(f"CREATE DATABASE IF NOT EXISTS {DB_CONFIG['db']} ;")
        conn_tmp.commit()
        cur.close()
    except Exception as e:
        print("Could not create database:", e)
        if conn_tmp:
            conn_tmp.close()
        messagebox.showerror("Database Error", f"Could not create database:\n{e}\n\nExiting.")
        sys.exit(1)

    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute('''
    CREATE TABLE IF NOT EXISTS TeacherMaster (
        teacher_id VARCHAR(50) PRIMARY KEY,
        password VARCHAR(128) NOT NULL,
        name VARCHAR(200),
        subject_main VARCHAR(100),
        subject1 VARCHAR(100),
        subject2 VARCHAR(100),
        subject3 VARCHAR(100),
        subject4 VARCHAR(100),
        class1 VARCHAR(20),
        class2 VARCHAR(20),
        class3 VARCHAR(20),
        class4 VARCHAR(20),
        class5 VARCHAR(20),
        class6 VARCHAR(20)
    ) ENGINE=InnoDB ;
    ''')

    cur.execute('''
    CREATE TABLE IF NOT EXISTS StudentMaster (
        admno VARCHAR(50) PRIMARY KEY,
        student_name VARCHAR(200),
        father_name VARCHAR(200),
        mother_name VARCHAR(200),
        class VARCHAR(20),
        section VARCHAR(10),
        subject1 VARCHAR(100), subject2 VARCHAR(100), subject3 VARCHAR(100), subject4 VARCHAR(100),
        subject5 VARCHAR(100), subject6 VARCHAR(100), subject7 VARCHAR(100), subject8 VARCHAR(100),
        subject9 VARCHAR(100), subject10 VARCHAR(100),
        address TEXT,
        mobno VARCHAR(30),
        attendance FLOAT
    ) ENGINE=InnoDB ;
    ''')

    cur.execute('''
    CREATE TABLE IF NOT EXISTS MarksMaster (
        id INT AUTO_INCREMENT PRIMARY KEY,
        admno VARCHAR(50),
        class VARCHAR(20),
        section VARCHAR(10),
        subject VARCHAR(100),
        exam_name VARCHAR(200),
        max_marks INT,
        marks_obtained FLOAT,
        teacher_id VARCHAR(50),
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (admno) REFERENCES StudentMaster(admno) ON DELETE CASCADE,
        FOREIGN KEY (teacher_id) REFERENCES TeacherMaster(teacher_id) ON DELETE SET NULL
    ) ENGINE=InnoDB ;
    ''')

    cur.execute('''
    CREATE TABLE IF NOT EXISTS ReportDetails (
        id INT PRIMARY KEY DEFAULT 1,
        school_name VARCHAR(255),
        school_address TEXT,
        contact VARCHAR(100),
        website VARCHAR(255),
        logo_path VARCHAR(1024),
        principal_name VARCHAR(200)
    ) ENGINE=InnoDB ;
    ''')

    conn.commit()
    cur.close()
    conn.close()
    print("Database initialized successfully.")

# ----------------------- HELPERS -----------------------

def show_table(records, headers):
    t = PrettyTable()
    t.field_names = headers
    for r in records:
        t.add_row(r)
    print(t)
    
def create_label_entry(parent, text, row, col=0, width=30, show=None, sticky="w"):
    ttk.Label(parent, text=text, font=("Segoe UI", 10)).grid(row=row, column=col, sticky=sticky, padx=5, pady=2)
    entry_var = tk.StringVar()
    entry = ttk.Entry(parent, textvariable=entry_var, width=width, show=show)
    entry.grid(row=row, column=col + 1, sticky="we", padx=5, pady=2)
    return entry_var, entry

# ----------------------- TEACHER MASTER-----------------------

def teacher_entry():
    
    def submit_details():
        tid = entry_tid.get().strip()
        pwd = entry_pwd.get().strip()
        name = entry_name.get().strip()
        subject_main = entry_subject_main.get().strip()
        subjects = [entry.get().strip() for entry in subject_entries]
        classes = [entry.get().strip() for entry in class_entries]

        if not tid or not pwd or not name:
            messagebox.showerror("Input Error", "Teacher ID, Name, and Password are required!", parent=app)
            return

        conn = get_db_connection()
        cur = conn.cursor()
        try:
            cur.execute('''INSERT INTO TeacherMaster (teacher_id, password, name, subject_main, subject1, subject2, subject3, subject4, class1, class2, class3, class4, class5, class6)
                           VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
                         ''', (tid, pwd, name, subject_main, subjects[0], subjects[1], subjects[2], subjects[3], classes[0], classes[1], classes[2], classes[3], classes[4], classes[5]))
            conn.commit()
            messagebox.showinfo("Success", "Teacher inserted successfully.", parent=app)
            app.destroy()
        except Exception as e:
            messagebox.showerror("Error", f"Error inserting teacher:\n{e}", parent=app)
            conn.rollback()
        finally:
            cur.close()
            conn.close()

    app = tk.Toplevel()
    app.title("Teacher Registration Form")
    app.geometry("450x720")
    app.resizable(False, False)

    title_lbl = ttk.Label(
        app,
        text="🧑‍🏫 Teacher Registration Form",
        font=("Helvetica", 18, "bold")
    )
    title_lbl.pack(pady=15)

    card = ttk.Frame(app, padding=20)
    card.pack(padx=20, pady=10, fill="both", expand=True)

    def make_label_entry(parent, text, row, show=None):
        ttk.Label(parent, text=text, font=("Segoe UI", 10, "bold")).grid(row=row, column=0, sticky="w", pady=5)
        entry = ttk.Entry(parent, width=30, show=show)
        entry.grid(row=row, column=1, pady=5)
        return entry

    entry_tid = make_label_entry(card, "Teacher ID:", 0)
    entry_pwd = make_label_entry(card, "Password:", 1, show="*")
    entry_name = make_label_entry(card, "Teacher Name:", 2)
    entry_subject_main = make_label_entry(card, "Subject being taught:", 3)

    ttk.Label(card, text="Other Subjects:", font=("Segoe UI", 10, "bold")).grid(row=4, column=0, sticky="nw", pady=(10, 5))
    subject_entries = []
    for i in range(4):
        e = ttk.Entry(card, width=30)
        e.grid(row=4 + i, column=1, pady=3)
        subject_entries.append(e)

    ttk.Label(card, text="Classes:", font=("Segoe UI", 10, "bold")).grid(row=8, column=0, sticky="nw", pady=(10, 5))
    class_entries = []
    for i in range(6):
        e = ttk.Entry(card, width=30)
        e.grid(row=8 + i, column=1, pady=3)
        class_entries.append(e)

    btn_frame = ttk.Frame(app)
    btn_frame.pack(pady=15)

    submit_btn = ttk.Button(
        btn_frame,
        text="Submit Details",
        width=20,
        command=submit_details
    )
    submit_btn.pack(side="left", padx=10)

    clear_btn = ttk.Button(
        btn_frame,
        text="Clear All",
        width=15,
        command=lambda: [
            entry_tid.delete(0, 'end'),
            entry_pwd.delete(0, 'end'),
            entry_name.delete(0, 'end'),
            entry_subject_main.delete(0, 'end'),
            [e.delete(0, 'end') for e in subject_entries],
            [e.delete(0, 'end') for e in class_entries]
        ]
    )
    clear_btn.pack(side="left", padx=10)


def teacher_update():
    
    ALL_FIELDS = ["name", "password", "subject_main", "subject1", "subject2", "subject3", "subject4",
                  "class1", "class2", "class3", "class4", "class5", "class6"]

    def execute_all_update(tid, updated_values, all_window):
        conn = None
        try:
            conn = get_db_connection()
            if not conn:
                return
            cur = conn.cursor()

            updates = {}
            for k, v in updated_values.items():
                if v:
                    updates[k] = v
            
            if updates:
                set_clause = ','.join([f"{k}=%s" for k in updates.keys()])
                params = list(updates.values()) + [tid]
                
                cur.execute(f"UPDATE TeacherMaster SET {set_clause} WHERE teacher_id=%s", tuple(params))
                conn.commit()
                
                messagebox.showinfo("Success", f"Successfully updated ALL fields for Teacher ID {tid}.", parent=all_window)
                all_window.destroy()
                clear_fields()
            else:
                messagebox.showinfo("No Change", "No new values provided. No update was performed.", parent=all_window)
                
        except Exception as e:
            messagebox.showerror("Error", f"Error updating record: {e}", parent=all_window)
            if conn:
                conn.rollback()
        finally:
            if cur:
                cur.close()
            if conn:
                conn.close()

    def open_all_update_window(tid):
        conn = None
        try:
            conn = get_db_connection()
            if not conn:
                return
            cur = conn.cursor()
            
            cur.execute("SELECT * FROM TeacherMaster WHERE teacher_id=%s", (tid,))
            r = cur.fetchone()
            headers = [d[0] for d in cur.description]
            
            if not r:
                messagebox.showerror("Error", f"No teacher found with ID: {tid}", parent=update_window)
                return
            
        except Exception as e:
            messagebox.showerror("DB Error", f"Error fetching teacher data: {e}", parent=update_window)
            return
        finally:
            if cur: cur.close()
            if conn: conn.close()
            
        all_window = tk.Toplevel(update_window)
        all_window.title(f"Update All Fields - Teacher {tid}")
        all_window.geometry("450x550")
        
        tk.Label(all_window, text=f"Update All Fields for ID: {tid}", font=("Arial", 12, "bold")).pack(pady=10)
        
        canvas = tk.Canvas(all_window)
        scrollbar = ttk.Scrollbar(all_window, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(
                scrollregion=canvas.bbox("all")
            )
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        entries = {}

        for i, field in enumerate(ALL_FIELDS):
            if field in headers:
                h_index = headers.index(field)
                current_value = r[h_index] if r[h_index] is not None else ""

                tk.Label(scrollable_frame, text=f"{field.title()} (Current: {current_value}):", font=("Arial", 9)).grid(row=i, column=0, sticky="w", padx=5, pady=3)
                ent = tk.Entry(scrollable_frame, width=30)
                ent.grid(row=i, column=1, padx=5, pady=3)
                entries[field] = ent
            
        def submit_all():
            updated_values = {k: v.get().strip() for k, v in entries.items()}
            execute_all_update(tid, updated_values, all_window)

        ttk.Button(all_window, text="Submit All Updates", command=submit_all).pack(pady=15)

    def update_record():
        tid = tid_var.get().strip()
        col = col_var.get().strip()
        val = value_var.get().strip()

        if not tid:
            messagebox.showerror("Error", "Please enter **Teacher ID**", parent=update_window)
            return
        if not col:
            messagebox.showerror("Error", "Please select a **column name** to update", parent=update_window)
            return

        if col.lower() != "all" and not val:
            messagebox.showerror("Error", "Please enter a **new value** for the selected column", parent=update_window)
            return

        if col.lower() == 'all':
            open_all_update_window(tid)
            return
        
        conn = None
        try:
            conn = get_db_connection()
            if not conn:
                return
            cur = conn.cursor()
            
            cur.execute(f"UPDATE TeacherMaster SET {col}=%s WHERE teacher_id=%s", (val, tid))
            conn.commit()
            
            messagebox.showinfo("Success", f"Updated **{col}** for Teacher ID **{tid}** → **{val}**", parent=update_window)
            clear_fields()
            
        except Exception as e:
            messagebox.showerror("Error", f"Error updating record: {e}", parent=update_window)
            if conn:
                conn.rollback()
        finally:
            if cur:
                cur.close()
            if conn:
                conn.close()

    def clear_fields():
        tid_var.set("")
        col_var.set("")
        value_var.set("")


    update_window = tk.Toplevel()
    update_window.title("Update Teacher Record")
    update_window.geometry("400x350")
    update_window.resizable(False, False)

    tk.Label(update_window, text="--- Update Teacher Record ---", font=("Arial", 14, "bold")).pack(pady=10)

    main_frame = ttk.Frame(update_window, padding=20)
    main_frame.pack(fill='both', expand=True)

    tk.Label(main_frame, text="Teacher ID:").grid(row=0, column=0, sticky="w", pady=5)
    tid_var = tk.StringVar()
    tk.Entry(main_frame, textvariable=tid_var, width=25).grid(row=0, column=1)

    tk.Label(main_frame, text="Select Column:").grid(row=1, column=0, sticky="w", pady=5)
    col_var = tk.StringVar()
    columns = ["name", "password", "subject_main", "subject1", "subject2", "subject3", "subject4", 
               "class1", "class2", "class3", "class4", "class5", "class6", "all"]
    col_dropdown = ttk.Combobox(main_frame, textvariable=col_var, width=22, state="readonly", values=columns)
    col_dropdown.grid(row=1, column=1)

    tk.Label(main_frame, text="New Value (Ignore for 'all'):").grid(row=2, column=0, sticky="w", pady=5)
    value_var = tk.StringVar()
    tk.Entry(main_frame, textvariable=value_var, width=25).grid(row=2, column=1)

    ttk.Button(main_frame, text="Update", command=update_record).grid(row=3, column=0, pady=15, padx=5)
    ttk.Button(main_frame, text="Clear", command=clear_fields).grid(row=3, column=1, pady=15, padx=5)


def teacher_delete():
    def delete_record():
        tid = tid_var.get().strip()

        if not tid:
            messagebox.showerror("Error", "Please enter **Teacher ID** to delete.", parent=delete_window)
            return

        confirm = messagebox.askyesno(
            "Confirm Deletion", 
            f"Are you sure you want to delete the record for Teacher ID: **{tid}**?\nThis action cannot be undone.",
            parent=delete_window
        )
        
        if not confirm:
            return

        conn = None
        try:
            conn = get_db_connection()
            if not conn:
                return
            cur = conn.cursor()
            
            cur.execute("DELETE FROM TeacherMaster WHERE teacher_id=%s", (tid,))
            conn.commit()
            
            deleted_count = cur.rowcount
            
            if deleted_count > 0:
                messagebox.showinfo("Success", f"Successfully deleted **{deleted_count}** record(s) for Teacher ID **{tid}**.", parent=delete_window)
            else:
                messagebox.showwarning("Not Found", f"No record found for Teacher ID **{tid}**. Nothing was deleted.", parent=delete_window)
                
            clear_fields()
            
        except Exception as e:
            messagebox.showerror("Error", f"Error deleting record: {e}", parent=delete_window)
            if conn:
                conn.rollback()
        finally:
            if cur:
                cur.close()
            if conn:
                conn.close()

    def clear_fields():
        tid_var.set("")

    delete_window = tk.Toplevel()
    delete_window.title("Delete Teacher Record")
    delete_window.geometry("350x200")
    delete_window.resizable(False, False)

    tk.Label(delete_window, text="--- Delete Teacher Record ---", font=("Arial", 14, "bold")).pack(pady=10)

    main_frame = ttk.Frame(delete_window, padding=20)
    main_frame.pack(fill='both', expand=True)

    tk.Label(main_frame, text="Teacher ID to Delete:").grid(row=0, column=0, sticky="w", pady=5)
    tid_var = tk.StringVar()
    tk.Entry(main_frame, textvariable=tid_var, width=20).grid(row=0, column=1)

    ttk.Button(main_frame, text="Delete Record", command=delete_record).grid(row=1, column=0, pady=15, padx=5, sticky="e")
    ttk.Button(main_frame, text="Clear", command=clear_fields).grid(row=1, column=1, pady=15, padx=5, sticky="w")

    

def teacher_query_reports():
    print("\n--- Query & Reports (TeacherMaster) ---")
    print("This report will show in the console.")
    conn = get_db_connection()
    cur = conn.cursor()
    print("Options: 1- Show All  2- Search by row")
    o = input().strip()
    try:
        if o == '1':
            cur.execute("SELECT * FROM TeacherMaster")
            rows = cur.fetchall()
            headers = [d[0] for d in cur.description]
            show_table(rows, headers)
        else:
            col = input("Enter row name to search (e.g., name, subject_main): ").strip()
            val = input("Enter value to search for: ").strip()
            cur.execute(f"SELECT * FROM TeacherMaster WHERE {col} LIKE %s", (f"%{val}%",))
            rows = cur.fetchall()
            headers = [d[0] for d in cur.description]
            show_table(rows, headers)
    except Exception as e:
        print("Error querying:", e)
    finally:
        cur.close()
        conn.close()
    print("--- End of Console Report ---")

# ----------------------- STUDENT MASTER (GUI) -----------------------

def student_entry_gui():
    
    def submit_student():
        values = {
            'admno': admno_var.get().strip(),
            'name': name_var.get().strip(),
            'father': father_var.get().strip(),
            'mother': mother_var.get().strip(),
            'cls': cls_var.get().strip(),
            'section': sec_var.get().strip(),
            'address': addr_var.get().strip(),
            'mob': mob_var.get().strip(),
            'attendance': att_var.get().strip(),
            'subjects': [s_var.get().strip() for s_var in subject_vars]
        }
        
        if not values['admno'] or not values['name'] or not values['cls'] or not values['section']:
            messagebox.showerror("Input Error", "Adm No, Name, Class, and Section are required.", parent=win)
            return

        try:
            attendance_val = float(values['attendance']) if values['attendance'] else 0.0
        except ValueError:
            messagebox.showerror("Input Error", "Attendance must be a number.", parent=win)
            return
            
        conn = get_db_connection()
        cur = conn.cursor()
        try:
            cur.execute('''INSERT INTO StudentMaster (admno, student_name, father_name, mother_name, class, section, 
                           subject1, subject2, subject3, subject4, subject5, subject6, subject7, subject8, subject9, subject10, 
                           address, mobno, attendance)
                           VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
                         ''', (values['admno'], values['name'], values['father'], values['mother'], values['cls'], values['section'],
                               values['subjects'][0], values['subjects'][1], values['subjects'][2], values['subjects'][3],
                               values['subjects'][4], values['subjects'][5], values['subjects'][6], values['subjects'][7],
                               values['subjects'][8], values['subjects'][9],
                               values['address'], values['mob'], attendance_val))
            conn.commit()
            messagebox.showinfo("Success", "Student inserted successfully.", parent=win)
            win.destroy()
        except Exception as e:
            messagebox.showerror("Error", f"Error inserting student:\n{e}", parent=win)
            conn.rollback()
        finally:
            cur.close()
            conn.close()

    win = tk.Toplevel()
    win.title("New Student Entry")
    
    frame = ttk.Frame(win, padding="10")
    frame.pack(fill="both", expand=True)

    left_frame = ttk.Frame(frame)
    left_frame.grid(row=0, column=0, padx=10, sticky="nsew")
    right_frame = ttk.Frame(frame)
    right_frame.grid(row=0, column=1, padx=10, sticky="nsew")
    
    admno_var, _ = create_label_entry(left_frame, "Admission No:", 0)
    name_var, _ = create_label_entry(left_frame, "Student Name:", 1)
    father_var, _ = create_label_entry(left_frame, "Father's Name:", 2)
    mother_var, _ = create_label_entry(left_frame, "Mother's Name:", 3)
    cls_var, _ = create_label_entry(left_frame, "Class:", 4)
    sec_var, _ = create_label_entry(left_frame, "Section:", 5)
    addr_var, _ = create_label_entry(left_frame, "Address:", 6)
    mob_var, _ = create_label_entry(left_frame, "Mobile No:", 7)
    att_var, _ = create_label_entry(left_frame, "Attendance %:", 8)
    
    ttk.Label(right_frame, text="Subjects:", font=("Segoe UI", 10, "bold")).grid(row=0, column=0, columnspan=2, pady=5)
    subject_vars = []
    for i in range(10):
        s_var, _ = create_label_entry(right_frame, f"Subject {i+1}:", i + 1, width=20)
        subject_vars.append(s_var)
        
    ttk.Button(frame, text="Submit New Student", command=submit_student).grid(row=1, column=0, columnspan=2, pady=15)


def student_update_gui():
    def fetch_and_open_update():
        admno = admno_var.get().strip()
        if not admno:
            messagebox.showerror("Error", "Please enter an Admission No.", parent=win)
            return

        conn = get_db_connection()
        cur = conn.cursor(MySQLdb.cursors.DictCursor)
        cur.execute("SELECT * FROM StudentMaster WHERE admno=%s", (admno,))
        student_data = cur.fetchone()
        cur.close()
        conn.close()
        
        if not student_data:
            messagebox.showerror("Not Found", f"No student found with Admission No: {admno}", parent=win)
            return
            
        open_update_window(student_data)
        
    def open_update_window(student_data):
        
        def save_changes():
            values = {
                'admno': admno,
                'name': name_var.get().strip(),
                'father': father_var.get().strip(),
                'mother': mother_var.get().strip(),
                'cls': cls_var.get().strip(),
                'section': sec_var.get().strip(),
                'address': addr_var.get().strip(),
                'mob': mob_var.get().strip(),
                'attendance': att_var.get().strip(),
                'subjects': [s_var.get().strip() for s_var in subject_vars]
            }

            try:
                attendance_val = float(values['attendance']) if values['attendance'] else 0.0
            except ValueError:
                messagebox.showerror("Input Error", "Attendance must be a number.", parent=update_win)
                return

            conn = get_db_connection()
            cur = conn.cursor()
            try:
                cur.execute('''UPDATE StudentMaster SET 
                               student_name=%s, father_name=%s, mother_name=%s, class=%s, section=%s,
                               subject1=%s, subject2=%s, subject3=%s, subject4=%s, subject5=%s, 
                               subject6=%s, subject7=%s, subject8=%s, subject9=%s, subject10=%s,
                               address=%s, mobno=%s, attendance=%s
                               WHERE admno=%s
                             ''', (values['name'], values['father'], values['mother'], values['cls'], values['section'],
                                   values['subjects'][0], values['subjects'][1], values['subjects'][2], values['subjects'][3],
                                   values['subjects'][4], values['subjects'][5], values['subjects'][6], values['subjects'][7],
                                   values['subjects'][8], values['subjects'][9],
                                   values['address'], values['mob'], attendance_val,
                                   values['admno']))
                conn.commit()
                messagebox.showinfo("Success", "Student updated successfully.", parent=update_win)
                update_win.destroy()
                win.destroy()
            except Exception as e:
                messagebox.showerror("Error", f"Error updating student:\n{e}", parent=update_win)
                conn.rollback()
            finally:
                cur.close()
                conn.close()

        
        admno = student_data['admno']
        update_win = tk.Toplevel()
        update_win.title(f"Update Student: {admno}")
        
        frame = ttk.Frame(update_win, padding="10")
        frame.pack(fill="both", expand=True)

        left_frame = ttk.Frame(frame)
        left_frame.grid(row=0, column=0, padx=10, sticky="nsew")
        right_frame = ttk.Frame(frame)
        right_frame.grid(row=0, column=1, padx=10, sticky="nsew")

        def create_and_set(parent, text, row, data_key):
            ttk.Label(parent, text=text, font=("Segoe UI", 10)).grid(row=row, column=0, sticky="w", padx=5, pady=2)
            var = tk.StringVar(value=student_data.get(data_key, ''))
            entry = ttk.Entry(parent, textvariable=var, width=30)
            entry.grid(row=row, column=1, sticky="we", padx=5, pady=2)
            return var
        
        name_var = create_and_set(left_frame, "Student Name:", 1, 'student_name')
        father_var = create_and_set(left_frame, "Father's Name:", 2, 'father_name')
        mother_var = create_and_set(left_frame, "Mother's Name:", 3, 'mother_name')
        cls_var = create_and_set(left_frame, "Class:", 4, 'class')
        sec_var = create_and_set(left_frame, "Section:", 5, 'section')
        addr_var = create_and_set(left_frame, "Address:", 6, 'address')
        mob_var = create_and_set(left_frame, "Mobile No:", 7, 'mobno')
        att_var = create_and_set(left_frame, "Attendance %:", 8, 'attendance')
        
        ttk.Label(right_frame, text="Subjects:", font=("Segoe UI", 10, "bold")).grid(row=0, column=0, columnspan=2, pady=5)
        subject_vars = []
        for i in range(10):
            var = create_and_set(right_frame, f"Subject {i+1}:", i + 1, f'subject{i+1}')
            subject_vars.append(var)
            
        ttk.Button(frame, text="Save Changes", command=save_changes).grid(row=1, column=0, columnspan=2, pady=15)

    win = tk.Toplevel()
    win.title("Update Student Profile")
    win.geometry("350x150")
    
    frame = ttk.Frame(win, padding="20")
    frame.pack(fill="both", expand=True)
    
    admno_var, _ = create_label_entry(frame, "Admission No:", 0)
    
    ttk.Button(frame, text="Fetch Student Data", command=fetch_and_open_update).grid(row=1, column=0, columnspan=2, pady=20)


def student_delete_gui():
    def delete_student():
        admno = admno_var.get().strip()
        if not admno:
            messagebox.showerror("Error", "Please enter an Admission No.", parent=win)
            return
            
        confirm = messagebox.askyesno(
            "Confirm Deletion", 
            f"Are you sure you want to delete student {admno}?\nAll associated marks will also be deleted (ON DELETE CASCADE).",
            parent=win
        )
        
        if not confirm:
            return

        conn = get_db_connection()
        cur = conn.cursor()
        try:
            cur.execute("DELETE FROM StudentMaster WHERE admno=%s", (admno,))
            conn.commit()
            deleted_count = cur.rowcount
            if deleted_count > 0:
                messagebox.showinfo("Success", f"Student {admno} deleted successfully.", parent=win)
                win.destroy()
            else:
                messagebox.showwarning("Not Found", f"No student found with Admission No: {admno}", parent=win)
        except Exception as e:
            messagebox.showerror("Error", f"Error deleting student:\n{e}", parent=win)
            conn.rollback()
        finally:
            cur.close()
            conn.close()

    win = tk.Toplevel()
    win.title("Delete Student")
    win.geometry("350x150")
    
    frame = ttk.Frame(win, padding="20")
    frame.pack(fill="both", expand=True)
    
    admno_var, _ = create_label_entry(frame, "Admission No:", 0)
    
    
    ttk.Button(frame, text="Delete Student Record", command=delete_student).grid(row=1, column=0, columnspan=2, pady=20)


def student_display_and_export_gui():
    
    win = tk.Toplevel()
    win.title("Student Records Display")
    win.geometry("1000x600")

    frame = ttk.Frame(win, padding="10")
    frame.pack(fill="both", expand=True)

    tree_frame = ttk.Frame(frame)
    tree_frame.pack(fill="both", expand=True, pady=10)

    columns = ("admno", "name", "class", "section", "father", "mobno", "attendance")
    tree = ttk.Treeview(tree_frame, columns=columns, show="headings")
    
    tree.heading("admno", text="Adm No")
    tree.heading("name", text="Student Name")
    tree.heading("class", text="Class")
    tree.heading("section", text="Section")
    tree.heading("father", text="Father's Name")
    tree.heading("mobno", text="Mobile No")
    tree.heading("attendance", text="Attendance")

    tree.column("admno", width=80, anchor="center")
    tree.column("name", width=200)
    tree.column("class", width=60, anchor="center")
    tree.column("section", width=60, anchor="center")
    tree.column("father", width=200)
    tree.column("mobno", width=120)
    tree.column("attendance", width=100, anchor="e")

    vsb = ttk.Scrollbar(tree_frame, orient="vertical", command=tree.yview)
    hsb = ttk.Scrollbar(tree_frame, orient="horizontal", command=tree.xview)
    tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)

    vsb.pack(side="right", fill="y")
    hsb.pack(side="bottom", fill="x")
    tree.pack(fill="both", expand=True)
    
    all_rows = []
    
    def refresh_data():
        nonlocal all_rows
        for i in tree.get_children():
            tree.delete(i)
        
        all_rows = []
        try:
            conn = get_db_connection()
            cur = conn.cursor()
            cur.execute("SELECT admno, student_name, class, section, father_name, mobno, attendance FROM StudentMaster ORDER BY class, section, student_name")
            rows = cur.fetchall()
            
            headers = [d[0] for d in cur.description]
            all_rows.append(headers)
            
            for row in rows:
                tree.insert("", "end", values=row)
                all_rows.append(row)
                
            cur.close()
            conn.close()
        except Exception as e:
            messagebox.showerror("Error", f"Could not fetch student data:\n{e}", parent=win)

    def export_to_csv():
        if not all_rows or len(all_rows) <= 1:
            messagebox.showwarning("No Data", "No data to export. Please refresh first.", parent=win)
            return
            
        fname = f"students_export_{datetime.now().strftime('%Y%m%d%H%M%S')}.csv"
        try:
            with open(fname, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerows(all_rows)
            messagebox.showinfo("Success", f"Data exported successfully to:\n{os.path.abspath(fname)}", parent=win)
        except Exception as e:
            messagebox.showerror("Export Error", f"Could not write CSV file:\n{e}", parent=win)

    btn_frame = ttk.Frame(frame)
    btn_frame.pack(fill="x")
    
    ttk.Button(btn_frame, text="Refresh Data", command=refresh_data).pack(side="left", padx=10)
    ttk.Button(btn_frame, text="Export to CSV", command=export_to_csv).pack(side="left", padx=10)

    refresh_data()


# ----------------------- MARKS MASTER (GUI) -----------------------

def teacher_login_gui():
    
    def attempt_login():
        tid = tid_var.get().strip()
        pwd = pwd_var.get().strip()
        
        if not tid or not pwd:
            messagebox.showerror("Error", "Please enter Teacher ID and Password", parent=win)
            return

        conn = get_db_connection()
        cur = conn.cursor()
        try:
            cur.execute("SELECT * FROM TeacherMaster WHERE teacher_id=%s AND password=%s", (tid, pwd))
            r = cur.fetchone()
            if r:
                messagebox.showinfo("Success", f"Login successful. Welcome {r[2]}")
                win.destroy()
                open_marks_dashboard(tid)
            else:
                messagebox.showerror("Login Failed", "Invalid Teacher ID or Password.", parent=win)
        except Exception as e:
            messagebox.showerror("Error", f"Error during login:\n{e}", parent=win)
        finally:
            cur.close()
            conn.close()

    win = tk.Toplevel()
    win.title("Teacher Login")
    win.geometry("350x200")
    
    frame = ttk.Frame(win, padding="20")
    frame.pack(fill="both", expand=True)

    ttk.Label(frame, text="Marks & Report Menu", font=("Segoe UI", 14, "bold")).grid(row=0, column=0, columnspan=2, pady=(0, 15))
    
    tid_var, _ = create_label_entry(frame, "Teacher ID:", 1)
    pwd_var, _ = create_label_entry(frame, "Password:", 2, show="*")
    
    ttk.Button(frame, text="Login", command=attempt_login).grid(row=3, column=0, columnspan=2, pady=20)
    
    _.focus_set()


def open_marks_dashboard(teacher_id):
    
    win = tk.Toplevel()
    win.title(f"Marks Dashboard - {teacher_id}")
    win.geometry("600x600")
    
    frame = ttk.Frame(win, padding="20")
    frame.pack(fill="both", expand=True)
    
    ttk.Label(frame, text="Marks & Report Menu", font=("Segoe UI", 16, "bold")).pack(pady=10)
    ttk.Label(frame, text=f"Logged in as: {teacher_id}", font=("Segoe UI", 10)).pack(pady=(0, 20))

    style = ttk.Style()
    style.configure('Dash.TButton', font=('Segoe UI', 12), padding=10)

    ttk.Button(frame, text="Marks Entry", command=lambda: marks_entry_gui(teacher_id), style='Dash.TButton').pack(fill="x", pady=5)
    ttk.Button(frame, text="Update Marks", command=lambda: marks_update_gui(teacher_id), style='Dash.TButton').pack(fill="x", pady=5)
    ttk.Button(frame, text="Delete Marks", command=lambda: marks_delete_gui(teacher_id), style='Dash.TButton').pack(fill="x", pady=5)
    ttk.Button(frame, text="View Marks", command=lambda: view_marksmaster_gui(), style='Dash.TButton').pack(fill="x", pady=5)
    
    sep = ttk.Separator(frame, orient="horizontal")
    sep.pack(fill="x", pady=15, padx=10)
    
    ttk.Button(frame, text="Report Card Menu", command=report_card_gui, style='Dash.TButton').pack(fill="x", pady=5)

def view_marksmaster_gui():
    """Opens a new window to display the contents of the MarksMaster table with Mark ID."""
    try:
        conn = get_db_connection()
    except Exception:
        return
        
    cur = conn.cursor()
    
    view_win = tk.Toplevel()
    view_win.title("MarksMaster Table Data")
    

    try:

        cur.execute("SELECT id, admno, subject, exam_name, max_marks, marks_obtained FROM MarksMaster ORDER BY admno, exam_name, subject")
        records = cur.fetchall()
        

        columns = ("Mark ID", "Adm No", "Subject", "Exam Name", "Max Marks", "Marks Obtained")
        
    except Exception as e:
        messagebox.showerror("Database Error", f"Could not retrieve MarksMaster data:\n{e}", parent=view_win)
        view_win.destroy()
        return
    finally:
        cur.close()
        conn.close()


    tree = ttk.Treeview(view_win, columns=columns, show="headings")
    

    for col in columns:
        tree.heading(col, text=col, anchor=tk.CENTER)
        tree.column(col, anchor=tk.CENTER, width=100)
    

    tree.column("Mark ID", width=70, anchor=tk.CENTER)
    tree.column("Adm No", width=80)
    tree.column("Subject", width=120)
    tree.column("Exam Name", width=100)
    tree.column("Max Marks", width=80)
    tree.column("Marks Obtained", width=100)
    

    for record in records:
        tree.insert("", tk.END, values=record)

    vsb = ttk.Scrollbar(view_win, orient="vertical", command=tree.yview)
    hsb = ttk.Scrollbar(view_win, orient="horizontal", command=tree.xview)
    tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
    
    vsb.pack(side='right', fill='y')
    hsb.pack(side='bottom', fill='x')
    tree.pack(fill='both', expand=True, padx=10, pady=10)

    view_win.geometry("750x400")




def marks_entry_gui(teacher_id):
    def submit_marks():
        adm = admno_var.get().strip()
        cls = cls_var.get().strip()
        sec = sec_var.get().strip()
        subj = subj_var.get().strip()
        exam = exam_var.get().strip()
        max_m = max_var.get().strip()
        obtained = obt_var.get().strip()
        
        if not all([adm, cls, sec, subj, exam, max_m, obtained]):
            messagebox.showerror("Error", "All fields are required.", parent=win)
            return

        try:
            marks_val = float(obtained)
            max_marks_val = int(max_m)
        except ValueError:
            messagebox.showerror("Error", "Marks must be numbers.", parent=win)
            return
            
        conn = get_db_connection()
        cur = conn.cursor()
        try:
            cur.execute('''INSERT INTO MarksMaster (admno, class, section, subject, exam_name, max_marks, marks_obtained, teacher_id)
                           VALUES (%s,%s,%s,%s,%s,%s,%s,%s)
                         ''', (adm, cls, sec, subj, exam, max_marks_val, marks_val, teacher_id))
            conn.commit()
            messagebox.showinfo("Success", "Marks saved successfully.", parent=win)
            admno_var.set("")
            obt_var.set("")
            admno_entry.focus_set()
        except Exception as e:
            messagebox.showerror("Error", f"Error saving marks:\n{e}", parent=win)
            conn.rollback()
        finally:
            cur.close()
            conn.close()

    win = tk.Toplevel()
    win.title(f"Marks Entry (Teacher: {teacher_id})")
    
    frame = ttk.Frame(win, padding="10")
    frame.pack(fill="both", expand=True)
    
    ttk.Label(frame, text="Batch Details", font=("Segoe UI", 12, "bold")).grid(row=0, column=0, columnspan=4, pady=10)
    
    cls_var, _ = create_label_entry(frame, "Class:", 1)
    sec_var, _ = create_label_entry(frame, "Section:", 2)
    subj_var, _ = create_label_entry(frame, "Subject:", 1, col=2)
    exam_var, _ = create_label_entry(frame, "Exam Name:", 2, col=2)
    max_var, _ = create_label_entry(frame, "Max Marks:", 3, col=0)
    
    ttk.Separator(frame, orient="horizontal").grid(row=4, column=0, columnspan=4, sticky="we", pady=15)
    
    ttk.Label(frame, text="Enter Marks", font=("Segoe UI", 12, "bold")).grid(row=5, column=0, columnspan=4, pady=10)
    
    admno_var, admno_entry = create_label_entry(frame, "Admission No:", 6)
    obt_var, _ = create_label_entry(frame, "Marks Obtained:", 7)
    
    ttk.Button(frame, text="Submit Marks", command=submit_marks).grid(row=8, column=0, columnspan=4, pady=20)


def marks_update_gui(teacher_id):
    def find_and_update_marks():
        admno = admno_var.get().strip()
        
        marks_id = marks_id_var.get().strip()
        new_marks = new_marks_var.get().strip()
        
        if not all([admno, marks_id, new_marks]):
            messagebox.showerror("Error", "All fields are required.\n(First find marks by Adm No, then enter ID to update)", parent=win)
            return

        try:
            marks_val = float(new_marks)
            marks_id_val = int(marks_id)
        except ValueError:
            messagebox.showerror("Error", "Marks ID and New Marks must be numbers.", parent=win)
            return

        conn = get_db_connection()
        cur = conn.cursor()
        try:
            cur.execute("UPDATE MarksMaster SET marks_obtained=%s WHERE id=%s AND teacher_id=%s", 
                        (marks_val, marks_id_val, teacher_id))
            conn.commit()
            if cur.rowcount > 0:
                messagebox.showinfo("Success", "Marks updated successfully.", parent=win)
                marks_id_var.set("")
                new_marks_var.set("")
            else:
                messagebox.showwarning("Warning", "No mark found with that ID for this student/teacher.", parent=win)
        except Exception as e:
            messagebox.showerror("Error", f"Error updating marks:\n{e}", parent=win)
            conn.rollback()
        finally:
            cur.close()
            conn.close()

    win = tk.Toplevel()
    win.title(f"Update Marks (Teacher: {teacher_id})")
    
    frame = ttk.Frame(win, padding="20")
    frame.pack(fill="both", expand=True)

    ttk.Label(frame, text="Update Marks", font=("Segoe UI", 14, "bold")).grid(row=0, column=0, columnspan=2, pady=(0, 15))
    
    admno_var, _ = create_label_entry(frame, "Admission No:", 1)
    
    ttk.Label(frame, text="(Note: Find the Marks ID from the console query or Student Display)", font=("Segoe UI", 8, "italic")).grid(row=2, column=0, columnspan=2, pady=(0,10))

    marks_id_var, _ = create_label_entry(frame, "Marks Entry ID to Update:", 3)
    new_marks_var, _ = create_label_entry(frame, "New Marks Obtained:", 4)
    
    ttk.Button(frame, text="Update Marks", command=find_and_update_marks).grid(row=5, column=0, columnspan=2, pady=20)


def marks_delete_gui(teacher_id):
    def delete_marks():
        marks_id = marks_id_var.get().strip()
        
        if not marks_id:
            messagebox.showerror("Error", "Marks Entry ID is required.", parent=win)
            return
            
        if not messagebox.askyesno("Confirm Deletion", f"Delete Marks Entry ID {marks_id}?\nThis cannot be undone.", parent=win):
            return

        try:
            marks_id_val = int(marks_id)
        except ValueError:
            messagebox.showerror("Error", "Marks ID must be a number.", parent=win)
            return

        conn = get_db_connection()
        cur = conn.cursor()
        try:
            cur.execute("DELETE FROM MarksMaster WHERE id=%s AND teacher_id=%s", 
                        (marks_id_val, teacher_id))
            conn.commit()
            if cur.rowcount > 0:
                messagebox.showinfo("Success", "Marks entry deleted successfully.", parent=win)
                marks_id_var.set("")
            else:
                messagebox.showwarning("Warning", "No mark found with that ID for this teacher.", parent=win)
        except Exception as e:
            messagebox.showerror("Error", f"Error deleting marks:\n{e}", parent=win)
            conn.rollback()
        finally:
            cur.close()
            conn.close()

    win = tk.Toplevel()
    win.title(f"Delete Marks (Teacher: {teacher_id})")
    
    frame = ttk.Frame(win, padding="20")
    frame.pack(fill="both", expand=True)

    ttk.Label(frame, text="Delete Marks Entry", font=("Segoe UI", 14, "bold")).grid(row=0, column=0, columnspan=2, pady=(0, 15))
    
    ttk.Label(frame, text="(Note: Find the Marks ID from the console query or Student Display)", font=("Segoe UI", 8, "italic")).grid(row=1, column=0, columnspan=2, pady=(0,10))

    marks_id_var, _ = create_label_entry(frame, "Marks Entry ID to Delete:", 2)
    
    
    ttk.Button(frame, text="Delete Entry", command=delete_marks).grid(row=3, column=0, columnspan=2, pady=20)

# ----------------------- REPORT CARD (GUI) -----------------------

def fetch_report_details():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT school_name, school_address, contact, website, logo_path, principal_name FROM ReportDetails WHERE id=1")
    r = cur.fetchone()
    cur.close()
    conn.close()
    if r:
        keys = ['school_name','school_address','contact','website','logo_path','principal_name']
        return dict(zip(keys, r))
    return {}


def generate_report_card(admno, filename):
    school_details = fetch_report_details()
    
    
    if not school_details.get('school_name'):
        raise Exception("School Report Details not set. Please set them in the Report Card menu.")

    conn = get_db_connection()
    cur = conn.cursor()
    try:
        
        cur.execute("SELECT student_name, father_name, class, section, attendance FROM StudentMaster WHERE admno=%s", (admno,))
        student_r = cur.fetchone()
        if not student_r:
            raise Exception(f"Student with Admission No {admno} not found.")
        student_details = dict(zip(['student_name', 'father_name', 'class', 'section', 'attendance'], student_r))

        
        cur.execute("SELECT subject, exam_name, max_marks, marks_obtained FROM MarksMaster WHERE admno=%s ORDER BY exam_name, subject", (admno,))
        marks_r = cur.fetchall()
        
        
        doc = SimpleDocTemplate(filename, pagesize=A4, rightMargin=20*mm, leftMargin=20*mm, topMargin=15*mm, bottomMargin=15*mm)
        styles = getSampleStyleSheet()
        story = []
        
        
        logo_path = school_details.get('logo_path')
        
        if logo_path:
            
            absolute_logo_path = os.path.abspath(logo_path)
            
            if os.path.exists(absolute_logo_path):
                try:
                    
                    story.append(Image(absolute_logo_path, width=40*mm, height=20*mm)) 
                    story.append(Spacer(1, 4 * mm))
                    print(f"DEBUG: Successfully attempted to embed logo from: {absolute_logo_path}")
                except Exception as logo_e:
                    
                    print(f"ERROR: Image embedding failed! Check image format (use PNG/JPG). Error: {logo_e}")
                    story.append(Paragraph("<b>[LOGO FAILED TO RENDER]</b>", styles['Normal']))
            else:
                
                print(f"ERROR: Logo file not found at path: {absolute_logo_path}")
                story.append(Paragraph("<b>[LOGO PATH INVALID]</b>", styles['Normal']))
        
        # Header Information
        story.append(Paragraph(f"<b>{school_details['school_name']}</b>", styles['h1']))
        story.append(Paragraph(school_details['school_address'], styles['Normal']))
        story.append(Spacer(1, 4 * mm))

        story.append(Paragraph("<font size=14><b>ACADEMIC REPORT CARD</b></font>", styles['h2']))
        story.append(Spacer(1, 3 * mm))

        # Student Details Table
        student_data = [
            ["Student Name:", student_details['student_name'], "Class/Section:", f"{student_details['class']}-{student_details['section']}"],
            ["Admission No:", admno, "Attendance:", f"{student_details.get('attendance', 0):.1f}%"],
            ["Father's Name:", student_details['father_name'], "Date:", datetime.now().strftime('%d-%m-%Y')]
        ]
        t = Table(student_data, colWidths=[40*mm, 55*mm, 35*mm, 55*mm])
        t.setStyle(TableStyle([
            ('INNERGRID', (0,0), (-1,-1), 0.25, colors.black),
            ('BOX', (0,0), (-1,-1), 0.25, colors.black),
            ('BACKGROUND', (0,0), (0,-1), colors.lightgrey),
            ('BACKGROUND', (2,0), (2,-1), colors.lightgrey),
            ('FONTSIZE', (0,0), (-1,-1), 10),
            ('FONT', (0,0), (-1,-1), 'Helvetica'),
        ]))
        story.append(t)
        story.append(Spacer(1, 5 * mm))

        # Marks Table
        if marks_r:
            marks_data = [["Subject", "Exam Name", "Max Marks", "Marks Obtained", "Result"]]
            total_max = 0
            total_obtained = 0
            
            for subject, exam, max_m, obtained_m in marks_r:
                if max_m is None or obtained_m is None: continue

                max_m = int(max_m)
                obtained_m = float(obtained_m)
                
                total_max += max_m
                total_obtained += obtained_m
                result = "PASS" if obtained_m >= (max_m * 0.33) else "FAIL"
                marks_data.append([subject, exam, str(max_m), f"{obtained_m:.2f}", result])

            if total_max > 0:
                marks_data.append(["TOTAL", "", str(total_max), f"{total_obtained:.2f}", ""])
                percentage = (total_obtained / total_max) * 100
                marks_data.append(["Percentage", "", "", f"{percentage:.2f}%", ""])
            else:
                marks_data.append(["No valid marks to calculate total.", "", "", "", ""])


            t = Table(marks_data, colWidths=[40*mm, 60*mm, 30*mm, 30*mm, 20*mm])
            t.setStyle(TableStyle([
                ('INNERGRID', (0,0), (-1,-1), 0.25, colors.black),
                ('BOX', (0,0), (-1,-1), 0.25, colors.black),
                ('BACKGROUND', (0,0), (-1,0), colors.lightgrey),
                ('BACKGROUND', (0,-2), (1,-2), colors.lightgrey),
                ('BACKGROUND', (0,-1), (2,-1), colors.lightblue),
                ('ALIGN', (2,1), (-1,-1), 'CENTER'),
            ]))
            story.append(t)
            story.append(Spacer(1, 10 * mm))

        else:
            story.append(Paragraph("<b>No marks entered for this student yet.</b>", styles['Normal']))
            story.append(Spacer(1, 10 * mm))
        footer_data = [
            ["Class Teacher Sign", "Principal Sign"],
            ["", ""],
            ["", school_details.get('principal_name', 'Principal')]
        ]
        t = Table(footer_data, colWidths=[90*mm, 90*mm])
        t.setStyle(TableStyle([
            ('LINEBELOW', (0,0), (0,0), 0.25, colors.black),
            ('LINEBELOW', (1,0), (1,0), 0.25, colors.black),
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
            ('VALIGN', (0,0), (-1,-1), 'BOTTOM'),
            ('TOPPADDING', (0,0), (-1,-1), 15),
        ]))
        story.append(t)
        doc.build(story)

    except Exception as e:
        raise e
    finally:
        cur.close()
        conn.close()


def set_report_details_cli():
    """Sets school details via the console."""
    conn = get_db_connection()
    cur = conn.cursor()
    print("\n--- Enter School Details for Report Card (in console) ---")
    school_name = input("School Name: ").strip()
    school_address = input("School Address: ").strip()
    contact = input("Contact: ").strip()
    website = input("Website: ").strip()
    logo = input("Logo file name present in the folder (optional, leave blank if none): ").strip()
    principal = input("Principal Name: ").strip()
    try:
        cur.execute("REPLACE INTO ReportDetails (id, school_name, school_address, contact, website, logo_path, principal_name) VALUES (1,%s,%s,%s,%s,%s,%s)", (school_name, school_address, contact, website, logo, principal))
        conn.commit()
        print("Report details saved.")
        messagebox.showinfo("Success", "School details saved successfully.")
    except Exception as e:
        print("Error saving report details:", e)
        messagebox.showerror("Error", f"Could not save details:\n{e}")
        conn.rollback()
    finally:
        cur.close()
        conn.close()


def report_card_gui():
    
    def run_generate_single():
        admno = admno_var.get().strip()
        if not admno:
            messagebox.showerror("Error", "Please enter an Admission No.", parent=win)
            return
            
        
        safe_admno = admno.replace('/', '_').replace('\\', '_')
        
    
        filename = f"Report_Card_{safe_admno}_{datetime.now().strftime('%Y')}.pdf"
        try:
            generate_report_card(admno, filename)
            messagebox.showinfo("Success", f"Report card saved as:\n{os.path.abspath(filename)}", parent=win)
        except Exception as e:
            
            messagebox.showerror("Error", f"Could not generate report:\n{e}", parent=win)
            
    def run_batch_generate():
        cls = cls_var.get().strip()
        sec = sec_var.get().strip()
        if not cls or not sec:
            messagebox.showerror("Error", "Please enter Class and Section.", parent=win)
            return
            
        try:
            conn = get_db_connection()
        except Exception:
            return
            
        cur = conn.cursor()
        try:
            cur.execute("SELECT admno FROM StudentMaster WHERE class=%s AND section=%s", (cls, sec))
            admnos = [r[0] for r in cur.fetchall()]
            
            if not admnos:
                messagebox.showwarning("No Students", f"No students found in Class {cls} Section {sec}.", parent=win)
                return
            
            batch_folder = f"Reports_{cls}_{sec}_{datetime.now().strftime('%Y%m%d')}"
            os.makedirs(batch_folder, exist_ok=True)
            
            success_count = 0
            for admno in admnos:
                
                safe_admno = str(admno).replace('/', '_').replace('\\', '_')
                filename = os.path.join(batch_folder, f"Report_Card_{safe_admno}.pdf")
                
                generate_report_card(admno, filename)
                success_count += 1
                
            messagebox.showinfo("Batch Complete", f"Batch generation complete.\n{success_count} reports created in:\n{os.path.abspath(batch_folder)}", parent=win)

        except Exception as e:
            messagebox.showerror("Batch Error", f"Error during batch generation:\n{e}", parent=win)
        finally:
            cur.close()
            conn.close()

    
    win = tk.Toplevel()
    win.title("Report Card Generator")
    
    notebook = ttk.Notebook(win)
    notebook.pack(fill="both", expand=True, padx=10, pady=10)
    
    
    single_frame = ttk.Frame(notebook, padding="20")
    notebook.add(single_frame, text="Single Report")
    
    ttk.Label(single_frame, text="Generate Single Report Card", font=("Segoe UI", 12, "bold")).grid(row=0, column=0, columnspan=2, pady=10)
    
    
    admno_var, admno_entry = create_label_entry(single_frame, "Admission No:", 1)
    
    ttk.Button(single_frame, text="Generate PDF", command=run_generate_single).grid(row=2, column=0, columnspan=2, pady=15)
    
    
    batch_frame = ttk.Frame(notebook, padding="20")
    notebook.add(batch_frame, text="Batch Report")

    ttk.Label(batch_frame, text="Batch Generate by Class/Section", font=("Segoe UI", 12, "bold")).grid(row=0, column=0, columnspan=2, pady=10)
    
    
    cls_var, cls_entry = create_label_entry(batch_frame, "Class:", 1)
    sec_var, sec_entry = create_label_entry(batch_frame, "Section:", 2)
    
    ttk.Button(batch_frame, text="Generate Batch PDFs", command=run_batch_generate).grid(row=3, column=0, columnspan=2, pady=15)

   
    settings_frame = ttk.Frame(notebook, padding="20")
    notebook.add(settings_frame, text="School Settings")
    
    ttk.Label(settings_frame, text="Set School Details", font=("Segoe UI", 12, "bold")).pack(pady=10)
    
    ttk.Button(settings_frame, text="Open Settings (in Console)", command=set_report_details_cli).pack(pady=20)

# ----------------------- MAIN APPLICATION -----------------------

def create_main_dashboard(root):
    initialize_database()

    root = tk.Tk()
    root.title("Exams & Tests System")
    root.geometry("900x650")
    root.configure(bg="#e6f0ff")

    style = ttk.Style()
    style.theme_use("clam")  
    style.configure("TLabel", font=("Segoe UI", 11))
    style.configure("TButton", font=("Segoe UI", 10, "bold"), padding=5)
    style.configure("TEntry", padding=5)
    style.configure("TNotebook", background="#e6f0ff", borderwidth=0)
    style.configure("TNotebook.Tab", font=("Arial", 11, "bold"), padding=[12, 6])

    style.map("TNotebook.Tab", background=[("selected", "#4a7abc")], foreground=[("selected", "white")])
   
    

    notebook = ttk.Notebook(root)
    notebook.pack(expand=True, fill="both", padx=10, pady=10)

    
    home_tab = tk.Frame(notebook, bg="#e6f0ff")
    notebook.add(home_tab, text="🏫 Home")

    tk.Label(home_tab, text="Welcome to Exams & Tests Management System",
             font=("Arial", 20, "bold"), bg="#e6f0ff", fg="#003366").pack(pady=30)

    tk.Label(home_tab,
             text="Manage Teachers, Students, Marks and Reports all in one place!",
             font=("Arial", 13), bg="#e6f0ff", fg="#004080").pack(pady=10)

    tk.Label(home_tab,
             text="(Developed By Kaushal Jha XII A)",
             font=("Arial", 11, "italic"), bg="#e6f0ff", fg="#004080").pack(pady=10)

    
    teacher_tab = tk.Frame(notebook, bg="#e6f0ff")
    notebook.add(teacher_tab, text="👩‍🏫 Teacher Master")

    tk.Label(teacher_tab, text="Teacher Master Functions", font=("Arial", 16, "bold"), bg="#e6f0ff").pack(pady=10)
    for text, cmd in [
        ("Entry of Teacher Details", teacher_entry),
        ("Update Teacher Record", teacher_update),
        ("Delete Teacher Record", teacher_delete),
        ("Query & Reports(IN CONSOLE)", teacher_query_reports)
    ]:
        ttk.Button(teacher_tab, text=text, command=cmd).pack(pady=6, ipadx=10, ipady=4)

   
    student_tab = tk.Frame(notebook, bg="#e6f0ff")
    notebook.add(student_tab, text="🎓 Student Master")

    tk.Label(student_tab, text="Student Master Functions", font=("Arial", 16, "bold"), bg="#e6f0ff").pack(pady=10)
    for text, cmd in [
        ("Entry of Student Profile", student_entry_gui),
        ("Update Student Record", student_update_gui),
        ("Delete Student Record", student_delete_gui),
        ("Display / Export Students", student_display_and_export_gui)
    ]:
        ttk.Button(student_tab, text=text, command=cmd).pack(pady=6, ipadx=10, ipady=4)

   
    marks_tab = tk.Frame(notebook, bg="#e6f0ff")
    notebook.add(marks_tab, text="🧮 Marks & Reports")

    tk.Label(marks_tab, text="Marks & Reports Functions", font=("Arial", 16, "bold"), bg="#e6f0ff").pack(pady=10)
    ttk.Label(marks_tab, text="This section requires a teacher login.").pack(pady=5)
    ttk.Button(marks_tab, text="Login as Teacher", command=teacher_login_gui).pack(fill="x", pady=20)

    ttk.Button(root, text="Exit", command=root.destroy).pack(pady=15)

    root.mainloop()
if __name__ == "__main__":
    print("Initializing Database and Tables...")
    create_main_dashboard(root="parent")
