import sys

from independent_cascade_analyzer.graph_analyzer import independent_cascade_process, setup, estimate_expected_outcome, \
    maximize_expected_outcome, translate, maximize_target_outcome
from twitter_data_retrieve.twitter_data_retriever import SOURCE

RUNS = 3

def simulation(g, tweet):
    tweet = tweet.replace("#", " #")
    hashtags = set([i[1:] for i in tweet.split() if i.startswith("#")])

    # independent_cascade_process(g, source, tweet_hashtags)
    # g = grafo creato nel setup
    # source = numero, usare metodo per fare il mapping
    # tweet_hashtags = hashtag presenti nel tweet inserito dall'utente
    independent_cascade_process(g, translate(SOURCE), hashtags)
    return "simulation"

def expected_value(g, tweet):
    tweet = tweet.replace("#", " #")
    hashtags = set([i[1:] for i in tweet.split() if i.startswith("#")])
    # estimate_expected_outcome(g, source, hashtags, runs, expected_outcome):
    # g = grafo creato nel setup
    # source = numero, usare metodo per fare il mapping
    # hashtags =  hashtag presenti nel tweet inserito dall'utente
    # runs = numero di volte che vogliamo simulare
    # expected_outcome = lista vuota

    expected_outcome = []
    estimate_expected_outcome(g, translate(SOURCE), hashtags, RUNS, expected_outcome)
    return "expected_value"


def max_expected_value(g, tweet):
    tweet = tweet.replace("#", " #")
    hashtags = set([i[1:] for i in tweet.split() if i.startswith("#")])
    # maximize_expected_outcome(g, source, current_hashtags, runs, current_outcome)
    # g = grafo creato nel setup
    # source = numero, usare metodo per fare il mapping
    # hashtags = hashtag presenti nel tweet inserito dall'utente
    # runs = numero di volte che vogliamo simulare
    # current_outcome = expected_outcome di estimate_expected_outcome(..)

    expected_outcome = []
    estimate_expected_outcome(g, translate(SOURCE), hashtags, RUNS, expected_outcome)
    maximize_expected_outcome(g, translate(SOURCE), hashtags, RUNS, expected_outcome)

    return "maximize_probility_reach_node"

def maximize_probility_reach_node(person, tweet=None):
    # maximize_target_outcome(g, source, target, tweet_hashtags, outcomes, k=1)
    # g = grafo creato nel setup
    # source = numero, usare metodo per fare il mapping
    # target = numero, usare metodo per fare il mapping
    # tweet_hashtags = hashtag presenti nel tweet inserito dall'utente
    # outcomes = TODO
    if tweet!=None:
        tweet = tweet.replace("#", " #")
        hashtags = set([i[1:] for i in tweet.split() if i.startswith("#")])

    maximize_target_outcome(g, translate(SOURCE), translate(person), hashtags, outcomes, k=1)

if __name__ == "__main__":

    g = setup()

    s = ""
    while "esc" not in s:
        print "premi"

        print "1-[SIMULAZIONE] Cosa POTREBBE SUCCEDERE dato un certo tweet coi relativi hashtags"
        print "2-[VALORE ATTESO] Avere il valore atteso dato un certo tweet coi relativi hashtags"
        print "3-[MASSIMIZZARE IL VALORE ATTESO] (consiglia gli hashtag da usare per massimizzare il risultato(cioe la visibilita della SOURCE)"
        print "4-[MASSIMIZZARE LA PROBABILITA' DI RAGGIUNGERE UN CERTO NODO]dato un certo tweet coi relativi hashtags" \
              " e la peronsa da raggiungere, o solo la persona."
        s = sys.stdin.readline()

        if "1" in s or "2" in s or "3" in s:
            print "inserisci un tweet coi relativi hashtag"
            tweet = sys.stdin.readline()
            # print "tweet: ", tweet

        if "1" in s:
            # [SIMULAZIONE]
            print "[SIMULAZIONE]"

            print simulation(g, tweet)
        elif "2" in s:
            # [VALORE ATTESO]
            print "[VALORE ATTESO]"
            print expected_value(g, tweet)

        elif "3" in s:
            # [MASSIMIZZARE IL VALORE ATTESO]
            print "[MASSIMIZZARE IL VALORE ATTESO]"
            print max_expected_value(g, tweet)

        elif "4" in s:
            # [MASSIMIZZARE LA PROBABILITA' DI RAGGIUNGERE UN CERTO NODO]
            print "[MASSIMIZZARE LA PROBABILITA' DI RAGGIUNGERE UN CERTO NODO]"

            print "premi"
            print "     a- inserisci solo la persona"
            print "     b- inserisci solo la persona, il tweet e gli hashtag da inserire"
            choose = sys.stdin.readline()

            if "a" in choose:
                print "inserisci la persona: "
                person = sys.stdin.readline()
                print maximize_probility_reach_node(person)
            elif "b" in choose:
                print "inserisci la persona: "
                person = sys.stdin.readline()
                print "inserisci il tweet con gli hashtag: "
                tweet = sys.stdin.readline()
                print maximize_probility_reach_node(person, tweet)


            else:
                print "digita solo 'a' o 'b'"

        else:
            print "digita solo 1,2,3 o 4"


        print "--------------------------------------------------"