# Exams & Tests Management System

A comprehensive, desktop-based GUI application designed to manage school examinations, student records, teacher profiles, and automated report card generation. Built with Python and Tkinter, it features a robust MySQL backend.

*(Developed By Kaushal Jha XII A)*

---

## 🌟 Key Features

### 👩‍🏫 Teacher Master
- **Registration**: Add new teachers with their specific subjects and assigned classes.
- **Record Management**: Update existing teacher details or delete records seamlessly.
- **Queries & Reports**: View all teachers or search specific records (displayed via console using `PrettyTable`).

### 🎓 Student Master
- **Profile Management**: Complete CRUD (Create, Read, Update, Delete) operations for student profiles, including admission numbers, parent details, and attendance.
- **Export Functionality**: Instantly view all student records in a dynamic data grid and export them to a `.csv` file with one click.

### 🧮 Marks & Reports (Requires Teacher Login)
- **Secure Access**: Teachers must log in using their credentials to modify marks.
- **Marks Entry**: Add, update, and delete marks for specific students, subjects, and exams.
- **Data Viewing**: View a comprehensive table of all marks entered.

### 📄 Automated Report Card Generation
- **School Settings**: Configure your school's name, address, contact, and logo.
- **PDF Generation**: Automatically generate beautiful, formatted PDF report cards using `reportlab`.
- **Batch Processing**: Generate report cards for an entire class/section in one go, or generate them individually by Admission Number.

---

## 🛠️ Technology Stack
- **Language**: Python 3.x
- **GUI Framework**: Tkinter / ttk
- **Database**: MySQL (`mysqlclient` / `MySQLdb`)
- **PDF Generation**: ReportLab
- **Other Libraries**: `Pillow` (PIL), `prettytable`

---

## ⚙️ Setup & Installation

### 1. Prerequisites
Ensure you have Python installed along with a running local instance of MySQL Server.

Install the required Python packages using pip:
```bash
pip install mysqlclient reportlab prettytable pillow
```

### 2. Database Configuration
By default, the application attempts to connect to a local MySQL server with the following credentials:
- **Host**: `localhost`
- **User**: `root`
- **Password**: `tiger`

*Note: If your MySQL server uses a different password or user, open the Python script and update the `DB_CONFIG` dictionary at the top of the file.*

### 3. Database Initialization
You don't need to manually create the database or tables. Upon running the script, the application will automatically:
1. Create the database `exams_tests_db`.
2. Create all necessary tables (`TeacherMaster`, `StudentMaster`, `MarksMaster`, `ReportDetails`).

---

## 🚀 How to Run

Navigate to the project directory and run the main Python script:
```bash
python main.py
```
*(Replace `main.py` with the actual name of the script file).*

---

## 📖 Usage Guide

1. **Start the App**: You will be greeted by the Home Dashboard.
2. **Register a Teacher**: Go to the **Teacher Master** tab and register a new teacher (you will need these credentials to enter marks later).
3. **Add Students**: Go to the **Student Master** tab to populate the system with student data.
4. **Enter Marks**: 
   - Go to the **Marks & Reports** tab and click **Login as Teacher**.
   - Enter the credentials of the teacher you created in Step 2.
   - Use the dashboard to enter marks for the students.
5. **Generate Reports**:
   - Inside the Teacher dashboard, click **Report Card Menu**.
   - First, go to the **School Settings** tab to configure your school's header details.
   - Then, use the **Single Report** or **Batch Report** tabs to generate PDF report cards!
