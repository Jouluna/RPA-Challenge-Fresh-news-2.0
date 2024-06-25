# Automated AP News Extraction
This project aims to automate the extraction of news articles from the Associated Press (AP) website using web scraping techniques in Python.

Roadblocks and Issues Encountered
1. Website Structure Changes
The AP website's HTML structure changed periodically, requiring frequent updates to our scraping scripts to ensure compatibility. Also they use a dynamic HTML and CSS for parts with images, or in this case when they reach a resolution o XX * XX pixels so handling that was kinda troublesome. Still it seems the page does that on purpose to prevent or difficult the scrapping of their website.

2. Force Reloads and Rate Limiting
Forced reloads and rate limiting, it required implementing delays and modifyng the mechanisms in the code a lot. Mostly because due to DOM, since I kept having issues with stale selectors due to the page refreshing specific parts of the website.

3. Data Formatting Consistency
Ensuring consistent formatting of extracted data (such as headlines, dates, and article content) proved challenging due to variations in HTML tags and content presentation across different articles.

# Template: Python - Minimal
This project was created for the Fresh News challenge for the recrutiing process. 

Despite these challenges, the project provided to be quite a learning experience in how websites behave these days, also a good intro into web scraping techniques and data extraction processes. Addressing the roadblocks required quite a few tries for solutions and meticulous attention to detail. 

At the end, it was a fun.

#  ,-.       _,---._ __  / \
# /  )    .-'       `./ /   \
#(  (   ,'            `/    /|
# \  `-"             \'\   / |
#  `.              ,  \ \ /  |
#   /`.          ,'-`----Y   |
#  (            ;        |   '
#  |  ,-.    ,-'         |  /
#  |  | (   |            | /
#  )  |  \  `.___________|/
#  `--'   `--'
