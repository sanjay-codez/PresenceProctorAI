import tkinter as tk
from tkinter import ttk
import tkinter.messagebox
import customtkinter
from PIL import Image
import os
import re
import csv
import requests
from datetime import datetime

customtkinter.set_appearance_mode("Dark")  # Modes: "System" (standard), "Dark", "Light"
customtkinter.set_default_color_theme("green")  # Themes: "blue" (standar d), "green", "dark-blue"
username = "Sir"

# call the function and returns MM/DD/YYYY
def get_current_date():
    response = requests.get('http://worldtimeapi.org/api/timezone/Etc/UTC')
    data = response.json()
    datetime_string = data['datetime']
    if datetime_string[-3] == ':':
        datetime_string = datetime_string
    else:
        datetime_string = datetime_string[:-2] + ':' + datetime_string[-2:]
    current_datetime = datetime.fromisoformat(datetime_string)
    return current_datetime.strftime('%m/%d/%Y')


class App(customtkinter.CTk):
    width = 1920
    height = 1080

    def __init__(self):
        super().__init__()

        ### configure window ###
        self.title("PresenceProctor AI")
        self.geometry(f"{1920}x{1080}")

        # configure grid layout (4x4)
        self.grid_columnconfigure(1, weight=1)
        self.grid_columnconfigure((2, 3), weight=0)
        self.grid_rowconfigure((0, 1, 2), weight=1)


        ### START OF HOME TAB ###
        # create sidebar frame with widgets
        self.sidebar_frame = customtkinter.CTkFrame(self, width=140, corner_radius=0)
        self.sidebar_frame.grid(row=0, column=0, rowspan=4, sticky="nsew")
        self.sidebar_frame.grid_rowconfigure(8, weight=1)

        current_path = os.path.dirname(os.path.realpath(__file__))

        # HOME FRAME #
        self.homeFrame = customtkinter.CTkFrame(self, width=self.width, corner_radius=0)
        self.homeFrame.grid(row=0, column=1, rowspan=4, sticky="nsew")
        self.homeFrame.grid_columnconfigure(8, weight=1)
        self.homeFrame.grid_rowconfigure(4, weight=1)

        # Welcome Label #
        self.welcomeLabel = customtkinter.CTkLabel(self.homeFrame, text="Welcome, " + username, font=customtkinter.CTkFont(size=60, weight="bold"))
        self.welcomeLabel.grid(row=3, column=8, padx=0, pady=(70, 70))
        ### END OF HOME FRAME ###

        # Replace logo image with cropped logo image
        self.logo_image = customtkinter.CTkImage(Image.open(current_path + "/test_images/logo1.png"),
                                               size=(150, 150))
        self.logo_image = customtkinter.CTkLabel(self.sidebar_frame,text="", image=self.logo_image)
        self.logo_image.grid(row=0, column=0)

        self.logo_label = customtkinter.CTkLabel(self.sidebar_frame, text="PresenceProctor", font=customtkinter.CTkFont(size=20, weight="bold"))
        self.logo_label.grid(row=2, column=0, padx=20, pady=(20, 10))
        self.sidebar_button_1 = customtkinter.CTkButton(self.sidebar_frame,text="Home",corner_radius=0, command=self.home_button_event)
        self.sidebar_button_1.grid(row=4, column=0, padx=20, pady=10)
        self.sidebar_button_2 = customtkinter.CTkButton(self.sidebar_frame,text="Attendance", command=self.attendance_button_event)
        self.sidebar_button_2.grid(row=5, column=0, padx=20, pady=10)
        self.sidebar_button_3 = customtkinter.CTkButton(self.sidebar_frame,text="Setup", command=self.setup_button_event)
        self.sidebar_button_3.grid(row=6, column=0, padx=20, pady=10)
        self.appearance_mode_label = customtkinter.CTkLabel(self.sidebar_frame, text="Appearance Mode:", anchor="w")
        self.appearance_mode_label.grid(row=9, column=0, padx=20, pady=(10, 0))
        self.appearance_mode_optionmenu = customtkinter.CTkOptionMenu(self.sidebar_frame, values=["Light", "Dark", "System"],
                                                                      command=self.change_appearance_mode_event)
        self.appearance_mode_optionmenu.grid(row=9, column=0, padx=20, pady=(10, 10))
        self.scaling_label = customtkinter.CTkLabel(self.sidebar_frame, text="UI Scaling:", anchor="w")
        self.scaling_label.grid(row=10, column=0, padx=20, pady=(10, 0))
        self.scaling_optionmenu = customtkinter.CTkOptionMenu(self.sidebar_frame, values=["100%"],
                                                              command=self.change_scaling_event)
        self.scaling_optionmenu.grid(row=11, column=0, padx=20, pady=(10, 20))
        # Name label #
        self.label_frame = customtkinter.CTkFrame(self, width=150, corner_radius=0)
        self.label_frame.grid(row=0, column=1, sticky = "n")
        self.main_label = customtkinter.CTkLabel(self.label_frame, text="PresenceProctor Dashboard", font=customtkinter.CTkFont(size=20, weight="bold"))
        self.main_label.grid(row=0, column=0, padx=10, pady=(10, 15))

        # Setting Default Values #
        self.scaling_optionmenu.set("100%")
        self.appearance_mode_optionmenu.set("Dark")
        ### END OF HOME TAB ###

        # Style configuration for the Treeview to make it dark
        style = ttk.Style(self)
        style.theme_use("clam")  # 'clam' theme supports customizing colors, choose the theme that suits your OS

        # Configure the Treeview colors
        style.configure("Treeview",
                        background="#333333",
                        fieldbackground="#333333",
                        foreground="white",
                        rowheight=25)  # Adjust the height of rows if needed

        # Configure the Treeview Heading colors (Treeview.Heading)
        style.configure("Treeview.Heading",
                        background="#333333",
                        foreground="white")

        # Change selected color
        style.map('Treeview', background=[('selected', '#0a82cc')])  # Adjust selected color if needed

        ### START OF ATTENDANCE FRAME ###
        self.attendanceFrame = customtkinter.CTkFrame(self, width=self.width, corner_radius=0)
        self.attendanceFrame.grid(row=0, column=1, rowspan=4, sticky="nsew")
        self.attendanceFrame.grid_columnconfigure(0, weight=1)
        self.attendanceFrame.grid_rowconfigure(0, weight=0)  # Title row shouldn't stretch
        self.attendanceFrame.grid_rowconfigure(1, weight=1)  # Content below the title should stretch

        # Add a title label to the attendance frame at the top
        self.attendanceLabel = customtkinter.CTkLabel(self.attendanceFrame, text="Take Attendance",
                                                      font=customtkinter.CTkFont(size=60, weight="bold"))
        self.attendanceLabel.grid(row=0, column=0, padx=20, pady=(20, 0), sticky="n")

        # Initially, the attendance frame should not be visible, so we use grid_forget
        self.attendanceFrame.grid_forget()
        ### END OF ATTENDANCE FRAME ###

        ### START OF SETUP FRAME ###
        self.setupFrame = customtkinter.CTkFrame(self, width=self.width, corner_radius=0)
        self.setupFrame.grid(row=0, column=1, rowspan=4, sticky="nsew")

        # Adjust the column configuration for a centered look
        self.setupFrame.grid_columnconfigure(0, weight=1)
        self.setupFrame.grid_columnconfigure(1, minsize=600, weight=0)  # Control the width of the center column
        self.setupFrame.grid_columnconfigure(2, weight=1)
        self.setupFrame.grid_rowconfigure(1, weight=1)
        self.setupFrame.grid_rowconfigure(2, weight=1)
        self.setupFrame.grid_rowconfigure(3, weight=2)
        # Adjust the column configuration for a centered look with a slight offset to the left


        # Place the label at the top of the setup frame, centered
        self.setupLabel = customtkinter.CTkLabel(self.setupFrame, text="Setup Students Page",
                                                 font=customtkinter.CTkFont(size=60, weight="bold"))

        self.setupLabel.grid(row=0, column=0, columnspan=3, sticky="n")

        # Add Subtitle
        self.addStudentLabel = customtkinter.CTkLabel(self.setupFrame, text="Add Student",
                                                      font=customtkinter.CTkFont(size=30), fg_color=None,
                                                      text_color='white')
        self.addStudentLabel.grid(row=1, column=0, sticky="s")



        # Student Setup Section, using the column 1 with controlled width
        self.studentSetupSection = customtkinter.CTkFrame(self.setupFrame, corner_radius=10)
        self.studentSetupSection.grid(row=2, column=0, sticky="n", padx=50, pady=20)

        # Adjust padding for the error label here
        error_label_padx = 50
        error_label_pady = 200

        # Error label to display errors
        self.error_message = tkinter.StringVar()
        # self.error_label = customtkinter.CTkLabel(self.setupFrame, textvariable=self.error_message, fg_color=None,
        #                                           text_color='red')

        self.error_label = customtkinter.CTkLabel(self.setupFrame, textvariable=self.error_message,
                                                  font=customtkinter.CTkFont(size=10, weight="bold"))

        self.error_label.grid(row=3, column=0, columnspan=1, padx=50, pady=(0, 500), sticky="n")

        # Adjust padding and size for entries and buttons here
        entry_padx = 10
        entry_pady = 5
        entry_ipady = 5  # internal padding for height

        # First Name Entry
        self.firstNameEntry = customtkinter.CTkEntry(self.studentSetupSection, placeholder_text="First Name")
        self.firstNameEntry.grid(row=1, column=0, padx=entry_padx, pady=entry_pady, sticky="ew", ipady=entry_ipady)

        # Last Name Entry
        self.lastNameEntry = customtkinter.CTkEntry(self.studentSetupSection, placeholder_text="Last Name")
        self.lastNameEntry.grid(row=2, column=0, padx=entry_padx, pady=entry_pady, sticky="ew", ipady=entry_ipady)

        # Gender Selection Label
        self.genderLabel = customtkinter.CTkLabel(self.studentSetupSection, text="Gender:")
        self.genderLabel.grid(row=3, column=0, padx=(entry_padx, 0), pady=entry_pady, sticky="w")

        # Gender Radio Buttons
        self.genderVar = tkinter.StringVar(value="M")
        self.maleRadioButton = customtkinter.CTkRadioButton(self.studentSetupSection, text="Male",
                                                            variable=self.genderVar, value="M")
        self.maleRadioButton.grid(row=4, column=0, padx=(entry_padx, 2), pady=2, sticky="w")
        self.femaleRadioButton = customtkinter.CTkRadioButton(self.studentSetupSection, text="Female",
                                                              variable=self.genderVar, value="F")
        self.femaleRadioButton.grid(row=4, column=0, padx=(entry_padx + 100, 2), pady=2, sticky="w")

        # Email Entry
        self.emailEntry = customtkinter.CTkEntry(self.studentSetupSection, placeholder_text="Email")
        self.emailEntry.grid(row=5, column=0, padx=entry_padx, pady=entry_pady, sticky="ew", ipady=entry_ipady)

        # Submit Button
        self.submitButton = customtkinter.CTkButton(self.studentSetupSection, text="Submit",
                                                    command=self.submit_student_info)
        self.submitButton.grid(row=6, column=0, padx=entry_padx, pady=(entry_pady, 20))

        self.setupFrame.grid_forget()
        ### END OF SETUP FRAME ###

    def open_input_dialog_event(self):
        dialog = customtkinter.CTkInputDialog(text="Type in a number:", title="CTkInputDialog")
        print("CTkInputDialog:", dialog.get_input())

    def change_appearance_mode_event(self, new_appearance_mode: str):
        customtkinter.set_appearance_mode(new_appearance_mode)

    def change_scaling_event(self, new_scaling: str):
        new_scaling_float = int(new_scaling.replace("%", "")) / 100
        customtkinter.set_widget_scaling(new_scaling_float)

    def home_button_event(self):
        self.attendanceFrame.grid_forget()
        self.setupFrame.grid_forget()
        self.homeFrame.grid(row=0, column=1, rowspan=4, sticky="nsew")

    def attendance_button_event(self):
        self.homeFrame.grid_forget()
        self.setupFrame.grid_forget()
        self.attendanceFrame.grid(row=0, column=1, rowspan=4, sticky="nsew")

    def setup_button_event(self):
        # Hide the other frames
        self.homeFrame.grid_forget()
        self.attendanceFrame.grid_forget()
        # Show the setup frame
        self.setupFrame.grid(row=0, column=1, rowspan=4, sticky="nsew")
        self.create_student_table()
        self.setup_table_buttons()  # Create edit and delete buttons when setup tab is shown

    def submit_student_info(self):
        # Validation for First and Last Name
        first_name = self.firstNameEntry.get().strip()
        if not first_name or len(first_name) < 2 or not first_name[0].isupper():
            self.error_message.set("First Name : Invalid First Name\n First Name : Capitalize first letter\n First Name : Minimum length: 2")
            self.firstNameEntry.delete(0, tkinter.END)  # Clear the entry field
            return

        last_name = self.lastNameEntry.get().strip()
        if not last_name or len(last_name) < 2 or not last_name[0].isupper():
            self.error_message.set("Last Name : Invalid Last Name\n Last Name : Capitalize first letter\n Last Name : Minimum length: 2")
            self.lastNameEntry.delete(0, tkinter.END)  # Clear the entry field
            return

        # Validation for Email using regex
        email = self.emailEntry.get().strip()
        if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            self.error_message.set("Invalid email address.\nOr left blank")
            self.emailEntry.delete(0, tkinter.END)  # Clear the entry field
            return

        gender = self.genderVar.get()

        # No errors, clear the error message
        self.error_message.set("")

        try:
            with open('student_data.csv', 'r', newline='') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    if row['First Name'].strip().lower() == first_name.lower() and \
                            row['Last Name'].strip().lower() == last_name.lower():
                        self.error_message.set("Duplicate entry:\n - This student is already added.")
                        return
                    if row['Email'].strip().lower() == email.lower():
                        self.error_message.set("Duplicate email:\n - This email is already used.")
                        return
        except FileNotFoundError:
            # If the file doesn't exist yet, no need to check for duplicates
            pass

            # Append the new data to the CSV file
        # No duplicate found, append the new data to the CSV file
        try:
            with open('student_data.csv', 'a', newline='') as file:
                fieldnames = ['First Name', 'Last Name', 'Gender', 'Email', 'Presence']
                writer = csv.DictWriter(file, fieldnames=fieldnames)
                if file.tell() == 0:
                    writer.writeheader()
                writer.writerow({'First Name': first_name, 'Last Name': last_name, 'Gender': gender, 'Email': email,
                                 'Presence': "Absent"})
                # Show success message
                self.error_message.set("Student information successfully added.")
        except Exception as e:
            self.error_message.set("An error occurred while writing to the file.")

        # Clear all fields after successful submission or error
        self.firstNameEntry.delete(0, tkinter.END)
        self.lastNameEntry.delete(0, tkinter.END)
        self.emailEntry.delete(0, tkinter.END)
        self.genderVar.set("M")

        # Show success message
        self.error_message.set("Student information successfully added.")

    def create_student_table(self):
        # Treeview
        self.tree = ttk.Treeview(self.setupFrame, columns=('First Name', 'Last Name', 'Gender', 'Email'), height=10,
                                 show='headings', style="Treeview")  # Added style argument here
        for col in self.tree['columns']:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=150)  # Adjust the column's width if necessary

        # Scrollbar
        self.scrollbar = ttk.Scrollbar(self.setupFrame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscroll=self.scrollbar.set)

        # Adjust grid placements for the treeview and scrollbar
        self.tree.grid(row=2, column=1, sticky='nsew', padx=(10, 0))  # Adjust row and column index if needed
        self.scrollbar.grid(row=2, column=2, sticky='ns', padx=(0, 10))  # Adjust row and column index if needed

        # Grid configuration for the treeview
        self.setupFrame.grid_rowconfigure(2, weight=1)
        self.setupFrame.grid_columnconfigure(1, weight=1)

        # Load Data
        self.load_data()

    def load_data(self):
        # Load data from CSV and insert into the treeview
        try:
            with open('student_data.csv', 'r', newline='') as file:
                self.tree.delete(*self.tree.get_children())  # Clear current items
                reader = csv.DictReader(file)
                for row in reader:
                    self.tree.insert('', 'end',
                                     values=(row['First Name'], row['Last Name'], row['Gender'], row['Email']))
        except FileNotFoundError:
            pass  # File doesn't exist yet, nothing to load

        self.setup_table_buttons()  # Set up buttons after loading data

    def setup_table_buttons(self):
        # Remove previous buttons if they exist
        try:
            self.edit_button.destroy()
            self.delete_button.destroy()
        except AttributeError:
            pass  # Buttons were not yet created

        # Define a maximum button width
        button_width = 100  # You can adjust this value as needed

        # Create Edit Button
        self.edit_button = customtkinter.CTkButton(self.setupFrame, text="Edit",
                                                   command=self.edit_student, width=button_width)
        self.edit_button.grid(row=3, column=1, pady=(5, 400), padx=(0, 1100), sticky="")

        # Create Delete Button
        self.delete_button = customtkinter.CTkButton(self.setupFrame, text="Delete",
                                                     command=self.delete_student, width=button_width)
        self.delete_button.grid(row=3, column=1, pady=(5, 400), padx=(0, 900), sticky="")

        # Adjust the grid row and column configurations to align buttons
        self.setupFrame.grid_columnconfigure(1, weight=0)  # Remove weight from column where the button is
        self.setupFrame.grid_columnconfigure(2, weight=0)  # Remove weight from column where the button is

    def edit_student(self):
        selected = self.tree.selection()
        if selected:
            item = self.tree.item(selected[0])
            values = item['values']
            # Logic for editing the student
            print("Edit:", values)  # Replace with your editing logic
        else:
            tkinter.messagebox.showinfo("Edit", "Please select a student to edit.")

    def delete_student(self):
        selected = self.tree.selection()
        if selected:
            item = self.tree.item(selected[0])
            values = item['values']
            # Logic for deleting the student
            print("Delete:", values)  # Replace with your deletion logic
            response = tkinter.messagebox.askyesno("Delete", "Are you sure you want to delete this student?")
            if response:
                # Add your code here to delete the student from the CSV and reload the table
                pass
        else:
            tkinter.messagebox.showinfo("Delete", "Please select a student to delete.")





if __name__ == "__main__":
    app = App()
    app.mainloop()