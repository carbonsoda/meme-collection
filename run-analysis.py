import os
import pandas as pd
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


def openmissingtxt(missinglistfile):
    missinglist = []
    with open(missinglistfile, "r") as f:
        for meme in f:
            missinglist.append(meme[:-1])
    return missinglist


def runanalysis(memes_df):
    analysisdf, tokensdf = MemeAnalysis.runanalysis(memes_df)
    analysisdf.to_csv(checkfilename('data/analyzed/master_analysis'))
    tokensdf.to_csv(checkfilename('data/analyzed/master_tokenfreq'))


def runtrends(memeset, missingver=False):
    trends = MemeTrends()
    trendsdf, missingtrends = None, None
    if missingver:
        redotrends = openmissingtxt(memeset)
        trendsdf, missingtrends = trends.makeupmissing(redotrends)
    else:
        trendsdf, missingtrends = trends.runtrends(memeset)

    if missingtrends:
        logmissingtrends(missingtrends)
    trendsdf.to_csv(checkfilename('data/analyzed/master_trends'))


if __name__ == "__main__":
    # either doing first round of analysis or doing trends
    # memesdf = pd.read_csv("data/collected/master_urls.csv", header=0, names=['meme type', 'meme', 'url'])
    memesdf = pd.read_csv("data/analyzed/master_analysis.csv", header=0)

    # runanalysis(memesdf)
    # runtrends("data/analyzed/missing_trends.txt", True)
    # runtrends(memesdf)

