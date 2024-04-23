
#import necessary stuff
import tkinter as tk
from tkinter import ttk
import tkinter.messagebox
import customtkinter
from PIL import Image, ImageTk
import os
import re
import csv
import requests
from datetime import datetime
from tkinter import filedialog, messagebox
from shutil import copyfile
from face_recognition import detect_face_in_video
from win32com.client import Dispatch
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt



customtkinter.set_appearance_mode("Dark")  # Modes: "System" (standard), "Dark", "Light"
customtkinter.set_default_color_theme("green")  # Themes: "blue" (standar d), "green", "dark-blue"
username = "Teacher"

# speaking audio function cool
def speak(str1):
    speak=Dispatch(("SAPI.SpVoice"))
    speak.Speak(str1)

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

        # Initialize the fullscreen state
        self.is_fullscreen = False  # Start with windowed mode

        # Set initial fullscreen mode
        self.toggle_fullscreen()

        # Bind the escape key to the toggle_fullscreen method
        self.bind("<F11>", self.toggle_fullscreen)

        ### configure window ###
        self.title("PresenceProctor")
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
        self.welcomeLabel = customtkinter.CTkLabel(self.homeFrame, text="Welcome, " + username,
                                                   font=customtkinter.CTkFont(size=60, weight="bold"))
        self.welcomeLabel.grid(row=3, column=8, padx=0, pady=(70, 70))
        # Date Label #
        self.dateLabel = customtkinter.CTkLabel(
            self.homeFrame,
            text="Today's Date: " + get_current_date(),
            font=customtkinter.CTkFont(size=40),
            text_color='white'
        )
        self.dateLabel.grid(row=3, column=8, padx=0, pady=(150, 0))

        self.graph_frame = customtkinter.CTkFrame(self, width=700, height=600)
        self.graph_frame.grid(row=0, column=1, padx=20, pady=250)

        self.load_attendance_data_and_draw_graph()

        ### END OF HOME FRAME ###

        # Replace logo image with cropped logo image
        self.logo_image = customtkinter.CTkImage(Image.open(current_path + "/test_images/logo1.png"),
                                                 size=(150, 150))
        self.logo_image = customtkinter.CTkLabel(self.sidebar_frame, text="", image=self.logo_image)
        self.logo_image.grid(row=0, column=0)

        self.logo_label = customtkinter.CTkLabel(self.sidebar_frame, text="PresenceProctor",
                                                 font=customtkinter.CTkFont(size=20, weight="bold"))
        self.logo_label.grid(row=2, column=0, padx=20, pady=(20, 10))
        self.sidebar_button_1 = customtkinter.CTkButton(self.sidebar_frame, text="Home", corner_radius=0,
                                                        command=self.home_button_event)
        self.sidebar_button_1.grid(row=4, column=0, padx=20, pady=10)
        self.sidebar_button_2 = customtkinter.CTkButton(self.sidebar_frame, text="Attendance",
                                                        command=self.attendance_button_event)
        self.sidebar_button_2.grid(row=5, column=0, padx=20, pady=10)
        self.sidebar_button_3 = customtkinter.CTkButton(self.sidebar_frame, text="Setup",
                                                        command=self.setup_button_event)
        self.sidebar_button_3.grid(row=6, column=0, padx=20, pady=10)
        self.appearance_mode_label = customtkinter.CTkLabel(self.sidebar_frame, text="Appearance Mode:", anchor="w")
        self.appearance_mode_label.grid(row=9, column=0, padx=20, pady=(10, 0))
        self.appearance_mode_optionmenu = customtkinter.CTkOptionMenu(self.sidebar_frame,
                                                                      values=["Light", "Dark", "System"],
                                                                      command=self.change_appearance_mode_event)
        self.appearance_mode_optionmenu.grid(row=9, column=0, padx=20, pady=(10, 10))
        self.scaling_label = customtkinter.CTkLabel(self.sidebar_frame, text="UI Scaling:", anchor="w")
        self.scaling_label.grid(row=10, column=0, padx=20, pady=(10, 0))
        self.scaling_optionmenu = customtkinter.CTkOptionMenu(self.sidebar_frame, values=["100%"],
                                                              command=self.change_scaling_event)
        self.scaling_optionmenu.grid(row=11, column=0, padx=20, pady=(10, 20))
        # Name label #
        self.label_frame = customtkinter.CTkFrame(self, width=150, corner_radius=0)
        self.label_frame.grid(row=0, column=1, sticky="n")
        self.main_label = customtkinter.CTkLabel(self.label_frame, text="PresenceProctor Dashboard",
                                                 font=customtkinter.CTkFont(size=20, weight="bold"))
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

        # Upload Image Button
        self.uploadImageButton = customtkinter.CTkButton(self.studentSetupSection, text="Upload Image",
                                                         command=self.upload_student_image)
        self.uploadImageButton.grid(row=7, column=0, padx=entry_padx, pady=(entry_pady, 20), sticky="ew")

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

        # if light then black image
        # else light image

    def change_scaling_event(self, new_scaling: str):
        new_scaling_float = int(new_scaling.replace("%", "")) / 100
        customtkinter.set_widget_scaling(new_scaling_float)

    def home_button_event(self):
        self.attendanceFrame.grid_forget()
        self.setupFrame.grid_forget()
        self.homeFrame.grid(row=0, column=1, rowspan=4, sticky="nsew")
        self.load_attendance_data_and_draw_graph()



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
        last_name = self.lastNameEntry.get().strip()
        email = self.emailEntry.get().strip()
        gender = self.genderVar.get()

        # First check if an image has been uploaded
        if not hasattr(self, 'student_image_path'):
            self.error_message.set("Please upload an image for the student.")
            return

        # Continue with validation for the rest of the form
        if not first_name or len(first_name) < 2 or not first_name[0].isupper():
            self.error_message.set(
                "First Name : Invalid First Name\n First Name : Capitalize first letter\n First Name : Minimum length: 2")
            self.firstNameEntry.delete(0, tkinter.END)  # Clear the entry field
            return

        if not last_name or len(last_name) < 2 or not last_name[0].isupper():
            self.error_message.set(
                "Last Name : Invalid Last Name\n Last Name : Capitalize first letter\n Last Name : Minimum length: 2")
            self.lastNameEntry.delete(0, tkinter.END)  # Clear the entry field
            return

        if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            self.error_message.set("Invalid email address.\nOr left blank")
            self.emailEntry.delete(0, tkinter.END)  # Clear the entry field
            return

        # Check for duplicate entries
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
            pass  # If the file doesn't exist yet, no need to check for duplicates

        # No duplicate found, append the new data to the CSV file
        try:
            with open('student_data.csv', 'a', newline='') as file:
                fieldnames = ['First Name', 'Last Name', 'Gender', 'Email', 'Presence']
                writer = csv.DictWriter(file, fieldnames=fieldnames)
                if file.tell() == 0:
                    writer.writeheader()
                writer.writerow({'First Name': first_name, 'Last Name': last_name, 'Gender': gender, 'Email': email,
                                 'Presence': "Absent"})
                self.error_message.set("Student information successfully added.")
        except Exception as e:
            self.error_message.set(f"An error occurred while writing to the file: {e}")
            return

        # Clear the stored image path after successful submission
        del self.student_image_path

        # Clear all fields after successful submission or error
        self.firstNameEntry.delete(0, tkinter.END)
        self.lastNameEntry.delete(0, tkinter.END)
        self.emailEntry.delete(0, tkinter.END)
        self.genderVar.set("M")
        self.load_data()

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
            # Get the selected item's information
            item = self.tree.item(selected[0])
            values = item['values']

            # Create a popup dialog
            self.edit_window = customtkinter.CTkToplevel(self)
            self.edit_window.title("Edit Student")
            self.edit_window.geometry("300x300")
            self.edit_window.configure(bg="#333333")

            # Define local method for closing the dialog
            def close_edit_dialog():
                self.edit_window.destroy()

            # Define local method to save changes
            def save_changes():
                # Perform validation for each field
                first_name = self.firstNameEditEntry.get().strip()
                last_name = self.lastNameEditEntry.get().strip()
                email = self.emailEditEntry.get().strip()
                gender = self.genderEditVar.get()

                if not first_name or len(first_name) < 2 or not first_name[0].isupper():
                    tkinter.messagebox.showerror("Error", "Please enter a valid first name.")
                    return

                if not last_name or len(last_name) < 2 or not last_name[0].isupper():
                    tkinter.messagebox.showerror("Error", "Please enter a valid last name.")
                    return

                if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
                    tkinter.messagebox.showerror("Error", "Please enter a valid email address.")
                    return

                # Check for duplicate entries in the CSV file
                with open('student_data.csv', 'r', newline='') as file:
                    reader = csv.DictReader(file)
                    for row in reader:
                        if row['Email'].strip().lower() == email.lower() and row['Email'] != values[3]:
                            tkinter.messagebox.showerror("Error", "This email is already used by another student.")
                            return

                # Update the CSV file
                new_data = []
                with open('student_data.csv', 'r', newline='') as file:
                    reader = csv.DictReader(file)
                    for row in reader:
                        if row['Email'] == values[3]:
                            row['First Name'] = first_name
                            row['Last Name'] = last_name
                            row['Gender'] = gender
                            row['Email'] = email
                        new_data.append(row)

                with open('student_data.csv', 'w', newline='') as file:
                    writer = csv.DictWriter(file, fieldnames=['First Name', 'Last Name', 'Gender', 'Email', 'Presence'])
                    writer.writeheader()
                    writer.writerows(new_data)

                # Close the edit window
                close_edit_dialog()

                # Reload data in the treeview
                self.load_data()

            # Set up the entry fields and radio buttons
            self.firstNameEditEntry = customtkinter.CTkEntry(self.edit_window, placeholder_text="First Name")
            self.firstNameEditEntry.insert(0, values[0])
            self.firstNameEditEntry.pack(pady=10)

            self.lastNameEditEntry = customtkinter.CTkEntry(self.edit_window, placeholder_text="Last Name")
            self.lastNameEditEntry.insert(0, values[1])
            self.lastNameEditEntry.pack(pady=10)

            self.emailEditEntry = customtkinter.CTkEntry(self.edit_window, placeholder_text="Email")
            self.emailEditEntry.insert(0, values[3])
            self.emailEditEntry.pack(pady=10)

            self.genderEditVar = tkinter.StringVar(value=values[2])
            self.maleEditRadioButton = customtkinter.CTkRadioButton(self.edit_window, text="Male",
                                                                    variable=self.genderEditVar, value="M")
            self.maleEditRadioButton.pack(pady=2)
            self.femaleEditRadioButton = customtkinter.CTkRadioButton(self.edit_window, text="Female",
                                                                      variable=self.genderEditVar, value="F")
            self.femaleEditRadioButton.pack(pady=2)

            # Save Changes Button
            self.saveChangesButton = customtkinter.CTkButton(self.edit_window, text="Save Changes",
                                                             command=save_changes)
            self.saveChangesButton.pack(pady=20)

            # Cancel Button
            self.cancelButton = customtkinter.CTkButton(self.edit_window, text="Cancel", command=close_edit_dialog)
            self.cancelButton.pack(pady=20)
        else:
            tkinter.messagebox.showinfo("Edit", "Please select a student to edit.")


    def delete_student(self):
        selected = self.tree.selection()
        if selected:
            item = self.tree.item(selected[0])
            values = item['values']
            # Confirm deletion
            response = tkinter.messagebox.askyesno("Delete", "Are you sure you want to delete this student?")
            if response:
                # Formulate the expected image filename based on the student's first and last name
                image_filename = f"{values[0]}_{values[1]}.jpg"
                image_path = os.path.join(os.getcwd(), "images_data", image_filename)
                try:
                    # Attempt to delete the image file
                    if os.path.exists(image_path):
                        os.remove(image_path)
                    else:
                        print("Image file not found. It may have already been deleted.")
                except Exception as e:
                    print(f"An error occurred while deleting the image file: {e}")

                # Read all data excluding the selected row
                new_data = []
                with open('student_data.csv', 'r', newline='') as file:
                    reader = csv.DictReader(file)
                    for row in reader:
                        if row['Email'] != values[3]:
                            new_data.append(row)

                # Write the data back to the CSV, excluding the selected student
                with open('student_data.csv', 'w', newline='') as file:
                    writer = csv.DictWriter(file, fieldnames=['First Name', 'Last Name', 'Gender', 'Email', 'Presence'])
                    writer.writeheader()
                    writer.writerows(new_data)

                # Reload data in the treeview
                self.load_data()
                tkinter.messagebox.showinfo("Success", "Student and their image have been successfully deleted.")
        else:
            tkinter.messagebox.showinfo("Delete", "Please select a student to delete.")

    def upload_student_image(self):
        # Open a dialog to select an image file
        file_path = filedialog.askopenfilename(filetypes=[("Image files", "*.jpg *.jpeg *.png")])
        if file_path:
            first_name = self.firstNameEntry.get().strip().capitalize()
            last_name = self.lastNameEntry.get().strip().capitalize()

            if not (first_name and last_name):
                tkinter.messagebox.showerror("Error", "Please enter the first and last name before uploading an image.")
                return

            # Rename the image and save it to the images_data directory
            new_filename = f"{first_name}_{last_name}.jpg"
            image_directory = os.path.join(os.getcwd(), "images_data")
            if not os.path.exists(image_directory):
                os.makedirs(image_directory)

            new_file_path = os.path.join(image_directory, new_filename)
            copyfile(file_path, new_file_path)

            # Store the path or just the filename depending on your needs
            self.student_image_path = new_file_path  # or just `new_filename`

            tkinter.messagebox.showinfo("Success", "Image uploaded successfully.")

    def setup_reset_attendance_section(self):
        # Create the reset frame and place it on the left side
        self.resetFrame = customtkinter.CTkFrame(self.attendanceFrame, corner_radius=10)
        self.resetFrame.grid(row=1, column=0, padx=100, pady=30, sticky="nw")

        # Configure the inner grid of the resetFrame
        self.resetFrame.grid_columnconfigure(0, weight=1)
        self.resetFrame.grid_rowconfigure(0, weight=1)
        self.resetFrame.grid_rowconfigure(1, weight=1)
        self.resetFrame.grid_rowconfigure(2, weight=1)
        self.resetFrame.grid_rowconfigure(3, weight=1)
        self.resetFrame.grid_rowconfigure(4, weight=1)

        # Add subtitle label
        self.resetSubtitleLabel = customtkinter.CTkLabel(self.resetFrame, text="Reset Today's Attendance",
                                                         font=customtkinter.CTkFont(size=16))
        self.resetSubtitleLabel.grid(row=0, column=0, padx=10, pady=10)

        # Add 'Teacher control only' label
        self.teacherControlLabel = customtkinter.CTkLabel(self.resetFrame, text="Teacher Control Only",
                                                          font=customtkinter.CTkFont(size=12))
        self.teacherControlLabel.grid(row=1, column=0, padx=10)

        # Add entry for username
        self.usernameEntry = customtkinter.CTkEntry(self.resetFrame, placeholder_text="Username")
        self.usernameEntry.grid(row=2, column=0, padx=50, pady=10)  # Changed sticky from "ew" to default

        # Add entry for password
        self.passwordEntry = customtkinter.CTkEntry(self.resetFrame, placeholder_text="Password", show="*")
        self.passwordEntry.grid(row=3, column=0, padx=50, pady=10)  # Changed sticky from "ew" to default

        # Add reset button
        self.resetButton = customtkinter.CTkButton(self.resetFrame, text="Reset Attendance",
                                                   command=self.reset_attendance)
        self.resetButton.grid(row=4, column=0, padx=10, pady=10)




        self.attendanceLabel.grid(row=0, column=0, columnspan=3, sticky="new", padx=20, pady=(10, 20))

    def reset_attendance(self):
        username = self.usernameEntry.get()
        password = self.passwordEntry.get()

        # Check if the provided username and password are correct
        if username == 'username' and password == 'password':
            try:
                # Read the data from the CSV
                with open('student_data.csv', 'r', newline='') as file:
                    reader = csv.DictReader(file)
                    students = list(reader)

                # Reset the Presence field for all students to 'Absent'
                for student in students:
                    student['Presence'] = 'Absent'

                # Write the updated data back to the CSV
                with open('student_data.csv', 'w', newline='') as file:
                    writer = csv.DictWriter(file, fieldnames=reader.fieldnames)
                    writer.writeheader()
                    writer.writerows(students)

                tkinter.messagebox.showinfo("Reset Attendance", "All attendance has been reset to 'Absent'.")
            except FileNotFoundError:
                tkinter.messagebox.showerror("Error", "The student data file does not exist.")
        else:
            tkinter.messagebox.showerror("Access Denied", "The username or password is incorrect.")

    def attendance_button_event(self):
        # Clear any previous widgets in the frame
        for widget in self.attendanceFrame.winfo_children():
            widget.destroy()

        # Make the attendance frame visible and configure grid
        self.homeFrame.grid_forget()
        self.setupFrame.grid_forget()
        self.attendanceFrame.grid(row=0, column=1, rowspan=4, sticky="nsew")

        # Configure columns and rows
        self.attendanceFrame.grid_columnconfigure(0, weight=1)
        self.attendanceFrame.grid_columnconfigure(1, weight=0)
        self.attendanceFrame.grid_columnconfigure(2, weight=1)
        self.attendanceFrame.grid_rowconfigure(0, weight=0)
        self.attendanceFrame.grid_rowconfigure(1, weight=1)

        # Title Label
        self.attendanceLabel = customtkinter.CTkLabel(
            self.attendanceFrame,
            text="Take Attendance",
            font=customtkinter.CTkFont(size=60, weight="bold"),
            text_color='white'
        )
        self.attendanceLabel.grid(row=0, column=1, sticky="nsew", padx=20, pady=(10, 20))

        # Attendance Section Frame
        self.takeAttendanceSection = customtkinter.CTkFrame(self.attendanceFrame, corner_radius=10)
        self.takeAttendanceSection.grid(row=1, column=0, padx=20, pady=20, sticky="ne")
        # Instruction Label
        self.instructionLabel = customtkinter.CTkLabel(
            self.takeAttendanceSection,
            text="Enter first and last name, then press the button and keep your face clear in front of the webcam to detect and mark you present.",
            font=customtkinter.CTkFont(size=17),  # Adjusted for readability
            fg_color=None,
            text_color='white',
            wraplength=500  # Adjusted to wrap the text
        )
        self.instructionLabel.grid(row=1, column=0, sticky="ew", padx=20, pady=(25, 50))

        # First Name Entry
        self.firstNameEntry = customtkinter.CTkEntry(self.takeAttendanceSection, placeholder_text="First Name")
        self.firstNameEntry.grid(row=2, column=0, sticky="ew", padx=20, pady=(0, 10))

        # Last Name Entry
        self.lastNameEntry = customtkinter.CTkEntry(self.takeAttendanceSection, placeholder_text="Last Name")
        self.lastNameEntry.grid(row=3, column=0, sticky="ew", padx=20, pady=(0, 10))

        # Take Attendance Button
        self.takeAttendanceButton = customtkinter.CTkButton(
            self.takeAttendanceSection,
            text="Take Attendance",
            command=self.take_attendance  # Assuming there's a method defined to handle the attendance taking process
        )
        self.takeAttendanceButton.grid(row=4, column=0, sticky="ew", padx=20, pady=(0, 20))
        # Call to create the attendance table
        self.create_attendance_table()
        # Reset Section
        self.setup_reset_attendance_section()

    def take_attendance(self):
        first_name = self.firstNameEntry.get().strip().capitalize()
        last_name = self.lastNameEntry.get().strip().capitalize()

        if not first_name or not last_name:

            tkinter.messagebox.showinfo("Error", "Please enter both first and last names.")

            return

        # Locate the student in the CSV file
        found = False
        student_image_path = None
        with open('student_data.csv', 'r', newline='') as file:
            reader = csv.DictReader(file)
            for row in reader:
                if row['First Name'].capitalize() == first_name and row['Last Name'].capitalize() == last_name:
                    found = True
                    student_image_path = os.path.join(os.getcwd(), "images_data", f"{first_name}_{last_name}.jpg")
                    break

        if not found:
            # customtkinter.CTkMessageBox.show_error("Error", "Student not found in the database.")
            tkinter.messagebox.showinfo("Error", "Student not found in the database.")
            return

        # Face detection
        if student_image_path and detect_face_in_video(student_image_path):
            # Update CSV to mark student as present
            new_data = []
            with open('student_data.csv', 'r', newline='') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    if row['First Name'] == first_name and row['Last Name'] == last_name:
                        row['Presence'] = 'Present'
                    new_data.append(row)

            with open('student_data.csv', 'w', newline='') as file:
                fieldnames = ['First Name', 'Last Name', 'Gender', 'Email', 'Presence']
                writer = csv.DictWriter(file, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(new_data)


            speak(f"Success! Student found, welcome {first_name} {last_name}!")
            #tkinter.messagebox.showinfo("Success", f"Student found, welcome {first_name} {last_name}!")

        else:
            tkinter.messagebox.showinfo("Error", "Student not detected. Please try again.")
            #customtkinter.CTkMessageBox.show_error("Error", "Student not detected. Please try again.")

    def toggle_fullscreen(self, event=None):
        # This method toggles the fullscreen state
        self.is_fullscreen = not self.is_fullscreen  # Just toggling the boolean
        self.attributes("-fullscreen", self.is_fullscreen)

    def create_attendance_table(self):
        # Define Treeview for the attendance list
        self.attendance_tree = ttk.Treeview(self.attendanceFrame, columns=("First Name", "Last Name", "Presence"),
                                            height=10, show='headings')
        self.attendance_tree.heading("First Name", text="First Name")
        self.attendance_tree.heading("Last Name", text="Last Name")
        self.attendance_tree.heading("Presence", text="Presence")
        self.attendance_tree['selectmode'] = 'none'  # Disables selecting rows

        # Define columns width and alignment
        self.attendance_tree.column("First Name", anchor="center", width=100)
        self.attendance_tree.column("Last Name", anchor="center", width=100)
        self.attendance_tree.column("Presence", anchor="center", width=100)

        # Scrollbar for the Treeview
        scrollbar = ttk.Scrollbar(self.attendanceFrame, orient="vertical", command=self.attendance_tree.yview)
        self.attendance_tree.configure(yscrollcommand=scrollbar.set)

        # Position the Treeview and scrollbar
        self.attendance_tree.grid(row=2, column=0, sticky="nsew", padx=(20, 0))
        scrollbar.grid(row=2, column=1, sticky='nsew')

        # Load the attendance data
        self.load_attendance_data()

        # Assuming your table was originally at row=2, you want to move it to row=1
        self.attendance_tree.grid(row=1, column=0, sticky="nsew", padx=(100, 0), pady=(400, 0))  # Add some top padding
        scrollbar.grid(row=1, column=1, sticky='nsew', pady=(400, 0))  # Match the padding for the scrollbar

        # Make sure to configure the grid weights accordingly
        self.attendanceFrame.grid_rowconfigure(1, weight=0)  # This row will have the table, no stretching
        self.attendanceFrame.grid_rowconfigure(2, weight=1)  # The next row should stretch to fill space

    def load_attendance_data(self):
        # Load the attendance data from the CSV and sort it
        try:
            with open('student_data.csv', 'r', newline='') as file:
                reader = csv.DictReader(file)
                # Sorting data by First Name alphabetically
                sorted_list = sorted(reader, key=lambda r: r['First Name'])
                for row in sorted_list:
                    presence = row.get('Presence', 'Absent')  # Assume absent if no presence info
                    self.attendance_tree.insert('', 'end', values=(row['First Name'], row['Last Name'], presence))
        except FileNotFoundError:
            # Handle the error or create a new file if necessary
            pass

    def load_attendance_data_and_draw_graph(self):
        # Load attendance data from CSV
        try:
            with open('student_data.csv', 'r', newline='') as file:
                reader = csv.DictReader(file)
                attendance_count = {'Present': 0, 'Absent': 0}
                for row in reader:
                    presence = row['Presence']
                    if presence == 'Present':
                        attendance_count['Present'] += 1
                    else:
                        attendance_count['Absent'] += 1
        except FileNotFoundError:
            tkinter.messagebox.showerror("Error", "The data file is missing.")
            return

        # Create the bar graph
        fig = Figure(figsize=(7, 6), dpi=100)
        fig.patch.set_facecolor('#333333')
        ax = fig.add_subplot(111)
        ax.set_facecolor('#333333')
        ax.bar(attendance_count.keys(), attendance_count.values(), color=['green', 'red'])
        ax.set_title("Today's Analysis", color='white')
        ax.set_xlabel('Status', color='white')
        ax.set_ylabel('Number of Students', color='white')
        ax.tick_params(colors='white')

        # Embed the graph in the tkinter window
        canvas = FigureCanvasTkAgg(fig, master=self.graph_frame)  # A tk.DrawingArea.
        canvas.draw()
        canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)



if __name__ == "__main__":
    app = App()
    app.mainloop()