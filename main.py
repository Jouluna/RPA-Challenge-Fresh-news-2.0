import os
import json
import re
from datetime import datetime, timedelta
from RPA.Browser.Selenium import Selenium
from RPA.Excel.Files import Files
from RPA.HTTP import HTTP
from RPA.Robocloud.Items import Items

browser = Selenium()
excel = Files()
http = HTTP()
items = Items()

def get_work_item_variables():
    """
    Get the input work item variables.
    """
    items.get_input_work_item()
    search_phrase = items.get_work_item_variable("search_phrase")
    news_category = items.get_work_item_variable("news_category")
    months = items.get_work_item_variable("months")
    return search_phrase, news_category, months

def get_past_date(months):
    """
    Calculate the past date based on the number of months provided.
    """
    today = datetime.now()
    past_date = today - timedelta(days=30*months)
    return past_date

def count_matches_in_text(text, phrase):
    """
    Count the occurrences of a phrase in a text.
    """
    return text.lower().count(phrase.lower())

def contains_monetary_value(text):
    """
    Check if a text contains any monetary values.
    """
    money_patterns = ["\\$\\d+(\\.\\d{2})?", "\\d+\\s+USD", "\\d+\\s+dollars"]
    for pattern in money_patterns:
        if re.search(pattern, text):
            return True
    return False

def download_image(url, download_dir):
    """
    Download an image from the given URL and save it to the specified directory.
    """
    response = http.get(url)
    image_filename = url.split("/")[-1]
    image_path = os.path.join(download_dir, image_filename)
    with open(image_path, "wb") as image_file:
        image_file.write(response.content)
    return image_filename

def main():
    # Get parameters from work items
    search_phrase, news_category, months = get_work_item_variables()
    past_date = get_past_date(months)
    download_dir = "./output/images"
    os.makedirs(download_dir, exist_ok=True)

    # Open the AP News website and perform the search
    browser.open_available_browser("https://apnews.com")
    browser.input_text("id:search-field", search_phrase)
    browser.click_button("css:button[type='submit']")
    browser.wait_until_page_contains_element("css:.CardHeadline", timeout=10)
    
    news_list = []
    articles = browser.find_elements("css:.CardHeadline")
    for article in articles:
        title = browser.get_text(article.find_element_by_css_selector(".CardHeadline__title"))
        date = browser.get_text(article.find_element_by_css_selector(".Timestamp"))
        description = browser.get_text(article.find_element_by_css_selector(".CardHeadline__content"))
        image_url = article.find_element_by_css_selector("img").get_attribute("src")

        if datetime.strptime(date, "%B %d, %Y") < past_date:
            continue

        count = count_matches_in_text(title, search_phrase)
        contains_money = contains_monetary_value(title)
        image_file = download_image(image_url, download_dir)

        news_list.append([title, date, description, image_file, count, contains_money])

    # Save the results to an Excel file
    excel.create_workbook("output/news_data.xlsx")
    excel.append_worksheet(news_list, header=["Title", "Date", "Description", "Image Filename", "Phrase Count", "Contains Money"])
    excel.save_workbook()

    # Close the browser
    browser.close_all_browsers()

if __name__ == "__main__":
    main()

