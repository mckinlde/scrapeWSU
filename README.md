
# scrapes linkedin links from cougsconnect website
# 1. open https://cougsconnect.wsu.edu/, prompt the user to sign in, then continue
# 2. navigate to https://cougsconnect.wsu.edu/directory, which is an infinite scrolling feed, saved as saved_pages\Directory _ Cougs Connect.html
# 3. scroll the feed, opening each profile page in a new tab
# 4. for each profile (examples saved as saved_pages\User _ Cougs Connect.html, saved_pages\User _ Cougs Connect(1).html, and saved_pages\User _ Cougs Connect(2).html), if there is a link to their linkedin profile, append it to profile_links.csv
# write out to csv file on each new profile, so the program is robust to interruption

## Setup
1. Install Python 3.x
2. Install dependencies: `pip install -r requirements.txt`
3. Ensure Chrome browser is installed

## Running the Scraper
Run `python scraper.py`

The script will open Chrome, navigate to CougsConnect, and prompt you to sign in. After signing in, press Enter to continue scraping.

LinkedIn links will be saved to `profile_links.csv`.