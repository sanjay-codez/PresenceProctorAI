
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

#check_in_time DATETIME
#status TEXT

# Sample data for Students table
students_data = [
    (1, 'Adit', 'Tripathi', 'Male', 'aditsparents@gmail.com', 'images_data/Adit.jpg'),
    (2, 'Carlos', 'LastName', 'Male', 'carlosparents@gmail.com', 'images_data/Carlos.jpg'),
    (3, 'Alex', 'Tran', 'Male', 'alexsparents@gmail.com', 'images_data/Alex.jpg'),
    (4, 'Jack', 'Wise', 'Male', 'jacksparents@gmail.com', 'images_data/Jack.jpg'),
    (5, 'Johnny', 'Nguyen', 'Male', 'johnnysparents@gmail.com', 'images_data/Johnny.jpg'),
    (6, 'Sanjay', 'Krishnan', 'Male', 'sanjaysparents@gmail.com', 'images_data/Sanjay.jpg')
]

# Insert sample data into Students table
cursor.executemany('INSERT or IGNORE INTO Students (student_id, first_name, last_name, gender, parent_email, photo_url) VALUES (?, ?, ?, ?, ?, ?)', students_data)

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
