import os
import subprocess
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import json
from pandas import json_normalize
import xlsxwriter
from PIL import Image
import hashlib
import time  # Import time module for sleep

# Function to get installed chromedriver version
def get_installed_chromedriver_version():
    try:
        result = subprocess.run(["chromedriver", "--version"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        version = result.stdout.decode("utf-8").split()[1]
        return version
    except Exception as e:
        print(f"Error fetching installed chromedriver version: {e}")
        return None

# Function to install Chromedriver in a custom directory
def install_chromedriver():
    chromedriver_url = "https://storage.googleapis.com/chrome-for-testing-public/132.0.6834.159/linux64/chrome-headless-shell-linux64.zip"  # Update the URL to match Chrome version 120
    chromedriver_dir = os.path.join(os.getcwd(), 'chromedriver')  # Install to the current working directory
    
    current_version = get_installed_chromedriver_version()
    desired_version = "132.0.6834.159"  # Update this to the desired version

    if current_version == desired_version:
        print("Chromedriver is already up-to-date.")
        return  # Exit early if the version is correct

    try:
        print("Downloading Chromedriver...")
        subprocess.run(f"wget -q -O chromedriver_linux64.zip {chromedriver_url}", shell=True, check=True)
        
        # Unzip the file
        subprocess.run("unzip -o chromedriver_linux64.zip", shell=True, check=True)
        
        # Make the downloaded chromedriver executable
        subprocess.run("chmod +x chromedriver", shell=True, check=True)

        # Only move the file if it does not already exist at the destination
        if not os.path.exists(chromedriver_dir):
            subprocess.run(f"mv -f chromedriver {chromedriver_dir}", shell=True, check=True)
            print(f"Chromedriver installed successfully to {chromedriver_dir}")
        else:
            print(f"Chromedriver already exists at {chromedriver_dir}, skipping move.")

    except subprocess.CalledProcessError as e:
        print(f"Error installing Chromedriver: {e}")
        exit(1)  # Exit script if installation fails

# Install Chromedriver if not up-to-date
install_chromedriver()

# Configure Chrome options for headless execution
chrome_options = Options()
chrome_options.add_argument("--headless")  # Run in headless mode (no UI)
chrome_options.add_argument("--no-sandbox")  # Required for running as root in containers
chrome_options.add_argument("--disable-dev-shm-usage")  # Fix memory issues
chrome_options.add_argument("--window-size=1920x1080")  # Ensures elements are visible
chrome_options.add_argument("--disable-gpu")  # Fixes issues in some environments

# Define the path to Chromedriver (local path)
chromedriver_path = os.path.join(os.getcwd(), 'chromedriver')  # Using the local chromedriver path

# Initialize WebDriver with service and options
driver = webdriver.Chrome(service=Service(chromedriver_path), options=chrome_options)

# Debug: Print to confirm headless mode is active
print("WebDriver initialized in headless mode.")


# List of URLs to scrape
my_urls = [
]

# Create a directory for screenshots
screenshot_dir = "screenshots"
os.makedirs(screenshot_dir, exist_ok=True)

# Data storage
all_clickable_data_layers = []
processed_ids = set()  # Track processed component IDs

def rename_key(key):
    if '@type' in key:
        return 'component_type'
    elif 'dc:title' in key:
        return 'link_name'
    elif 'xdm:linkURL' in key:
        return 'link_url'        
    else:
        return key

for page in my_urls:
    driver.get(page)

    # Handle cookie consent
    try:
        accept_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, "close-pc-btn-handler"))
        )
        accept_button.click()
        print("Cookie consent accepted.")
    except Exception:
        print("Cookie consent button not found or not clickable.")

    # Parse page source
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    clickable_elements = soup.find_all(attrs={"data-cmp-clickable": True})
    print(f"Found {len(clickable_elements)} clickable elements on {page}")

    # Extract data layers
    for index, element in enumerate(clickable_elements):
        component_id = element.get('id')
        if component_id in processed_ids:
            continue
        
        data_layer = element.get('data-cmp-data-layer')
        if data_layer:
            try:
                data_layer_dict = json.loads(data_layer)
                flattened_data = json_normalize(data_layer_dict)
                flattened_data['page_url'] = page
                
                # Transpose data
                transposed_data = flattened_data.T.reset_index()
                transposed_data.columns = ['Key', 'Value']
                transposed_data['Element Index'] = index
                transposed_data['Page URL'] = page
                transposed_data['Key'] = transposed_data['Key'].apply(rename_key)
                
                combined_kv = [(row.Key, row.Value) for row in transposed_data.itertuples()]
                
                # Unique filename for screenshot
                unique_id = hashlib.md5(f"{page}_{index}".encode()).hexdigest()
                screenshot_path = os.path.join(screenshot_dir, f"{unique_id}.png")

                # Capture screenshot
                selenium_element = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, f"(//*[@data-cmp-clickable])[{index+1}]"))
                )
                driver.execute_script("arguments[0].scrollIntoView();", selenium_element)
                time.sleep(1)

                if selenium_element.screenshot(screenshot_path):
                    print(f"Screenshot saved to {screenshot_path}")

                # Store data
                all_clickable_data_layers.append({
                    'Combined KV': combined_kv,
                    'Screenshot Path': screenshot_path
                })
                processed_ids.add(component_id)

            except json.JSONDecodeError:
                print(f"Error decoding JSON for element at index {index}")
            except Exception as e:
                print(f"Error taking screenshot for element {index}: {e}")

# Convert data to DataFrame
data_layers_df = pd.DataFrame(all_clickable_data_layers)
print(data_layers_df.head())

# Create Excel file
workbook = xlsxwriter.Workbook("C:/Users/scott/Downloads/output.xlsx")
worksheet = workbook.add_worksheet("DataLayers")

# Write headers
worksheet.write(0, 0, "Key-Value Pairs")
worksheet.write(0, 1, "Screenshot")

# Define formats
bold_format = workbook.add_format({'bold': True})
wrap_format = workbook.add_format({'text_wrap': True})

# Set column widths
worksheet.set_column('A:A', 50)
worksheet.set_column('B:B', 30)

# Set max image dimensions
max_width = 150  # Adjust these values based on the desired max size
max_height = 100

# Track the tallest image height (in Excel row height units)
max_row_height = 0  

def insert_scaled_image(worksheet, img_path, row, col, max_width, max_height):
    global max_row_height  # Allow updating max row height across all rows

    if os.path.exists(img_path):
        with Image.open(img_path) as img:
            original_width, original_height = img.size

            # Calculate aspect ratio-preserving scaling factor
            scaling_factor = min(max_width / original_width, max_height / original_height)

            # Ensure the scaling factor is not greater than 1 (no upscaling)
            scaling_factor = min(scaling_factor, 1.0)

            # Calculate new dimensions
            img_width = original_width * scaling_factor
            img_height = original_height * scaling_factor

            # Convert pixel height to Excel row height (approximation: divide by 1.33)
            excel_row_height = img_height / 1.33  
            max_row_height = max(max_row_height, excel_row_height)  # Track largest row height

            # Set row height dynamically
            worksheet.set_row(row, excel_row_height)

        # Insert the image with proper scaling
        worksheet.insert_image(row, col, img_path, {
            'x_scale': scaling_factor,
            'y_scale': scaling_factor,
            'x_offset': 5,
            'y_offset': 5
        })
        print(f"Inserted image at row {row} with scaling factor {scaling_factor}, row height {excel_row_height}")


# Write data and add images
for idx, row in enumerate(data_layers_df.itertuples(index=False), start=1):
    kv_pairs = row[0]
    formatted_text = []
    
    for key, value in kv_pairs:
        formatted_text.append(bold_format)
        formatted_text.append(f"{key}: ")
        formatted_text.append(value + "\n")

    worksheet.write_rich_string(idx, 0, *formatted_text, wrap_format)

    # Insert image and track max row height
    img_path = row[1]
    insert_scaled_image(worksheet, img_path, idx, 1, max_width=200, max_height=150)

# Apply the largest row height to all rows
for row in range(1, len(data_layers_df) + 1):
    worksheet.set_row(row, max_row_height)

print(f"Set all rows to minimum height: {max_row_height}")


# Close workbook and driver
workbook.close()
driver.quit()
