from langchain.text_splitter import TextSplitter
import requests
import logging
import html2markdown
from bs4 import BeautifulSoup


def get_urls_from_sitemap(sitemap_url):
    """
    Scrape only blog URLs from a sitemap.xml file, excluding image URLs
    """
    try:
        # Fetch the sitemap
        response = requests.get(sitemap_url, headers={
                                'User-Agent': 'Mozilla/5.0'})
        response.raise_for_status()

        # Parse XML
        soup = BeautifulSoup(response.text, 'lxml')

        # Initialize empty list for URLs
        urls = []

        # Find all url tags and extract only blog URLs
        for url_tag in soup.find_all('url'):
            # Get the loc tag that's a direct child of url tag
            loc = url_tag.find('loc', recursive=False)
            if loc and not loc.text.strip().startswith('image:'):
                urls.append(loc.text.strip())

        return urls

    except requests.RequestException as e:
        logging.error(f"Error fetching sitemap: {e}")
        return []
    except Exception as e:
        logging.error(f"Error parsing sitemap: {e}")
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
        markdown_content = html2markdown.convert(content_text)

        return {'title': title, 'content': markdown_content, 'source_url': url}

    except Exception as e:
        logging.error(f"Error processing {url}: {e}")
        return None
