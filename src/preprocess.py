from bs4 import BeautifulSoup
import requests
import markdownify
import logging


def get_urls_from_sitemap(sitemap_url, exclude_prefixes=None):
    """
    Scrape URLs from a sitemap (XML or HTML), even if the extension is misleading.

    Args:
        sitemap_url (str): The URL of the sitemap.
        exclude_prefixes (list, optional): List of URL prefixes to exclude (e.g., ['image:', 'video:']).

    Returns:
        list: A list of extracted URLs.
    """
    try:
        response = requests.get(sitemap_url, headers={
                                'User-Agent': 'Mozilla/5.0'})
        response.raise_for_status()

        soup = BeautifulSoup(response.content, 'html.parser')

        if soup.find("urlset"):
            urls = [
                url_tag.find('loc').text.strip()
                for url_tag in soup.find_all('url')
                if url_tag.find('loc') and not any(
                    url_tag.find('loc').text.strip().startswith(prefix)
                    for prefix in (exclude_prefixes or [])
                )
            ]
            print("URLs from sitemap: ", urls)
            return urls

        elif soup.find("table"):
            urls = [
                a_tag['href'].strip()
                for a_tag in soup.find_all('a', href=True)
                if not any(a_tag['href'].strip().startswith(prefix) for prefix in (exclude_prefixes or []))
            ]
            print("URLs from sitemap: ", urls)
            return urls

        print("Unknown sitemap format.")
        return []

    except requests.exceptions.RequestException as e:
        print(f"Error fetching sitemap: {e}")
        return []
    except Exception as e:
        print(f"Error parsing sitemap: {e}")
        return []


def fetch_article_content(url):
    try:
        response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
        soup = BeautifulSoup(response.content, 'html.parser')

        # Find article content (adjust selectors based on website structure)
        article = soup.find('article')
        if not article:
            return None

        # Extract title
        title = soup.find('h1').text.strip()

        # Extract main content
        content = article.find_all(['p', 'h2', 'h3', 'h4', 'ul', 'ol'])
        content_text = '\n\n'.join([elem.text.strip() for elem in content])

        # Convert to markdown
        markdown_content = markdownify.convert(content_text)

        return {'title': title, 'content': markdown_content, 'source_url': url}

    except Exception as e:
        logging.error(f"Error processing {url}: {e}")
        return None
