import tweepy
import twitter

from tweepy import *


NOME = "matteosalvinimi"
FILE = "tweets.txt"
FILE_REPLIES = "replies.txt"

NUM_TWEETS = 100

access_token = "815961135321059330-7i5Mh5wC2q6WNJJiJMrlqD6k3m9DRMm"
access_token_secret = "9yDVE9SlD1qwHNPcew3mxTysYgU7onmEVmFvpnWsKr844"
consumer_key = "kZEJIcJ5t9FNGWhMEkm8WyEV7"
consumer_secret = "oIsyfHv8wbxsHcmvMXAOLkv4HzuoR09ii1fANUHXMnO8JEVfmn"


class StdOutListener(StreamListener):
    """A basic listener that just prints received tweets to stdout."""
    def on_data(self, data):
        print data
        return True

    def on_error(self, status):
        print status


def setup():
    auth = OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)

    # listener = StdOutListener()
    # stream = Stream(auth, listener)

    # Construct the API instance
    api = tweepy.API(auth)
    return api


def setup_2():
    api = twitter.Api(consumer_key=consumer_key,
                      consumer_secret=consumer_secret,
                      access_token_key=access_token,
                      access_token_secret=access_token_secret)
    dict = {}
    rep = api.GetSearch(raw_query="q=salvini&count=100&page=1")
    for r in rep:
        dict[r.id] = 1

    rep = api.GetSearch(raw_query="q=salvini&count=100&page=2")
    for r in rep:
        dict[r.id] = 2

    for k in dict.keys():
        print k, ": ", dict[k]
    # replies = (q="to:{}".format(NOME), count=100, page=15)
    # print "Replies: ", len(replies)


def get_reply(stream):
    stream.filter()


def get_source_tweets(api, screenname=NOME):
    tweets_retrieved = 0

    first_try = True
    max_id = None
    min_id = None

    with open(FILE, 'wt') as f:

        while tweets_retrieved < NUM_TWEETS:
            try:
                if not first_try:
                    status_set = api.user_timeline(screen_name=NOME, count=100, max_id=max_id)
                else:
                    status_set = api.user_timeline(screen_name=NOME, count=100)
            except tweepy.error.TweepError as err:
                print err
                break

            print "<!----NUM_TWEETS:", len(status_set)

            # RETRIEVE ALL LEVEL 0 TWEETS
            first_tweet = True
            for status in status_set:
                if first_tweet:
                    min_id = status.id
                    first_tweet = False

                if status.in_reply_to_status_id is not None:
                    continue

                if len(status.entities[u'hashtags']) == 0:
                    continue

                # SALVINI TEST
                if status.entities[u'hashtags'][0][u'text'] == u'Salvini' and len(status.entities[u'hashtags']) < 2:
                    continue

                if min_id > status.id:
                    min_id = status.id

                line = "{}\n{}\n".format(status.id, status.text.encode('utf-8').replace("\n", " "))
                f.write(line)
                print line

                tweets_retrieved += 1

                if tweets_retrieved >= NUM_TWEETS:
                    break

            max_id = min_id
            # TODO
            # Create file per tweet
    return min_id


def get_replies(screen_name=NOME, min_id=None, max_replies=-1, filename=FILE_REPLIES):
    ids_set = set()

    with open(filename, "wt") as f:
        try:
            if min_id is None:
                replies = tweepy.Cursor(api.search, q="to:{}".format(screen_name))
            else:
                replies = tweepy.Cursor(api.search, q="to:{}".format(screen_name), since_id=min_id)

            for s in replies.items():
                if s.in_reply_to_status_id is None:
                    continue

                if id in ids_set:
                    break
                else:
                    ids_set.add(s.id)
                    line = "{}\t{}\t{}\t{}\n\n".format(s.id, s.in_reply_to_status_id, s.author.screen_name, s.text.encode('utf-8').replace("\n", " "))
                    print line
                    f.write(line)
                    if max_replies != -1 and len(ids_set) >= max_replies:
                        break
        except tweepy.error.TweepError as err:
            print err
        finally:
            print "<------Tweets retrieved: ", len(ids_set)


def tweet_graph_builder(file_tweets=FILE):
    # TODO
    return None


if __name__ == "__main__":
    api = setup()
    # get_source_tweets(api)
    get_replies()
