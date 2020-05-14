import pandas as pd
from pytrends.request import TrendReq
import string


class MemeTrends:
    def __init__(self):
        self.pytrend = TrendReq(hl='en-US', tz=360, retries=1, backoff_factor=600)
        # credit to Martijn Pieters, for efficent method
        self.translator = str.maketrans('', '', string.punctuation)

    def runtrends(self, memesdf):
        trendslist, missingtrends = self.getalltrends(memesdf)
        trendsdf = self.join_dfs(trendslist)

        return trendsdf, missingtrends

    def getalltrends(self, memesdf):
        trendslist = []
        trendmissing = []

        for row in memesdf.itertuples():
            meme = row[2]
            memetrend = self.getmemetrend(meme)

            if type(memetrend) == pd.DataFrame:
                memetrend = memetrend.drop(columns="isPartial")
                trendslist.append(memetrend)
            else:
                trendmissing.append(meme)

        return trendslist, trendmissing

    # Gets Google Trend for individual meme
    # cat=299 is for "Online Communities"
    def getmemetrend(self, memetxt, cat=299, retry=0):
        if not self.buildpayload(memetxt, cat):
            return None

        memetrend = self.pytrend.interest_over_time()

        # sometimes it won't raise exception but it will come back falsely empty
        if memetrend.empty:
            if retry == 0:
                # try just without punctuation
                self.getmemetrend(self.removepunc(memetxt), retry=1)
            elif retry == 1:
                # try just general category 0
                self.getmemetrend(memetxt, cat=0, retry=2)
        return memetrend

    def buildpayload(self, memetxt, cat, retry=0):
        try:
            self.pytrend.build_payload([memetxt], timeframe='all', cat=cat)
        except:
            retry += 1
            if retry == 1:
                # try just without punctuation
                self.buildpayload(self.removepunc(memetxt), cat, retry=retry)
            elif retry == 2:
                # try just general category now
                self.buildpayload(memetxt, cat=0, retry=retry)
            else:
                return False

        return True

    def join_dfs(self, dfs_list):
        df_master = dfs_list[0].join(dfs_list[1:])
        return df_master

    # Helper method
    def removepunc(self, memetxt):
        return memetxt.translate(self.translator)
