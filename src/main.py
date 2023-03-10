from selenium import webdriver
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.by import By

from selenium.webdriver.firefox.options import Options

from dotenv import load_dotenv

import csv
import sqlite3
import os

### Implementation

def get_selenium_driver():
    options = Options()
    options.binary_location = r'C:\Program Files\Mozilla Firefox\firefox.exe'
    driver = webdriver.Firefox(executable_path=os.environ['gecko_location'], options=options)
    driver.implicitly_wait(3)
    return driver

## Scraping FDIC Failed Bank List and Exporting to CSV

class FailedBank:
    def __init__(self, bank_name, bank_fdic_link,
                 city, state, fdic_cert,
                 aquiring_institution,
                 closing_date, funds):
        self.bank_name = bank_name.replace('\n', ' ')
        self.bank_fdic_link = bank_fdic_link
        self.city = city
        self.state = state
        self.fdic_cert = fdic_cert
        self.aquiring_institution = aquiring_institution
        self.closing_date = closing_date
        self.funds = funds

    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_value, exc_traceback):
        return

    def __repr__(self):
        return f"{self.bank_name};{self.bank_fdic_link};{self.city};{self.state};" \
                f"{self.fdic_cert};{self.aquiring_institution};{self.closing_date};{self.funds}"

def get_table_rows_of_failed_banks(driver):
    url = "https://www.fdic.gov/resources/resolutions/bank-failures/failed-bank-list/index.html"

    driver.get(url)

    # Get Select element that controls how many entries we see
    select = Select(driver.find_element(By.CSS_SELECTOR, 'div#DataTables_Table_0_length label select'))

    # Set Select element to -1, i.e. All
    select.select_by_value('-1')

    table_rows = driver.find_elements(By.CSS_SELECTOR, 'div.data-table--content table tbody tr')

    return table_rows

def convert_table_row_to_FailedBank(table_row):
    tds = table_row.find_elements(By.TAG_NAME, 'td')

    # Bank Name & Link
    bank_name = tds[0].text.replace("En Espa??ol", "").strip()
    bank_fdic_link = tds[0].find_elements(By.TAG_NAME, 'a')[0].get_attribute('href')

    # City & State
    city = tds[1].text
    state = tds[2].text

    # FDIC Cert
    fdic_cert = tds[3].text
    
    # Aquiring Institution
    aquiring_institution = tds[4].text

    # Closing Date & Funds
    closing_date = tds[5].text
    funds = tds[6].text

    return FailedBank(bank_name, bank_fdic_link, city, state,
                      fdic_cert, aquiring_institution, closing_date, funds)

def convert_table_rows_to_FailedBanks(table_rows):
    failed_banks = []

    for table_row in table_rows:
        failed_banks.append(convert_table_row_to_FailedBank(table_row))
    
    return failed_banks

def export_failed_banks_to_CSV(failed_banks):
    with open('src/failed_banks.csv', 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['bank_name', 'bank_fdic_link', 'city', 'state',
                      'fdic_cert', 'aquiring_institution', 'closing_date', 'funds']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames, delimiter='|')

        writer.writeheader()

        i = 0
        total = len(failed_banks)
        for failed_bank in failed_banks:
            i += 1
            with failed_bank as fb:
                print(f'Exporting {fb.bank_name} ({i}/{total})')
                writer.writerow({
                    'bank_name': fb.bank_name,
                    'bank_fdic_link': fb.bank_fdic_link,
                    'city': fb.city,
                    'state': fb.state,
                    'fdic_cert': fb.fdic_cert,
                    'aquiring_institution': fb.aquiring_institution,
                    'closing_date': fb.closing_date,
                    'funds': fb.funds
                })

def import_failed_banks_from_csv(csv_file_path):
    failed_banks = []

    with open(csv_file_path, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile, delimiter='|')

        i = 0
        for row in reader:
            i += 1
            print("Converting " + row['bank_name'] + f' to FailedBank object. ({i})')
            failed_banks.append(FailedBank(
                row['bank_name'],
                row['bank_fdic_link'],
                row['city'],
                row['state'],
                row['fdic_cert'],
                row['aquiring_institution'],
                row['closing_date'],
                row['funds']
            ))
    
    return failed_banks

## Import FDIC Failed bank List from CSV File

class DBConnector:
    def __init__(self, database_name):
        self.con = sqlite3.connect(database_name)
        self.cursor = self.con.cursor()
    
    def execute(self, sql_code, data=None):
        if (data):
            return self.cursor.execute(sql_code, data)
        else:
            return self.cursor.execute(sql_code)
    
    def executemany(self, sql_code, data):
        return self.cursor.executemany(sql_code, data)
    
    def commit(self):
        self.con.commit()

    def execute_and_commit(self, sql_code):
        res = self.execute(self, sql_code)
        self.commit(self)
        return res
    
    def close(self):
        self.con.close()

def failed_bank_table_build_up(db):
    query = 'CREATE TABLE failed_banks(bank_name, bank_fdic_link, city, state, fdic_cert, aquiring_institution, closing_date, funds);'

    if(table_exists('failed_banks')):
        failed_bank_table_teardown(db)
    
    db.execute(query)

def failed_bank_table_teardown(db):
    db.execute('DROP TABLE failed_banks;')

def insert_failed_bank(db, failed_bank):
    data = (failed_bank.bank_name, failed_bank.bank_fdic_link,
                failed_bank.city, failed_bank.state,
                failed_bank.fdic_cert, failed_bank.aquiring_institution,
                failed_bank.closing_date, failed_bank.funds)
    db.execute("INSERT INTO failed_banks VALUES(?,?,?,?,?,?,?,?);", data)
    db.commit()

def insert_failed_banks(db, list_of_failed_banks):
    list_of_data = []

    for failed_bank in list_of_failed_banks:
        list_of_data.append((failed_bank.bank_name, failed_bank.bank_fdic_link,
                failed_bank.city, failed_bank.state, failed_bank.fdic_cert,
                failed_bank.aquiring_institution, failed_bank.closing_date, failed_bank.funds))
    
    db.executemany("INSERT INTO failed_banks VALUES(?,?,?,?,?,?,?,?);", list_of_data)
    db.commit()

## Scrape Bank Failures in Brief

class BriefPage:
    def __init__(self, bank_name, bank_link, city, state, press_releases, closing_date, assets, deposit, acquirer_notes):
        self.bank_name = bank_name
        self.bank_link = bank_link
        self.city = city
        self.state = state
        self.press_releases = press_releases
        self.closing_date = closing_date
        self.assets = assets
        self.deposit = deposit
        self.acquirer_notes = acquirer_notes
    
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, exc_traceback):
        return
    
    def __repr__(self):
        return f"{self.bank_name};{self.bank_link};{self.city};{self.state};" \
                f"NO_PR;{self.closing_date};{self.assets};" \
                f"{self.deposit};{self.acquirer_notes}"

def extract_bank_info(bank_info):
    *bank_name, city, state = str.split(bank_info, ',')
    bank_name = ''.join(bank_name)
    city = city.strip()
    state = state.strip()

    # I cry because of this code, there is a missing ',' in the 2004 data
    # This is just to capture it and fix it so I can have a clean run
    # This will break if they ever decide to add in that comma
    if (city == 'Dollar Savings Bank Newark'):
        bank_name = 'Dollar Savings Bank'
        city = 'Newark'

    return (bank_name, city, state)

def extract_press_releases(anchor_elements):
    press_releases = []
    for anchor_el in anchor_elements:
        press_releases.append({
            'pr_id': anchor_el.text,
            'pr_link': anchor_el.get_attribute('href')
        })
    return press_releases

def convert_table_row_to_BriefPage(table_row):
    tds = table_row.find_elements(By.TAG_NAME, 'td')
    
    if(len(tds) <= 1):
        return []
    
    print(f'Processing {tds[0].text}')

    (bank_name, city, state) = extract_bank_info(tds[0].text)
    bank_link = tds[0].find_elements(By.TAG_NAME, 'a')[0].get_attribute('href')
    press_releases = extract_press_releases(tds[1].find_elements(By.TAG_NAME, 'a'))
    closing_date = tds[2].text
    assets = tds[3].text
    deposit = tds[4].text
    acquirer_notes = tds[5].text.split('\n')[0]

    return [BriefPage(bank_name, bank_link, city, state, press_releases, closing_date, assets, deposit, acquirer_notes)]
    

def scrape_brief_page_by_year(driver, year):
    bank_briefs = []
    page_url = f'https://www.fdic.gov/bank/historical/bank/bfb{year}.html'

    print(f'Scraping Brief Page for year {year}')

    driver.get(page_url)

    table_rows = driver.find_elements(By.CSS_SELECTOR, f'[id="{year}-description"] table.details tbody tr')

    # If there was no table body, just return an empty BriefPage
    if (len(table_rows) == 0):
        return []
    
    for table_row in table_rows:
        bank_briefs.extend(convert_table_row_to_BriefPage(table_row))
    
    return bank_briefs

def setup_brief_pages_csv(briefcsv):
    bank_fieldnames = ['bank_name', 'bank_link', 'city', 'state',
                            'closing_date', 'assets', 'deposit', 'acquirer_notes']
    bank_writer = csv.DictWriter(briefcsv, fieldnames=bank_fieldnames, delimiter='|')
    bank_writer.writeheader()
    return bank_writer

def setup_pr_links_csv(prcsv):
    pr_fieldnames = ['bank_link', 'pr_id', 'pr_link']
    pr_writer = csv.DictWriter(prcsv, fieldnames=pr_fieldnames, delimiter='|')
    pr_writer.writeheader()
    return pr_writer

def write_bank_brief_row(bank_writer, brief_page):
    with brief_page as bp:
        bank_writer.writerow({
                    'bank_name': bp.bank_name,
                    'bank_link': bp.bank_link,
                    'city': bp.city,
                    'state': bp.state,
                    'closing_date': bp.closing_date,
                    'assets': bp.assets,
                    'deposit': bp.deposit,
                    'acquirer_notes': bp.acquirer_notes
                })
        
def write_press_release_rows(pr_writer, brief_page):
    for press_release in brief_page.press_releases:
        pr_writer.writerow({
            'bank_link': brief_page.bank_link,
            'pr_id': press_release['pr_id'],
            'pr_link': press_release['pr_link']
        })

def export_BriefPages_to_CSV(bank_briefs):
    with open('src/brief_pages.csv', 'w', newline='', encoding='utf-8') as briefcsv, \
            open('src/press_releases.csv', 'w', newline='', encoding='utf-8') as prcsv:
        
        bank_writer = setup_brief_pages_csv(briefcsv)
        pr_writer = setup_pr_links_csv(prcsv)
        
        i = 0
        total = len(bank_briefs)
        for brief_page in bank_briefs:
            i += 1
            print(f'Exporting {brief_page.bank_name} ({i}/{total})')
            write_bank_brief_row(bank_writer, brief_page)
            write_press_release_rows(pr_writer, brief_page)

def table_exists(db, table_name):
    if (db.execute('SELECT name from sqlite_master where name=(?)', (table_name,)).fetchone() is None):
        return False
    else:
        return True

def bank_brief_table_teardown(db):
    db.execute('DROP TABLE bank_briefs;')

## Import Bank Briefs from CSV to DB
def bank_brief_table_build_up(db):
    query = 'CREATE TABLE bank_briefs(bank_name, bank_link, city, state, closing_date, assets, deposit, acquirer_notes);'

    if(table_exists(db, 'bank_briefs')):
        bank_brief_table_teardown(db)
    
    db.execute(query)

def insert_bank_briefs(db, bank_briefs):
    list_of_briefs = []

    for bank_brief in bank_briefs:
        list_of_briefs.append((
            bank_brief.bank_name,
            bank_brief.bank_link,
            bank_brief.city,
            bank_brief.state,
            bank_brief.closing_date,
            bank_brief.assets,
            bank_brief.deposit,
            bank_brief.acquirer_notes
        ))
    db.executemany('INSERT INTO bank_briefs VALUES(?,?,?,?,?,?,?,?);', list_of_briefs)
    db.commit()

def import_bank_briefs_from_csv(briefcsv):
    bank_briefs = []

    with open(briefcsv, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile, delimiter='|')

        i = 0

        for row in reader:
            i+1
            print(f'Converting {row["bank_name"]} to BankBrief object. ({i})')
            bank_briefs.append(BriefPage(
                row['bank_name'],
                row['bank_link'],
                row['city'],
                row['state'],
                [], # Skipping Press Releases
                row['closing_date'],
                row['assets'],
                row['deposit'],
                row['acquirer_notes']
            ))
        
    return bank_briefs

def press_release_table_teardown(db):
    db.execute('DROP TABLE press_releases')

def press_release_table_build_up(db):
    query = 'CREATE TABLE press_releases(bank_link, pr_id, pr_link);'

    if(table_exists(db, 'press_releases')):
        press_release_table_teardown(db)

    db.execute(query)

def import_press_releases_from_csv(prcsv):
    press_releases = []

    with open(prcsv, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile, delimiter='|')
        
        i = 0

        for row in reader:
            i += 1
            print(f'Converting Press Release #{row["pr_id"]} ({i})')
            press_releases.append({
                'bank_link': row['bank_link'],
                'pr_id': row['pr_id'],
                'pr_link':row['pr_link']
            })
    
    return press_releases

def insert_press_releases(db, press_release_list):
    list_of_prs = []

    for press_release in press_release_list:
        list_of_prs.append((press_release['bank_link'],
                            press_release['pr_id'],
                            press_release['pr_link']))
    
    db.executemany('INSERT INTO press_releases VALUES(?,?,?)', list_of_prs)
    db.commit()

### For Interactive

# driver = get_selenium_driver()
db = DBConnector("src/testing.db")

## Scraping FDIC Failed Bank List and Exporting to CSV

# failed_banks_table_rows = get_table_rows_of_failed_banks(driver)
# failed_banks = convert_table_rows_to_FailedBanks(failed_banks_table_rows)

# export_failed_banks_to_CSV(failed_banks)

## Import FDIC Failed bank List from CSV File to DB

## Build up will automatically teardown if needed
# failed_bank_table_build_up(db)

# failed_bank_list = import_failed_banks_from_csv("src/failed_banks.csv")
# insert_failed_banks(db, failed_bank_list)
# print(db.execute("SELECT COUNT(*) from failed_banks;").fetchone()) # Should give 563 results

# Scrape Bank Failures in Brief

# Scraping and Exporting to CSV
# bank_briefs = []

# for year in range(2001, 2023):
#     bank_briefs.extend(scrape_brief_page_by_year(driver, year))

# export_BriefPages_to_CSV(bank_briefs)

# driver.close()

## Import BankBriefs data from CSV to DB

# bank_brief_table_build_up(db)

# bank_brief_list = import_bank_briefs_from_csv("src/brief_pages.csv")
# insert_bank_briefs(db, bank_brief_list)

# print(db.execute("SELECT COUNT(*) from bank_briefs;").fetchone()) # Should give 561

## Import Press Releases to DB

# press_release_table_build_up(db)

# press_release_list = import_press_releases_from_csv("src/press_releases.csv")
# insert_press_releases(db, press_release_list)

# print(db.execute("SELECT COUNT(*) from press_releases;").fetchone()) # Should give 568