"""
Authors: Alex Hagemeister & Marcel LAstnAmE
Spring Quarter, 2023
CIS41B Advanced Python

Lab 3: Web Scraping and Database Interaction
"""

import tkinter as tk
from tkinter import messagebox, Listbox, Scrollbar
import sqlite3
import webbrowser


class MainWindow(tk.Tk):
    """
    The MainWindow class is the main window of the application, with two buttons to search by city or cuisine.
    When the user clicks on a button, a dialog window appears with a listbox of cities or cuisines.
    Requirements:
        - buttons in the main window should be disabled when the dialog window is open
        - The listbox shows ecactly six items at a time, with a scrollbar to scroll through the list
        - the user can click on only one item in the listbox, then click the "Select" button, which closes the dialog window
        - the user can also click the X to close the dialog window

        After the dialog window closes, if the user made at least one restaurant choice,
        then for each of the chosen restaurants, the main window creates a display window.
    """

    def __init__(self):
        # The super() function is used to give access to methods and properties of a parent or sibling class.
        super().__init__()
        self.title("Restaurants")
        self.geometry("500x300")

        self.database = self.connect_db()
        # If the database is not connected, then the program will close.
        if not self.database:
            return

        # The dialog_window attribute is used to keep track of whether the dialog window is open or not.
        # If the dialog window is open, then the main window should disable the buttons.
        self.dialog_window = None

        # Set up the main window buttons and labels
        self.info_text = tk.Label(self, text="Choose a search method below:").grid(row=0, column=0, pady=20)

        self.search_by_city_button = tk.Button(self, text="Search by City", command=self.search_by_city).grid(row=1, column=0)

        self.search_by_cuisine_button = tk.Button(self, text="Search by Cuisine", command=self.search_by_cuisine).grid(
            row=2, column=0
        )

    def connect_db(self):
        try:
            conn = sqlite3.connect("restaurants.db")
            return conn
        except Exception as e:
            messagebox.showerror("Error", "Unable to connect to the database")
            self.destroy()
            return None

    def search_by_city(self):
        query = "SELECT DISTINCT location_name FROM Location"
        if self.dialog_window is None:
            self.dialog_window = DialogWindow(
                self.database,
                self,
                query,
                self.on_dialog_window_close,
                """SELECT Restaurant.street_address, Restaurant.restaurant_name, Cost.cost_symbol, Cuisine.cuisine_name, Restaurant.restaurant_url
                                                                                                          FROM (((Restaurant 
                                                                                                          INNER JOIN Location ON Location.location_id = Restaurant.location_id)
                                                                                                          INNER JOIN Cost ON Cost.cost_id = Restaurant.cost_id)
                                                                                                          INNER JOIN Cuisine ON Cuisine.cuisine_id = Restaurant.cuisine_id)
                                                                                                          WHERE Location.location_name IN ({})""",
            )

    def search_by_cuisine(self):
        query = "SELECT DISTINCT cuisine_name FROM Cuisine"
        if self.dialog_window is None:
            self.dialog_window = DialogWindow(
                self.database,
                self,
                query,
                self.on_dialog_window_close,
                "SELECT restaurant_name FROM Restaurant WHERE cuisine_id IN ({})",
            )

    def on_dialog_window_close(self):
        self.dialog_window = None


class DialogWindow(tk.Toplevel):
    def __init__(self, database, master, query, on_close, restaurant_query):
        super().__init__(master)
        self.title("Select")
        self.geometry("200x200")
        self.database = database
        self.master = master
        self.query = query
        self.restaurant_query = restaurant_query

        self.scrollbar = Scrollbar(self)
        self.scrollbar.grid(row=0, column=1, sticky="NS")

        self.listbox = Listbox(self, yscrollcommand=self.scrollbar.set)
        self.listbox.grid(row=0, column=0, sticky="NSEW")

        self.scrollbar.config(command=self.listbox.yview)

        self.selection_button = tk.Button(self, text="Select", command=self.select_item)
        self.selection_button.grid(row=1, column=0, pady=10)

        self.protocol("WM_DELETE_WINDOW", on_close)

        self.load_data()

    def load_data(self):
        cursor = self.database.cursor()
        cursor.execute(self.query)

        for row in cursor.fetchall():
            self.listbox.insert(tk.END, row[0])

    def select_item(self):
        selected = self.listbox.curselection()
        if selected:
            selected_values = [self.listbox.get(i) for i in selected]
            self.destroy()
            for value in selected_values:
                DisplayWindow(self.database, value, self.restaurant_query)


class DisplayWindow(tk.Toplevel):
    def __init__(self, database, value, query):
        super().__init__()
        self.title(value)
        self.geometry("400x200")
        self.database = database

        cursor = self.database.cursor()
        print(value)
        cursor.execute(query.format("?"), (value,))

        row = cursor.fetchone()
        if row:
            self.address, self.restaurant_name, self.cost, self.cuisine, self.url = row
        else:
            messagebox.showerror("Error", "Unable to find restaurant information")
            self.destroy()
            return

        self.label = tk.Label(
            self,
            text=f"Name: {self.restaurant_name}\nAddress: {self.address}\nCost: {'$'*self.cost}\nCuisine: {self.cuisine}",
        )
        self.label.grid(row=0, column=0, padx=10, pady=10)

        self.url_button = tk.Button(self, text="Open URL", command=lambda: webbrowser.open(self.url))
        self.url_button.grid(row=1, column=0, pady=10)


if __name__ == "__main__":
    MainWindow().mainloop()
