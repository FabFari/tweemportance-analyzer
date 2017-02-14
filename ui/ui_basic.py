import sys

from independent_cascade_analyzer.graph_analyzer import independent_cascade_process, setup, estimate_expected_outcome, \
    maximize_expected_outcome, translate, maximize_target_outcome, is_hashtag
from twitter_data_retrieve.twitter_data_retriever import SOURCE

RUNS = 3

def simulation(g, tweet):

    tweet = tweet.replace("#", " #")
    hashtags = set([i[0:] for i in tweet.split() if i.startswith("#")])
    hashtags = list(hashtags)
    if len(hashtags) ==0:
        return "hashtags not found"

    if not is_hashtag(hashtags):
        return "hashtags not found"


    # independent_cascade_process(g, source, tweet_hashtags)
    # g = grafo creato nel setup
    # source = numero, usare metodo per fare il mapping
    # tweet_hashtags = hashtag presenti nel tweet inserito dall'utente
    return independent_cascade_process(g, translate(SOURCE), hashtags)

def expected_value(g, tweet):
    tweet = tweet.replace("#", " #")
    hashtags = set([i[0:] for i in tweet.split() if i.startswith("#")])
    hashtags = list(hashtags)
    if len(hashtags) ==0:
        return "hashtags not found", None

    if not is_hashtag(hashtags):
        return "hashtags not found",None
    # estimate_expected_outcome(g, source, hashtags, runs, expected_outcome):
    # g = grafo creato nel setup
    # source = numero, usare metodo per fare il mapping
    # hashtags =  hashtag presenti nel tweet inserito dall'utente
    # runs = numero di volte che vogliamo simulare
    # expected_outcome = lista vuota

    expected_outcome = []
    n = estimate_expected_outcome(g, translate(SOURCE), hashtags, RUNS, expected_outcome)
    return n, expected_outcome

def max_expected_value(g, tweet):
    tweet = tweet.replace("#", " #")
    hashtags = set([i[0:] for i in tweet.split() if i.startswith("#")])
    hashtags = list(hashtags)
    if len(hashtags) ==0:
        return "hashtags not found"

    if not is_hashtag(hashtags):
        return "hashtags not found"
    # maximize_expected_outcome(g, source, current_hashtags, runs, current_outcome)
    # g = grafo creato nel setup
    # source = numero, usare metodo per fare il mapping
    # hashtags = hashtag presenti nel tweet inserito dall'utente
    # runs = numero di volte che vogliamo simulare
    # current_outcome = expected_outcome di estimate_expected_outcome(..)

    expected_outcome = []
    estimate_expected_outcome(g, translate(SOURCE), hashtags, RUNS, expected_outcome)
    return maximize_expected_outcome(g, translate(SOURCE), hashtags, RUNS, expected_outcome)

def maximize_probility_reach_node(person, tweet=None):
    # maximize_target_outcome(g, source, target, tweet_hashtags, k=5)
    # g = grafo creato nel setup
    # source = numero, usare metodo per fare il mapping
    # target = numero, usare metodo per fare il mapping
    # tweet_hashtags = hashtag presenti nel tweet inserito dall'utente
    hashtags = []
    if tweet!=None:
        tweet = tweet.replace("#", " #")
        hashtags = set([i[0:] for i in tweet.split() if i.startswith("#")])
        hashtags = list(hashtags)
        if len(hashtags) == 0:
            return "hashtags not found"

        if not is_hashtag(hashtags):
            return "hashtags not found"


    return maximize_target_outcome(g, translate(SOURCE), translate(person), hashtags)


if __name__ == "__main__":

    g = setup()

    s = ""
    while "5" not in s:
        print "type"

        print "1-[SIMULATION]"
        print "2-[EXPECTED VALUE]"
        print "3-[MAXIMIZE THE EXPECTED VALUE]"
        print "4-[MAXIMIZE THE PROBABILITY TO REACH A NODE]"
        print "5-[ESC]"
        s = sys.stdin.readline()

        if "1" in s or "2" in s or "3" in s:
            print "Insert a tweet with hashtag"
            tweet = sys.stdin.readline()
            # print "tweet: ", tweet

        if "1" in s:
            # [SIMULAZIONE]
            print "[SIMULATION]"

            print simulation(g, tweet)

        elif "2" in s:
            # [VALORE ATTESO]
            print "[EXPECTED VALUE]"
            n, ev = expected_value(g, tweet)
            if ev is None:
                print n
            else:
                print "expected number nodes: ", n
                print ev

        elif "3" in s:
            # [MASSIMIZZARE IL VALORE ATTESO]
            print "[MAXIMIZE THE EXPECTED VALUE]"
            print max_expected_value(g, tweet)

        elif "4" in s:
            # [MASSIMIZZARE LA PROBABILITA' DI RAGGIUNGERE UN CERTO NODO]
            print "[MAXIMIZE THE PROBABILITY TO REACH A NODE]"

            print "type"
            print "     a- Insert only a target(person)"
            print "     b- Insert target(person)and aa tweet with hashtag"
            choose = sys.stdin.readline()

            if "a" in choose:
                print "Insert the target(person): "
                person = sys.stdin.readline()
                print maximize_probility_reach_node(person)
            elif "b" in choose:
                print "Insert the target(person): "
                person = sys.stdin.readline()
                print "Insert a tweet with hashtag"
                tweet = sys.stdin.readline()
                print maximize_probility_reach_node(person, tweet)


            else:
                print "type only 'a' o 'b'"

        else:
            print "type only 1,2,3 o 4"


        print "--------------------------------------------------"