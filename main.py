from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
import time
from webdriver_manager.chrome import ChromeDriverManager
import requests as req
from bs4 import BeautifulSoup
import models as m

# List of NIPTs to search for
nipt_list = ['your-nipt-1', 'your-nipt-2', 'your-nipt-3']  # Replace with actual NIPTs

# Headless Chrome Setup
chrome_options = Options()
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument("--disable-setuid-sandbox")
chrome_options.add_argument("--headless")  # Run in headless mode
chrome_options.add_argument("--disable-dev-shm-usage")  # To avoid running out of memory
chrome_options.add_argument("--remote-debugging-port=9222")

# Initialize WebDriver with ChromeDriverManager (no need for manual path)
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

# URL for the QKB business search page
web_url = 'https://qkb.gov.al/kerko/kerko-ne-regjistrin-tregtar/kerko-per-subjekt/'

# Iterate over the NIPTs
for nipt in nipt_list:
    driver.get(web_url)

    # Enter NUI (Nipt) into the input field
    nui_input = driver.find_element(By.ID, 'Nipt')
    nui_input.clear()  # Clear the input field before typing
    nui_input.send_keys(nipt)  # Replace with the NIPT

    # Optionally, you can fill in other fields if necessary
    txtSubjectName = driver.find_element(By.ID, 'SubjectName')
    txtSubjectName.send_keys('')  # Leave empty if you don't want to filter by Subject Name

    txtTradeName = driver.find_element(By.ID, 'ObjectDesc')
    txtTradeName.send_keys('')  # Leave empty if you don't want to filter by Trade Name

    txtFullAddress = driver.find_element(By.ID, 'FullAddress')
    txtFullAddress.send_keys('')  # Leave empty if you don't want to filter by Address

    txtIdentificationNumber = driver.find_element(By.ID, 'IdentificationNumber')
    txtIdentificationNumber.send_keys('')  # Leave empty if you don't want to filter by ID number

    # Wait until the submit button is clickable, then click it
    submit_button = driver.find_element(By.CSS_SELECTOR, 'input[type="submit"]')

    # Wait until the submit button is clickable using WebDriverWait
    WebDriverWait(driver, 10).until(EC.element_to_be_clickable(submit_button))

    # Option 1: Scroll to the element if it's hidden or covered
    driver.execute_script("arguments[0].scrollIntoView();", submit_button)

    # Option 2: Click using ActionChains if the element is not clickable directly
    action = ActionChains(driver)
    action.move_to_element(submit_button).click().perform()

    # Wait for the results to load
    time.sleep(3)

    # Switch to the results page window (if necessary)
    for handle in driver.window_handles:
        driver.switch_to.window(handle)

    # Extract the business information from the resulting page
    try:
        row = driver.find_element(By.CSS_SELECTOR, 'table.results-table tbody tr td a')  # Modify as needed
        response = req.get(row.get_attribute('href'))
        soup = BeautifulSoup(response.text, 'lxml')

        business_data_table = soup.select('table.business-info-table')  # Modify as necessary
        business_data = business_data_table[0].select('tbody tr')

        business = m.BusinessInfo()

        # Extracting data from the table (adjust selectors as needed)
        business.Name = business_data[0].select('td > span')[0].getText().strip()
        business.TradeName = business_data[1].select('td > span')[0].getText().strip()
        business.Type = business_data[2].select('td > span')[0].getText().strip()
        business.NUI = business_data[3].select('td > span')[0].getText().strip()
        business.BusinessNo = business_data[4].select('td > span')[0].getText().strip()
        business.FiscalNo = business_data[5].select('td > span')[0].getText().strip()
        business.NoOfEmployees = business_data[7].select('td > span')[0].getText().strip()
        business.RegistrationDate = business_data[8].select('td > span')[0].getText().strip()
        business.Municipality = business_data[9].select('td > span')[0].getText().strip()
        business.Address = business_data[10].select('td > span')[0].getText().strip()
        business.PhoneNo = business_data[11].select('td > span')[0].getText().strip()
        business.Email = business_data[12].select('td > span')[0].getText().strip()
        business.KBRAStatus = business_data[14].select('td > span')[0].getText().strip()
        business.TAKStatus = business_data[16].select('td > span')[0].getText().strip()
        business.BaseURL = row.get_attribute('href')

        # Print the business data for each NIPT
        print(f"Results for NIPT: {nipt}")
        print(business)

    except Exception as e:
        print(f"Error extracting business data for NIPT {nipt}: {e}")

# Close the browser
time.sleep(3)
driver.quit()
