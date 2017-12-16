__author__ = 'Rizwan Hameed'
__date__ = 'October 29, 2017'
"""
Check out my main scraping projects !
https://www.youtube.com/playlist?list=PLh2kzLvQxb76sv7s6aUB6378zy4Tkpzv0
"""
import re
from bs4 import BeautifulSoup
from selenium import webdriver
import time
import pythonLib
import os
import random


# function to start browsing and getting page soup
def request(url, driver):
    driver.maximize_window()
    driver.get(url)
    time.sleep(random.randint(2, 3) * .931467298)

    return driver


# function to make soup
def make_soup(driver):
    page = driver.page_source
    soup = BeautifulSoup(page, "html5lib")
    return soup


def save_links(link, links_file):
    if os.path.exists(links_file) == False:
        headings = ["link"]
        pythonLib.save_to_csv(links_file, headings)

    pythonLib.save_to_csv(links_file, link)


def save_data(data, output_file):
    if os.path.exists(output_file) == False:
        headings = ["URL", "Title", "Company", "Location", "Requirements", "Posted on", "Description"]
        pythonLib.save_to_csv(output_file, headings)

    pythonLib.save_to_csv(output_file, data)


#function to read seach keywords text file
def read_search_words(search_words_file):
    lines = list()
    with open(search_words_file) as f:
        lines = f.readlines()
        f.close()

    return [line.strip() for line in lines]


#function to parse search page of jobs
def parse_search_page(jobs_links, jobs_data_file, done_links_file):

    for link in jobs_links:
        print("Visiting URL: "+str(link))

        #Extracting data
        soup = pythonLib.request_fun(link)
        
        heading_panel = soup.find("div", {"class":"panel-heading"})

        try:
            job_title = heading_panel.find("h1", {"class":"panel-title"}).get_text().strip()
        except:
            job_title = ""

        try:
            company = heading_panel.find_all("h2", {"class":"panel-title"})[0].get_text().strip()
        except:
            company = ""
        try:    
            location = heading_panel.find_all("h2", {"class":"panel-title"})[1].get_text().strip()
        except:
            location = ""

        try:
            posted_date_count = heading_panel.find("p", {"class": "text-sm"}).find("span")["count"]
        except:
            posted_date_count = -1
            
        posted_date = ""
        if posted_date_count == 0:
            posted_date = "Today"
        elif posted_date_count == 1:
            posted_date = "1 day ago"
        elif posted_date_count == -1:
            posted_date = ""
        else:
            posted_date = "{0} days ago".format(posted_date_count)

        body_panel = soup.find("div", {"class":"panel-body"})

        try:
            job_description = body_panel.find("h3", {"class": "header-ribbon"}).find_next_siblings('p')[0].get_text().strip()
        except:
            job_description = ""
        try:
            job_requirements = body_panel.find("h4", {"class": "header-ribbon"}).find_next_siblings('p')[0].get_text().strip()
        except:
            job_requirements = ""

        #Saving data
        data = [link, job_title, company, location, job_requirements, posted_date, job_description]
        save_data(data, jobs_data_file)

        #Saving job link in done file
        save_links([link], done_links_file)

        time.sleep(random.randint(1, 2) * .931467298)


## main function...
def start_extraction(main_url, search_words, jobs_data_file, done_keywords_file, done_links_file):

    driver = webdriver.PhantomJS()
    print("Reading done files data...")
    done_keywords = pythonLib.read_col_csv(done_keywords_file, 0)
    
    for search_word in search_words:
        done_links = pythonLib.read_col_csv(done_links_file, 0)
        print("Search: ", search_word)
        if search_word in done_keywords:
            print(search_word + ": already searched !")
        else:
            driver = request(main_url, driver)

            fldInput = driver.find_element_by_xpath("//input[@name='pos_ref']")
            fldInput.clear()
            pythonLib.click_send(driver, fldInput, search_word)

            search_click = driver.find_element_by_xpath("//button[@type='submit' and contains(text(), 'Search')]")
            pythonLib.click(driver, search_click)
            time.sleep(random.randint(2, 3) * .931467298)

            soup = make_soup(driver)
            print("Extracting Jobs...")
            next_page = True
            while next_page:
                try:
                    search_container = soup.find("div", {"id": "facetedSearchResults"}).find('table').find('tbody')
                    search_list = search_container.find_all('tr')
                except:
                    print("No job found.")
                    search_list = list()
                
                job_links= list()
                for job in search_list:
                    a_tag = job.find('a')['href']
                    job_link = 'https://www.gulftalent.com' + a_tag
                    job_links.append(job_link)

                parse_search_page(job_links, jobs_data_file, done_links_file)

                try:
                    next_element = soup.find("ul", {"class": "pagination"}).find_all('li')[-2]
                    if 'disabled' in next_element['class']:
                        print("Next Page not found")
                        next_page = False
                    else:
                        print("Loading Next Page...")
                        #driver.execute_script("document.getElementsByClassName('pagination')[0].getElementsByTagName('a')[6].click()")
                        driver.execute_script("document.getElementsByClassName('pagination')[0].getElementsByTagName('a')[document.getElementsByClassName('pagination')[0].getElementsByTagName('a').length - 2].click();")
                        time.sleep(random.randint(2, 3) * .931467298)
                        soup = make_soup(driver)
                except Exception as error:
                    print("Next Page not found1")
                    next_page = False

            print(search_word + ": search completed !")
            save_links([search_word], done_keywords_file)

    driver.quit()


if __name__ == '__main__':
    done_keywords_file = "done_files/done_keywords.csv"
    done_links_file = "done_files/done_links.csv"
    search_words_file = "search_keywords.txt"
    jobs_data_file = "jobs_data.csv"

    search_words = read_search_words(search_words_file) #Search Keywords

    main_url = "https://www.gulftalent.com/jobs/search?pos_ref=IT+jobs&frmPositionCountry=10111112000000#!?category=&industry=&seniority=&country=&city=&keyword=IT%20jobs"
    start_extraction(main_url, search_words, jobs_data_file, done_keywords_file, done_links_file)
