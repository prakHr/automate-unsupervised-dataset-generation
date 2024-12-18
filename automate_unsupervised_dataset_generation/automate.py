import time
import multiprocessing 
from mpire import WorkerPool
from playwright.sync_api import sync_playwright
from pprint import pprint


def extract_text_from_url(url,sleep_time):
    time.sleep(2)
    """
    Extract the main text content from a given URL.
    """
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)  # Use headless mode
        page = browser.new_page()

        try:
            # Navigate to the URL
            page.goto(url, wait_until="domcontentloaded", timeout=sleep_time)

            # Extract all text from <p> and <div> elements
            paragraphs = page.locator("p").all_text_contents()  # All <p> tags
            div_texts = page.locator("div").all_text_contents()  # All <div> tags

            # Combine and deduplicate text content
            main_text = "\n".join(set(paragraphs + div_texts))
            return {"url": url, "text": main_text}
        except Exception as e:
            # print(e)
            pass
        finally:
            browser.close()
    return  {"url": url, "text":""}
# # Example usage
# if __name__ == "__main__":
#     urls = [
#         "https://example.com",
#         "https://openai.com",
#         "https://www.wikipedia.org"
#     ]
    
#     for url in urls:
#         result = extract_text_from_url(url)
#         if "error" in result:
#             print(f"Error extracting {url}: {result['error']}")
#         else:
#             print(f"Text from {url}:\n{result['text'][:500]}...\n")  # Show first 500 characters


# Initialize a browser for each worker
def extract_all_url_sync(query, task,sleep_time):
    time.sleep(2)
    urls = []
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)  # Start browser per worker
        page = browser.new_page()
        try:
            # Go to Google
            page.goto("https://www.google.com", wait_until="domcontentloaded", timeout=sleep_time)

            # Accept cookies if present
            if page.locator("button:has-text('I agree')").count() > 0:
                page.locator("button:has-text('I agree')").click()

            # Fill in the search query
            search_input = page.locator("textarea[name='q']")
            search_input.fill(query)
            search_input.press("Enter")

            # Wait for search results to load
            page.wait_for_selector("a:has(h3)", timeout=sleep_time)

            # Extract URLs from the first page
            for element in page.locator("a:has(h3)").all():
                url = element.get_attribute("href")
                if url:
                    urls+=[{"url": url}]

            # Navigate to the second page
            next_button = page.locator(f"a[aria-label='Page {task}']")  # Locate "Next" or page 2 button
            if next_button.count() > 0:
                next_button.click()
                page.wait_for_selector("a:has(h3)", timeout=sleep_time)

                # Extract URLs from the second page
                for element in page.locator("a:has(h3)").all():
                    url = element.get_attribute("href")
                    if url:
                        urls+=[{"url": url}]
        except Exception as e:
            # print(e)
            return urls
        finally:
            browser.close()  # Close the browser for this worker
    return urls

def extract_all_url_sync_without_task(query,sleep_time):
    time.sleep(2)
    urls = []
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)  # Start browser per worker
        page = browser.new_page()
        try:
            # Go to Google
            page.goto("https://www.google.com", wait_until="domcontentloaded", timeout=sleep_time)

            # Accept cookies if present
            if page.locator("button:has-text('I agree')").count() > 0:
                page.locator("button:has-text('I agree')").click()

            # Fill in the search query
            search_input = page.locator("textarea[name='q']")
            search_input.fill(query)
            search_input.press("Enter")

            # Wait for search results to load
            page.wait_for_selector("a:has(h3)", timeout=sleep_time)

            # Extract URLs from the first page
            for element in page.locator("a:has(h3)").all():
                url = element.get_attribute("href")
                if url:
                    urls.append({"url": url})

            # Navigate to the second page
            next_button = page.locator(f"a[aria-label='Page 1']")  # Locate "Next" or page 2 button
            if next_button.count() > 0:
                next_button.click()
                page.wait_for_selector("a:has(h3)", timeout=sleep_time)

                # Extract URLs from the second page
                for element in page.locator("a:has(h3)").all():
                    url = element.get_attribute("href")
                    if url:
                        urls+=[{"url": url}]
        except Exception as e:
            # print(e)
            return urls
        finally:
            browser.close()  # Close the browser for this worker
    return urls
def find_number_of_google_pages(query,sleep_time):
    time.sleep(2)
    """
    Finds the total number of pages for a Google search query.
    """
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)  # Use headless browser
        page = browser.new_page()

        try:
            # Navigate to Google
            page.goto("https://www.google.com", wait_until="domcontentloaded")

            # Accept cookies if prompted
            if page.locator("button:has-text('I agree')").count() > 0:
                page.locator("button:has-text('I agree')").click()

            # Perform a search
            search_input = page.locator("textarea[name='q']")
            search_input.fill(query)
            search_input.press("Enter")

            # Wait for the search results to load
            page.wait_for_selector("a:has(h3)", timeout=sleep_time)

            # Locate the pagination section
            pagination_elements = page.locator("td a").all_text_contents()

            # Extract numbers from the pagination links
            page_numbers = [int(num) for num in pagination_elements if num.isdigit()]
            total_pages = max(page_numbers) if page_numbers else 1

            return total_pages
        except Exception as e:
            # print(e)
            pass
        finally:
            browser.close()
    return 0

def get_description_from_url(url: str,sleep_time):
    time.sleep(2)
    description = None
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        
        try:
            # Go to the target URL
            page.goto(url, wait_until="domcontentloaded", timeout=sleep_time)
            
            # Attempt to retrieve the meta description content
            # description_element = page.locator("meta[name='description']")
            # if description_element.count() > 0:
            #     description = description_element.get_attribute("content")
            # else:
            #     # If no meta description, try getting the first paragraph as a fallback
            #     paragraph_element = page.locator("p")
            #     if paragraph_element.count() > 0:
            #         description = paragraph_element.first.text_content()
            paragraphs = page.locator("p").all_text_contents()  # All <p> tags
            
            # Combine and deduplicate text content
            main_text = "\n".join(set(paragraphs))
            return main_text
        
        except Exception as e:
            # print(e)
            pass
            # print(f"An error occurred: {e}")
        finally:
            browser.close()
    
    return ""

def parallel_scraping(query,num_page,sleep_time=10):
    sleep_time*=1000
    
    time.sleep(2)
    # init_browser_pool()
    total_pages = find_number_of_google_pages(query,sleep_time)
    
    num_cores = multiprocessing.cpu_count()-1
    # print(num_cores)
    queries = [{"query":query,"task":task,"sleep_time":sleep_time} for task in range(min(num_page,total_pages))]
    
    with WorkerPool(n_jobs=num_cores) as pool:
        urls = pool.map(extract_all_url_sync, queries, progress_bar=True, chunk_size=1)
    mod_urls = []
    for url in urls:
        mod_urls+=url
    new_urls = []
    for url in mod_urls:
        new_urls.append(url["url"])
    new_urls=list(set(new_urls))
    new_urls = [{"url":url,"sleep_time":sleep_time} for url in new_urls]
    with WorkerPool(n_jobs=num_cores) as pool:
        descriptions = pool.map(get_description_from_url, new_urls, progress_bar=True, chunk_size=1)
    # pprint(descriptions)
    descriptions = [{"query":descriptions[i],"sleep_time":sleep_time} for i in range(len(descriptions)) if descriptions[i]!=""]
    # return
    with WorkerPool(n_jobs=num_cores) as pool:
        urls = pool.map(extract_all_url_sync_without_task, descriptions, progress_bar=True, chunk_size=1)
    mod_urls = []
    for url in urls:
        mod_urls+=url
    new_urls = []
    for url in mod_urls:
        new_urls.append(url["url"])
    new_urls=list(set(new_urls))
    new_urls = [{"url":url,"sleep_time":sleep_time} for url in new_urls]
    with WorkerPool(n_jobs=num_cores) as pool:
        descriptions = pool.map(get_description_from_url, new_urls, progress_bar=True, chunk_size=1)
    # pprint(descriptions)
    descriptions = [descriptions[i] for i in range(len(descriptions)) if descriptions[i]!=""]
    # pprint(descriptions)
    
    return descriptions


# if __name__ == "__main__":
#     query = "Artificial Intelligence"
#     num_page = 1
#     sleep_time = 10
#     rv = parallel_scraping(query,num_page,sleep_time)
#     pprint(rv)

    
    
