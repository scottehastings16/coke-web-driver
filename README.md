# coke-web-driver

 Web Scraper and Data Layer Extractor

This Python script scrapes web pages, extracts data from `data-cmp-data-layer` attributes, captures screenshots of clickable elements, and compiles the information into an Excel spreadsheet.

## Features

* **Web Scraping:** Uses Selenium to navigate web pages and BeautifulSoup to parse HTML.
* **Data Layer Extraction:** Extracts JSON data from `data-cmp-data-layer` attributes of clickable elements.
* **Screenshot Capture:** Takes screenshots of each clickable element.
* **Data Organization:** Flattens and restructures the extracted JSON data for better readability.
* **Excel Export:** Exports the scraped data, including key-value pairs and corresponding screenshots, to an Excel file.
* **Cookie Consent Handling:** Includes logic to handle cookie consent popups.
* **Error Handling:** Implements error handling for JSON decoding and screenshot capture.
* **Image Resizing:** Resizes images before inserting them into the Excel file to maintain reasonable file size.

## Requirements

* **Python 3.x:** Ensure you have Python 3 installed.
* **Libraries:** Install the required libraries using pip:
```bash
pip install selenium beautifulsoup4 pandas json xlsxwriter Pillow

ChromeDriver: Download the appropriate ChromeDriver executable for your Chrome browser version and place it in a location accessible by your system's PATH.
Usage

Clone the repository:
git clone [https://github.com/scottehastings16/coke-web-driver.git]

Update URLs: Modify the my_urls list in the script to include the URLs you want to scrape.

Run the script:
python coke-web-driver.py
Output: The script will create an Excel file named output.xlsx in the specified directory (currently C:/Users/scott/Downloads/), containing the scraped data and screenshots. **Update this path if needed.**

## Configuration
my_urls: List of URLs to scrape.
screenshot_dir: Directory to store screenshots. Defaults to "screenshots".
output.xlsx Path: Update the path in the workbook = xlsxwriter.Workbook() line if needed.
Image Resizing: Adjust max_width and max_height variables to control the maximum dimensions of screenshots in the Excel file.
Code Structure
The script is organized into several functions:

rename_key(key): Renames specific keys in the extracted JSON for clarity.
Main loop: Iterates through the URLs, extracts data, captures screenshots, and stores the information.
Excel Export: Creates an Excel workbook and writes the data and images to a worksheet.
