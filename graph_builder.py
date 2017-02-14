import os
import operator

from collections import defaultdict
from BitVector import BitVector

# TODO File with all constants
SOURCE_LABEL = "matteosalvinimi"
NUM_TWEETS = 100
DATA = "data1"
PEOPLE = "people1"
FINAL_GRAPH = "graph"

def tweet_parser(filename, hashtags_map=None, hashtags_bitmask=None, graph_id=None, debug=False):
    tweet_graph = dict()

    f = open(os.path.join(DATA, PEOPLE, SOURCE_LABEL, filename), 'r')

    raw_hashtags = f.readline().strip("\n").split("\t")
    raw_hashtags.pop()

    hs = set()

    # Hashtag Normalization
    ind = -1
    for ht in raw_hashtags:
        for char in ht:
            if char in [",", ".", ";", '"', ")", "?", "!", ":", "'"]:
                ind = ht.find(char)
                if ind != -1:
                    hs.add(ht[0:ind])
                    break
                # print ht[0:ind]
        if ind == -1:
                hs.add(ht)

    hashtags = list(hs)

    if debug:
        print "hashtags:", hashtags

    line = f.readline()
    while len(line) > 0:
        edge = line.strip("\n").split("\t")

        if debug:
            print "edge:", edge

        if edge[1] == SOURCE_LABEL:
            line = f.readline()
            continue

        if edge[0] not in tweet_graph:
            tweet_graph[edge[0]] = set()
            tweet_graph[edge[0]].add(edge[1])
        else:
            tweet_graph[edge[0]].add(edge[1])

        if edge[1] not in tweet_graph:
            tweet_graph[edge[1]] = set()

        line = f.readline()

    if hashtags_map is not None:
        for h in hashtags:
            hashtags_map[h].append(tweet_graph)
            hashtags_bitmask[h][graph_id] = 1

    if debug:
        print tweet_graph
        '''
        from collections import deque
        queue = deque(tweet_graph[SOURCE_LABEL])
        # queue = tweet_graph[SOURCE_LABEL]
        print SOURCE_LABEL
        while len(queue) > 0:
            node = queue.popleft()
            print node
            queue.extend(tweet_graph[node])
        '''

    f.close()

    return tweet_graph, hashtags


# UNUSED, for the moment...
def join_graphs(graph_map):
    union_graph = defaultdict(lambda: set())

    for entry in graph_map.values():
        graph = entry[0]
        for nodes in graph.keys():
            union_graph[nodes].update(graph[nodes])

    return union_graph


def graph_file_writer(final_graph, filename="final_graph.tsv"):
    f = open(os.path.join(DATA, FINAL_GRAPH, filename), 'wt')

    for edge in final_graph.keys():
        nodes = edge.split("->")
        f.write("{}\t{}\t".format(nodes[0], nodes[1]))
        prob = ""
        for ht in final_graph[edge].keys():
            if prob == "":
                prob += "{}\t{}".format(ht, final_graph[edge][ht])
            else:
                prob += "\t{}\t{}".format(ht, final_graph[edge][ht])
        prob += "\n"
        f.write(prob)

    f.close()


def jaccard_all_pairs_similarity_file_writer(ht_bitmasks, filename="jaccard_all_pairs_similarity.tsv"):
    ht_pair_sim = defaultdict(lambda: dict())
    for (ht1, bm1) in ht_bitmasks.iteritems():
        for (ht2, bm2) in ht_bitmasks.iteritems():
            if ht1 == ht2:
                continue
            ht_pair_sim[ht1][ht2] = bm1.jaccard_similarity(bm2)
        ht_pair_sim[ht1] = sorted(ht_pair_sim[ht1].items(), key=operator.itemgetter(1), reverse=True)

    f = open(os.path.join(DATA, FINAL_GRAPH, filename), 'wt')
    line = ""
    for (ht1, all_pairs_sim) in ht_pair_sim.iteritems():
        line += ht1
        for pair in all_pairs_sim:
            line += "\t{}:{}".format(pair[0], pair[1])
        f.write("{}\n".format(line))
        line = ""

    f.close()


def bitmask_file_writer(ht_bitmasks, filename="hashtags_bitmasks.tsv"):
    f = open(os.path.join(DATA, FINAL_GRAPH, filename), 'wt')

    for (ht, bm) in ht_bitmasks.iteritems():
        f.write("{}\t{}\n".format(ht, str(bm)))

    f.close()


def name_to_index_dict_writer(name_to_index_dict, filename="name_to_index_graph_translation.tsv"):
    f = open(os.path.join(DATA, FINAL_GRAPH, filename), 'wt')

    for (id, name) in name_to_index_dict.iteritems():
        f.write("{}\t{}\n".format(name, id))

    f.close()


def final_graph_builder():
    hashtags_map = defaultdict(lambda: [])
    graphs_map = {}
    index = 0
    name_to_index_dict = {}
    ht_bitmasks = defaultdict(lambda: BitVector(intVal=0, size=NUM_TWEETS))

    if not os.path.exists(os.path.join(DATA, FINAL_GRAPH)):
        os.makedirs(os.path.join(DATA, FINAL_GRAPH))

    filenames = os.listdir(os.path.join(DATA, PEOPLE, SOURCE_LABEL))

    for filename in filenames:
        graph, hashtags = tweet_parser(filename=filename, hashtags_map=hashtags_map,
                                       hashtags_bitmask=ht_bitmasks, graph_id=index)
        graphs_map[filename] = (graph, hashtags)
        name_to_index_dict[index] = filename
        index += 1

    name_to_index_dict_writer(name_to_index_dict)

    jaccard_all_pairs_similarity_file_writer(ht_bitmasks)
    bitmask_file_writer(ht_bitmasks)
    # union_graph = join_graphs(graphs_map)

    # nodes_counters = defaultdict(lambda: defaultdict(lambda: 0))
    edges_counters = defaultdict(lambda: defaultdict(lambda: 0))
    hashtags_counters = defaultdict(lambda: 0)

    for h in hashtags_map.keys():
        hashtags_counters[h] = len(hashtags_map[h])
        for g in hashtags_map[h]:
            for (node, replies) in g.iteritems():
                # nodes_counters[node][h] += 1
                for reply in replies:
                    edges_counters["{}->{}".format(node, reply)][h] += 1

    final_graph = defaultdict(lambda: defaultdict(lambda: 0))

    for edge in edges_counters.keys():
        # informer = edge.split("->")[0]
        for edge_ht in edges_counters[edge].keys():
            # final_graph[edge][edge_ht] = float(edges_counters[edge][edge_ht])/float(nodes_counters[informer][edge_ht])
            final_graph[edge][edge_ht] = float(edges_counters[edge][edge_ht]) / float(hashtags_counters[edge_ht])

    graph_file_writer(final_graph)


if __name__ == "__main__":
    final_graph_builder()