import os
import re
import logging
import xlsxwriter
from robocorp.tasks import task
from datetime import datetime, timedelta
from RPA.Browser.Selenium import Selenium
from RPA.Excel.Files import Files
from RPA.HTTP import HTTP
from RPA.Robocloud.Items import Items
from selenium.webdriver.support.ui import Select

#Libraries I'm using
browser = Selenium()
excel = Files()
http = HTTP()
items = Items()

#Initialize log
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def get_variables():
    """Getting item variables from config."""
    # items.get_input_work_item()
    # search_phrase = items.get_work_item_variable("search_phrase")
    # months = items.get_work_item_variable("months")
    # category = items.get_work_item_variable("category")
    # return search_phrase, category, months"""

    items.get_input_work_item() # Added exception in case the work items cannot be fetch.
    try:
        search_phrase = items.get_work_item_variable("search_phrase")
    except KeyError:
        logging.warning("search_phrase not found in work item. Using default value.")
        search_phrase = "Tech"

    try:
        category = items.get_work_item_variable("news_category")
    except KeyError:
        logging.warning("news_category not found in work item. Using default value.")
        category = "Tech"  # If not found it uses a default value I set here
    
    try:
        months = items.get_work_item_variable("months")
    except KeyError:
        logging.warning("months not found in work item. Using default value.")
        months = 1  # If not found it uses a default value I set here
    
    logging.info(f"Work item variables - search_phrase: {search_phrase}, news_category: {category}, months: {months}")
    return search_phrase, category, months

def get_date(months):
    """This will define the date the bot should stop getting records from."""
    current_date = datetime.now()
    stop_date = current_date - timedelta(days = 30 * months) 
    return stop_date

def count_matches(text, phrase):
    """Will count how many times the seach phrase is in the page."""
    return text.lower().count(phrase.lower())

def contains_money(text):
    """Will chaeck if theres any money patterns."""
    """Regular expression below."""
    money_pattern = ["\\$\\d+(\\.\\d{2})?", "\\d+\\s+USD", "\\d+\\s+dollars"]
    
    """This will check if any text matches the regex."""
    for pattern in money_pattern:
        if re.search(pattern, text):
            return True
        return False

def dowload_image(url, download_dir):
    """Download the image from an URL and saves it to a directory especified."""
    response = http.get(url)

    """Just following naming patterns we take whatever goes in the url."""
    image_filename = url.split("/")[-1]
    image_path = os.path.join(download_dir, image_filename)
    with open(image_path, "wb") as image_file:
        image_file.write(response.content)
    return image_filename

def process_article(article, past_date, download_dir, search_phrase): # I added this function I had originally in main since it might crash due to DOM changes. I was getting a stale element issue before.
    """Processing articles in the website."""
    try:
        # I will relocate elements for arach article to prevent the stale issue
        title_element = browser.find_element("css:.PagePromo-title", parent=article)
        date_element = browser.find_element("css:.Timestamp-template", parent=article)
        description_element = browser.find_element("css:.PagePromo-description", parent=article)
        
        try: # In case there are no images in the container of the news the bot will just keep going.
            image_element = browser.find_element("css:img", parent=article)
        except Exception:
            logging.warning("No image found in current 'article'.")
            image_element = None

        title = title_element.text if title_element else ""
        date = date_element.text if date_element else ""
        description = description_element.text if description_element else ""

        logging.info(f"Processing article: {title} - {date}") # Debugging

        # The page sometimes does not have a valid date in the footer of the news, for example it uses the word now 
        # or 1 hour ago (etc), however to keep the process going I will simply create a try catch so that it continues
        # for any of the cases that use words just keep moving on since I haven't found all the cases for this website's 
        # footer nor they are documented most probably there might be other labels I have not seen yet, so to prevent any 
        # malfunction I will just keep it simple for this bot. The page only uses these for recent posts so they are still
        # under the date scope we want
        
        # Some dates use words lie xx time ago, I will parse these as today so that the validation can still continue on since there are too many cases. However the
        # date using the 'newest' filter we select previous to this method execution does keep the scope within the same year we are so we don't fall off the scope anyways.
        try: 
            article_date = datetime.strptime(date, "%B %d")
        except ValueError:
            logging.warning("Date format not recognized, setting to current timestamp.")
            article_date = datetime.now()

        if article_date < past_date:
            logging.info(f"Article '{title}' is older than {past_date}. Skipping.")
            return None  # Skip this article if it is older than the date I calculated

        image_url = image_element.get_attribute("src") if image_element else ""
        count = count_matches(title, search_phrase)
        contains_money_flag = contains_money(title)
        image_file = dowload_image(image_url, download_dir) if image_url else ""

        return[title, date, description, image_file, count, contains_money_flag]

    except Exception as e:
        logging.error(f"Error processing article: {str(e)}")
        return None

def write_to_excel(news_list, file_path): # Created to substitute the RPA.Excel.Files method 
    """Write news list to an Excel file using xlsxwriter."""
    workbook = xlsxwriter.Workbook(file_path)
    worksheet = workbook.add_worksheet("News Articles")

    # Header of the file as to the challenge instructions
    headers = ["Title", "Date", "Description", "Image Filename", "Phrase Matches", "Has Money"]
    for col_num, header in enumerate(headers):
        worksheet.write(0, col_num, header)

    # Writing all the news data
    for row_num, row_data in enumerate(news_list, start=1):
        for col_num, cell_data in enumerate(row_data):
            worksheet.write(row_num, col_num, cell_data)

    workbook.close()

@task
def minimal_task():
    # Filling all necessary variables from workitems.
    search_phrase, category, months = get_variables()
    past_date = get_date(months)
    download_dir = "./output/images"
    os.makedirs(download_dir, exist_ok=True)

    """Opening ap news."""
    # I am using generic ids to identify the places the bot should
    # input text at however these may change according to the website.
    browser.open_available_browser("https://apnews.com")
    browser.click_element('xpath:/html/body/div[2]/bsp-header/div[2]/div[3]/bsp-search-overlay/button')
    browser.input_text("xpath:/html/body/div[2]/bsp-header/div[2]/div[3]/bsp-search-overlay/div/form/label/input", search_phrase)
    browser.click_button("xpath:/html/body/div[2]/bsp-header/div[2]/div[3]/bsp-search-overlay/div/form/button")
    
    # make the bot wait until a page loads the container with the news.
    browser.wait_until_page_contains_element("css:.SearchResultsModule-main", timeout=10) # This module is the container of all the news results.

    # Setting the page filter to the newest articles so that we can
    # go back from that point.
    dropdown = browser.find_element("xpath:/html/body/div[3]/bsp-search-results-module/form/div[2]/div/bsp-search-filters/div/main/div[1]/div/div/div/label/select")
    select = Select(dropdown)
    select.select_by_visible_text("Newest")
    browser.wait_until_page_contains_element("css:.SearchResultsModule-main", timeout=15)

    """Getting all articles."""
    news_list = []
    articles = browser.find_elements("css:.PageList-items-item")
    logging.info(f"Found {len(articles)} articles.") # Debugging
    for index, article in enumerate(articles):
        logging.info(f"Processing article {index + 1}/{len(articles)}")
        processed_article = process_article(article, past_date, download_dir, search_phrase)
        if processed_article:
            news_list.append(processed_article)

    logging.info(f"Processed {len(news_list)} articles.") # Debugging
    logging.info(f"news_list contents: {news_list}") # Debugging

    """Getting excel file ready"""
    # The RPA.Excel.Files was not working correctly so I substitued it with xlsxwriter,
    # seems a function was deprecated 'write_worksheet' since it was not resolvable in
    # the latest version.

    # Before xlsxwriter:
    # excel.create_workbook("output/fresh_news.xlsx")
    # excel.write_worksheet(news_list, header=["Title", "Date", "Description", "Image Filename", "Phrase Matches", "Has Money"])
    # excel.save_workbook()
    # excel.close_workbook()

    # Write news in array to Excel file
    write_to_excel(news_list, "output/fresh_news.xlsx")

    # Close the browser
    browser.close_all_browsers()

# Making sure the task can be run, for testing
if __name__ == "__main__":
    minimal_task()