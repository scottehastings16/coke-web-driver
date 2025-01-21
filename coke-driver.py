import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import json
from pandas import json_normalize
import os
import xlsxwriter
from PIL import Image
import hashlib

# Initialize the WebDriver
driver = webdriver.Chrome()

# List of URLs to scrape
my_urls = [
"https://www.coca-cola.com/us/en",
# Add other URLs here...
]

# Create a directory for screenshots if it doesn't exist
screenshot_dir = "screenshots"
os.makedirs(screenshot_dir, exist_ok=True)

# Data storage
all_clickable_data_layers = []

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

# Wait for the cookie consent button to be present and click it
try:
    accept_button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.ID, "close-pc-btn-handler"))
    )
    accept_button.click()
    print("Cookie consent accepted.")
except Exception as e:
    print(f"Cookie consent button not found or not clickable: {e}")

# Use BeautifulSoup to parse the page source
soup = BeautifulSoup(driver.page_source, 'html.parser')

# Find all elements with the data-cmp-clickable attribute
clickable_elements = soup.find_all(attrs={"data-cmp-clickable": True})

# Debug: Print number of clickable elements found
print(f"Found {len(clickable_elements)} clickable elements on {page}")

# Extract and flatten data-cmp-data-layer JSON from each element
for index, element in enumerate(clickable_elements):
    data_layer = element.get('data-cmp-data-layer')
    if data_layer:
        try:
            # Parse the JSON string into a Python dictionary
            data_layer_dict = json.loads(data_layer)
            
            # Debug: Print the parsed JSON
            print(f"Parsed JSON for element {index}: {data_layer_dict}")
            
            # Flatten the JSON and append it to the list
            flattened_data = json_normalize(data_layer_dict)
            flattened_data['page_url'] = page  # Add the page URL to each row
            
            # Transpose the DataFrame to have keys and values in rows
            transposed_data = flattened_data.T.reset_index()
            transposed_data.columns = ['Key', 'Value']
            transposed_data['Element Index'] = index
            transposed_data['Page URL'] = page
            
            # Rename keys using the custom function
            transposed_data['Key'] = transposed_data['Key'].apply(rename_key)
            
            # Combine key-value pairs into a list of tuples
            combined_kv = [(row.Key, row.Value) for row in transposed_data.itertuples()]
            
            # Generate a unique filename using hash
            unique_id = hashlib.md5(f"{page}_{index}".encode()).hexdigest()
            screenshot_path = os.path.join(screenshot_dir, f"{unique_id}.png")
            
            # Locate the element using Selenium and take a screenshot
            selenium_element = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, f"(//*[@data-cmp-clickable])[{index+1}]"))
            )
            
            # Scroll the element into view
            driver.execute_script("arguments[0].scrollIntoView();", selenium_element)
            
            # Capture the screenshot
            if selenium_element.screenshot(screenshot_path):
                print(f"Screenshot saved to {screenshot_path}")
            else:
                print(f"Failed to save screenshot for element at index {index}")
            
            # Store the combined data and screenshot path
            all_clickable_data_layers.append({
                'Combined KV': combined_kv,
                'Screenshot Path': screenshot_path
            })
            
        except json.JSONDecodeError:
            print(f"Error decoding JSON for element: {element}")
        except Exception as e:
            print(f"Error taking screenshot for element: {element}, Error: {e}")

# Convert the collected data into a DataFrame
data_layers_df = pd.DataFrame(all_clickable_data_layers)

# Debug: Print the DataFrame to verify its content
print(data_layers_df.head())

# Create a new workbook using xlsxwriter
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

# Set maximum dimensions for images
max_width = 100  # Max width in pixels
max_height = 50  # Max height in pixels

# Write data and add images
for idx, row in enumerate(data_layers_df.itertuples(index=False), start=1):  # Start at row 1 (0-based index)
    kv_pairs = row[0]
    formatted_text = []
    for key, value in kv_pairs:
        formatted_text.append(bold_format)
        formatted_text.append(f"{key}: ")
        formatted_text.append(value + "\n")

    worksheet.write_rich_string(idx, 0, *formatted_text, wrap_format)

    img_path = row[1]  # Access the Screenshot Path
    if os.path.exists(img_path):
        # Open the image to get its size
        with Image.open(img_path) as img:
            original_width, original_height = img.size
            scaling_factor = min(max_width / original_width, max_height / original_height, 1)
            img_width = int(original_width * scaling_factor)
            img_height = int(original_height * scaling_factor)

        # Insert the image starting at the top-left corner of the cell
        worksheet.insert_image(idx, 1, img_path, {
            'x_scale': scaling_factor,
            'y_scale': scaling_factor,
            'x_offset': 0,  # Align to the left edge of the cell
            'y_offset': 0   # Align to the top edge of the cell
        })
        print(f"Image added to Excel at row {idx}")

# Close the workbook
workbook.close()

# Close the WebDriver
driver.quit()
