from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

url = "https://codeforces.com/contest/1985/submission/368355859"

driver = webdriver.Chrome()
driver.get(url)

code_element = WebDriverWait(driver, 20).until(
    EC.presence_of_element_located((By.ID, "program-source-text"))
)

print(code_element.text)

driver.quit()