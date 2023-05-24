"""
Authors: Alex Hagemeister & Marcel Gunadi
Spring Quarter, 2023
CIS41B Advanced Python

Lab 3: Web Scraping and Database Interaction
"""

import tkinter as tk
import tkinter.messagebox as tkmb
import sqlite3
import webbrowser


class MainWindow(tk.Tk):
    """
    Main window of the program:

        - Responsible for displaying the main user interface and options
        - Handles user interactions related to searching by city or cuisine
        - Creates and manages instances of other windows
    """

    def __init__(self):
        super().__init__()  # Need to call the constructor of the parent class
        self.title("Restaurants")

        # Add labels to the main window
        tk.Label(self, text="Local Michelin Guild Restaurants", fg="blue", font=("Arial", 17)).grid(
            row=0, column=0, columnspan=3, pady=10, padx=10
        )
        tk.Label(self, text="Search by", fg="black", font=("Arial", 15)).grid(row=1, column=0, columnspan=3, pady=10)

        # Add buttons that call the search_by_city and search_by_cuisine methods
        tk.Button(self, text="City", fg="blue", command=self.search_by_city).grid(row=2, column=0, padx=15, pady=10)
        tk.Button(self, text="Cuisine", fg="blue", command=self.search_by_cuisine).grid(
            row=2, column=1, padx=15, pady=10
        )

        # Call closeWin method when user clicks on the close button
        self.protocol("WM_DELETE_WINDOW", self.closeWin)

        # Try to connect to database
        try:
            self.conn = sqlite3.connect("restaurants.db")
            self.cur = self.conn.cursor()
        # If failed, show error message and close the program
        except sqlite3.OperationalError:
            tkmb.showerror("Error", "Failed to open database")
            self.destroy() # Close the main window
            self.quit() # Close the program

    def search_by_city(self):
        """
        RHandles the user's choice to search for restaurants by city.

            - Retrieves a list of cities from the database and displays them in a dialog window.
            - Waits for the user to select a city and retrieves the corresponding restaurants for that city.
            - Displays the selected restaurants in another dialog window.
            - User can choose one or more restaurants, opening a separate DisplayWindow for each selection

        """
        # Create an instance of DialogWindow, passing the current instance of MainWindow and the database connection
        self.cities_window = DialogWindow(self, self.conn)
        # Call displayCity method of DialogWindow to display a list of cities
        self.cities_window.display_cities()
        # Wait for the dialog window to be closed before continuing
        # blocks execution of the next line until the dialog window is closed
        self.wait_window(self.cities_window)

        # check if user has selected a city
        if len(self.cities_window.getSelection) != 0:
            # indices of choices in the listbox starts with 0, so add 1 to get correct ID
            cityID = self.cities_window.getSelection[0] + 1

            # create a new dialog win to retrieve restaurant's city
            self.restauraunts_window = DialogWindow(self, self.conn)
            # retrieve restaurant from given cityID
            self.restauraunts_window.get_restauraunt_from_cityID(cityID)
            # wait for the dialog window to be closed before continuing
            self.wait_window(self.restauraunts_window)

            # Get the restaurant with the selected index from the listbox
            self.cur.execute(
                "SELECT Restaurant.restaurant_id FROM Restaurant WHERE Restaurant.location_id = ?", (cityID,)
            )
            selectedRestaurant = self.cur.fetchall()

            # open a new DisplayWindow for each selected restaurant
            for i in self.restauraunts_window.getSelection:
                # Pass the restaurant's ID that was selected from the dialog to DisplayWindow
                DisplayWindow(self, selectedRestaurant[i][0], self.conn)

        print(f"Selected restaurant: {selectedRestaurant}")

    def search_by_cuisine(self):
        """
        Handles the user's choice to search for restaurants by cuisine.

            - Retrieves a list of cuisines from the database and displays them in a dialog window.
            - Waits for the user to select a cuisine and retrieves the restaurant
            - Displays the selected restaurants in another dialog window.
            - Allows the user to choose one or more restaurants, opening a separate window (DisplayWindow) for each selection
        """
        # Create an instance of DialogWindow, passing the current instance of MainWindow and the database connection
        self.cities_window = DialogWindow(self, self.conn)
        # Call displayCuisine method of DialogWindow to display a list of cuisines
        self.cities_window.display_cuisines()
        # Wait for the dialog window to be closed before continuing
        self.wait_window(self.cities_window)

        # Set selectedRestaurant to a default value
        selectedRestaurant = "No selection"

        if len(self.cities_window.getSelection) != 0:
            # indices of choices in the listbox starts with 0, so should be +1 to get correct ID
            cuisineID = self.cities_window.getSelection[0] + 1

            # create a new dialog win to retrieve restaurant's city
            self.restauraunts_window = DialogWindow(self, self.conn)
            self.restauraunts_window.get_restauraunts_by_cuisine(cuisineID)
            self.wait_window(self.restauraunts_window)

            # fetch the restaurant with the selected index
            self.cur.execute(
                "SELECT Restaurant.restaurant_id FROM Restaurant WHERE Restaurant.cuisine_id = ?", (cuisineID,)
            )
            selectedRestaurant = self.cur.fetchall()

            # open a new DisplayWindow for each selected restaurant by passing the restaurant's ID to DisplayWindow
            for i in self.restauraunts_window.getSelection:
                DisplayWindow(self, selectedRestaurant[i][0], self.conn)

        print(f"Selected restaurant IDs in processCuisine: {selectedRestaurant}")

    def closeWin(self):
        """
        Closes the database connection and closes the program.
        """
        self.conn.close()
        self.destroy()
        self.quit()


class DialogWindow(tk.Toplevel):
    """
    Dialog window that interacts with the user and gets input.

        - Displays a list of cities or cuisines for the user to select.
        - Retrieves information from the database based on the user's selection (city or cuisine).
        - Allows the user to select items from the list and returns the selected items.
        - Provides methods to close the dialog window and communicate with the MainWindow.
    """

    def __init__(self, master, db_connection):
        super().__init__(master)  # Need to call the constructor of the parent class
        self.grab_set()  # Prevents user from interacting with the main window while the dialog is open
        self.focus_set()  # Sets the focus to the dialog window
        self.transient(master)  # Makes the dialog window dependent on the main window
        self.protocol("WM_DELETE_WINDOW", self.closeWindow)  # Call closeWin method when user clicks on the close button
        self._selection = ()  # Stores the user's selection
        self.conn = db_connection  # Stores the database connection

    def display_cities(self):
        """
        Displays a list of cities for the user to select.

            - Retrieves the list of cities from the database.
            - Displays the cities in a listbox within a dialog window.
            - Waits for the user to make a selection from the list.
            - Returns the selected city to the calling function (MainWindow).
        """
        tk.Label(self, text="Click on a city to select", font=("Helvetica", 15)).grid(row=0, padx=15, pady=10)

        # Define Listbox and Scrollbar widgets
        self.listbox = tk.Listbox(self, height=6)
        self.scrollbar = tk.Scrollbar(self, orient=tk.VERTICAL, command=self.listbox.yview)
        self.listbox.configure(yscrollcommand=self.scrollbar.set)

        # Connect to database
        self.cur = self.conn.cursor()

        # Add items to the listbox from the database query
        for city in self.cur.execute("SELECT * FROM Location"):
            self.listbox.insert(tk.END, city[1])  # city[0] is city's ID

        self.listbox.grid(row=1, column=0, ipadx=5, padx=20, pady=20, sticky="nsew")
        self.scrollbar.grid(row=1, column=1, sticky="ns")

        # Select button that calls the on_click method
        tk.Button(self, text="Click to select", font=("Helvetica", 15), command=self.click_select).grid(
            row=2, column=0, columnspan=2, padx=20, pady=20
        )

    def display_cuisines(self):
        """
        Displays a list of cuisines for the user to select.

            - Retrieves the list of cuisines from the database.
            - Displays the cuisines in a listbox within a dialog window.
            - Waits for the user to make a selection from the list.
            - Returns the selected cuisine to the calling function (MainWindow).
        """
        tk.Label(self, text="Click on a cuisine to select", font=("Helvetica", 15)).grid(row=0, padx=15, pady=10)

        # Listbox and Scrollbar
        self.listbox = tk.Listbox(self, height=6)
        self.scrollbar = tk.Scrollbar(self, orient=tk.VERTICAL, command=self.listbox.yview)
        self.listbox.configure(yscrollcommand=self.scrollbar.set)

        self.cur = self.conn.cursor()

        # Add items to the listbox from the database query
        for city in self.cur.execute("SELECT * FROM Cuisine"):
            self.listbox.insert(tk.END, city[1])

        self.listbox.grid(row=1, column=0, ipadx=5, padx=20, pady=20, sticky="nsew")
        self.scrollbar.grid(row=1, column=1, sticky="ns")

        # Select button that calls the on_click method
        tk.Button(self, text="Click to select", font=("Helvetica", 15), command=self.click_select).grid(
            row=2, column=0, columnspan=2, padx=20, pady=20
        )

    def get_restauraunt_from_cityID(self, cityID):
        """
        Displays restaurants based on the selected city ID for the user to select.

            - Retrieves the restaurants from the database that match the selected city ID.
            - Displays the restaurants in a listbox within a dialog window.
            - Waits for the user to make a selection from the list.
            - Returns the selected restaurants to the calling function (MainWindow).
        """
        tk.Label(self, text="Click on a restaurant to select", font=("Helvetica", 15)).grid(row=0, padx=15, pady=10)

        # Create the Listbox and Scrollbar widgets
        self.listbox = tk.Listbox(self, height=6, selectmode="multiple")
        self.scrollbar = tk.Scrollbar(self, orient=tk.VERTICAL, command=self.listbox.yview)
        self.listbox.configure(yscrollcommand=self.scrollbar.set)

        # Connect to database
        self.cur = self.conn.cursor()

        self.cur.execute(
            "SELECT Restaurant.restaurant_name FROM Restaurant WHERE Restaurant.location_id = ?", (cityID,)
        )

        restaurants = self.cur.fetchall()  # for debugging
        print(f"Restaurants in city {cityID}: {restaurants}")  # Debug print

        for restaurant in restaurants:
            self.listbox.insert(tk.END, restaurant[0])

        self.listbox.grid(row=1, column=0, ipadx=5, padx=20, pady=20, sticky="nsew")
        self.scrollbar.grid(row=1, column=1, sticky="ns")

        # Select button that calls the select method, which closes the dialog window
        tk.Button(self, text="Click to select", font=("Helvetica", 15), command=self.click_select).grid(
            row=2, column=0, columnspan=2, padx=20, pady=20
        )

    def get_restauraunts_by_cuisine(self, cuisineID):
        """
        Displays restaurants based on the selected cuisine ID for the user to select.

            - Retrieves the restaurants from the database that match the selected cuisine ID.
            - Displays the restaurants in a listbox within a dialog window.
            - Allows the user to select one or more restaurants.
            - Returns the selected restaurants to the calling function (MainWindow).
        """
        tk.Label(self, text="Click on a restaurant to select", font=("Helvetica", 15)).grid(row=0, padx=15, pady=10)

        # Listbox and Scrollbar
        self.listbox = tk.Listbox(self, height=6, selectmode="multiple")
        self.scrollbar = tk.Scrollbar(self, orient=tk.VERTICAL, command=self.listbox.yview)
        self.listbox.configure(yscrollcommand=self.scrollbar.set)

        self.cur = self.conn.cursor()  # Connect to database

        # Find all the restaurants that match the selected cuisine ID
        self.cur.execute(
            "SELECT Restaurant.restaurant_name FROM Restaurant WHERE Restaurant.cuisine_id = ?", (cuisineID,)
        )
        # Fetch all the restaurants from the query
        restaurants = self.cur.fetchall()

        # Loop used to add restaurants to the listbox
        for restaurant in restaurants:
            self.listbox.insert(tk.END, restaurant[0])

        # Add the listbox and scrollbar to the dialog window
        self.listbox.grid(row=1, column=0, ipadx=5, padx=20, pady=20, sticky="nsew")
        self.scrollbar.grid(row=1, column=1, sticky="ns")

        # Select button that calls the on_click method, which closes the dialog window
        tk.Button(self, text="Click to select", font=("Helvetica", 15), command=self.click_select).grid(
            row=2, column=0, columnspan=2, padx=20, pady=20
        )

    def click_select(self):
        """
        Retrieves the user's selection from the listbox and closes the dialog window.
        """
        self._selection = self.listbox.curselection()
        self.closeWindow()

    @property  # @property decorator allows the method to be called without parentheses
    def getSelection(self):
        return self._selection

    def closeWindow(self):
        self.destroy() # Close the dialog window without closing the main window


class DisplayWindow(tk.Toplevel):
    """
    Displays information about selected restaurants in a separate window.

        - Shows details such as the restaurant's name, address, cost, cuisine, and a button to visit its webpage.
        - Retrieves information from the database based on the selected restaurant ID.
        - Provides a method to open the restaurant's webpage in a web browser.
    """

    # Call the constructor of the parent class, passing the current instance of MainWindow, the restaurant's ID, and the database connection
    def __init__(self, master, restaurant_ID, db_connection):
        super().__init__(master)
        self.transient(
            master
        )  # .transient() makes the dialog window dependent on the main window (it will close when the main window is closed)

        self.conn = db_connection  # Connect to database
        self.cur = self.conn.cursor()  # Create cursor object

        # Get the restaurant's details from the database based on the restaurant's ID
        self.cur.execute("SELECT * FROM Restaurant WHERE Restaurant.restaurant_id = ?", (restaurant_ID,))
        restaurant = self.cur.fetchone()
        name, address = restaurant[1], restaurant[6]

        # Get the restaurant's cost and cuisine from the database based on the restaurant's ID
        self.cur.execute(
            "SELECT Cost.cost_symbol FROM Restaurant JOIN Cost ON Restaurant.cost_id = Cost.cost_id AND Restaurant.restaurant_id = ?",
            (restaurant_ID,),
        )
        cost = self.cur.fetchone()[0]

        # Get the restaurant's cuisine from the database based on the restaurant's ID
        self.cur.execute(
            "SELECT Cuisine.cuisine_name FROM Restaurant JOIN Cuisine ON Restaurant.cuisine_id = Cuisine.cuisine_id AND Restaurant.restaurant_id = ?",
            (restaurant_ID,),
        )
        cuisine = self.cur.fetchone()[0]

        # Get the restaurant's URL
        url = restaurant[2]

        tk.Label(self, text=name, font=("Helvetica", 18), fg="blue").grid(row=0, padx=15, pady=10)
        tk.Label(self, text=address, font=("Helvetica", 15)).grid(row=1, padx=15, pady=10)
        tk.Label(self, text=f"Cost: {cost}", font=("Helvetica", 15)).grid(row=2, padx=15, pady=10)
        tk.Label(self, text=f"Cuisine: {cuisine}", font=("Helvetica", 15), fg="blue").grid(row=3, padx=15, pady=10)

        # Add a button to open the restaurant's webpage in a web browser using the webbrowser module
        tk.Button(
            self, text="Visit Webpage", font=("Helvetica", 15), fg="blue", command=lambda: webbrowser.open_new(url)
        ).grid(row=4, padx=15, pady=10)


if __name__ == "__main__":
    MainWindow().mainloop()
