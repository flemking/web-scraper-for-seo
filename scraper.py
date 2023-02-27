from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
import time
from datetime import datetime
from urllib.parse import urlparse
import re
PATH = "./chromedriver"


driver = webdriver.Chrome(service=Service(PATH))


def find_and_scrap_url(selected_url):
    kw1 = selected_url[0]
    kw2 = selected_url[1]
    camp_url = selected_url[2]

    # Scraping Start
    google_url = "http://www.google.com/search?q="+kw2+"&oq="+kw1
    driver.get(google_url)

    max_google_pages = 10
    page_number = 0
    url_found = False
    outputData = {
        "url": camp_url,
        "keywords": selected_url[1] + ", " + selected_url[0],
        "found": url_found,
        "found_page": page_number,
        "contact_page_found": False,
        "emails_found": [],
    }

    # try:
    # ? modifier la variable 'max_google_pages' pour changer le noombre maximum de page Google à scraper
    for i in range(max_google_pages):
        results = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "res"))
        )
        next_page = driver.find_element(By.ID, "pnnext")
        result_urls = results.find_elements(By.TAG_NAME, "cite")

        for result in result_urls:
            if camp_url in result.text:
                # ? result.click() ne fonctionne pas donc j'utilise diver.execute_script
                driver.execute_script("arguments[0].click()", result)
                page_number += 1
                url_found = True
                outputData["found"] = True
                outputData["found_page"] = page_number
                print("Website found on page:", page_number)
                break
            else:
                page_number += 1
                pass

        if url_found == True:
            break

        driver.execute_script("arguments[0].click()", next_page)
        time.sleep(5)

    time.sleep(5)
    driver.maximize_window()
    scrool_up_and_down()

    # finding some contact links
    body = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.TAG_NAME, "body"))
    )
    website_links = body.find_elements(
        By.CSS_SELECTOR, f"a[href*='contact']")
    for link in website_links:
        if link.text == "" or link.text == "#" or link.text == camp_url:
            continue
        else:
            # link.click() | not working so I used JS to click the button
            outputData["contact_page_found"] = True
            driver.execute_script("arguments[0].click()", link)
            break

    # ? Resetting body
    new_body = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.TAG_NAME, "body"))
    )
    emails = new_body.find_elements(By.CSS_SELECTOR, f"a[href*='mailto']")
    for email in emails:
        if email.text == "" or email.text == "#" or email.text == camp_url:
            continue
        else:
            # link.click() | not working so I used JS to click the button
            match = re.search(r'[\w.+-]+@[\w-]+\.[\w.-]+',
                              email.get_attribute('href'))
            found = match.group(0)

            outputData["emails_found"].append(found)
            print("✅ Email found:", found)

    # ! checking if we entered a new page before returning back
    time.sleep(5)
    if (outputData["contact_page_found"]):
        driver.back()
        scrool_up_and_down()

    # ? exxporting the data in a .md file
    exporting(outputData)

    time.sleep(5)
    # finally:
    #     time.sleep(10)
    #     driver.quit()


# ? Fontionalite scrolling
def scrool_up_and_down(downspeed=20, upspeed=10):
    # ? Scrolling feature - plus grand sont les arguments et plus smooth est le scroll
    screen_height = driver.execute_script("return document.body.scrollHeight")

    for i in range(downspeed):
        driver.execute_script(
            f"window.scrollBy(0, {str(screen_height/downspeed)})")
        time.sleep(0.2)
    for i in range(upspeed):
        driver.execute_script(
            f"window.scrollBy(0, -{str(screen_height/upspeed)})")
        time.sleep(0.5)


# ? exporting as a txt file
def exporting(data):
    currentDateTime = datetime.now().strftime("%Y%m%d-%H%M%S")
    path = f"./stats/{urlparse(data['url']).netloc}-stats_{currentDateTime}.md"
    message = f"""
# Stats du site <{data['url']}>

## Keywords utiliser: {data["keywords"]}

- {f"🚀 Super, le site web à été trouvé sur la page Nº{data['found_page']}" if data['found'] else "😶‍🌫️ Désolé, votre page n'est pas correctement référencée."}
- {"🔻 Les réglages SEO de votre page peuvent être encore améliorés." if data['found_page'] > 1 else "🥇 Bon travail, vous êtes sur la première page de Google !!!"}
- {"✅ Page de contact trouvé!" if data['contact_page_found'] else "🔻 Page de Contact non trouvé!"}
- {f"✅ Emails trouves: {', '.join(data['emails_found'])}" if len(data['emails_found']) > 0 else "🔻 Emails non trouvé!"}
"""
    with open(path, "w") as f:
        f.write(message)


if __name__ == "__main__":
    sites = [
        ["tesla", "tesla contact", "https://www.tesla.com"],
        ["cours en ligne en france", "openclassroom", "https://openclassrooms.com"],
    ]
    try:
        for site in sites:
            find_and_scrap_url(site)
    finally:
        time.sleep(10)
        driver.quit()
