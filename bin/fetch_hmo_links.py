#!/usr/bin/env python

import csv
import datetime

# Geckodriver: https://github.com/mozilla/geckodriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver import Firefox
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support.ui import Select

timestamp = datetime.datetime.now().strftime("%Y-%m-%d-%H%M%S")
DATAFILE = f"data/hmo-links-{timestamp}.csv"

WARDS = [
    "CENGRE",  # Central Greenford
    "DORWE",  # Dormers Wells
    "EALBDY",  # Ealing Broadway
    "EALCOM",  # Ealing Common
    "EASACT",  # East Acton
    "GREBDY",  # Greenford Broadway
    "HANHIL",  # Hanger Hill
    "HANBDY",  # Hanwell Broadway
    "LDYMAR",  # Lady Margaret
    "NORACT",  # North Acton
    "NORGRE",  # North Greenford
    "NORHAN",  # North Hanwell
    "NORFLD",  # Northfield
    "NORMAN",  # Northolt Mandeville
    "NORWED",  # Northolt West End
    "NOWGRE",  # Norwood Green
    "OOB",  # Out Of Borough
    "PERVAL",  # Perivale
    "PITSHG",  # Pitshanger
    "SOUACT",  # South Acton
    "SOUBDY",  # Southall Broadway
    "SOUGRE",  # Southall Green
    "SOUWST",  # Southall West
    "SOUFLD",  # Southfield
    "UNKNOW",  # Use With Unknown Trader Only
    "WALPLE",  # Walpole
]


class Browser:
    LANDING_PAGE: str = "https://pam.ealing.gov.uk/online-applications/search.do?action=advanced&searchType=Licencing"

    def __init__(self):
        options = Options()
        options.add_argument("-headless")
        print("Starting headless browser...")
        self.browser = Firefox(options=options)

    def fetch_hmo_links(self, ward: str) -> list[str]:
        print(f"Fetching links for ward '{ward}'", end=" ")
        links: list[str] = []

        # goto landing page
        self.browser.get(self.LANDING_PAGE)

        # complete and submit form
        select = Select(self.browser.find_element(By.ID, "categoryType"))
        select.select_by_value("HMO")
        select = Select(self.browser.find_element(By.ID, "ward"))
        select.select_by_value(ward)
        self.browser.find_element(By.CSS_SELECTOR, "input[type=submit]").click()

        # return if no results were found
        try:
            self.browser.find_element(By.XPATH, '//*[text() = "No results found."]')
            print("No links found")
            return links
        except NoSuchElementException:
            pass

        # change paging to view 100 results per page
        select = Select(self.browser.find_element(By.ID, "resultsPerPage"))
        select.select_by_value("100")
        self.browser.find_element(By.CSS_SELECTOR, "input[type=submit]").click()

        # fetch link for each HMO licence application
        try:
            links += self._fetch_links()
            next = self.browser.find_element(By.CSS_SELECTOR, "a.next")
            while True:
                next.click()
                links += self._fetch_links()
                next = self.browser.find_element(By.CSS_SELECTOR, "a.next")
        except NoSuchElementException:
            pass

        print(f" Found {len(links)} links")
        return links

    def quit(self) -> None:
        print("Quitting browser")
        self.browser.quit()

    def _fetch_links(self) -> list[str]:
        print(".", end="", flush=True)
        return [
            ele.find_element(By.TAG_NAME, "a").get_attribute("href")
            for ele in self.browser.find_elements(By.CSS_SELECTOR, "li.searchresult")
        ]


def write_links(filename: str, links: list[str]) -> None:
    print(f"Writing {len(links)} links to file.")
    with open(filename, "a", newline="") as csvfile:
        writer = csv.writer(csvfile, quoting=csv.QUOTE_MINIMAL)
        for link in links:
            writer.writerow([ward, link])



if __name__ == "__main__":
    browser = Browser()

    for ward in WARDS:
        links = browser.fetch_hmo_links(ward)
        if len(links) == 0:
            continue
        write_links(DATAFILE, links)

    browser.quit()
