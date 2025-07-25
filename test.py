from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

options = Options()
options.add_argument("--headless")  # Remove this line to see the browser open
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")

try:
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    driver.get("https://www.google.com")

    print("Page title:", driver.title)

    with open("google_page.html", "w", encoding="utf-8") as f:
        f.write(driver.page_source)

    driver.quit()
except Exception as e:
    print("❌ Error launching Selenium:", e)
