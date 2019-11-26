import os
import pandas as pd
from collections import defaultdict
from lib.memecollection import MemeCollection

memecollect = MemeCollection()


# Runs through procedure of a collection, returns list
# memecollect suffix + prefix are changed in respective methods
def run_collect(desired_count):
    base_url = memecollect.build_urls(pg_count=1)
    page_limit = memecollect.get_page_limit(base_url, desired_count)

    if page_limit < 1:
        return []
    return memecollect.collect_pages(base_url, page_limit)


# Collecting by specific 'types' in the Meme category of KnowYourMeme, aka sub-categories
def getmemes_types(types_list, desired_count):
    # shows in order of meme itself, not by date added to the database
    memecollect.suffix = '?sort=reverse-chronological'

    memetypes_urls = defaultdict(list)

    for meme_type in types_list:
        memecollect.prefix = 'types/' + meme_type + '/page/'
        memetypes_urls[meme_type] += run_collect(desired_count)

        # "related sub-meme entries"
        memecollect.prefix = 'memes/' + meme_type + '/children/page/'
        memetypes_urls[meme_type] += run_collect(desired_count)

    return memetypes_urls


# Collecting memes via search queries/tags
def getmemes_search(tags_list, desired_count):
    memecollect.prefix = 'search?context=entries&page='
    suff1 = '&q=tags%3A%28"'
    suff2 = '"%29+status%3Aconfirmed&sort=reverse-chronological'

    altsuf1 = '&q='
    altsuf2 = '+status%3Aconfirmed&sort=reverse-chronological'

    memesearch_urls = defaultdict(list)

    for search_tag in tags_list:
        memecollect.suffix = suff1 + search_tag + suff2
        results = run_collect(desired_count)

        if not results:
            tag = search_tag.replace(' ', '+')
            memecollect.suffix = altsuf1 + tag + altsuf2
            results = run_collect(desired_count)

        memesearch_urls[search_tag] += results

    return memesearch_urls


# Prevent overwriting
def checkexisting(savefile, ext='.csv'):
    file = savefile + ext
    i = 1
    while True:
        if os.path.exists(file):
            file = savefile + '_' + str(i) + ext
            i += 1
        else:
            return file


# Compile into master dict of lists, to then compile into a master list of tuples (meme, url)
def build_df(memes_dict, savefile):
    # compile given memes_dict into a master list of tuples (meme, url)
    list_form = [
        (
            term,
            memeurl,
            memeurl.rsplit('/memes/')[1].replace('-', ' ')
        )
        for term, urls in memes_dict.items()
        for memeurl in urls
    ]

    df = pd.DataFrame.from_records(list_form, columns=['meme type', 'url', 'meme'])
    df.drop_duplicates('url', keep='first', inplace=True)
    df.dropna()  # might not need

    savename = checkexisting(savefile, ext='.csv')
    df.to_csv(savename, index=False)

    return df


page_count = 5  # 16 memes/page max

meme_types = ['catchphrase', 'snowclone', 'emoticon', 'slang', 'hashtag']
search_queries = [
    'quote', 'engrish', 'rage-comics', 'reaction', 'expression',
    'copypasta', 'catchphrase', 'snowclone', 'phrasal-template'
]  # Picks up confirmed memes which have NO type assigned

types_urls = getmemes_types(meme_types, page_count)
search_urls = getmemes_search(search_queries, page_count)

masterdf = build_df({**types_urls, **search_urls}, './output/master_urls')
# search urls may require some hand care
searchdf = build_df(search_urls, './output/search_urls')
