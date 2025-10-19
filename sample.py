import cv2
import sqlite3
import pyttsx3
from datetime import datetime

# Text-to-speech engine
engine = pyttsx3.init()

def speak(text):
    engine.say(text)
    engine.runAndWait()

# Create DB and tables
def create_db():
    conn = sqlite3.connect('attendance_system.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS students (
            student_id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS attendance (
            student_id INTEGER,
            date TEXT,
            status TEXT,
            FOREIGN KEY(student_id) REFERENCES students(student_id)
        )
    ''')
    conn.commit()
    conn.close()

# Enroll student
def enroll_student(name):
    conn = sqlite3.connect('attendance_system.db')
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO students (name) VALUES (?)", (name,))
        conn.commit()
        speak(f"{name} has been enrolled.")
    except sqlite3.IntegrityError:
        print("Student already enrolled.")
    conn.close()

# Get student ID
def get_student_id(name):
    conn = sqlite3.connect('attendance_system.db')
    cursor = conn.cursor()
    cursor.execute("SELECT student_id FROM students WHERE name = ?", (name,))
    result = cursor.fetchone()
    conn.close()
    return result[0] if result else None

# Mark attendance
def mark_attendance(student_id, status):
    conn = sqlite3.connect('attendance_system.db')
    cursor = conn.cursor()
    date_today = datetime.now().strftime('%Y-%m-%d')
    cursor.execute("SELECT * FROM attendance WHERE student_id = ? AND date = ?", (student_id, date_today))
    if cursor.fetchone() is None:
        cursor.execute("INSERT INTO attendance (student_id, date, status) VALUES (?, ?, ?)",
                       (student_id, date_today, status))
        conn.commit()
    conn.close()

# Webcam-based attendance
def webcam_attendance():
    cap = cv2.VideoCapture(0)
    print("Press 'n' to enter name, 'q' to quit webcam.")
    while True:
        ret, frame = cap.read()
        if not ret:
            continue

        # Show instructions
        cv2.putText(frame, "Press 'n' in terminal to enter name, 'q' to quit", (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

        # Display frame
        cv2.imshow('Attendance Camera', frame)

        key = cv2.waitKey(1) & 0xFF
        if key == ord('n'):
            name = input("Enter your name: ").strip()
            student_id = get_student_id(name)
            if student_id:
                mark_attendance(student_id, "Present")
                speak(f"Welcome {name}. Your attendance has been recorded.")
                print(f"Attendance marked for {name}")
            else:
                print("Student not found. Please enroll first.")
        elif key == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

# Main menu
def main():
    create_db()
    while True:
        print("\n1. Enroll Student")
        print("2. Start Webcam Attendance")
        print("3. Exit")
        choice = input("Choose option: ")

        if choice == '1':
            name = input("Enter student name: ").strip()
            enroll_student(name)
        elif choice == '2':
            webcam_attendance()
        elif choice == '3':
            break
        else:
            print("Invalid option.")

if __name__ == "__main__":
    main()
