
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

Perfect! The scraper now processes profiles incrementally during the scrolling flow. It scrolls to load more profiles, collects the new ones, processes them immediately (opening tabs, extracting LinkedIn links, closing tabs), and continues scrolling until no more profiles load.

This approach avoids loading all profiles into memory at once and processes them in batches as the infinite scroll reveals them.

Run the script again. It should now handle the infinite scroll more efficiently. Monitor the terminal for progress and check the profile_links.csv for extracted LinkedIn URLs. If issues persist, the debug files will help identify problems with specific profiles.