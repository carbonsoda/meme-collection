import pandas as pd
from nltk.tokenize import wordpunct_tokenize
import textstat
import emoji
import re
from collections import defaultdict
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer


class LingAnalysis:
    def __init__(self):
        self.vader = SentimentIntensityAnalyzer()
        # Categories identified as meme pastiche by (cite)
        self.pastichetypes = {"snowclone", "catchphrase", "copypaste", "phrasal-template"}

    # handles sentiment-related values
    def entry_sentiment(self, entry):
        vs = self.vader.polarity_scores(entry['meme'])

        entry['compound'] = vs.get('compound')
        entry['neutral'] = vs.get('neu')

        # negative score vs everything else
        entry['negative'] = vs.get('neg')
        entry['non-negative'] = vs.get('neu') + vs.get('pos')

    # Avoids repeated parsing of hashtag memes
    def parsehashtags(self, memetxt, memetype):
        if memetype == 'hashtag':
            # strips hashtag and split at uppercase letters
            return " ".join(re.findall('[A-Z][^A-Z]*', memetxt))
        else:
            return memetxt

    def wordcount(self, memetxt):
        return len(re.findall(r"[\w']+", memetxt))

    # Text readibility
    def wordcomplexity(self, memetxt):
        # Uses Flesh reading ease formula which is based on the content itself
        # instead of list of hard/common words
        # highest score is 121.22
        return textstat.flesch_reading_ease(memetxt)

    # Emoji count
    def hasemojis(self, memetxt):
        return emoji.emoji_count(memetxt) > 0

    # Is it a snowclone, catchphrase, copypasta, phrasal-template
    def ispastiche(self, meme_type):
        if meme_type in self.pastichetypes:
            return True
        return False


def entrytemplate(meme_text, memetype):
    entry = {'memetype': memetype,
             'meme': meme_text,
             'count': 0,
             'complexity': 0,
             'compound': 0.0,
             'neutral': 0.0,
             'negative': 0.0,
             'non-negative': 0.0,
             'hasemoji': False,
             'ispastiche': False}
    return entry


# Tracks token count per meme
# Hashtags are passed through as spaced out string
def frequencies(meme_text, memefreq):
    for token in wordpunct_tokenize(meme_text):
        memefreq[token.lower()] += 1


def runanalysis(urlsdf):
    analysis = LingAnalysis()
    newentries = []
    memefreq = defaultdict(int)

    for row in urlsdf.itertuples():
        memetype = row[1]
        meme = row[2]
        entry = entrytemplate(meme, memetype)

        analysis.entry_sentiment(entry)

        # Only vadar handles hashtags, the others can't (properly)
        meme = analysis.parsehashtags(meme, memetype)
        entry['count'] = analysis.wordcount(meme)
        entry['complexity'] = analysis.wordcomplexity(meme)
        entry['hasemoji'] = analysis.hasemojis(meme)
        entry['ispastiche'] = analysis.ispastiche(memetype)

        frequencies(meme, memefreq)
        newentries.append(entry)

    analysisdf = pd.DataFrame(newentries)
    tokendf = pd.Series(memefreq).sort_values(ascending=False)

    return analysisdf, tokendf
