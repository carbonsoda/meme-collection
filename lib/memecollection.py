import requests
from urllib.error import HTTPError
from urllib.request import urlopen
from bs4 import BeautifulSoup


class MemeCollection:
    def __init__(self):
        self.root = 'https://knowyourmeme.com/'
        self.prefix = ''
        self.suffix = ''

    def getHTMLContent(self, link):
        html = urlopen(link)
        soup = BeautifulSoup(html, 'lxml')
        return soup

    # Accounts for varying lengths of subcategories, ie 14 vs 300 entries
    # returns int for maximum pages
    def get_page_limit(self, base_url, desired_limit):
        try:
            content = self.getHTMLContent(base_url)
        except HTTPError:
            return 0

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
                        entry_title = entry.find('img')
                        entry_urls.append((entry_title.get('title'), entry_link.get('href')))

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

    def collect_tags(self, meme_tag):
        prefix = 'search?context=entries&page='
        suffix = '&q=tags%3A%28"' + str(meme_tag) + '"%29+status%3Aconfirmed&sort=reverse-chronological'



