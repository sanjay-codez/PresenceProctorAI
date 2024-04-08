import customtkinter
import tkinter

import customtkinter
from PIL import Image
import os
import subprocess
import sys

customtkinter.set_appearance_mode("dark")


#current_directory = os.path.dirname(os.path.abspath(__file__))
#parent_directory = os.path.dirname(current_directory)

class App(customtkinter.CTk):
    width = 500
    height = 720

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.title("CustomTkinter example_background_image.py")
        self.geometry(f"{self.width}x{self.height}")
        self.resizable(True,True)

        # load and create background image
        current_path = os.path.dirname(os.path.realpath(__file__))
        self.bg_image = customtkinter.CTkImage(Image.open(current_path + "/test_images/bg_gradient.jpg"),
                                               size=(self.width, self.height))
        self.bg_image_label = customtkinter.CTkLabel(self, image=self.bg_image)
        self.bg_image_label.grid(row=0, column=0)

        # create login frame
        self.login_frame = customtkinter.CTkFrame(self, corner_radius=0)
        self.login_frame.grid(row=0, column=0, sticky="ns")
        self.login_label = customtkinter.CTkLabel(self.login_frame, text="PresenseProctor AI\nLogin Page",
                                                  font=customtkinter.CTkFont(size=20, weight="bold"))
        self.login_label.grid(row=0, column=0, padx=30, pady=(150, 15))

        # create login label
        self.SignInLabel = customtkinter.CTkLabel(self.login_frame, text="",
                                                  font=customtkinter.CTkFont(size=10, weight="bold"))
        self.SignInLabel.grid(row=4, column=0, padx=30, pady=(0, 15))

        self.username_entry = customtkinter.CTkEntry(self.login_frame, width=200, placeholder_text="username")
        self.username_entry.grid(row=1, column=0, padx=30, pady=(15, 15))
        self.password_entry = customtkinter.CTkEntry(self.login_frame, width=200, show="*", placeholder_text="password")
        self.password_entry.grid(row=2, column=0, padx=30, pady=(0, 15))
        self.login_button = customtkinter.CTkButton(self.login_frame, text="Login", command=self.login_event, width=200)
        self.login_button.grid(row=3, column=0, padx=30, pady=(15, 15))

        ##############
        # Main Frame #
        ##############

        # create main frame
        self.main_frame = customtkinter.CTkFrame(self, corner_radius=0)
        self.main_frame.grid_columnconfigure(0, weight=100)
        self.main_label = customtkinter.CTkLabel(self.main_frame, text="PresenseProctor AI\nDashboard",
                                                 font=customtkinter.CTkFont(size=20, weight="bold"))
        self.main_label.grid(row=0, column=0, padx=0, pady=(30, 15))
        self.back_button = customtkinter.CTkButton(self.main_frame, text="Back", command=self.back_event, width=200)
        self.back_button.grid(row=0, column=0, padx=600, pady=(15, 15))

    def login_event(self):
        if self.username_entry.get() == "username" and self.password_entry.get() == "password":
            self.SignInLabel.configure(text="")
            self.username_entry.delete(first_index=0, last_index=10000)
            self.password_entry.delete(first_index=0, last_index=10000)
            self.login_frame.grid_forget()  # remove login frame

            # Separate the Python executable path and the script file path as separate arguments
            python_exe_path = sys.executable
            script_file_path = os.path.dirname(os.path.abspath(__file__)) + "\C&P.py"

            # Execute the command with both paths as separate arguments
            subprocess.Popen([python_exe_path, script_file_path])
        else:
            self.login_frame.grid(row=0, column=0, sticky="ns")  # show login frame
            self.SignInLabel.configure(text="Wrong Username or Password,\n Please try again.")
            self.username_entry.delete(first_index=0, last_index=10000)
            self.password_entry.delete(first_index=0, last_index=10000)



    def back_event(self):
        self.main_frame.grid_forget()  # remove main frame
        self.login_frame.grid(row=0, column=0, sticky="ns")  # show login frame


if __name__ == "__main__":
    app = App()
    app.mainloop()