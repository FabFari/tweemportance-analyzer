import os

import time
import tweepy

from tweepy import *

SOURCE = "VittorioSgarbi"#"BissoliAn" # "matteosalvinimi"
FILE_TWEETS = "tweets.txt"
FILE_REPLIES = "replies.txt"
DATA_DIRECTORY = "data/"
TWEETS_DIRECTORY = "tweets/"
PEOPLE_DIRECTORY = "people/"
PEOPLE_VISITED = "people_visited.txt"
REPLIES_SOURCE = "replies_salvini.txt"

NUM_TWEETS = 1
TIME_TO_SLEEP = 960

access_token = "815961135321059330-7i5Mh5wC2q6WNJJiJMrlqD6k3m9DRMm"
access_token_secret = "9yDVE9SlD1qwHNPcew3mxTysYgU7onmEVmFvpnWsKr844"
consumer_key = "kZEJIcJ5t9FNGWhMEkm8WyEV7"
consumer_secret = "oIsyfHv8wbxsHcmvMXAOLkv4HzuoR09ii1fANUHXMnO8JEVfmn"

'''
access_token = '2341848095-rFwC9RZJceJGUvAsTEUivc8Hq6mdaHBGoFlNo44'
access_token_secret = 'xFCaYxcGjN2X4aVCXu3cV0U8spIAiiVgwabygVfFkmIbU'
consumer_key = 'tZRi2DVFSeEl4K77R2yNLE8aQ'
consumer_secret = 'Wnewl8PFjgBC9QlIimLpirYvdPvrvE9Mx4vEOeCvFPeuQr9s5G'
'''



def setup():
    auth = OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)

    data_path = os.path.join(os.pardir, DATA_DIRECTORY)
    if not os.path.exists(data_path):
        os.makedirs(data_path)

    path_people = os.path.join(data_path, PEOPLE_DIRECTORY)
    if not os.path.exists(path_people):
        os.makedirs(path_people)

    if not os.path.exists(os.path.join(data_path, PEOPLE_VISITED)):
        visited = open(os.path.join(data_path, PEOPLE_VISITED), 'w')
        visited.close()
    # Construct the API instance
    api = tweepy.API(auth)
    return api


# prende i primi 100 tweets della source
def get_source_tweets(api, screen_name=SOURCE, verbose=True):
    tweets_retrieved = 0

    first_try = True
    max_id = None
    min_id = None

    with open(os.path.join(os.pardir, DATA_DIRECTORY, FILE_TWEETS), 'wt') as f:
        n_tweets = NUM_TWEETS
        id_seen = set()
        while tweets_retrieved < n_tweets:
            try:
                if not first_try:
                    status_set = api.user_timeline(screen_name=screen_name, count=100, max_id=max_id-1)
                else:
                    status_set = api.user_timeline(screen_name=screen_name, count=100)
                    first_try = False
            except tweepy.error.TweepError as err:
                print err
                break

            if verbose:
                print "<!----NUM_TWEETS:", tweets_retrieved

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

                if status.id in id_seen:
                    if verbose:
                        print id_seen
                        print "status.id: ", status.id
                        print "status.text", status.text
                    n_tweets = tweets_retrieved
                    break
                else:
                    id_seen.add(status.id)

                if min_id > status.id:
                    min_id = status.id

                line = "{}\n{}\n".format(status.id, status.text.encode('utf-8').replace("\n", " "))
                f.write(line)
                if verbose:
                    print line.replace("\n", "\t")

                tweets_retrieved += 1

                if tweets_retrieved >= NUM_TWEETS:
                    break

            max_id = min_id

    return min_id


# dato il nome=NAME ritorna i tweets rivolti a quella persona (<=2700)
def get_replies(screen_name=SOURCE, min_id=None, max_replies=-1, filename=FILE_REPLIES):
    ids_set = set()
    return_value = 0

    if screen_name == SOURCE and os.path.exists(os.path.join(DATA_DIRECTORY, REPLIES_SOURCE)):
        return return_value

    with open(os.path.join(os.pardir, DATA_DIRECTORY, filename), "wt") as f:
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
                    line = "{}\t{}\t{}\t{}\n".format(s.id, s.in_reply_to_status_id, s.author.screen_name,
                                                     s.text.encode('utf-8').replace("\n", " "))
                    print line.strip("\n")
                    f.write(line)
                    if max_replies != -1 and len(ids_set) >= max_replies:
                        break
        except tweepy.error.TweepError as err:
            print err
            return_value = -1
        finally:
            print "<------Tweets retrieved: ", len(ids_set)
            return return_value


# generare un file per ognuno dei primi 100 tweets, dentro la cartella people ci mette il nome della Source
def generate_tweets_file():
    path_people = os.path.join(os.pardir, DATA_DIRECTORY, PEOPLE_DIRECTORY)
    if not os.path.exists(path_people):
        os.makedirs(path_people)

    path_person = os.path.join(path_people, SOURCE)
    if not os.path.exists(path_person):
        os.makedirs(path_person)

    with open(os.path.join(os.pardir, DATA_DIRECTORY, FILE_TWEETS), "r") as f:
       for r in f:
            row = r.split("\t")
            with open(path_person + '/' + row[0], 'w')as f_tweet:


                f_tweet.write(row[1])


# data la persona, andiamo a prendere tutti gli archi uscenti per tom, per andrea andiamo a prendere tutte le
# risposte verso quella persona e vado a controllare nel set di people se presente (e quindi ci interessa)
def get_people(name=SOURCE):
    # creo la cartella PEOPLE
    path_people = os.path.join(os.pardir, DATA_DIRECTORY, PEOPLE_DIRECTORY)

    with open(os.path.join(os.pardir, DATA_DIRECTORY, FILE_REPLIES), "r") as f:
        for r in f:
            row = r.split('\t')
            #  print row[2]

            if row[2] != SOURCE:
                # controllo che dentro(la cartella)la persona ci sia il file con il tweet
                if os.path.exists(os.path.join(path_people, name, row[1])):

                    # creo la cartella per la nuova persona, se non esiste
                    if not os.path.exists(os.path.join(path_people, row[2])):
                        os.makedirs(os.path.join(path_people, row[2]))

                    # aggiungo il file con l'informazione dell'arco
                    with open(os.path.join(path_people, row[2], row[0]), "w") as f_person:
                        line = "{}\t{}\n".format(row[1], name)
                        f_person.write(line)


def get_graph_data(verbose=True):
    visited_all_nodes = False
    # set delle persone visitate
    people_visited = set()

    with open(os.path.join(os.pardir, DATA_DIRECTORY, PEOPLE_VISITED), 'r') as f_vis:
        for r in f_vis:
            # dal file che abbiamo leggiamo le persone che abbiamo visitato fino a questo momento
            people_visited.add(r.strip("\n"))

    while not visited_all_nodes:
        if verbose:
            print "<----------------------------------------------------------------------------------------------------->"
            print "<--------------------------------------------- ITERATION --------------------------------------------->"
            print "<----------------------------------------------------------------------------------------------------->"

        # dalla dir people vedo tutte le persone presenti
        # all'inizio ci sara solo la SOURCE perche dal metodo generate_tweets_file() generiamo solo la cartella con nome
        # della source
        people = get_dir_people()

        # se sono uguali vuol dire che abbiamo finito
        if len(people) == len(people_visited):
            visited_all_nodes = True
            continue
        else:
            if verbose:
                print "People before removing visited: ", people
            # faccio la differenze per ricavare le persone ancora da visitare
            people = people.difference(people_visited)
            if verbose:
                print "People after removing duplicates", people

        # dobbiamo andare per livelli altrimenti perdiamo archi
        while len(people) != 0:

            name = people.pop()

            if verbose:
                print "Current person: ", name

            # prendiamo tutte le risposte rivolte a name
            ret = get_replies(screen_name=name, max_replies=40)
            print "ret: ", ret

            if ret != -1 or name == SOURCE:

                get_people(name)
                people_visited.add(name)

                # add name into file PEOPLE_VISITED
                with open(os.path.join(os.pardir, DATA_DIRECTORY, PEOPLE_VISITED), 'a') as f_vis:
                    f_vis.write("{}\n".format(name))

            else:
                # Reinsert the person in the set
                people.add(name)
                if verbose:
                    print "We will try again in 16 minutes, Everything comes to him who waits.."
                # c e stato un errore, Twitter mi ha cacciato, aspettiamo e rifacciamo
                time.sleep(TIME_TO_SLEEP)

            if verbose:
                print "People so far visited: ", people_visited


def get_dir_people(verbose=True):
    path_people = os.path.join(os.pardir, DATA_DIRECTORY, PEOPLE_DIRECTORY)
    l = [name for name in os.listdir(path_people)
         if os.path.isdir(os.path.join(path_people, name))]
    if verbose:
        print "[get_dir_people]   People currently in the directory: ", l
    return set(l)


if __name__ == "__main__":
    api = setup()
    get_source_tweets(api)
    generate_tweets_file()
    get_graph_data()
