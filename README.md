# Redbus Data Scraping Project

## Overview
This project is designed to scrape bus information from the Redbus website for multiple states in India. The collected data includes details like bus names, types, departure times, durations, arrival times, star ratings, seat availability, and prices. The data is saved into a CSV file for further analysis or usage.

## Features
- Scrapes bus route details for multiple states.
- Collects and organizes data for attributes such as:
  - Bus Name
  - Bus Type
  - Departure Time
  - Duration
  - Arrival Time
  - Star Rating
  - Price
  - Seat Availability
- Saves the scraped data into a CSV file.
- Supports multiple pages of data for each route.

## States Covered
This project currently supports scraping bus details for the following states:
- Rajasthan
- South Bengal
- Telengana
- UP
- Assam
- KAAC
- KADAMBA
- Kerala
- Himachal
- West bengal

## Technologies Used
- **Python**: For scripting and data handling.
- **Selenium**: For web scraping and automating interactions with the website.
- **Pandas**: For organizing and saving the data into CSV format.
- **Git**: For version control.

## Prerequisites
- Python 3.7+
- Google Chrome browser
- ChromeDriver
- Selenium package
- Pandas package
- Git

## Installation
1. Clone this repository:
   ```bash
   git clone https://github.com/your-username/redbus-scraping.git
   ```
2. Navigate to the project directory:
   ```bash
   cd redbus-scraping
   ```
3. Install the required Python packages:
   ```bash
   pip install -r requirements.txt
   ```

## Usage
1. Update the script to include the desired states and their corresponding URLs.
2. Run the script:
   ```bash
   python main.py
   ```
3. The scraped data will be saved as a CSV file in the project directory.

## Project Structure
```
redbus-scraping/
├── redbus_scrapped_sl.py # Streamlit application 
├── README.md           # Project documentation
├── scraping_data_of_various_states/      # Main script for scraping
└── mysql_redbus/       # to store data in DB
```

## Contact
For any queries or issues, please contact:
- **Name**: Abarna Venkatasubramanian
- **Email**: abarnavenkat31@gmail.com
