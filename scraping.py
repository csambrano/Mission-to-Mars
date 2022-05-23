# Import Splinter and BeautifulSoup
from splinter import Browser
from bs4 import BeautifulSoup as soup
from webdriver_manager.chrome import ChromeDriverManager
import datetime as dt
import pandas as pd

def scrape_all():
    # Set-up Splinter
    executable_path = {'executable_path': ChromeDriverManager().install()}
    browser = Browser('chrome', **executable_path, headless=False)

    # set news title and paragraph variables
    news_title, news_paragraph = mars_news(browser)
    hemisphere_image_urls = hemisphere(browser)

     # Run all scraping functions and store results in dictionary
    data = {
        "news_title": news_title,
        "news_paragraph": news_paragraph,
        "featured_image": featured_image(browser),
        "facts": mars_facts(),
        "hemispheres": hemisphere_image_urls,
        "last_modified": dt.datetime.now()
    }

    # Stop webdriver and return data
    browser.quit()
    return data

def mars_news(browser): 

    # Visit the mars nasa news site
    url = 'https://redplanetscience.com'
    browser.visit(url)

    # Optional delay for loading the page
    browser.is_element_present_by_css('div.list_text', wait_time=1)

    # set up HTML parser
    html = browser.html
    news_soup = soup(html, 'html.parser')

    #Add try/except for error handling
    try: 
        slide_elem = news_soup.select_one('div.list_text')

        ##slide_elem.find('div', class_='content_title')

        # Use the parent element to find the first 'a' tag and save it as 'news_title'
        news_title = slide_elem.find('div', class_='content_title').get_text()

        # Use the parent element to find the paragraph text
        news_p = slide_elem.find('div', class_='article_teaser_body').get_text()

    except AttributeError:
        return None, None

    return news_title, news_p

# ### Featured Images 
def featured_image(browser):
    # Visit URL
    url = 'https://spaceimages-mars.com'
    browser.visit(url)

    # Find and click the full image button
    full_image_elem = browser.find_by_tag('button')[1]
    full_image_elem.click()

    # Parse the resulting html with soup
    html = browser.html
    img_soup = soup(html, 'html.parser')

    try: 
        # Find the relative image url
        img_url_rel = img_soup.find('img', class_='fancybox-image').get('src')
    
    except AttributeError:
        return None
    
    # Use the base URL to create an absolute URL
    img_url = f'https://spaceimages-mars.com/{img_url_rel}'
    
    return img_url

def mars_facts():
    try:
        df = pd.read_html('https://galaxyfacts-mars.com')[0]

    except BaseException:
        return None

    df.columns=['description', 'Mars', 'Earth']
    df.set_index('description', inplace=True)

    # convert dataframe back into HTML-ready code
    return df.to_html(classes="table table-striped")

def hemisphere(browser):
    url = 'https://marshemispheres.com/'
    browser.visit(url)

    hemisphere_image_urls = []

    for i in range(4):

        # Find and click hemisphere image buttons
        hemisphere_urls = browser.find_by_css('a.product-item h3')[i]
        hemisphere_urls.click()
        
        # Parse the resulting html with soup
        html = browser.html
        img_soup = soup(html, 'html.parser')
        
        list_item = img_soup.find('li')
        img_url_rel = url + list_item.find('a')['href']
        
        # look inside h2 tag for text w/ title 
        title_rel = img_soup.select_one('h2', class_='title').get_text()
        
        hemispheres = {"img_url": img_url_rel, "title": title_rel}
        
        # add to dictionary 
        hemisphere_image_urls.append(hemispheres)
        
        # return to url
        browser.back()
    
    return hemisphere_image_urls

if __name__ == "__main__":
    # If running as script, print scraped data
    print(scrape_all())

