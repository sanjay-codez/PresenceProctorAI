"""
This module imports the necessary libraries and sets up the graphical user interface (GUI) for a student attendance
system using tkinter and customtkinter libraries.
It provides functions and classes to manage attendance tracking, student setup, and system settings with features
such as face recognition, speech output, and data management via CSV files.
"""
import sys
# import necessary modules
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
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
import smtplib
from email.mime.text import MIMEText
import base64


customtkinter.set_appearance_mode("Dark")  # Modes: "System" (standard), "Dark", "Light"
customtkinter.set_default_color_theme("green")  # Themes: "blue" (standar d), "green", "dark-blue"
username = "Mr. Gilbert"

# speaking audio function cool
def speak(str1):
    """
        This function uses the SAPI.SpVoice interface from the Windows Speech API to convert text to speech.
        It speaks out loud the text passed to it.

        Args:
        str1 (str): The string of text that will be spoken by the system.

        Example:
        speak("Hello, world!")  # This will speak "Hello, world!" aloud.
    """
    spieak = Dispatch("SAPI.SpVoice")
    spieak.Speak(str1)

# call the function and returns MM/DD/YYYY
def get_current_date():
    """
        Fetches the current date from the World Time API in UTC timezone and returns it in 'mm/dd/yyyy' format.

        Returns:
            str: A string representing the current date in 'mm/dd/yyyy' format.

        Raises:
            Exception: If there is an issue with fetching the data from the World Time API.
    """
    response = requests.get('http://worldtimeapi.org/api/timezone/Etc/UTC')
    data = response.json()
    datetime_string = data['datetime']
    if datetime_string[-3] == ':':
        datetime_string = datetime_string
    else:
        datetime_string = datetime_string[:-2] + ':' + datetime_string[-2:]
    current_datetime = datetime.fromisoformat(datetime_string)
    return current_datetime.strftime('%m/%d/%Y')

def send_email(subject, body, to_email):

    sender_email = "presenceproctor@gmail.com"  # Your SendGrid verified sender email
    message = MIMEText(body)
    message['From'] = sender_email
    message['To'] = to_email
    message['Subject'] = subject

    server = smtplib.SMTP('smtp.sendgrid.net', 587)
    server.ehlo()
    server.starttls()
    server.ehlo()
    crow = None
    part_one = "SG."
    part_two = "mTWRYDhrRwCf1I0aPUta2w.uv_"
    part_three = "1YmmIIC8LSYP68-tSVuiGXkf81kHrt-Vr7N9Yo2M"
    api_key = part_one + part_two + part_three
    # with open('lol.txt') as file:
    #     encoded_api_key = file.read()
    #     crow = base64.b64decode(encoded_api_key.encode()).decode()



    server.login('apikey', api_key)
    server.sendmail(sender_email, to_email, message.as_string())
    server.quit()
    print("Email sent!")

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

        # configure window
        self.title("PresenceProctor")
        self.geometry(f"{1920}x{1080}")

        # configure grid layout (4x4)
        self.grid_columnconfigure(1, weight=1)
        self.grid_columnconfigure((2, 3), weight=0)
        self.grid_rowconfigure((0, 1, 2), weight=1)

        # start of home tab
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

        # end of home frame

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

        self.sidebar_button_4 = customtkinter.CTkButton(self.sidebar_frame, text="Send Emails\n   to    \nAbsent Students",
                                                        command=self.send_emails_to_absent_students)
        self.sidebar_button_3.grid(row=6, column=0, padx=20, pady=10)
        self.sidebar_button_4.grid(row=7, column=0, padx=20, pady=10)
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
        # end of home tab

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

        # start of attendance frame
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
        # end of attendance frame

        # start of step frame
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
        # end of setup frame

    def open_input_dialog_event(self):
        """
            Opens a custom input dialog using CTkInputDialog, prompts the user to type in a number,
            and prints the input value.

            This function creates a custom input dialog using the CTkInputDialog class from customtkinter module.
            The dialog prompts the user to enter a number. Once the user enters the number and confirms,
            the input value is retrieved using the `get_input()` method of the dialog instance.

            Returns:
                None

            Raises:
                No specific exceptions are raised by this function. However, it relies on the behavior
                of the CTkInputDialog class from customtkinter module. If there are any issues with
                creating or interacting with the dialog, they might be raised within the customtkinter module.

            Note:
                The customtkinter module containing CTkInputDialog class must be imported prior to calling this function.
        """
        dialog = customtkinter.CTkInputDialog(text="Type in a number:", title="CTkInputDialog")
        print("CTkInputDialog:", dialog.get_input())

    def change_appearance_mode_event(self, new_appearance_mode: str):
        """
            Changes the appearance mode of the application using customtkinter module.

            Args:
                new_appearance_mode (str): The new appearance mode to set for the application.
                    It should be one of the supported appearance modes provided by customtkinter module.

            Returns:
                None

            Raises:
                No specific exceptions are raised by this function. However, it relies on the behavior
                of the customtkinter module. If there are any issues with setting the appearance mode,
                they might be raised within the customtkinter module.

            Note:
                The customtkinter module containing set_appearance_mode() function must be imported prior to calling this function.
        """
        customtkinter.set_appearance_mode(new_appearance_mode)



    def change_scaling_event(self, new_scaling: str):
        """
            Changes the scaling factor of widgets in the application using customtkinter module.

            Args:
                new_scaling (str): The new scaling factor to set for the widgets in the application.
                    It should be in percentage format (e.g., '100%', '80%', etc.).

            Returns:
                None

            Raises:
                ValueError: If the provided scaling factor is not in the correct format or cannot be converted to a float.
                No specific exceptions are raised by this function. However, it relies on the behavior
                of the customtkinter module. If there are any issues with setting the widget scaling,
                they might be raised within the customtkinter module.

            Note:
                The customtkinter module containing set_widget_scaling() function must be imported prior to calling this function.
        """
        new_scaling_float = int(new_scaling.replace("%", "")) / 100
        customtkinter.set_widget_scaling(new_scaling_float)

    def home_button_event(self):
        """
            Switches the application to the home frame, hiding other frames if necessary, and loads attendance data.

            This function hides the attendance frame and setup frame by calling the `grid_forget()` method on them,
            and displays the home frame by placing it in the grid layout. Additionally, it triggers the loading of
            attendance data and drawing of a graph in the home frame.

            Returns:
                None

            Note:
                This function assumes the existence of 'attendanceFrame', 'setupFrame', and 'homeFrame' attributes
                in the class instance representing the frames in the application layout. Additionally, it relies
                on the 'load_attendance_data_and_draw_graph()' method to load attendance data and draw a graph,
                which should be defined in the class.

            Example:
                To use this function, call it when the home button is clicked in your application interface.
                For example:
                    my_app.home_button_event()
        """
        self.attendanceFrame.grid_forget()
        self.setupFrame.grid_forget()
        self.homeFrame.grid(row=0, column=1, rowspan=4, sticky="nsew")
        self.load_attendance_data_and_draw_graph()



    def setup_button_event(self):
        """
            Switches the application to the setup frame, hiding other frames if necessary, and sets up the student table.

            This function hides the home frame and attendance frame by calling the `grid_forget()` method on them,
            and displays the setup frame by placing it in the grid layout. Additionally, it triggers the creation
            of a student table and setup of table buttons (e.g., edit and delete) when the setup tab is shown.

            Returns:
                None

            Note:
                This function assumes the existence of 'homeFrame', 'attendanceFrame', and 'setupFrame' attributes
                in the class instance representing the frames in the application layout. Additionally, it relies
                on the 'create_student_table()' and 'setup_table_buttons()' methods to create the student table
                and setup table buttons, which should be defined in the class.
        """
        # Hide the other frames
        self.homeFrame.grid_forget()
        self.attendanceFrame.grid_forget()
        # Show the setup frame
        self.setupFrame.grid(row=0, column=1, rowspan=4, sticky="nsew")
        self.create_student_table()
        self.setup_table_buttons()  # Create edit and delete buttons when setup tab is shown

    def upload_student_image(self):
        """
                Temporarily stores a student image path selected by the user.

                This function opens a file dialog to allow the user to select an image file, storing the path
                temporarily in 'temp_student_image_path'. The image is not saved to 'images_data' until the student
                information is submitted successfully.

                Returns:
                    None
        """
        # Open a dialog to select an image file
        file_path = filedialog.askopenfilename(filetypes=[("Image files", "*.jpg *.jpeg *.png")])
        if file_path:
            # Temporarily store the file path
            self.temp_student_image_path = file_path
            tkinter.messagebox.showinfo("Image Selected",
                                        "Image selected successfully.\nYou can change the image before final submission.")

    def submit_student_info(self):
        """
                Validates and submits student information along with the student's image to the permanent directory.

                This function performs validation checks on the entered student information and the temporary image.
                After successful submission, it moves the image from temporary storage to the permanent 'images_data' directory,
                clears all entry fields, and displays a success message. In case of errors, it displays an appropriate error message.

                Returns:
                    None
        """

        # Validation for First and Last Name
        first_name = self.firstNameEntry.get().strip()
        last_name = self.lastNameEntry.get().strip()
        email = self.emailEntry.get().strip()
        gender = self.genderVar.get()

        # Check if an image has been temporarily selected
        if not hasattr(self, 'temp_student_image_path'):
            self.error_message.set("Please select an image for the student.")
            return

        # Validation for the rest of the form
        if not first_name or len(first_name) < 2 or not first_name[0].isupper():
            self.error_message.set("Invalid First Name. Ensure it is capitalized and at least 2 characters long.")
            return

        if not last_name or len(last_name) < 2 or not last_name[0].isupper():
            self.error_message.set("Invalid Last Name. Ensure it is capitalized and at least 2 characters long.")
            return

        if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            self.error_message.set("Invalid email address.")
            return

        # Check for duplicate entries
        try:
            with open('student_data.csv', 'r', newline='') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    if (row['First Name'].strip().lower() == first_name.lower() and row['Last Name'].strip().lower() == last_name.lower()) or row['Email'].strip().lower() == email.lower():
                        self.error_message.set("Duplicate entry detected. Either the name or the email is already used.")
                        return

        except FileNotFoundError:
            pass  # If the file doesn't exist yet, no need to check for duplicates


        # Append the new data to the CSV file and move the image to the permanent directory
        try:
            with open('student_data.csv', 'a', newline='') as file:
                fieldnames = ['First Name', 'Last Name', 'Gender', 'Email', 'Presence']
                writer = csv.DictWriter(file, fieldnames=fieldnames)
                if file.tell() == 0:
                    writer.writeheader()
                writer.writerow(
                    {'First Name': first_name, 'Last Name': last_name, 'Gender': gender, 'Email': email, 'Presence': "Present"})

            # Move the image to the permanent directory
            new_filename = f"{first_name}_{last_name}.jpg"
            image_directory = os.path.join(os.getcwd(), "images_data")
            if not os.path.exists(image_directory):
                os.makedirs(image_directory)
            new_file_path = os.path.join(image_directory, new_filename)
            copyfile(self.temp_student_image_path, new_file_path)

            self.error_message.set("Student information and image successfully added.")
        except Exception as e:
            self.error_message.set(f"An error occurred: {e}")
            return

        # Clear all fields and temporary image path after successful submission
        self.firstNameEntry.delete(0, tkinter.END)
        self.lastNameEntry.delete(0, tkinter.END)
        self.emailEntry.delete(0, tkinter.END)
        self.genderVar.set("M")
        del self.temp_student_image_path
        self.load_data()


    def create_student_table(self):
        """
            Creates a table to display student information in the setup frame.

            This function creates a table using the Treeview widget to display student information, including
            first name, last name, gender, and email. It also configures a scrollbar for scrolling through
            the table entries. Additionally, it configures the grid layout for proper placement of the table
            and scrollbar within the setup frame. Finally, it calls the 'load_data()' method to populate
            the table with student data.

            Returns:
                None

            Note:
                This function assumes the existence of a 'setupFrame' attribute in the class instance representing
                the setup frame in the application layout. Additionally, it relies on the 'load_data()' method
                to populate the table with student data.

            Example:
                To use this function, call it when setting up the student table in your application interface.
                For example:
                    my_app.create_student_table()
        """
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
        """
            Loads student data from the CSV file and populates the student table.

            This function reads student data from the CSV file ('student_data.csv') and inserts it into the
            student table (referenced as 'tree' attribute in the class instance) using the Treeview widget.
            It clears the current items in the table before inserting new data. After loading data, it calls
            the 'setup_table_buttons()' method to set up buttons for editing and deleting student records.

            Returns:
                None

            Note:
                This function assumes the existence of a 'tree' attribute in the class instance representing
                the student table. Additionally, it relies on the 'setup_table_buttons()' method to set up
                table buttons after loading data.

            Example:
                To use this function, call it when loading student data in your application interface.
                For example:
                    my_app.load_data()

        """
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
        """
            Sets up buttons for editing and deleting student records in the setup frame.

            This function creates and places 'Edit' and 'Delete' buttons in the setup frame (referenced as
            'setupFrame' attribute in the class instance) using the custom button widget. It adjusts the
            grid layout to align the buttons properly. If buttons from previous calls exist, they are
            destroyed before creating new ones.

            Returns:
                None

            Note:
                This function assumes the existence of 'edit_button' and 'delete_button' attributes in the
                class instance representing the buttons. Additionally, it relies on the 'edit_student()'
                and 'delete_student()' methods to handle button click events.

            Example:
                To use this function, call it when setting up buttons for editing and deleting student
                records in your application interface.
                For example:
                    my_app.setup_table_buttons()
        """
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
        """
            Allows editing of selected student information.

            This function enables editing of the selected student's information from the student table.
            It retrieves the selected item's information from the table, creates a popup dialog for editing,
            and provides entry fields for modifying the first name, last name, email, and gender. It performs
            validation for each field before saving changes to the CSV file ('student_data.csv'). Duplicate
            email validation is also performed to ensure uniqueness. After saving changes, it closes the edit
            window and reloads data in the student table.

            Returns:
                None

            Note:
                This function assumes the existence of entry fields and radio buttons for editing student
                information (referenced as 'firstNameEditEntry', 'lastNameEditEntry', 'emailEditEntry',
                'genderEditVar', 'maleEditRadioButton', and 'femaleEditRadioButton' attributes in the class
                instance). Additionally, it relies on the 'load_data()' method to reload data in the student
                table after saving changes.

            Example:
                To use this function, call it when editing a student's information in your application interface.
                For example:
                    my_app.edit_student()

        """
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
        """
            Deletes the selected student from the student table and CSV data.

            This function deletes the selected student from the student table and CSV data file
            ('student_data.csv'). It first confirms the deletion with a dialog box. If confirmed,
            it attempts to delete the student's associated image file from the 'images_data' directory.
            After successful deletion of the image file, it removes the student's data from the CSV
            file and reloads data in the student table. A success message is displayed upon successful
            deletion.

            Returns:
                None

            Note:
                This function assumes the existence of a 'tree' attribute in the class instance
                representing the student table. Additionally, it relies on the 'load_data()' method
                to reload data in the student table after deletion.

            Example:
                To use this function, call it when deleting a student's information in your application
                interface. For example:
                    my_app.delete_student()

        """
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



    def setup_reset_attendance_section(self):
        """
            Sets up the reset attendance section in the attendance frame.

            This function creates a frame for resetting today's attendance and places it on the left side
            of the attendance frame. It configures the inner grid of the reset frame and adds labels,
            entry fields for username and password, and a reset button. Additionally, it sets up the
            attendance label.

            Returns:
                None

            Note:
                This function assumes the existence of a 'resetFrame' attribute in the class instance
                representing the reset frame in the attendance layout. Additionally, it relies on the
                'reset_attendance()' method to handle the reset attendance functionality.

            Example:
                To use this function, call it when setting up the reset attendance section in your
                application interface. For example:
                    my_app.setup_reset_attendance_section()

        """
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
        """
            Resets today's attendance to 'Absent' for all students.

            This function prompts the user to enter a username and password for authentication.
            If the provided credentials are correct, it resets the attendance for all students
            to 'Absent' in the CSV file ('student_data.csv'). A success message is displayed
            upon successful reset.

            Returns:
                None

            Note:
                This function assumes the existence of entry fields for username and password
                (referenced as 'usernameEntry' and 'passwordEntry' attributes in the class instance).

            Example:
                To use this function, call it when resetting attendance in your application interface.
                For example:
                    my_app.reset_attendance()

        """
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
        """
            Event handler for the attendance button.

            This function clears any previous widgets in the attendance frame, makes the attendance
            frame visible, configures the grid layout, sets up the attendance label, and calls methods
            to create the attendance table and set up the reset attendance section.

            Returns:
                None

            Note:
                This function assumes the existence of the attendance frame (referenced as 'attendanceFrame'
                attribute in the class instance) and methods to create the attendance table and set up
                the reset attendance section.

            Example:
                To use this function, call it when handling the attendance button event in your application
                interface. For example:
                    my_app.attendance_button_event()

        """
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
        """
            Takes attendance for the entered student.

            This function retrieves the entered first and last names of the student, locates the student
            in the CSV file, performs face detection using the student's image, and marks the student
            as 'Present' in the CSV file if the face is detected. A success message is displayed upon
            successful attendance marking.

            Returns:
                None

            Note:
                This function assumes the existence of entry fields for first name and last name
                (referenced as 'firstNameEntry' and 'lastNameEntry' attributes in the class instance).
                Additionally, it relies on the 'detect_face_in_video()' function for face detection
                and the 'speak()' function for speech output.

            Example:
                To use this function, call it when taking attendance in your application interface.
                For example:
                    my_app.take_attendance()

            """
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
        """
            Toggles the fullscreen mode of the application window.

            This method toggles the fullscreen state of the application window by setting or removing
            the '-fullscreen' attribute. It updates the 'is_fullscreen' attribute accordingly.

            Args:
                event (Optional): Event object triggering the toggle. Defaults to None.

            Returns:
                None

            Example:
                To use this method, bind it to a key event or button click in your application interface.
                For example:
                    my_app.bind("<F11>", my_app.toggle_fullscreen)
                    my_app.bind("<Escape>", my_app.toggle_fullscreen)

        """
        # This method toggles the fullscreen state
        self.is_fullscreen = not self.is_fullscreen  # Just toggling the boolean
        self.attributes("-fullscreen", self.is_fullscreen)

    def create_attendance_table(self):
        """
            Creates and populates the attendance table.

            This method defines a Treeview widget for displaying the attendance list in the attendance frame.
            It sets up columns for 'First Name', 'Last Name', and 'Presence', configures column width and alignment,
            adds a scrollbar for the Treeview, positions the Treeview and scrollbar in the frame, loads attendance
            data from the CSV file, sorts it alphabetically by first name, and inserts data into the Treeview.

            Returns:
                None

            Note:
                This method assumes the existence of an attendance frame (referenced as 'attendanceFrame' attribute
                in the class instance) and a CSV file named 'student_data.csv' containing attendance data.

            Example:
                To use this method, call it when initializing the attendance section in your application interface.
                For example:
                    my_app.create_attendance_table()

        """
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
        """
            Loads attendance data from the CSV file and populates the attendance table.

            This method attempts to load attendance data from the 'student_data.csv' file, sorts it alphabetically
            by first name, and inserts the data into the attendance table. If the CSV file is not found, it handles
            the error gracefully.

            Returns:
                None

            Note:
                This method assumes the existence of a Treeview widget (referenced as 'attendance_tree' attribute
                in the class instance) for displaying the attendance table.

            Example:
                To use this method, call it when loading attendance data in your application interface.
                For example:
                    my_app.load_attendance_data()

        """
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
        """
            Loads attendance data from the CSV file and draws a bar graph based on the attendance.

            This method first clears any previous graph displayed on the canvas. Then, it loads attendance
            data from the 'student_data.csv' file, counts the number of students marked as 'Present' and 'Absent',
            and creates a bar graph to represent the attendance analysis. The graph is embedded into the tkinter
            window for display.

            Returns:
                None

            Note:
                This method assumes the existence of a graph frame (referenced as 'graph_frame' attribute
                in the class instance) and a CSV file named 'student_data.csv' containing attendance data.

            Example:
                To use this method, call it when loading attendance data and drawing the graph in your application
                interface. For example:
                    my_app.load_attendance_data_and_draw_graph()

        """
        # Clear previous graph
        self.canvas.get_tk_widget().forget() if hasattr(self, 'canvas') else None

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
        self.canvas = FigureCanvasTkAgg(fig, master=self.graph_frame)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)

    def send_emails_to_absent_students(self):

        filename = 'student_data.csv'
        try:
            with open(filename, newline='') as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:
                    if row['Presence'] == 'Absent':
                        first_name = row['First Name']
                        last_name = row['Last Name']
                        email = row['Email']
                        teacher_name = username  # Use the teacher's name from the class variable
                        subject = "Attendance Alert: Absence Notification"
                        body = (
                            f"Hello {first_name} {last_name},\n\n"
                            "Your absence was recorded in our recent session. "
                            "As a reminder, consistent attendance is crucial to your academic success and understanding of the material. "
                            f"Please ensure to check with your teacher, {username}, to address this absence as soon as possible. "
                            "If you believe there has been a mistake, or if you were marked absent accidentally, "
                            f"please do not hesitate to reach out directly to {username} to clarify your attendance status. "
                            "\n\nThank you for your attention to this matter.\n\nRegards,\nPresenceProctor"
                        )
                        send_email(subject, body, email)


        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {e}")
            if 'reached the maximum amount' in str(e):
                messagebox.showerror("Error", "You have reached the maximum amount of emails per day.")

        messagebox.showinfo("Success!", "Emails have been sent!")


if __name__ == "__main__":
    app = App()
    app.mainloop()