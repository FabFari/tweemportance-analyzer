import os
from collections import defaultdict
from collections import deque

SOURCE_LABEL = "S"


def tweet_parser(filename, path="data", hashtags_map=None, debug=False):
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

        if edge[0] not in tweet_graph:
            tweet_graph[edge[0]] = [edge[1]]
        else:
            tweet_graph[edge[0]].append(edge[1])

        if edge[1] not in tweet_graph:
            tweet_graph[edge[1]] = []

        line = f.readline()

    if hashtags_map is not None:
        for h in hashtags:
            hashtags_map[h].append(tweet_graph)

    if debug:
        queue = deque(tweet_graph[SOURCE_LABEL])
        # queue = tweet_graph[SOURCE_LABEL]
        print SOURCE_LABEL
        while len(queue) > 0:
            node = queue.popleft()
            print node
            queue.extend(tweet_graph[node])

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

if __name__ == "__main__":
    hashtags_map = defaultdict(lambda: [])
    graphs_map = {}

    for i in range(4, 7):
        graph, hashtags = tweet_parser(filename="tweet{}.txt".format(i), hashtags_map=hashtags_map)
        graphs_map[i] = (graph, hashtags)

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
