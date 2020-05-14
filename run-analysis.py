import os
import pandas as pd
import lib.analysis as MemeAnalysis
from lib.trends import MemeTrends


# Checks if file already exists, corrects filename
def checkfilename(savefile, ext='.csv'):
    file = savefile + ext
    i = 1
    while True:
        if os.path.exists(file):
            file = savefile + '_' + str(i) + ext
            i += 1
        else:
            return file


def logmissingtrends(missinglist):
    with open('data/analyzed/missing_trends.txt', "w+") as f:
        for meme in missinglist:
            f.write(meme + "\n")



if __name__ == "__main__":
    memesdf = pd.read_csv("data/collected/master_urls.csv", header=0, names=['meme type', 'meme', 'url'])

    analysisdf, tokensdf = MemeAnalysis.runanalysis(memesdf)
    analysisdf.to_csv(checkfilename('data/analyzed/master_analysis'))
    tokensdf.to_csv(checkfilename('data/analyzed/master_tokenfreq'))

    trends = MemeTrends()
    trendsdf, missingtrends = trends.runtrends(memesdf)
    trendsdf.to_csv(checkfilename('data/analyzed/master_trends'))
    if missingtrends:
        logmissingtrends(missingtrends)


