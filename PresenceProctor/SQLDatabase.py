
import sqlite3

# Connect to the SQLite database (or create a new one if it doesn't exist)
conn = sqlite3.connect('attendance_system.db')
cursor = conn.cursor()

# Create Students table
cursor.execute('''
    CREATE TABLE IF NOT EXISTS Students (
        student_id INTEGER PRIMARY KEY,
        first_name TEXT,
        last_name TEXT,
        gender TEXT,
        parent_email TEXT,
        photo_url TEXT
    )
''')

# Create Attendance table
cursor.execute('''
    CREATE TABLE IF NOT EXISTS Attendance (
        attendance_id INTEGER PRIMARY KEY,
        student_id INTEGER,
        check_in_time DATETIME,
        status TEXT,
        FOREIGN KEY (student_id) REFERENCES Students(student_id)
    )
''')

# Sample data for Students table
students_data = [
    (1, 'Sanjay', 'Krishnan', 'Male', 'sanjaysparents@gmail.com', 'images_data/Sanjay.jpg'),
    (2, 'Jane', 'Doe', 'Female', 'jane.doth@gmail.com', 'images_data/Elon Musk.jpg'),
]

# Sample data for Attendance table
attendance_data = [
    (1, 1, '2024-04-01 08:00:00', 'Present'),
    (2, 1, '2024-04-01 08:05:00', 'Late'),
    (3, 2, '2024-04-01 08:00:00', 'Present'),
    # Add more sample data as needed
]

# Insert sample data into Students table
cursor.executemany('INSERT INTO Students (student_id, first_name, last_name, gender, parent_email, photo_url) VALUES (?, ?, ?, ?, ?, ?)', students_data)

# Insert sample data into Attendance table
cursor.executemany('INSERT INTO Attendance (attendance_id, student_id, check_in_time, status) VALUES (?, ?, ?, ?)', attendance_data)

""""
# Filters out the students that are absent or late

cursor.execute('''
    SELECT s.first_name, s.last_name, a.check_in_time, a.status
    FROM Students s
    JOIN Attendance a ON s.student_id = a.student_id
    WHERE a.status = 'Late' OR a.status = 'Absent'
''')
"""

# Fetch and print the results
late_or_absent_records = cursor.fetchall()
for record in late_or_absent_records:
    print(record)

# Commit the transaction
conn.commit()

# Close the connection
conn.close()
