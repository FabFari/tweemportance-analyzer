import tweepy
import twitter

from tweepy import *


NOME = "matteosalvinimi"
FILE = "tweets.txt"
FILE_ANSWERS = "answers.txt"

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

    #listener = StdOutListener()
    #stream = Stream(auth, listener)

    # Construct the API instance
    api = tweepy.API(auth)
    return api

def setup_2():
    api = twitter.Api(consumer_key=consumer_key,
                     consumer_secret=consumer_secret,
                     access_token_key=access_token,
                     access_token_secret=access_token_secret)
    rep = api.GetSearch(raw_query="q=salvini&count=50&pages=20")
    print len(rep)
    #replies = (q="to:{}".format(NOME), count=100, page=15)
    #print "Replies: ", len(replies)

def get_reply(stream):
    stream.filter()



def get_tweets(api,screenname=NOME):
    status_set = api.user_timeline(screen_name=NOME)

    with open(FILE, 'wt') as f, open(FILE_ANSWERS, "wt") as f_a:

        for status in status_set:

            print status.id
            print status.text
            print status.in_reply_to_status_id
            user = status.author
            print user.screen_name
            #replies = api.search(q="to:{}".format(NOME), sinceId = status.id)
            replies = api.search(q="to:{}".format(NOME), count=100, page=1)
            print "Replies: ", len(replies)
            for a in replies:
                print "Replie: ", a.id
                f_a.write("{}:{}\n\n".format(status.id, a))
            f.write("id:{}\n\n".format(status))#.format(t['id'], t['text']))

if __name__ == "__main__":
    api = setup_2()
    #get_tweets(api)