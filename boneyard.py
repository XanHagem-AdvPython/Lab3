### Initial main, cut for testing
if __name__ == "__main__":

    # URLs to scrape data from
    urls = [
        'https://guide.michelin.com/us/en/california/san-jose/restaurants',
        'https://guide.michelin.com/us/en/california/cupertino/restaurants'
    ]

    # Part A
    # TODO: will this work? tbd...
    for url in urls:
        restaurant_data = fetch_restaurant_data(url)
        for restaurant in restaurant_data:
            restaurant.update(extract_restaurant_data_from_url(restaurant['url']))
        write_to_json_file(restaurant_data, f"{url.split('/')[-1]}.json")

    # # Part B
    # conn = create_database()
    # for url in urls:
    #     with open(f"{url.split('/')[-1]}.json", 'r') as f:
    #         data = json.load(f)
    #         insert_into_database(conn, data)
    # conn.close()