import os
import pandas as pd
from collections import defaultdict
from lib.memecollection import MemeCollection, EntryCollection

# DESIRED MEMES #
MEME_TYPES = ['catchphrase', 'snowclone', 'emoticon', 'slang', 'hashtag', 'copypasta', 'exploitable']
MEME_TAGS = [  # Picks up confirmed memes which have NO type assigned
    'quote', 'engrish', 'rage-comics', 'reaction', 'expression',
    'copypasta', 'catchphrase', 'snowclone', 'phrasal-template'
]
COL_NAMES = ['meme type', 'meme', 'url']


class RunCollect(MemeCollection):
    def __init__(self, memetypes, memetags):
        super().__init__()
        self.memetypes = memetypes
        self.memetags = memetags
        self.page_count = 5  # 16 memes/page max

    # Runs through procedure of a collection, returns list
    # MemeCollection (parent) suffix + prefix are changed in respective methods
    def run_collect(self, desired_count):
        base_url = self.build_urls(pg_count=1)
        page_limit = self.get_page_limit(base_url, desired_count)

        if not page_limit:
            return []
        return self.collect_pages(base_url, page_limit)

    # Collecting by specific 'types' in the Meme category of KnowYourMeme, aka sub-categories
    def getmemes_types(self, memetypes, desired_count):
        # shows in order of meme itself, not by date added to the database
        self.suffix = '?sort=reverse-chronological'

        memetypes_urls = defaultdict(list)

        for meme_type in memetypes:
            self.prefix = 'types/' + meme_type + '/page/'
            memetypes_urls[meme_type] += self.run_collect(desired_count)

            # "related sub-meme entries"
            self.prefix = 'memes/' + meme_type + '/children/page/'
            memetypes_urls[meme_type] += self.run_collect(desired_count)

        return memetypes_urls

    # Collecting memes via search queries/tags
    def getmemes_search(self, memetags, desired_count):
        self.prefix = 'search?context=entries&page='
        # prep for possible self.suffix needed
        suff1 = '&q=tags%3A%28"'
        suff2 = '"%29+status%3Aconfirmed&sort=reverse-chronological'
        suff1_alt = '&q='
        suff2_alt = '+status%3Aconfirmed&sort=reverse-chronological'

        memesearch_urls = defaultdict(list)

        for meme_tag in memetags:
            self.suffix = suff1 + meme_tag + suff2
            results = self.run_collect(desired_count)

            if not results:
                tag = meme_tag.replace(' ', '+')
                self.suffix = suff1_alt + tag + suff2_alt
                results = self.run_collect(desired_count)

            memesearch_urls[meme_tag] += results

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


# Compile given memes_dict into a dataframe and save it
def build_df(memes_dict, savefile, colnames=COL_NAMES):
    # compile given memes_dict into a master list of tuples (type/tag, title, url)
    list_form = [(term, memeurl[0], memeurl[1])
                 for term, urls in memes_dict.items()
                 for memeurl in urls
                 ]

    df = pd.DataFrame.from_records(list_form, columns=colnames)
    df.drop_duplicates('url', keep='first', inplace=True)
    df.dropna()  # might not need

    savename = checkexisting(savefile, ext='.csv')
    df.to_csv(savename, index=False)
    savename = checkexisting(savefile, ext='.xlsx')
    df.to_excel(savename, index=False)

    return df


def startmaster():
    page_count = 5
    mastercollect = RunCollect(MEME_TAGS, MEME_TYPES)
    types_urls = mastercollect.getmemes_types(MEME_TYPES, page_count)
    tags_urls = mastercollect.getmemes_search(MEME_TAGS, page_count)

    masterdf = build_df({**types_urls, **tags_urls}, './output/master_urls')
    # tag urls may require some hand care
    tagsdf = build_df(tags_urls, './output/tag_urls')


def startdetails(entryfile):
    runentry = EntryCollection()
    df_entries = pd.read_csv(entryfile, header=0)

    entries = defaultdict(lambda: defaultdict(list))
    for idx, memetype, memename, memeurl in df_entries.itertuples():
        details = runentry.entry_info(memeurl)
        entries[memetype][memename].append(details)


if __name__ == "__main__":
    master_collecting = True
    details_collecting = False
    if master_collecting:
        startmaster()
    if details_collecting:
        startdetails('output/master_urls.csv')
