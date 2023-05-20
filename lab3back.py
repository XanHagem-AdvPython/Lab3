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
from collections import defaultdict


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
    RETURN: a list of dictionaries, where each dictionary has restaurant details
    """
    import pdb

    # Get the page content and create a beautiful soup object
    page = requests.get(url)  # TODO: try-exception block
    soup = BeautifulSoup(page.content, "lxml")

    # Get the restaurant cards
    cards = soup.find_all("div", class_="card__menu box-placeholder js-restaurant__list_item js-match-height js-map")

    # Create list for restaurant dicts
    restaurant_dict_list = []

    # Get the restaurant details from each card in the list of cards
    for card in cards:

        # create a dictionary to store the restaurant details (w/ default vals to avoid key errors)
        restaurant = defaultdict(lambda: "N/A")

        # Get the restaurant name
        # restaurant["name"] = card.find("restaurant-name")
        restaurant["name"] = card.select_one('div.card__menu-content h3.card__menu-content--title').text.strip()
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

        # Add the restaurant dictionary to the list of restaurant dictionaries
        restaurant_dict_list.append(restaurant)

    # return restaurant_dict_list
    return restaurant_dict_list



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

    # try fetching data from the first URL to test
    restaraunts = fetch_restaurants_directory_data(urls[1])

    # List of dictionary keys
    keys = ["name", "url", "location", "cost", "cuisine"]

    for restaurant in restaraunts:
        for key in keys:
            print(f"{key}: {restaurant[key]}")
        print("\n")


if __name__ == "__main__":
    main()
