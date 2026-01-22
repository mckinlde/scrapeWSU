"""Minimal helper to open Luma's signup page, reveal the guests modal, and save attendee links."""

from __future__ import annotations

import csv
from pathlib import Path
from time import sleep

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager

LUMA_URL = "https://luma.com/intuitosssdgjan2026?tk=Ef1xLI"
ATTENDEE_CSV = Path("luma_attendee_profiles.csv")


def open_luma_session(url: str = LUMA_URL) -> webdriver.Chrome:
    """Open {url} in Chrome and wait until the user confirms they are logged in."""

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
    driver.get(url)
    print("Browser opened. Complete the captcha or login flow in the new window.")
    while True:
        user_ready = input("Press Enter when you are done and want to proceed, or type 'keep' to stay open: ")
        if user_ready.strip().lower() == "keep":
            print("Keeping the browser open for another 15 seconds to give you more time...")
            sleep(15)
            continue
        break
    return driver


def open_going_modal(driver: webdriver.Chrome, timeout: int = 15) -> None:
    """Reveal the full guest list by clicking the Going card button."""

    button_xpath = (
        "//div[contains(@class, 'content-card')][.//div[contains(@class, 'title-label') and contains(., 'Going')]]"
        "//button[contains(@class, 'guests-button')]"
    )
    pre_click_profiles = driver.find_elements(By.CSS_SELECTOR, "a[href*='/user/']")
    modal_buttons = WebDriverWait(driver, timeout).until(
        EC.presence_of_all_elements_located((By.XPATH, button_xpath))
    )

    clicked = False
    for modal_button in modal_buttons:
        if not modal_button.is_displayed():
            continue
        driver.execute_script(
            "arguments[0].scrollIntoView({block: 'center', inline: 'nearest'});",
            modal_button,
        )
        driver.execute_script("arguments[0].click();", modal_button)
        clicked = True
        break

    if not clicked:
        raise RuntimeError("Unable to click the visible Going button to open the guest list.")

    WebDriverWait(driver, timeout).until(
        lambda drv: len(drv.find_elements(By.CSS_SELECTOR, "a[href*='/user/']")) > len(pre_click_profiles)
    )
    print("Going list modal opened.")


def gather_attendee_profiles(driver: webdriver.Chrome) -> list[str]:
    """Capture the profile URLs that are revealed inside the going list modal."""

    anchors = driver.find_elements(By.CSS_SELECTOR, "a[href*='/user/']")
    urls: list[str] = []
    seen: set[str] = set()
    for anchor in anchors:
        href = anchor.get_attribute("href")
        if href and href not in seen:
            seen.add(href)
            urls.append(href)
    print(f"Discovered {len(urls)} unique attendee profile links.")
    return urls


def read_social_links(driver: webdriver.Chrome, profile_url: str) -> list[str]:
    """Open a profile page in a temporary tab and return every social link exposed."""

    original_handle = driver.current_window_handle
    driver.execute_script("window.open('');")
    driver.switch_to.window(driver.window_handles[-1])
    driver.get(profile_url)
    sleep(2)
    links: list[str] = []
    try:
        container = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "div[class*='social-links']"))
        )
        for social_link in container.find_elements(By.TAG_NAME, "a"):
            href = social_link.get_attribute("href")
            if href:
                links.append(href)
    except Exception as exc:  # pylint: disable=broad-except
        print(f"No social links found for {profile_url}: {exc}")
    finally:
        driver.close()
        driver.switch_to.window(original_handle)
    return links


def persist_profile_links(profile_url: str, social_links: list[str]) -> None:
    """Append the profile metadata into the CSV store."""

    fieldnames = ["profile_url", "social_links"]
    file_exists = ATTENDEE_CSV.exists()
    with ATTENDEE_CSV.open("a", newline="", encoding="utf-8") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        if not file_exists:
            writer.writeheader()
        writer.writerow({
            "profile_url": profile_url,
            "social_links": ";".join(social_links),
        })


def main() -> None:
    """Entry point for the CLI."""

    try:
        driver = open_luma_session()
        open_going_modal(driver)
        for profile_url in gather_attendee_profiles(driver):
            social_links = read_social_links(driver, profile_url)
            if social_links:
                persist_profile_links(profile_url, social_links)
        input("Press Enter to close the browser once you're finished with the modal...")
    except KeyboardInterrupt:
        print("Interrupted, closing the browser...")
    finally:
        driver.quit()


if __name__ == "__main__":
    main()