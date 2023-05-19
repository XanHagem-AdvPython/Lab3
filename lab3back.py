"""
Authors: Alex Hagemeister & Marcel LAstnAmE
Spring Quarter, 2023
CIS41B Advanced Python

Lab 3: Web Scraping and Database Interaction

lab3back.py

    This script is the back end component of the program, responsible for scraping data from the Michelin Guide website 
    to gather information about local restaurants.
    It performs web crawling, extraction, and data processing to create JSON files and an SQLite database for further analysis.

Two distinct parts: Part A and Part B. 
    - Only one part will run at a time. 
    - After finishing Part A, comment it out and write Part B.
 
    webpage ===> Part A ===> JSON file  
    JSON file ===> Part B ===> SQL Database 

PART A: Web Scraping

    - Scrape data from the Michelin Guide page for restaurants in San Jose.
    - Extract information such as URL, name, location, cost, and cuisine.
    - Crawl to individual restaurant pages to extract additional information like address.
    - Organize the web scraping code using OOP or functions.
    - Store the extracted data in a JSON file.

PART B: Data Storage

    - Enhance the web scraping code to scrape data from the Michelin Guide page for restaurants in Cupertino.
    - Create JSON files for both San Jose and Cupertino restaurants.
    - Read the data from the JSON files and store it in an SQLite database.
    - Design the database with tables for locations, costs, cuisines, and the main table for restaurant attributes.

"""

import urllib.request as ur
import requests
from bs4 import BeautifulSoup
import json
import re
import sqlite3


def fetch_restaurants_directory_data(url):
    """
    Fetch data from page: use use requests.get() to fetch the page content,
    and then use BeautifulSoup to parse the HTML and extract:
        1. URL of the restaurant
        2. Name of the restaurant
        3. Location or city name of the restaurant

    NOTE: Optional - can extract the following from the restaurant page instead of the main page:
        4. Cost of the restaurant (number of $$ signs)
        5. Cuisine of the restaurant

    PARAM: url (str) - the url to scrape data from
    RETURN: a list of dictionaries, where each dictionary has restaurant details
    """
    import pdb

    # pdb.set_trace()

    # Get the page content and create a beautiful soup object
    try:
        page = requests.get(url, timeout=3)
        page.raise_for_status() # ask Requests to raise any exception it finds
        # do work, status is no error if we get here
    except requests.exceptions.HTTPError as e:
        print("HTTP Error:", e)
    except requests.exceptions.ConnectionError as e:
        print("Error Connecting:", e)
    except requests.exceptions.Timeout as e:
        print("Timeout Error:", e)
    except requests.exceptions.RequestException as e: # any Requests error
        print("Requests Error:", e)
              

    soup = BeautifulSoup(page.content, "lxml")
    # print(soup.prettify())

    # Get the restaurant cards
    # cards = soup.find_all("card__menu-image")
    # cards = soup.find_all(string="image-wrapper pl-image")


def extract_restaurant_data_from_url(url):
    """
    Use the URL of the restaurant to do a web crawl to the restaurant page and extract the following information:
        - Address of the restaurant (street address and city) •
        - NOTE: Alternatively, the cost and cuisine can be extracted from this page instead of the previous page.

    PARAM: url (str) - the url to scrape data from
    RETURN: a list of dictionaries, where each dictionary has restaurant details
    """
    # TODO implement extract_restaurant_data_from_url
    pass


def write_to_json_file(data, filename):
    """
    Write data to a JSON file

    PARAM: data - the data to write to the file
    PARAM: filename - the name of the file to write to
    TODO: try using args and kwargs??
    """
    # TODO implement write_to_json_file
    pass


def create_database():
    """
    Create the SQLite database and the tables needed

    PARAM: None?
    RETURN: the database connection (type: sqlite3.connect??)
    """
    # TODO implement create_database
    pass


def insert_into_database(conn, data):
    """
    Insert the data into the SQLite database

    PARAM: conn - the database connection
    PARAM: data - the data to insert into the database
    """
    pass


def main():
    """
    Main function to run the program
    """
    print(
        """"
        ---------------
        Running main...
        ---------------
    """
    )
    # URLs to scrape data from
    urls = [
        "https://guide.michelin.com/us/en/california/san-jose/restaurants",
        "https://guide.michelin.com/us/en/california/cupertino/restaurants",
    ]

    fetch_restaurants_directory_data(urls[1])


if __name__ == "__main__":
    main()
