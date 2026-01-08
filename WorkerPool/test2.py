from master import MasterScheduler
import sys


def test_crawler():
    print("--- PHASE 2: Test Master Crawler ---")
    print("NOTE: Browser will open. Do not close it manually.")

    try:
        master = MasterScheduler(country='turkey')
        master.setup_driver()
        print("Driver Setup: OK")

        html = master.fetch_page_content()
        if not html or len(html) < 1000:
            print("ERROR: Invalid or empty HTML.")
            sys.exit(1)
        print("Fetch Page: OK")

        tasks = master.parse_links(html)

        if len(tasks) > 0:
            print(f"Link Extraction: OK (Found: {len(tasks)})")
            print("PHASE 2 SUCCESS: Master collects data.")
        else:
            print("ERROR: No links found.")

        master.driver.quit()

    except Exception as e:
        print(f"ERROR: {e}")
        sys.exit(1)


if __name__ == "__main__":
    test_crawler()