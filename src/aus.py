import csv
from datetime import datetime, date, timedelta
import time
import os
import logging
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (
    NoSuchElementException, 
    StaleElementReferenceException, 
    ElementNotInteractableException,
    TimeoutException
)

class AusLNGScraper(object):
    def __init__(self):
        super().__init__()

        # constants
        self.url_aemo = 'https://www.aemo.com.au/energy-systems/gas/gas-bulletin-board-gbb/gbb-reports/lng-maintenance'
        self.url_chevron = 'https://australia.chevron.com/our-businesses/scheduled-maintenance-activity-notices'
        self.url_woodside = 'https://www.woodside.com.au/sustainability/working-openly/facility-maintenance-information'
        self.output_dir = 'aus_' + time.strftime('%Y-%m-%d_%H,%M,%S', time.localtime()) + '/'
        filename_stem = time.strftime('%Y-%m-%d_%H,%M,%S', time.localtime())
        self.filename = self.output_dir + filename_stem + '.csv'

        self.DATE_FORMAT = '%Y/%m/%d'
        self.csv_headers = [['facility', 'start_date', 'end_date', 'notes']]

        # important info
        self.stats = { 'total_num_of_flights': 0 }

        # driver
        options = Options()
        # options.headless = True
        fp = webdriver.FirefoxProfile()
        fp.set_preference("browser.download.folderList", 2)
        fp.set_preference("browser.download.dir", str(Path.cwd()) + '/' + self.output_dir)
        fp.set_preference("browser.helperApps.neverAsk.openFile", "application/pdf, application/x-pdf")
        fp.set_preference("browser.helperApps.neverAsk.saveToDisk", "application/pdf")
        fp.set_preference("pdfjs.disabled", True)
        self.driver = webdriver.Firefox(fp, options=options)
        self.driver.implicitly_wait(1)
        self.driver.set_page_load_timeout(40)
        #ignored_exceptions = (NoSuchElementException, StaleElementReferenceException)
        self.wait = WebDriverWait(self.driver, 5)

        # logger
        FORMAT = '%(asctime)-15s  %(message)s'
        logging.basicConfig(level=logging.INFO, format=FORMAT)
        self.logger = logging.getLogger(__name__)
        self.logger.info("Initialization finished.")

    def run(self):
        Path(self.output_dir).mkdir(parents=True, exist_ok=True)
        self.logger.info('Files will be written in the directory: %s', self.output_dir)

        try:
            self.write_rows(self.csv_headers)
            self.scrape_aemo()
            #self.scrape_chevron()
            #self.scrape_woodside()
            self.logger.info('All done.')
        finally:
            #self.driver.quit()
            print('haha')

    def standardize_date(self, input_format):
        output_format = self.DATE_FORMAT
        def f(date_text):
            return datetime.strptime(date_text, input_format).strftime(output_format)
        return f
    
    def write_rows(self, rows):
        with open(self.filename, 'a') as f:
            writer = csv.writer(f)
            writer.writerows(row for row in rows if row)


    def scrape_aemo(self):
        self.driver.get(self.url_aemo)
        self.driver.execute_script('document.querySelector(\'a[title="File 18"]\').setAttribute("download", "")')
        submit_button = self.driver.find_element_by_css_selector('div.submit')
        submit_button.click()
        file_a = self.driver.find_element_by_css_selector('a[title="File 18"] > div.file-list-wrapper > h5.field-title')
        file_a.click()


    def scrape_chevron(self):
        def parse_tr(facility):
            def f(tr):
                try:
                    tds = tr.find_elements_by_tag_name('td')
                    date_orig = tds[0].get_attribute('innerText').strip().split(' - ')
                    dates = list(map(self.standardize_date('%d/%m/%Y'), date_orig))
                    li_list = tds[1].find_elements_by_css_selector('ul > li')
                    notes = list(map(lambda td: td.get_attribute('innerText').strip(), li_list))
                    notes_str = ' || '.join(notes)
                    return [facility, dates[0], dates[1], notes_str]
                except ValueError:
                    return []
            return f

        self.driver.get(self.url_chevron)
        tbodies = [
            self.driver.find_element_by_xpath("//h4[contains(text(), 'gorgon LNG facility')]/../../..//tbody"),
            self.driver.find_element_by_xpath("//h4[contains(text(), 'wheatstone LNG facility')]/../../..//tbody")
        ]
        tr_lists = list(map(lambda tbody: tbody.find_elements_by_tag_name('tr')[1:], tbodies))
        rows = list(map(parse_tr('gorgon'), tr_lists[0])) + list(map(parse_tr('wheatstone'), tr_lists[1]))
        self.write_rows(rows)
        

    def scrape_woodside(self):
        def parse_tr(tr):
            tds = tr.find_elements_by_tag_name('td')
            data_list = list(map(lambda td: td.text.strip(), tds))
            facility = data_list[0]
            notes = data_list[1]
            dates = list(map(self.standardize_date('%d %B %Y'), data_list[2:]))
            return [facility, dates[0], dates[1], notes]

        self.driver.get(self.url_woodside)
        tr_list = (self.driver
                .find_element_by_css_selector('table.table.k-table > tbody')
                .find_elements_by_tag_name('tr'))[1:]
        rows = list(map(parse_tr, tr_list))
        self.write_rows(rows)
        

if __name__ == "__main__":
    aus_lng_scraper = AusLNGScraper()
    aus_lng_scraper.run()
