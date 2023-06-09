"""
Authors: Alex Hagemeister & Marcel Gunadi
Spring Quarter, 2023
CIS41B Advanced Python

Lab 3: Web Scraping and Database Interaction

lab3back.py

    Back end component of the program, 
    Scrapes restauraunt data from the Michelin Guide website, and saves to json and sqlite database files.

PART A: Web Scraping

    - Scrapes data from the Michelin Guide page for restaurants in San Jose and/or Cupertino.
    - Extracts the URL, name, location, cost, and cuisine.
    - Crawls to individual restaurant pages to extract address.
    - Store the extracted data in a JSON file

PART B: Database with SQLite

    - Design the database with tables for locations, costs, cuisines, and the main table for restaurant attributes.
    - Read the data from the JSON files and store it in an SQLite database.
    - Insert the data into the database (ref db design).
"""

import requests
from bs4 import BeautifulSoup
import json
import sqlite3
from collections import defaultdict

# URLs to scrape data from
URL_DICT = {
    "San Jose": "https://guide.michelin.com/us/en/california/san-jose/restaurants",
    "Cupertino": "https://guide.michelin.com/us/en/california/cupertino/restaurants",
}


def fetch_restaurants_directory_data(url):
    """
    Fetch data from page: use use requests.get() to fetch the page content,
    and then use BeautifulSoup to parse the HTML and extract:
        1. URL of the restaurant
        2. Name of the restaurant
        3. Location or city name of the restaurant
        4. Cost of the restaurant (number of $$ signs)
        5. Cuisine of the restaurant

    PARAM: url (str) - the url to scrape data from
    RETURN: a list of dictionaries, where each dictionary has restaurant details, if fails returns false
    """
    # Create list for restaurant dicts
    restaurant_dict_list = []
    # while loop to get all pages
    # NOTE: recursion would also work, but could be risky for... reasons.
    while url:
        # Get the page content and create a beautiful soup object
        try:
            page = requests.get(url)  # TODO: try-exception block
        except:
            return False

        soup = BeautifulSoup(page.content, "lxml")

        # Get the restaurant cards
        cards = soup.find_all(
            "div", class_="card__menu box-placeholder js-restaurant__list_item js-match-height js-map"
        )

        # Get the restaurant details from each card in the list of cards
        for card in cards:
            # create a dictionary to store the restaurant details (w/ default vals to avoid key errors)
            restaurant = defaultdict(lambda: "N/A")

            # Get the restaurant name
            # restaurant["name"] = card.find("restaurant-name")
            restaurant["name"] = card.select_one("div.card__menu-content h3.card__menu-content--title").text.strip()
            # ^ select_one() returns the first element that matches the CSS selector
            # ^ div.card__menu-content h3.card__menu-content--title is the CSS selector
            # for the <h3> tag with class="card__menu-content--title" inside a <div> tag with class="card__menu-content"

            # Get the restaurant URL
            restaurant["url"] = "".join(["https://guide.michelin.com", card.select_one("a.link").get("href")])
            # ^ a.link is the CSS selector for the <a> tag with class="link"
            # ^ get() returns the value of the specified attribute - in this case, href (the URL)
            # print(url)

            # Get the restaurant location
            restaurant["location"] = card.select_one("div.card__menu-footer--location").text.strip()
            # ^ using CSS selector for <div> tag, class="card__menu-footer--location"
            # NOTE: this also gets the country, which is not needed. will keep for now.

            # Get the restaurant cost and cuisine type from the footer
            cost_and_type = card.select_one("div.card__menu-footer--price").text.split("·")
            restaurant["cost"] = cost_and_type[0].strip()
            restaurant["cuisine"] = cost_and_type[1].strip()

            restaurant_dict_list.append(restaurant)

        # Get the next page URL, if it exists. Only get the link with the right arrow icon!
        next_page_link = soup.select_one(
            "div.btn-carousel a.btn-carousel__link[href*='/page/'][href]:has(span.icon.fal.fa-angle-right)"
        )
        if next_page_link:
            url = "".join(["https://guide.michelin.com", next_page_link["href"]])
        else:
            url = None

    return restaurant_dict_list


def extract_restaurant_address(url):
    """
    Use the URL of the restaurant to extract address (street address and city)

    PARAM: url (str) - url of the restaurants' Michelin page
    RETURN: the street address and city of the restaurant (str)
    """
    # get the page content and create a beautiful soup object
    page = requests.get(url)
    soup = BeautifulSoup(page.content, "lxml")

    # get the restaurant address
    address_element = soup.select_one("li.restaurant-details__heading--address")
    if address_element:
        return address_element.text.strip()
    else:
        return ""


def write_to_json_file(restauraunts_dict, filename):
    """
    Write data to a JSON file

    PARAM: data - the data to write to the file
    PARAM: filename - the name of the file to write to
    TODO: try using args and kwargs??
    """
    with open(filename, "w", encoding="utf-8") as file:
        json.dump(restauraunts_dict, file, indent=4)


def create_database():
    """
    Create the SQLite database and the tables needed with the following schema:
    - Restaurant name
    - Restaurant URL
    - Location (lookup table), int : city
    - Cost (lookup table), int : n$
    - Cuisine type (lookup table), int : type
    - Addess (street address and city)

    RETURN: the database connection (type: sqlite3.connect??)
    """
    conn = sqlite3.connect("restaurants.db")  # Connect to the database
    cursor = conn.cursor()

    # -------------------------------------------#
    # Create the tables needed for the database #
    # -------------------------------------------#

    # Create the "Cuisine" lookup table
    cursor.execute(
        """CREATE TABLE IF NOT EXISTS Cuisine (
        cuisine_id INTEGER PRIMARY KEY,
        cuisine_name TEXT UNIQUE
        )"""
    )

    # Create the "Cost" lookup table
    cursor.execute(
        """CREATE TABLE IF NOT EXISTS Cost (
        cost_id INTEGER PRIMARY KEY,
        cost_symbol TEXT UNIQUE
        )"""
    )

    # Create the "Location" lookup table
    cursor.execute(
        """CREATE TABLE IF NOT EXISTS Location (
        location_id INTEGER PRIMARY KEY,
        location_name TEXT UNIQUE
        )"""
    )

    # Create the "Restaurant" table
    cursor.execute(
        """CREATE TABLE IF NOT EXISTS Restaurant (
        restaurant_id INTEGER PRIMARY KEY,
        restaurant_name TEXT UNIQUE,
        restaurant_url TEXT UNIQUE,
        cuisine_id INTEGER,
        cost_id INTEGER,
        location_id INTEGER,
        street_address TEXT NOT NULL,
        FOREIGN KEY (cuisine_id) REFERENCES Cuisine (cuisine_id),
        FOREIGN KEY (cost_id) REFERENCES Cost (cost_id),
        FOREIGN KEY (location_id) REFERENCES Location (location_id)
        )"""
    )

    # Add indeces to the foreign key columns in the "Restaurant" table
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_cuisine_id ON Restaurant (cuisine_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_cost_id ON Restaurant (cost_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_location_id ON Restaurant (location_id)")

    conn.commit()  # Commit the changes to the database

    return conn  # Return the database connection


def insert_into_database(conn, dict_list):
    """
    Insert the data into the SQLite database

    PARAM: conn - the database connection
    PARAM: dict_list - the data to insert into the database
    """
    cursor = conn.cursor()  # Get the cursor

    # Insert into the database in the order that respects the foreign key constraints
    for row in dict_list:
        # Extract the values from the dictionary
        restaurant_name = row["name"]
        restaurant_url = row["url"]
        cuisine_name = row["cuisine"]
        cost_symbol = row["cost"]
        location_name = row["location"]
        street_address = row["address"]

        # Insert the data into the "Cuisine" table, using INSERT OR IGNORE to avoid duplicate entries
        cursor.execute(
            "INSERT OR IGNORE INTO Cuisine (cuisine_name) VALUES (?)",
            (cuisine_name,),
        )
        cursor.execute("SELECT cuisine_id FROM Cuisine WHERE cuisine_name = ?", (cuisine_name,))
        cuisine_id = cursor.fetchone()[0]  # Use fetchone() to get the id of the last inserted row

        # Insert the data into the "Cost" table using INSERT OR IGNORE to avoid duplicate entries
        cursor.execute(
            "INSERT OR IGNORE INTO Cost (cost_symbol) VALUES (?)",
            (cost_symbol,),
        )
        # Get the id of the last inserted row to use as the foreign key for the "Restaurant" table
        cursor.execute("SELECT cost_id FROM Cost WHERE cost_symbol = ?", (cost_symbol,))
        cost_id = cursor.fetchone()[0]

        # Insert the data into the "Location" table
        cursor.execute(
            "INSERT OR IGNORE INTO Location (location_name) VALUES (?)",
            (location_name,),
        )
        cursor.execute("SELECT location_id FROM Location WHERE location_name = ?", (location_name,))
        location_id = cursor.fetchone()[0]

        # Insert the data into the "Restaurant" table using INSERT OR IGNORE to avoid duplicate entries
        cursor.execute(
            "INSERT OR IGNORE INTO Restaurant (restaurant_name, restaurant_url, cuisine_id, cost_id, location_id, street_address) "
            "VALUES (?, ?, ?, ?, ?, ?)",
            (restaurant_name, restaurant_url, cuisine_id, cost_id, location_id, street_address),
        )

    conn.commit()  # Commit the changes to the database


# UNIT TESTING #


def view_database(conn):
    """
    View the contents of the SQLite database in separate relational tables (for testing)

    PARAM: conn - the database connection
    """

    print("\n *** Viewing the database *** \n")

    # Get the cursor
    cursor = conn.cursor()

    # Get the table names in the database
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    table_names = cursor.fetchall()

    # Iterate over the table names
    for table in table_names:
        table_name = table[0]
        print(f"\n*** {table_name} ***")

        # Execute a SELECT query for the current table
        cursor.execute(f"SELECT * FROM {table_name}")

        # Fetch all the rows from the result set
        rows = cursor.fetchall()

        # Print the rows
        for row in rows:
            print(row)


def view_decoded_database(conn):
    """
    View the DECODED contents of the SQLite database (for testing)

    PARAM: conn - the database connection
    """
    
    print("\n *** Viewing DECODED database *** \n")
    
    # Get the cursor
    cursor = conn.cursor()

    # Execute a SELECT query with JOIN operations to retrieve data from the "Restaurant" table and related lookup tables
    cursor.execute(
        """
        SELECT R.restaurant_name, C.cuisine_name, CO.cost_symbol, L.location_name, R.street_address
        FROM Restaurant R
        JOIN Cuisine C ON R.cuisine_id = C.cuisine_id
        JOIN Cost CO ON R.cost_id = CO.cost_id
        JOIN Location L ON R.location_id = L.location_id
    """
    )

    # Fetch all the rows from the result set
    rows = cursor.fetchall()

    # Print the rows with row indices
    for index, row in enumerate(rows, start=1):
        print(f"Row {index}: {row}")


def test_partA_without_duplicates():
    print(
        """
        ---------------------------------------------------------
        |       Running part A (without dupicates in dict)       |
        ---------------------------------------------------------
    """
    )

    # Get the restaurant data from both cities
    restaurants = []

    # VERSION 1: skip duplicate dict entries (NOTE this is also handled elsewhere)

    restaurants.extend(r for r in fetch_restaurants_directory_data(URL_DICT["San Jose"]) if r not in restaurants)
    restaurants.extend(r for r in fetch_restaurants_directory_data(URL_DICT["Cupertino"]) if r not in restaurants)

    # Now, use the restaurant urls to get the restaurant street addresses, and add to dictionary
    for restaurant in restaurants:
        restaurant["address"] = extract_restaurant_address(restaurant["url"])

    # Now, write the data to a JSON file using the write_to_json_file() function
    write_to_json_file(restaurants, "restaurants.json")


def test_partA_with_duplicates():
    print(
        """
        ---------------------------------------------------------
        |       Running part A (WITH dupicates in dict   )       |
        ---------------------------------------------------------
    """
    )

    # Get the restaurant data from both cities
    restaurants = []

    # VERSION 2: get all restaurants, including duplicates to test db insertion
    for url in URL_DICT.values():
        restaurants.extend(fetch_restaurants_directory_data(url))

    # Now, use the restaurant urls to get the restaurant street addresses, and add to dictionary
    for restaurant in restaurants:
        restaurant["address"] = extract_restaurant_address(restaurant["url"])

    # Now, write the data to a JSON file using the write_to_json_file() function
    write_to_json_file(restaurants, "restaurants.json")


def test_partB():
    print(
        """
        ---------------------------------------------------------
        |       Running part B (writing to & reading from db)   |
        ---------------------------------------------------------
        """
    )

    # read the data from the JSON file
    with open("restaurants.json", "r") as file:
        restaurants_from_json = json.load(file)

    print(f"Number of restaurants: {len(restaurants_from_json)}")

    # Call the create_database() function to create the database and get the connection
    conn = create_database()

    # Call the insert_into_database() function to insert the data into the database
    insert_into_database(conn, restaurants_from_json)

    # # Call the view_database() function to view the contents of the database
    print("\n *** View the database *** \n")
    view_database(conn)

    # # Call the view_decoded_database() function to view the contents of the database
    print("\n *** View the DECODED database *** \n")
    view_decoded_database(conn)


def main():
    """
    Main function (testing)
    Does both part A and part B, but need to comment out
    NOTE: uses pages for both San Jose and Cupertino
    """
    print(
        """"
        --------------------------------
        |       Running main...        |
        --------------------------------
    """
    )

    print("\n ***** TESTING PART A: Scraping & writing to json ***** \b")

    # Get the restaurant data from both cities
    restaurants = []

    # VERSION 1: skip duplicate dict entries (NOTE this is also handled in db insertion)
    restaurants.extend(r for r in fetch_restaurants_directory_data(URL_DICT["San Jose"]) if r not in restaurants)
    restaurants.extend(r for r in fetch_restaurants_directory_data(URL_DICT["Cupertino"]) if r not in restaurants)

    # # VERSION 2: get all restaurants, including duplicates to test db insertion
    # for url in URL_DICT.values():
    #     restaurants.extend(fetch_restaurants_directory_data(url))

    # Use the restaurant urls to get the restaurant street addresses, and add to dictionary
    for restaurant in restaurants:
        restaurant["address"] = extract_restaurant_address(restaurant["url"])

    # Now, write the data to a JSON file using the write_to_json_file() function
    write_to_json_file(restaurants, "restaurants.json")

    print("\n ***** TESTING PART B: writing to & reading from db ***** \n")

    # read the data from the JSON file
    with open("restaurants.json", "r") as file:
        restaurants_from_json = json.load(file)

    print(f"Number of restaurants: {len(restaurants_from_json)}")

    # Call the create_database() function to create the database and get the connection
    conn = create_database()

    # Call the insert_into_database() function to insert the data into the database
    insert_into_database(conn, restaurants_from_json)

    # Call the view_database() function to view the contents of the database
    view_database(conn)

    # Call the view_decoded_database() function to view the contents of the database
    view_decoded_database(conn)


if __name__ == "__main__":

    main() # Runs both parts A and B

    # test_partA_without_duplicates()
    # test_partA_with_duplicates()
    # test_partB()
