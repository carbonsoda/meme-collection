from urllib.request import urlopen
from bs4 import BeautifulSoup
import requests


class MemeCollection:
    def __init__(self):
        self.root = 'https://knowyourmeme.com/'
        self.prefix = ''
        self.suffix = ''

    def getHTMLContent(self, link):
        html = urlopen(link)
        soup = BeautifulSoup(html, 'html.parser')
        return soup

    # Accounts for varying lengths of subcategories, ie 14 vs 300 entries
    # returns int for maximum pages
    def get_page_limit(self, base_url, desired_limit):
        content = self.getHTMLContent(base_url)

        pagination = content.find('div', {'class': 'pagination'})

        # If they only have 1 page, they lack the pagination tags
        if not pagination:
            return 1

        count_info = pagination.get_text().split(' ')
        counts = [int(c) for c in count_info if c.isdigit()]
        pg_max = max(counts)

        if pg_max < desired_limit:
            return pg_max
        elif pg_max > desired_limit:
            return desired_limit

    # source: https://github.com/kb22
    def collect_entry_urls(self, page_url):
        content = self.getHTMLContent(page_url)
        entry_urls = []

        entry_table = content.find('table', {'class': 'entry_list'})
        if not entry_table:
            print(page_url)
            return entry_urls, True
        entry_rows = entry_table.find_all('tr')

        for row in entry_rows:
            cells = row.find_all('td')

            if len(cells) > 1:
                for entry in cells:
                    if not entry.attrs:
                        return entry_urls, True
                    else:
                        entry_link = entry.find('a')
                        entry_urls.append(entry_link.get('href'))

        return entry_urls, False

    def build_urls(self, pg_count):
        return self.root + self.prefix + str(pg_count) + self.suffix

    # Iterates through all possible pages and their meme entries
    # returns list of meme urls (ie 'memes/uwu' or 'memes/slime-man')
    def collect_pages(self, page_url, pg_max, pg_count=1):
        # base case
        if pg_count > pg_max:
            return []
        else:
            page_url = self.build_urls(pg_count)
            # collecting this page's info
            page_entries, hit_limit = self.collect_entry_urls(page_url)  # collecting this page's info

            if hit_limit:
                return page_entries
            else:
                return page_entries + self.collect_pages(page_url, pg_max, pg_count + 1)

    def collect_categories(self, category):
        base = 'types/'

    def collect_searches(self, search_tag):
        prefix = 'search?context=entries&page='
        suffix = '&q=tags%3A%28"' + str(search_tag) + '"%29+status%3Aconfirmed&sort=reverse-chronological'


class EntryCollection:
    def __init__(self, parent=None):
        self.root = 'https://knowyourmeme.com/'

    def getHTMLContent(self, entry_url):
        html = urlopen('https://knowyourmeme.com/' + entry_url)
        soup = BeautifulSoup(html, 'html.parser')
        return soup

    def entry_info(self, entry_url):
        entry = {
            'title': '',
            'type': [],  # in case additional types
            'year': '',
            'origin': '',  # could be interesting
            'tags': [],
        }
        content = self.getHTMLContent(entry_url)

        title_info = content.find_all('section', {'class': 'info'}).find('h1')
        entry['title'] = info.find('h1').get('text')

        meme_info = content.find('aside', {'class': 'left'})
        stats = meme_info.find('dl')  # first one
        info_headers = stats.find_all('dt')
        info_subheaders = stats.find_all('dd')
        headers = [stat.get('text').lower() for stat in info_headers]


        tags_info = meme_info.find('dl', {'id': 'entry_tags'}).find('dd')
        tags = []
        for tag in tags_info:
            tagtext = tag.get('text')
            tags.append(tagtext)
        entry['tags'] = tags


