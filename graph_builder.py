import os
import operator

from collections import defaultdict
from BitVector import BitVector

SOURCE_LABEL = "S"
NUM_TWEETS = 4


def tweet_parser(filename, path="data", hashtags_map=None, hashtags_bitmask=None, graph_id=None, debug=False):
    tweet_graph = dict()

    f = open(os.path.join(path, filename), 'r')

    hashtags = f.readline().strip("\n").split("\t")

    if debug:
        print "hashtags:", hashtags

    line = f.readline()
    while len(line) > 0:
        edge = line.strip("\n").split("\t")

        if debug:
            print "edge:", edge

        if edge[1] == 'S':
            line = f.readline()
            continue

        if edge[0] not in tweet_graph:
            tweet_graph[edge[0]] = set(edge[1])
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


def graph_file_writer(final_graph, filename="final_graph.tsv", path="data"):
    f = open(os.path.join(path, filename), 'wt')

    for edge in final_graph.keys():
        nodes = edge.split("->")
        f.write("{}\t{}\n".format(nodes[0], nodes[1]))
        prob = ""
        for ht in final_graph[edge].keys():
            if prob == "":
                prob += "{}:{}".format(ht, final_graph[edge][ht])
            else:
                prob += "\t{}:{}".format(ht, final_graph[edge][ht])
        prob += "\n"
        f.write(prob)

    f.close()


def jaccard_all_pairs_similarity_file_writer(ht_bitmasks, filename="jaccard_all_pairs_similarity.tsv", path="data"):
    ht_pair_sim = defaultdict(lambda: dict())
    for (ht1, bm1) in ht_bitmasks.iteritems():
        for (ht2, bm2) in ht_bitmasks.iteritems():
            if ht1 == ht2:
                continue
            ht_pair_sim[ht1][ht2] = bm1.jaccard_similarity(bm2)
        ht_pair_sim[ht1] = sorted(ht_pair_sim[ht1].items(), key=operator.itemgetter(1), reverse=True)

    f = open(os.path.join(path, filename), 'wt')
    line = ""
    for (ht1, all_pairs_sim) in ht_pair_sim.iteritems():
        line += ht1
        for pair in all_pairs_sim:
            line += "\t{}:{}".format(pair[0], pair[1])
        f.write("{}\n".format(line))
        line = ""

    f.close()


def bitmask_file_writer(ht_bitmasks, filename="hashtags_bitmasks.tsv", path="data"):
    f = open(os.path.join(path, filename), 'wt')

    for (ht, bm) in ht_bitmasks.iteritems():
        f.write("{}\t{}\n".format(ht, str(bm)))

    f.close()


if __name__ == "__main__":
    hashtags_map = defaultdict(lambda: [])
    graphs_map = {}
    ht_bitmasks = defaultdict(lambda: BitVector(intVal=0, size=NUM_TWEETS))

    for i in range(NUM_TWEETS):
        graph, hashtags = tweet_parser(filename="tweet{}.txt".format(i), hashtags_map=hashtags_map,
                                       hashtags_bitmask=ht_bitmasks, graph_id=i)
        graphs_map[i] = (graph, hashtags)

    jaccard_all_pairs_similarity_file_writer(ht_bitmasks)
    bitmask_file_writer(ht_bitmasks)
    # union_graph = join_graphs(graphs_map)

    nodes_counters = defaultdict(lambda: defaultdict(lambda: 0))
    edges_counters = defaultdict(lambda: defaultdict(lambda: 0))

    for h in hashtags_map.keys():
        for g in hashtags_map[h]:
            for (node, replies) in g.iteritems():
                nodes_counters[node][h] += 1
                for reply in replies:
                    edges_counters["{}->{}".format(node, reply)][h] += 1

    final_graph = defaultdict(lambda: defaultdict(lambda: 0))

    for edge in edges_counters.keys():
        informer = edge.split("->")[0]
        for edge_ht in edges_counters[edge].keys():
            final_graph[edge][edge_ht] = float(edges_counters[edge][edge_ht])/float(nodes_counters[informer][edge_ht])

    graph_file_writer(final_graph)
