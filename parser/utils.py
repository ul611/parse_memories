import json
import logging
import time
from typing import Dict, Iterable, List

from selenium import webdriver
from selenium.webdriver.common.by import By
from tqdm import tqdm

from config import QUERY_TYPE


def browser(url: str) -> webdriver.Chrome:
    """Create a new instance of the Chrome webdriver and navigate to a URL.
    Args:
        url (str): The URL to navigate to.
    Returns:
        driver (webdriver.Chrome): The instance of the Chrome webdriver.
    Raises:
        Exception: If there is an error while creating the browser instance."""
    try:
        driver = webdriver.Chrome()
        driver.get(url)
        return driver
    except Exception as e:
        logging.error(f'Error while creating browser instance: {str(e)}')
        raise e


def scrape_ids(driver: webdriver.Chrome, query_type: str, query_value: str) -> Dict[str, int]:
    """
    Scrapes data from the Pamyat Naroda website to collect unique IDs for photos of soldiers and officers
    who fought in the Soviet Army during World War II.
    Args:
        driver (webdriver.Chrome): The instance of the Chrome webdriver.
        query_type (str): The type of query to make on the website.
        query_value (int or str): The value to use in the query.
    Returns:
        count_ids (dict): A dictionary containing the number of IDs collected for each query type and value.
    Raises:
        None.
    """
    count_ids = {}
    url = f'https://foto.pamyat-naroda.ru/?mode=main&{query_type}={query_value}'

    driver.get(url)
    prev_len = 0
    while True:
        ids = set()
        try:
            els = driver.find_elements(By.CLASS_NAME, 'main__photo-item')

            # iterate through the list of elements and retrieve the data-id attribute for each one
            for i, el in enumerate(els):
                data_id = el.get_attribute('data-id')
                ids.add(data_id)

            # scroll down to the bottom of the page
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(1)  # this pause 100% works

            if len(ids) == prev_len:
                count_ids[query_value] = len(ids) - 1  # without None
                ids = [i for i in ids if i is not None]
                logging.info(f'{QUERY_TYPE[query_type]} {query_value}, number of ids {len(ids)}')
                with open(f'data/ids/ids_{QUERY_TYPE[query_type]}s.txt', 'a') as f:
                    print(*list(ids), sep='\n', file=f)
                break
            prev_len = len(ids)
        except Exception as e:
            logging.warning(f'Error while collecting ids by {QUERY_TYPE[query_type]}: {str(e)}')
            break

    return count_ids


def collect_ids(driver: webdriver.Chrome, query_type: str, query_values: Iterable) -> List[str]:
    """
    Collects IDs from the website using the specified query type and values.
    Args:
        driver (WebDriver): A Chrome webdriver instance.
        query_type (str): The type of query to use (e.g. "year" or "find").
        query_values (list): A list of values to use in the query.
    Returns:
        list: A list of collected IDs.
        """
    json_file_name = f'data/other/count_ids_by_{QUERY_TYPE[query_type]}.json'
    text_file_name = f'data/ids/ids_{QUERY_TYPE[query_type]}s.txt'
    count_dict = {}
    for query_value in tqdm(query_values):
        logging.info(f'Scraping ids for {query_type} {query_value}')
        count_ids = scrape_ids(driver, query_type, query_value)
        count_dict.update(count_ids)

    with open(json_file_name, 'w', encoding='utf-8') as f:
        json.dump(count_dict, f)

    with open(text_file_name, 'r') as f:
        ids = f.read().strip().split('\n')

    logging.info(f'{len(set(ids))} of unique ids by {query_type} were collected')
    print(f'{len(set(ids))} of unique ids by {query_type} were collected')

    return ids
