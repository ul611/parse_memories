#!/usr/bin/env python
# coding: utf-8

"""
This script scrapes data from the Pamyat Naroda website
(https://foto.pamyat-naroda.ru/) to collect unique IDs for
photos of soldiers and officers who fought in the Soviet
Army during World War II.

The script first collects IDs by year and saves them to a file.
Then, it collects IDs by name and saves them to another file.
It also counts the number of unique IDs by year and by name,
and save this information in the files.

Finally, it prints the total number of unique IDs collected.
"""
import datetime
import logging
import os

from selenium.webdriver.common.by import By
from tqdm import tqdm

from utils import browser, collect_ids
from config import URL_FOR_NAMES, URL_FOR_IDS

# Configure logging
log_dir = 'logs'
if not os.path.exists(log_dir):
    os.mkdir(log_dir)

log_dir = os.path.join(log_dir, datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S'))
os.mkdir(log_dir)

logging.basicConfig(
    filename=os.path.join(log_dir, 'scraping.log'),
    level=logging.INFO,
    format='%(asctime)s:%(levelname)s:%(message)s'
)

# Collect names
print('Starting')
logging.info('Starting scraping links to every letter')
with browser(URL_FOR_NAMES) as driver:
    # collect letters
    letters = driver.find_elements(By.CLASS_NAME, 'list_alphabet_item')
    links_letter_by_letter = []

    for letter in letters[:2]: ######### letters
        link = letter.find_element(By.XPATH, './/a').get_attribute('href')
        links_letter_by_letter.append(link)

    logging.info('Finished scraping links to every letter')

    # collect names
    names = []
    logging.info('Starting collecting names')
    print('Collecting names')
    for link in tqdm(links_letter_by_letter):
        driver.get(link)
        names_els = driver.find_elements(By.CLASS_NAME, 'position_title')
        for names_el in names_els:
            names.append(names_el.text)
    logging.info('Finished collecting names')


# save names to the file
with open('data/other/names.txt', 'w') as f:
    print(*names, sep='\n', file=f)

logging.info(f'{len(names)} unique names collected')


with browser(URL_FOR_IDS) as driver:
    print('Collecting ids by year')
    ids_by_year = collect_ids(driver, 'year', range(1874, 2000))  # range(1874, 1880) for test mode
    print('Collecting ids by name')
    ids_by_name = collect_ids(driver, 'find', names)  # names[9:11] for test mode

    n_unique_ids = len(set(ids_by_year).union(ids_by_name))

    logging.info(f'{n_unique_ids} of unique ids were collected')
    print(f'{n_unique_ids} of unique ids were collected')

print('Program finished')
logging.info('Program finished')
