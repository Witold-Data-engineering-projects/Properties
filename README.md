---

# Real Estate Data Scraper

This project scrapes property listings from the Rightmove website for several UK towns and stores the results in a MySQL database. The data collected includes property details such as title, address, price, and more. The project uses Python for web scraping and data processing, and SQLAlchemy to manage database connections.

## Table of Contents
- [Project Overview](#project-overview)
- [Technologies Used](#technologies-used)
- [Setup Instructions](#setup-instructions)
- [How It Works](#how-it-works)
- [Database Schema](#database-schema)
- [Future Improvements](#future-improvements)

## Project Overview

The script scrapes data from five towns on Rightmove:
- Nuneaton
- Leicester
- Peterborough
- Hinckley
- Telford

It retrieves details for specific property types, such as bungalows, detached, semi-detached, and terraced houses listed within the last 14 days. The data is cleaned and then stored in a MySQL database for further analysis.

## Technologies Used

- **Python** for scripting
- **BeautifulSoup** for web scraping
- **SQLAlchemy** for handling database connections and queries
- **Pandas** for data manipulation
- **MySQL** as the database

## Setup Instructions

### Prerequisites
- Python 3.x installed
- MySQL server running and accessible
- Required Python libraries: 
  - `beautifulsoup4`
  - `pandas`
  - `sqlalchemy`
  - `pymysql`

### Installing Dependencies
Install the required Python libraries using `pip`:

```bash
pip install beautifulsoup4 pandas sqlalchemy pymysql
```

### MySQL Configuration
Update the MySQL connection details in the `connection()` function of the script to match your MySQL server settings:

```python
engine = sqlalchemy.create_engine("mysql+pymysql://<username>:<password>@<host>:<port>/<database>")
```

Make sure you have the appropriate database and tables set up or use SQLAlchemy's `to_sql()` method to create the tables automatically.

### Running the Script

To run the script and start scraping data:

```bash
python scraper.py
```

## How It Works

### Key Functions
- **`pages()`**: Determines the number of pages of property listings for each town.
- **`fetch()`**: Scrapes the property details such as title, address, price, description, and links from each page.
- **`connection()`**: Establishes a connection to the MySQL database using SQLAlchemy.
- **Data storage**: The property details are cleaned and then stored in separate tables for each town in the MySQL database.

### Data Pipeline
1. **Scraping**: Data is fetched from the Rightmove website for each town listed in the `URLS2` dictionary.
2. **Data Cleaning**: The raw data is processed to remove unwanted characters, extract meaningful information, and handle missing values.
3. **Data Storage**: Cleaned data is saved into the MySQL database, appending new entries to existing tables.

## Database Schema

Each town has its own table in the database with the following schema:

| Column   | Description                                |
|----------|--------------------------------------------|
| Title    | Property title                             |
| Address  | Full property address                      |
| Price    | Listing price                              |
| Updated  | Last updated by the estate agent           |
| Snip     | A brief description of the property        |
| Date     | Date the data was scraped                  |
| Bedrooms | Number of bedrooms                         |
| Street   | Extracted street from the address          |
| Town     | Extracted town from the address            |
| Keyb     | Unique key extracted from the property URL |
| Link     | Full URL to the property listing           |


Here's the updated `README.md` with the additional portion on local implementation:

---

## Local Implementation

This project is set up to run on a virtual machine using **Linux Ubuntu**, which is hosted on a **QNAP device**. The scraping script is automated using a **cron job**, which periodically fetches and loads the latest property data into the MySQL database.

### Setting Up the Cron Job
To automate the script, a cron job was configured on the Ubuntu virtual machine. The cron job runs weekly, ensuring that the database is regularly updated with the most recent listings:

### Database Aggregation

A **SQL view** was implemented to aggregate the results for easier querying and analysis. A **stored procedure** was created to periodically update this view, summarizing key metrics like average property price, number of listings, and property type distribution across the towns.

---

## Future Improvements

- **Error Handling**: Improve error handling in case the webpage structure changes or the server is unresponsive.
- **Enhancements**: Add more data points such as property images, floor plans, and agent contact information.
- **Parameterization**: To add flexibility variables such as town names, and property types, could be stored as parameters in a configuration file or as environment variables.
- **Dynamic Town Search**: Potential to utilise 'https://los.rightmove.co.uk/' as in example 'https://los.rightmove.co.uk/typeahead?query=north+walsham&limit=10&exclude' to obtain variables for towns.
- **Scalability**: Implement parallel scraping to improve performance for larger datasets.

---

## Demonstrating Efficiency with Minimal Resources
This project showcases how a data engineering pipeline can be successfully implemented even with limited resources. By leveraging a low-cost setup—using a QNAP device, a virtual machine, and open-source tools—it's possible to build an automated data pipeline for scraping, cleaning, storing, and analyzing data. This highlights that even smaller-scale environments can support effective data engineering practices.


