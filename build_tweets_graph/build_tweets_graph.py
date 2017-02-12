


# a questo punto abbiamo i dati in modo da costruire il grafo
from twitter_data_retrieve.twitter_data_retriever import *


def graph_from_data(source=SOURCE, verbose=True):
    tweets_map = {}
    people = get_dir_people()
    people.remove(SOURCE)
    base_path = os.path.join(os.pardir, DATA_DIRECTORY, PEOPLE_DIRECTORY)
    for p in people:
        tweets_map[p] = {}
        person_path = os.path.join(base_path, p)
        tweets = [name for name in os.listdir(person_path)]
        for t in tweets:
            with open(os.path.join(person_path, t), 'r') as f:
                line = f.readline().strip("\n")
                line = line.split("\t")
                tweets_map[p][t] = (line[0], line[1])
    for p in people:
        for k in tweets_map[p]:
            tup = tweets_map[p][k]
            if verbose:
                print "<-------------------------------------------------------------------------------------->"
                print "Adding edge: ", tup[1], "\t", p
            add_edges(tweets_map, tup[1], tup[0], tup[1], p)


def add_edges(tweets_map, person, tweet, source, target, verbose=True):
    if verbose:
        print "person: ", person
        print "tweet: ", tweet
        print "source: ", source
        print "target: ", target
        print
    if person == SOURCE:
        path = os.path.join(os.pardir, DATA_DIRECTORY, PEOPLE_DIRECTORY, person)
        with open(os.path.join(path, tweet), 'a')  as f:
            edge = "{}\t{}\n".format(source,target)
            f.write(edge)
    else :
        tup = tweets_map[person][tweet]
        add_edges(tweets_map, tup[1], tup[0], source, target)


if __name__ == "__main__":
    graph_from_data()