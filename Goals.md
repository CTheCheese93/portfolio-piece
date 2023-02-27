# Goals

## Data Visualization
### Summary

### [Failed Bank List](https://www.fdic.gov/resources/resolutions/bank-failures/failed-bank-list/index.html)
* ~~Scrape website for links to bank pages with more information on getting help~~
* [Duplicate This](https://www.fdic.gov/bank/historical/bank/bfb2020.html)
* Compose list of aquiring institutions websites
* [Scrape this over each year to download all and merge all data](https://www.fdic.gov/bank/historical/bank/bfb2002.html)
    * [This is a template for press releases](https://www.fdic.gov/news/press-releases/2011/pr11195.html)

### Scrape Bank Failure List Data into a CSV file
This brings an opportunity to implement CSV importing into SQLite and allows us to show off file system handling by being able to set directory and file name options once we get a UI going.

### Import Bank Failure List Data into a SQLite database
Because it's so minimal, using an SQLite to manage the data will allow for more complex filtering of information.

It will also hold onto extra information that isn't needed for visualization purposes, primarily urls.

With that being said, I believe Pandas uses CSV files or I will need to transform the SQL results into something that Pandas can use. So maybe this is an opportunity to implement SQL results to CSV.

!!NOTE!! We will need to separate Aquiring Companies into their own table and use a relationship, this will make things significantly easier when we grab their websites and import them into the database.

### Scrape Bank Failures in Brief from 2001 - 2022
These pages contain Press Release Numbers and Links, Approximate Assets/Deposits, and notes about the Acquirer. The goal is to get this information into it's own CSV file.

### Import Brief Data into SQLite database
We're going to import the Brief Data into the same database as the Bank Failure List Data, and (for now) build a table that links the new information to the existing banks on the FailedBanks table.

### Create a list of Aquiring Companies' websites
This one is going to be tricky but we're going to try a very straightforward approach. We're going to run a google search on each Aquiring Institution and capture the first result, and load it all into it's own csv.

### Validate all Aquiring Companies' websites
Afterward, we'll load in the csv and check each website to see if it seems like it's the correct website.

The cool part is that we're going to make the checking of each website something that is done with an interactive python terminal that you access by launching with a command line argument.

We'll use argparse to handle the command line argument and create a class that has commands to control a web browser and allows us to validate websites or change the url to it's proper destination before exporting the information to a CSV file

### Import Aquiring Companies' websites into SQLite database

### Basic UI Implementation
* A menu that allows you to search by key values
    * Bank Name, Acquiring Institution, FDIC Cert, Closing Date (month & year)
    * Maybe sorting?
    * Leads to a new menu to see more information about the bank and supporting links

### Setup static folder to hold onto pre-scraped data and databases

### Basic Data Visualization mimicing website

### Admin Panel
* Admin panel to manage data and attempt to pull updates from website via scraping
    * Fail quickly and apologize, potentially send an e-mail to a public e-mail?
* By this point, we need to have all created files going into a `dynamic` folder
* We might also find an excuse to use an ini file by this point

### Notes To Insert
* [Is scraping a government website legal?](https://www.silicon.co.uk/e-management/social-laws/us-court-data-scraping-legal-452720)

### Process Notes
* Looked at tutorials and attempted to use mechanicalsoup, but the Select element isn't wrapped in a form, which seems to break mechanicalsoup
* Now refreshing my knowledge on Selenium, which was my first choice anyways but thought I'd attempt a simpler solution first
    * I didn't spend too long trying to find a workaround with mechanicalsoup, so that could be a fault on me, but I know Selenium will work
* Well, I said that, but for some reason this website is giving me a lot of issues. Selenium doesn't want to acknowledge the existence of the Select element, and believes there are 15+ elements that fall under the class name "usa-select". Turns out, that's true. So we're going to try to make a very specific CSS Selector, but let it be known that the FDIC's iding needs significant work
* Using specific selectors was the biggest key, the time it took to come to that solution was a common gotcha with scraping. I'm taking this as a lesson to get specific fast instead of trying to avoid messy selectors
* We've now successfully scraped all the information, next step is to get the data into a CSV file
* CSV file creation is functioning as well as CSV importing to confirm there is no data loss during conversion
* Next steps are to start building out the SQLite functionality, we're doing this to get the initial `failed_banks` table built with the information we currently have. Afterward we will Scrape Bank Failures.
* `failed_banks` table built and data is being imported at a very basic level, we'll need to go back to refine the table creation to include explicit typing of columns and likely have to modify some of the data like closing dates to fit the DATETIME format. For now, we move forward.
    * The data is also still a little dirty. We stripped all line breaks in the bank name, but we need to filter out the occasional "En Espanol" that gets captured.
* I was able to get the Bank Failures in Brief data for each year, but the data is very dirty.
    * Banks can have multiple Press Releases, which actually makes things a little more complicated. Likely we will pull Press Releases into a list on the BriefPage object and put Press Releases into their own table with a relationship to the `brief_pages` table
    * Unlike the Bank Failure List data, the `bank_name` field has no line breaks or additional "En Espanol" text, however it currently holds onto the bank name, city, and state while the city and state columns are empty
    * These are the two things we need to focus on next
## Game Development
### Snake
### 2048
### Tic-Tac-Toe
### Quarto?!