from urllib.request import Request, urlopen
from bs4 import BeautifulSoup as soup
import datetime
import pandas as pd
import sqlalchemy
from sqlalchemy.orm import sessionmaker
import math
from itertools import cycle
from sqlalchemy.sql import text
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# URLs for property listings from Rightmove
URLS2 = {
    'Nuneaton': 'https://www.rightmove.co.uk/property-for-sale/find.html?locationIdentifier=REGION%5E1020&index=',
    'Leicester': 'https://www.rightmove.co.uk/property-for-sale/find.html?locationIdentifier=REGION%5E789&index=',
    'Peterborough': 'https://www.rightmove.co.uk/property-for-sale/find.html?locationIdentifier=REGION%5E1061&index=',
    'Hinckley': 'https://www.rightmove.co.uk/property-for-sale/find.html?locationIdentifier=REGION%5E640&index=',
    'Telford': 'https://www.rightmove.co.uk/property-for-sale/find.html?locationIdentifier=REGION%5E1323&index='
}

# Filter properties by type and add additional query parameters
type = '&propertyTypes=bungalow%2Cdetached%2Csemi-detached%2Cterraced&maxDaysSinceAdded=14&includeSSTC=false&mustHave=&dontShow=&furnishTypes=&keywords='

# Get current date for timestamping data
now = str(datetime.date.today())
print(now)

# Function to calculate the number of pages for a property search result
def pages(url):
    Area = Request(url=url+type, headers={'User-Agent': 'Mozilla/5.0'})
    uClient = urlopen(Area)
    page_html = uClient.read()
    uClient.close()
    page_soup = soup(page_html, "html.parser")
    
    # Extract total number of properties listed
    number_of_properties = page_soup.find("span", {"class": "searchHeader-resultCount"}).text.replace(",", "")
    print('Number of properties = ' + number_of_properties)
    
    # Calculate the number of pages based on 24 results per page
    number_of_pages = math.floor(int(number_of_properties) / 24) + 1
    return number_of_pages

# Function to fetch property data for a given URL
def fetch(url):
    header = ['Title', 'Address', 'Price', 'Updated', 'Snip', 'Date', 'Bedrooms']
    global propertyinfo
    propertyinfo = pd.DataFrame(columns=header)
    index = 0
    num_pages = pages(url)  # Get total number of pages

    for i in range(num_pages):
        index = str(index)
        Area = Request(url=url + index + type, headers={'User-Agent': 'Mozilla/5.0'})
        uClient = urlopen(Area)
        page_html = uClient.read()
        uClient.close()
        page_soup = soup(page_html, "html.parser")
        wrappers = page_soup.findAll("div", {"class": "propertyCard-wrapper"})

        print(i)
        index = int(index)
        index = index + 24  # Increment index by 24 for next page

        # Collecting property data from each wrapper
        for wrapper in wrappers:
            title = wrapper.find("h2", {"class": "propertyCard-title"}).text.replace("\n", "")
            address = wrapper.find("address", {"class": "propertyCard-address"}).text.replace("\n", "")
            price = wrapper.find("div", {"class": "propertyCard-priceValue"}).text.replace("Â", "")
            updated_by = wrapper.find("div", {"class": "propertyCard-branchSummary"}).text.replace("\n", "")
            snip = wrapper.find("span", {"itemprop": "description"}).text.replace("\n", "")
            
            # Extract the property link
            linkpres = wrapper.find("a", class_="propertyCard-img-link", attrs={"data-test": "property-img"})
            link_pro = linkpres["href"]
            start_html = "https://www.rightmove.co.uk"
            linkfull = start_html + link_pro

            # Add the new row to the DataFrame
            new_row = {'Title': title, 'Address': address, 'Price': price, 'Updated': updated_by, 'Snip': snip, 'Link': linkfull}
            propertyinfo = pd.concat([propertyinfo, pd.DataFrame([new_row])], ignore_index=True)

    # Splitting and cleaning the property information
    propertyinfo['Street'] = propertyinfo.Address.str.split(",").str[0]
    propertyinfo['Street'] = propertyinfo.Street.str.replace(' ', '-', regex=True)

    propertyinfo['Town'] = propertyinfo.Address.str.split(",").str[1]
    propertyinfo['Price'] = propertyinfo.Price.replace({"Â", ""}, regex=True)
    propertyinfo['Date'] = now
    propertyinfo['Bedrooms'] = [x[:14] for x in propertyinfo['Title']]
    propertyinfo['Keyb'] = [x[39:48] for x in propertyinfo['Link']]
    
    # Drop rows where 'Town' is missing
    propertyinfo = propertyinfo[propertyinfo['Town'].notna()]
    propertyinfo = propertyinfo.replace('Â', '', regex=True)
    
    # Remove duplicates based on 'Keyb' (unique property identifier)
    propertyinfo = propertyinfo.drop_duplicates(subset=['Keyb'])
    return propertyinfo

# Function to create database connection using credentials from .env file
def connection():
    # Fetch credentials from .env file
    db_user = os.getenv('DB_USER')
    db_password = os.getenv('DB_PASSWORD')
    db_host = os.getenv('DB_HOST')
    db_port = os.getenv('DB_PORT')
    db_name = os.getenv('DB_NAME')
    
    # Create database engine with environment variables
    engine = sqlalchemy.create_engine(f"mysql+pymysql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}")
    
    # Configure session
    Session = sessionmaker(bind=engine)
    session = Session()
    return engine

# Connect to the database
engine = connection()

# Fetch data for each town and upload it to the database
for key in URLS2:
    Town = key
    file_name = key
    print(Town)
    Town = fetch(URLS2[key])
    # Town.to_csv(file_name + '.csv')  # Option to save as CSV
    Town.to_sql(file_name, con=engine, if_exists="append", index=False)

'''
Example code for dropping a table (used for testing purposes)
with engine.connect() as con:
    statement = text("""DROP TABLE Nuneaton""")
    rs = con.execute(statement)
'''
