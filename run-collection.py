import csv
import pandas as pd
from collections import defaultdict
from memecollection import MemeCollection, EntryCollection


memecollect = MemeCollection()


def getmemes_types(types_list, desired_count):
    # shows in order of meme itself, not by date added to the database
    memecollect.suffix = '?sort=reverse-chronological'

    memetypes_urls = defaultdict(list)

    for meme_type in types_list:
        memecollect.prefix = 'types/' + meme_type + '/page/'
        base_url = memecollect.build_urls(pg_count=1)

        page_limit = memecollect.get_page_limit(base_url, desired_count)
        memetypes_urls[meme_type] += memecollect.collect_pages(base_url, page_limit)

    return memetypes_urls


def getmemes_search(tags_list, desired_count):
    memecollect.prefix = 'search?context=entries&page='
    suffix1 = '&q=tags%3A%28"'
    suffix2 = '"%29+status%3Aconfirmed&sort=reverse-chronological'

    memesearch_urls = defaultdict(list)

    for search_tag in tags_list:
        memecollect.suffix = suffix1 + search_tag + suffix2
        base_url = memecollect.build_urls(pg_count=1)

        page_limit = memecollect.get_page_limit(base_url, desired_count)
        memesearch_urls[search_tag] += memecollect.collect_pages(base_url, page_limit)

    return memesearch_urls


page_count = 5  # 16 memes/page

meme_types = ['catchphrase', 'snowclone', 'emoticon', 'slang', 'hashtag']
search_tags = ['quote', 'engrish', 'copypasta']

types_urls = getmemes_types(meme_types, page_count)
search_urls = getmemes_search(search_tags, page_count)

master_urls = {**types_urls, **search_urls}

master_listform = [(term, memeurl) for term, urls in master_urls.items() for memeurl in urls]

df = pd.DataFrame.from_records(master_listform, columns=['meme type', 'url'])
df.to_csv('output/master_urls.csv', index=False)






