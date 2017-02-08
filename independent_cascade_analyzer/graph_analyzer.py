import csv
import heapq
import random
import itertools
from collections import deque
from igraph import *
from translate.lang.ja import ja
from utils.graph_jaccard_similarity import graph_jaccard_similarity
from utils.vector_utils import compare_positivity

# File Names
GRAPH_FILE = "test_weight_1.tsv"
TRANSLATION_FILE = "ID_translation.tsv"

# Edges attributes
WEIGHT = "weight"
INC = "increase"
MAIN = "main"
# TODO
# Collection of all the hashtags
HASHTAGS = ["acqua", "sale"]

# Vertices attributes
ACTIVE = "active"
EXPECTED_VALUE = "e_v"
COST = "cost"

# Others
# Factor used to weight the jaccard similarity of hashtags
BALANCE_FACTOR = 1
# Max possible weight
MAX_WEIGHT = 100000
# Hashtags file
HASHTAGS_FILE = "hashtags_bitmasks.tsv"


# Load the graph in main memory
def load_graph(graph_in, translation_out=TRANSLATION_FILE):
    print "Loading  graph.."
    g = Graph(directed=True)
    # Open the graph file, and a  new file:
    # the new file will contain a mapping between the tweeter accounts and the nodes' IDs in the graph.
    with open(graph_in, 'rb') as tsvin, open(translation_out, 'wb') as tsvout:
        tsvin = csv.reader(tsvin, delimiter='\t')
        tsvout = csv.writer(tsvout, delimiter='\t')

        translator = {}
        current_id = 0
        current_edge = 0

        for row in tsvin:
            # Check if each of the twitter accounts of the current edge
            # have already a corresponding vertex in the graph.
            for i in range(0, 2):
                twitter_id = row[i]
                # If not create a new vertex and update the mapping
                if translator.has_key(twitter_id) is False:
                    translator[twitter_id] = current_id
                    tsvout.writerow([twitter_id, translator[twitter_id]])

                    g.add_vertex()
                    g.vs[current_id][ACTIVE] = False
                    g.vs[current_id][EXPECTED_VALUE] = 0.0
                    g.vs[current_id][COST] = 0.0

                    current_id += 1

            # Add the edge to the graph
            g.add_edge(translator.get(row[0]), translator.get(row[1]))

            # Add the edge attributes
            lenght = len(row)
            for i in range(2, lenght, 2):
                g.es[current_edge][row[i]] = float(row[i + 1])

            g.es[current_edge][WEIGHT] = 0.0
            g.es[current_edge][INC] = 0.0
            g.es[current_edge][MAIN] = False

            current_edge += 1

    print "Graph loaded."
    return g


# TOTEST
# TODO
# Computes the homogeneity of the group of hashtags
def homogeneity(hashtags):
    if len(hashtags) <= 1:
        return 1
    return 1
    # return 1 - (1 -graph_jaccard_similarity(hashtags))*BALANCE_FACTOR


# Simulate the independent cascade process
def independent_cascade_process(g, source, hashtags, result, debug=True):
    balance_coeff = homogeneity(hashtags)

    # Stack containing the nodes activated in the previous iteration
    # First iteration has only the source node
    it_cur = []
    g.vs[source][ACTIVE] = True
    it_cur.append(source)

    result.append(source)

    # Stack containing the nodes activated in the current iteration
    it_cur_n = []

    iteration = 1

    # Each new iteration of this cycle is a new iteration of the process
    while len(it_cur) > 0:

        if debug:
            print "------------------------------------------------------"
            print "Iteration: ", iteration

        # Simulate the process for each newly active node
        while len(it_cur) > 0:
            v = it_cur.pop()
            if debug:
                print "     Considering current active node: ", v

            edges = g.incident(v)
            for e in edges:

                # We consider only the hastag parameter that maximizes the probability,
                # this probability will then adjusted according to the jaccard similarity of the hashtags.
                # The Jaccard similarity is an indicator of how close the hashtags are.
                max = hashtags[0]

                for h in hashtags[1:]:
                    if g.es[e][h] > g.es[e][max]:
                        max = h

                pr = g.es[e][max] * balance_coeff
                if debug:
                    print "     Probability of activation on the considered edge: ", pr

                # Random number to simulate the biased coin flip
                r = random.random()

                if debug:
                    print "     Value obtained: ", r

                # If the result is head, activated the node
                if r <= pr:
                    u = g.es[e].target
                    # If the node was already active, do nothing
                    if g.vs[u][ACTIVE] is False:
                        if debug:
                            print  "            Node ", u, " activated."
                        g.vs[u][ACTIVE] = True
                        it_cur_n.append(u)
                        result.append(u)

        # Move to the next  iteration
        it_cur = it_cur_n
        it_cur_n = []
        iteration += 1
    if debug:
        print "------------------------------------------------------"
        print "Done."


# Estimate the expected outcome of an independent cascade run
def estimate_expected_outcome(g, source, hashtags, runs, expected_outcome):
    # This is the increment each node can get from a single run,
    # At the end, the number of increments received will be an estimation of the
    # probability of the node being activated.
    # Hence we will have an estimation of the expected outcome of the process.
    # This value can be used also to average the number of nodes activated in the different runs of the process
    inc = 1.0 / runs

    avg_acts = 0

    # Repeate the process "runs" times
    for i in range(runs):
        activations = 0
        result = []
        independent_cascade_process(g, source, hashtags, result)
        for i in result:
            activations += 1
            g.vs[i][EXPECTED_VALUE] += inc

        avg_acts += activations * inc

        deactivate(g)

    # Collect results
    for v in g.vs:
        expected_outcome.append(v[EXPECTED_VALUE])

    # Clean up
    reset_graph(g)

    return avg_acts

# TOTEST
# TODO
# Retrieve the most suitable hashtags, given as input  the set of hashtags currently adopted
def get_close_hahstags(hashtags_in, hashtags_out):
    hashtags_out.append("sale")


# TOTEST
# Maximize the expected outcome of an independent cascade run
def maximize_expected_outcome(g, source, hashtags, runs, current_outcome, outcomes, debug=True):
    if debug:
        print "Maximizing expected outcome.."

    if debug:
        print "     Retrieving most suitable hashtags.."
    suggested_hashtags = []
    get_close_hahstags(hashtags, suggested_hashtags)
    if debug:
        print "     Done."

    if debug:
        print  "     Starting simulations.."

    for h in suggested_hashtags:
        current_hashtags = []
        current_hashtags.extend(hashtags)
        current_hashtags.append(h)

        outcome = []
        n = estimate_expected_outcome(g, source, current_hashtags, runs, outcome)
        positivity = compare_positivity(outcome, current_outcome)
        if positivity >= 0:
            tup = (n, positivity)
            outcomes[h] = tup

    if debug:
        print "     Done."

    if debug:
        print "Done"


# TOTEST
# Retrieve the top-k hashtags according to the the vertex interests
def most_interested_in_hashtags(g, id, k, result, hashtags=None):

    w_heap = []

    dict = {}

    # Assume id already translated
    edges = g.incident(id)

    for h in HASHTAGS:
        cur_hashtags = []
        cur_hashtags.extend(hashtags)
        cur_hashtags.append(h)
        homogeneity = homogeneity(cur_hashtags)
        for e in edges:
            edge = g.es[e]
            if edge.hasKey(h):
                weight = 1 / (edge[h] * homogeneity())
                if  dict.has_key(h):
                    dict[h] += weight
                else:
                    dict[h] = weight

    for key in dict.keys():
        tup = (dict[key],key)
        w_heap.append(tup)

    heapq.heapify(w_heap)

    l = k
    if len(w_heap) < k:
        l = len(w_heap)

    for i in range(0,l):
        tup = heapq.heappop(w_heap)
        result.append(tup[1])



# Weight edges according to the input hashtag
def weight_edges(g, field, homogeneity=1):
    for edge in g.es:
        weight = MAX_WEIGHT
        if edge.attributes().has_key(field):
            den = (edge[field]*homogeneity)
            if den > 0:
                weight = 1 / den

        edge[WEIGHT] = weight

    # Stub method
    """g.es[0][WEIGHT] = 1
    g.es[1][WEIGHT] = 3
    g.es[2][WEIGHT] = 1
    g.es[3][WEIGHT] = 6
    g.es[4][WEIGHT] = 1
    g.es[5][WEIGHT] = 1
    g.es[6][WEIGHT] = 2
    g.es[7][WEIGHT] = 1"""

# Check whether the suggested side track edges can be inserted into a shortest path
def is_path(g,source, target, path, debug=True):
    d_path = {}
    count = 0

    if debug:
        print "[is_path] Path: ", path
    for t in path:
        key = int(t[1])
        d_path[key] = int(t[2])

    if debug:
        print "[is_path] Edges: ", d_path
    cur = source
    while cur != target:
        if debug:
            print "[is_path] Current node:", cur
        if d_path.has_key(cur):
            if debug:
                print "[is_path] Taking side edge from: ", cur
            old = cur
            cur = d_path[cur]
            del d_path[old]
            count += 1
            continue

        edges = g.incident(cur)
        for e in edges:
            edge = g.es[e]
            if edge[MAIN] is True:
                cur = edge.target

    return count == len(path)

# Remove the edges incident to the target node and return them in a list
def remove_incidents(g, target, debug=True):
    if debug:
        print "Temporary removing useless edges.."

    removed = {}
    out_edges = g.incident(target)
    for id in out_edges:
        edge = g.es[id]
        key = edge.target
        # Dictionary to keep the  attributes
        dict = {}
        dict[MAIN] = edge[MAIN]
        dict[WEIGHT] = edge[WEIGHT]
        dict[INC] = edge[INC]
        for h in HASHTAGS:
            dict[h] = edge[h]

        # Save the dictionary
        removed[key] = dict

    g.delete_edges(out_edges)

    if debug:
        print "Done."
        print
        print "Edges removed: ", removed

    return removed

# Add edges in the list to the target node
def add_edges(g, target, edges, debug=True):
    if debug:
        print "Reinserting removed edges.."

    for k in edges.keys():
        g.add_edge(target, k)

    edges = g.incident(target)
    for id in edges:
        edge = g.es[id]
        key = edge.target
        dict = edges[key]
        for k in dict.keys():
            edge[k] = dict[k]

    if debug:
        print "Done."

# Compute the shortest paths from every node to target
def compute_shortest_paths(g, target, weights=WEIGHT, mode=IN, debug=True):
    if debug:
        print "Computing inverse shortest paths.. "
    shortest_paths = g.get_shortest_paths(target, weights=weights, mode=mode, output="epath")
    for p in shortest_paths:
        for e in p:
            g.es[e][MAIN] = True
    if debug:
        print "Done."

# Reconstruct cost of shortes paths to target
def reconstruct_paths_cost(g,target, debug=True):
    if debug:
        print "[reconstruct_paths_cost] Reconstructing paths costs.."

    v_queue = deque()
    v_queue.append(target)
    g.vs[target][ACTIVE] = True
    while len(v_queue) > 0:
        v = v_queue.popleft()
        # Reuse ACTIVE field as VISITED flag
        edges = g.incident(v)
        for e in edges:
            if g.es[e][MAIN] is True:
                u = g.es[e].target
                if debug:
                    print "[reconstruct_paths_cost]     Edge: ", g.es[e].source, " ", g.es[e].target, \
                        " is in some shortest path with cost", g.es[e][WEIGHT]
                g.vs[v][COST] = g.es[e][WEIGHT] + g.vs[u][COST]
                break

        edges = g.incident(v, mode=IN)
        if debug:
            print "[reconstruct_paths_cost]     Considering  outer neighbors of ", v
        for e in edges:
            if g.es[e][MAIN] is True:
                u = g.es[e].source
                if debug:
                    print "         Considering node ", u
                if g.vs[u][ACTIVE] is False:
                    if debug:
                        print "         Node ", u, " is now active."
                    g.vs[u][ACTIVE] = True
                    v_queue.append(u)
        if debug:
            print

    for v in g.vs:
        if v[ACTIVE] is False:
            v[ACTIVE] is True
            v[COST] = MAX_WEIGHT

    if debug:
        print "[reconstruct_paths_cost] Done."

# TOTEST
def compute_top_k_sidetrack_edges(g, k, debug = True):
    sidetrack_edges = []

    count = 0
    max = 0

    if debug:
        print "[compute_sidetrack_edges_increment] Computing increment in cost of sidetrack edges.."

    costs = []
    heapq.heapify(costs)

    # Can be improved
    for edge in g.es:
        if edge[MAIN] is False:
            count += 1
            edge[INC] = edge[WEIGHT] + g.vs[edge.target][COST] - g.vs[edge.source][COST]
            if debug:
                print "[compute_sidetrack_edges_increment]      Edge: ", edge.source, " "\
                        , edge.target, " Side_track_cost: ", edge[INC]
            if count <= k - 1:
                heapq.heappush(costs,edge[INC])
                tup = (edge[INC], edge.source, edge.target)
                sidetrack_edges.append(tup)
            if count > k - 1:
                max = heapq.heappop(costs)
                cur = 1/edge[INC]
                if cur < max:
                    tup = (edge[INC], edge.source, edge.target)
                    sidetrack_edges.append(tup)
                    heapq.heappush(costs, cur)
                elif cur == max:
                    tup = (edge[INC], edge.source, edge.target)
                    sidetrack_edges.append(tup)
                    heapq.heappush(costs, max)
                else:
                    heapq.heappush(costs, max)
    if debug:
        print "[compute_sidetrack_edges_increment] Done."

    heapq.heapify(sidetrack_edges)
    ordered_s_e = []
    for i in range(1,k):
        ordered_s_e.append(heapq.heappop(sidetrack_edges))

    return ordered_s_e

# TOTEST
def get_k_shortest_paths(g, source, target, result, k=5, debug=True):
    # Need first to remove outgoing edges from target, edges will be restored at the end of the computation
    removed = remove_incidents(g, target)

    if debug:
        print "Computing ", k, "-least cost paths.."
        print "Source: ", source
        print "Target: ", target

    compute_shortest_paths(g, target, debug=debug)

    reconstruct_paths_cost(g,target)

    # Cost of the optimal path
    OPT = g.vs[source][COST]

    if debug:
        print "Computing side edges increment in cost.."

    ordered_s_e = compute_top_k_sidetrack_edges(g,k-1)

    if debug:
        print "Candidate shortest paths side edges: ", ordered_s_e
    # The least cost path is already known
    paths_found = 1
    candidate_paths = []
    s = ()
    tup = (OPT, s)
    paths = []
    heapq.heapify(paths)
    heapq.heappush(paths, tup)

    if len(ordered_s_e) == 0:
        return paths

    # Surely any of the k-top paths cannot cost more than this value
    t  = ordered_s_e.pop()
    upper_bound = t[0]
    ordered_s_e.append(t)

    for l in range(1, k - 1):
        for tup in itertools.combinations(ordered_s_e, l):
            candidate_paths.append(tup)
            if debug:
                print "Tuple: ", tup

    # Can be improved
    for p in candidate_paths:
        cost = 0
        for t in p:
            cost += t[0]

        # Check if path might be in the k-least cost paths
        if cost <= upper_bound:
            if is_path(source, target, p):
                tup = (cost + OPT, p)
                heapq.heappush(paths, tup)

    if debug:
        for p in paths:
            print p

    total = 0
    for i in range(0, k):
        tup = heapq.heappop(paths)
        total += tup[0]
        result.append(tup)

    heapq.heapify(result)

    add_edges(g,target,removed)

    return total

# TOTEST
# TARGET MAXIMIZATION HEURISTIC
def maximize_target_outcome(g, source, target, tweet_hashtags, current_outcome, outcomes, k=1):
    pref_hashtags = []
    most_interested_in_hashtags(g, target, k, pref_hashtags)
    for i in range(0, k):
        h = heapq.heappop(pref_hashtags)
        if h is None:
            break

        cur_hashtags = []
        cur_hashtags.extend(tweet_hashtags)
        cur_hashtags.append(h)

        homogeneity = homogeneity(cur_hashtags)

        weight_edges(g, h, homogeneity)
        result = []
        tot = get_k_shortest_paths(g, source, target, result, weight=h)
        outcomes.append(tot, result)

    heapq.heapify(outcomes)


# UTILS

# Deactivate nodes
def deactivate(g):
    # Deactivate all nodes
    for v in g.vs:
        v[ACTIVE] = False


# Reset edge weights
def reset_weights(g):
    for e in g.es:
        e[WEIGHT] = 0.0


# Reset the graph to default settings
def reset_graph(g):
    print "Resetting graph.."
    # Reset nodes to their default settings
    for v in g.vs:
        v[ACTIVE] = False
        v[EXPECTED_VALUE] = 0.0
        print v

    # Reset edges to their default settings
    for e in g.es:
        e[WEIGHT] = 0.0
        e[MAIN] = False
        e[INC] = 0.0
        print e

    print "Done."


if __name__ == "__main__":
    #
    g = load_graph(GRAPH_FILE, TRANSLATION_FILE)
    # r = g.get_shortest_paths(0,4)
    # print r
    # print g
    weight_edges(g, "sale")
    get_k_shortest_paths(g, 0, 4, [],1)

    # result = []
    # estimate_expected_outcome(g,0,["acqua"],50,result)
    # print result
    # most_interested_hashtags(g,0,0)