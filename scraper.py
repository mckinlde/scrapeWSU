import csv
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

def scrape_linkedin_links():
    # Initialize the Chrome driver
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))

    try:
        # Step 1: Open CougsConnect and prompt user to sign in
        driver.get("https://cougsconnect.wsu.edu/")
        input("Please sign in to CougsConnect and press Enter to continue...")

        # Step 2: Navigate to the directory
        driver.get("https://cougsconnect.wsu.edu/directory")
        time.sleep(5)  # Wait for page to load

        # Debug: Save page source
        with open('debug_directory.html', 'w', encoding='utf-8') as f:
            f.write(driver.page_source)

        # Wait for the directory to load
        # WebDriverWait(driver, 10).until(
        #     EC.presence_of_element_located((By.CSS_SELECTOR, ".directory-item"))  # Adjust selector as needed
        # )

        # Open CSV file for writing
        with open('profile_links.csv', 'a', newline='', encoding='utf-8') as csvfile:
            fieldnames = ['profile_url', 'linkedin_url']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            if csvfile.tell() == 0:  # Write header if file is empty
                writer.writeheader()

            # Step 3: Scroll and process profiles incrementally
            processed_profiles = set()
            last_height = driver.execute_script("return document.body.scrollHeight")

            while True:
                # Scroll down to load more profiles
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(2)  # Wait for loading

                # Collect current profile links
                all_links = driver.find_elements(By.CSS_SELECTOR, "a")
                current_profiles = set()
                for link in all_links:
                    href = link.get_attribute('href')
                    if href and '/user/' in href:
                        current_profiles.add(href)

                # Process new profiles
                new_profiles = current_profiles - processed_profiles
                print(f"Found {len(new_profiles)} new profiles to process")
                for profile_url in new_profiles:
                    print(f"Processing {profile_url}")
                    driver.execute_script("window.open('');")
                    driver.switch_to.window(driver.window_handles[-1])
                    driver.get(profile_url)
                    time.sleep(3)  # Wait for page to load

                    # Debug: Save profile page source
                    # profile_id = profile_url.split('/')[-1]
                    # with open(f'debug_profile_{profile_id}.html', 'w', encoding='utf-8') as f:
                    #     f.write(driver.page_source)

                    try:
                        # Wait for the profile to load
                        WebDriverWait(driver, 10).until(
                            EC.presence_of_element_located((By.TAG_NAME, "body"))
                        )

                        # Look for LinkedIn link
                        linkedin_link = None
                        links = driver.find_elements(By.TAG_NAME, "a")
                        for link in links:
                            href = link.get_attribute('href')
                            if href and 'linkedin.com' in href:
                                linkedin_link = href
                                break

                        if linkedin_link:
                            print(f"Found LinkedIn: {linkedin_link}")
                            writer.writerow({'profile_url': profile_url, 'linkedin_url': linkedin_link})
                            csvfile.flush()  # Write immediately for robustness

                    except Exception as e:
                        print(f"Error processing {profile_url}: {e}")

                    # Close the tab
                    driver.close()
                    driver.switch_to.window(driver.window_handles[0])

                    processed_profiles.add(profile_url)

                # Check if we've reached the end
                new_height = driver.execute_script("return document.body.scrollHeight")
                if new_height == last_height:
                    break
                last_height = new_height

            print(f"Total processed profiles: {len(processed_profiles)}")

    finally:
        input("Scraping complete. Press Enter to close the browser...")
        driver.quit()

if __name__ == "__main__":
    scrape_linkedin_links()
