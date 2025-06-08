import csv
import time
import json
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager

# List of suburbs to process
suburbs = [
    "abbotsford-vic-3067",
    "aberfeldie-vic-3040",
    "ascot-vale-vic-3032",
    "mont-albert-vic-3127"
    # Add all your other suburbs here
]

# The base URL for the API
base_url = "https://sales-events-api.realestate.com.au/sales-events/location/"
output_file = "real_estate_private_sales.csv"

# --- UPDATED Selenium Setup for Headless Environment ---
options = webdriver.ChromeOptions()
options.add_argument('--headless')  # Must run in headless mode in this environment.
options.add_argument('--no-sandbox') # Security feature that is often required in containers.
options.add_argument('--disable-dev-shm-usage') # Overcomes limited resource problems.
options.add_argument('--log-level=3') # Suppresses console messages from the driver

# This automatically downloads and manages the correct driver for your Chrome browser
service = ChromeService(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=options)

print("Selenium WebDriver initiated in headless mode.")

# Open the CSV file for writing
with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
    csv_writer = csv.writer(csvfile)
    csv_writer.writerow(["Suburb", "Address", "Price"])

    # Loop through each suburb
    for suburb_slug in suburbs:
        url = f"{base_url}{suburb_slug}"
        print(f"Processing {suburb_slug}...")

        try:
            # Tell the browser to go to the URL
            driver.get(url)

            # The data is inside a <pre> tag. We find the element.
            pre_element = driver.find_element(By.TAG_NAME, 'pre')
            json_text = pre_element.text

            # Now that we have the text, parse it as JSON
            data = json.loads(json_text)
            
            # --- Extract data just like before ---
            suburb_name = data.get("data", {}).get("suburb", {}).get("name", "N/A")
            private_sales = data.get("data", {}).get("privateSaleResults", [])

            if not private_sales:
                print(f"-> No private sales found for {suburb_name}.")
            else:
                for sale in private_sales:
                    address = sale.get("listing", {}).get("address", "N/A")
                    price = sale.get("price", {}).get("display", "N/A")
                    csv_writer.writerow([suburb_name, address, price])
            
            print(f"-> Successfully processed {suburb_name}")

        except Exception as e:
            print(f"-> An error occurred while processing {suburb_slug}: {e}")

        # A polite pause between requests is still a good idea
        time.sleep(3)

# Close the browser once done
driver.quit()

print(f"\nData processing complete. Results are in {output_file}")
