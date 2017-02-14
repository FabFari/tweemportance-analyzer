import csv
import heapq
import random
import itertools
from collections import deque
from igraph import *
from translate.lang.ja import ja
from utils.graph_jaccard_similarity import graph_jaccard_similarity, bitmask_file_parser, \
    jaccard_all_pairs_similarity_file_parser, jaccard_top_k_similar_hashtags
from utils.vector_utils import difference

# File Names
GRAPH_FILE = "final_graph.tsv"
TRANSLATION_FILE = "ID_translation.tsv"
DATA = "data"
GRAPH_DIR = "graph"

# Edges attributes
WEIGHT = "weight"
INC = "increase"
MAIN = "main"

# Hashtags variables
hashtags_bitmask = None
hashtags = ["#A"]#= None
hashtags_all_pairs_similarity = None

# Translations map
translations_map = {}

# Vertices attributes
ACTIVE = "active"
EXPECTED_VALUE = "e_v"
COST = "cost"

# Others
# Factor used to weight the jaccard similarity of hashtags
BALANCE_FACTOR = 0.5
# Max possible weight
MAX_WEIGHT = 100000


# Setup method to prepare the data, there is no need to call the methods individually
def setup():
    global hashtags_bitmask, hashtags, hashtags_all_pairs_similarity
    hashtags_bitmask = bitmask_file_parser()
    hashtags = hashtags_bitmask.keys()
    hashtags_all_pairs_similarity = jaccard_all_pairs_similarity_file_parser()
    path = os.path.join(os.pardir, DATA, GRAPH_DIR)
    g = load_graph(os.path.join(path, GRAPH_FILE), os.path.join(path, TRANSLATION_FILE))
    set_up_edges_empty_attributes(g)
    return g


# Set to 0.0 attributes with None values
def set_up_edges_empty_attributes(graph):
    for e in graph.es:
        for h in hashtags:
            if e[h] is None:
                e[h] = 0.0


# Load the graph in main memory
def load_graph(graph_in, translation_out=TRANSLATION_FILE, verbose=False):
    global translations_map
    if verbose:
        print "[load_graph]   Loading  graph.."

    g = Graph(directed=True)
    # Open the graph file, and a  new file:
    # the new file will contain a mapping between the tweeter accounts and the nodes' IDs in the graph.
    with open(graph_in, 'rb') as tsvin, open(translation_out, 'wb') as tsvout:
        tsvin = csv.reader(tsvin, delimiter='\t')
        tsvout = csv.writer(tsvout, delimiter='\t')

        current_id = 0
        current_edge = 0

        for row in tsvin:
            # Check if each of the twitter accounts of the current edge
            # have already a corresponding vertex in the graph.
            for i in range(0, 2):
                twitter_id = row[i]
                # If not create a new vertex and update the mapping
                if translations_map.has_key(twitter_id) is False:
                    translations_map[twitter_id] = current_id
                    tsvout.writerow([twitter_id, translations_map[twitter_id]])

                    g.add_vertex()
                    g.vs[current_id][ACTIVE] = False
                    g.vs[current_id][EXPECTED_VALUE] = 0.0
                    g.vs[current_id][COST] = 0.0

                    current_id += 1

            # Add the edge to the graph
            g.add_edge(translations_map.get(row[0]), translations_map.get(row[1]))

            # Add the edge attributes
            lenght = len(row)
            for i in range(2, lenght, 2):
                g.es[current_edge][row[i]] = float(row[i + 1])

            g.es[current_edge][WEIGHT] = 0.0
            g.es[current_edge][INC] = 0.0
            g.es[current_edge][MAIN] = False

            current_edge += 1
    if verbose:
        print "[load_graph]   Graph loaded."
    return g


# Get node id from screen_name
def translate(screen_name):
    return translations_map[screen_name]


# Computes the homogeneity of the group of hashtags
def homogeneity(hashtags_list, verbose=False):
    if verbose:
        print "[homogeneity]   Checking homogeneity."
    if len(hashtags) <= 1:
        return 1
    # return 1
    ht_dict = {}
    for h in hashtags_list:
        ht_dict[h] = hashtags_bitmask[h]

    return 1 - (1 - graph_jaccard_similarity(ht_dict)) * BALANCE_FACTOR


# Simulate the independent cascade process
def independent_cascade_process(g, source, tweet_hashtags, verbose=False):
    result = []
    balance_coeff = homogeneity(tweet_hashtags)

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

        if verbose:
            print "[independent_cascade_process]   ------------------------------------------------------"
            print "[independent_cascade_process]   Iteration: ", iteration

        # Simulate the process for each newly active node
        while len(it_cur) > 0:
            v = it_cur.pop()
            if verbose:
                print "[independent_cascade_process]     Considering current active node: ", v

            edges = g.incident(v)
            for e in edges:

                # We consider only the hastag parameter that maximizes the probability,
                # this probability will then adjusted according to the jaccard similarity of the hashtags.
                # The Jaccard similarity is an indicator of how close the hashtags are.
                max = tweet_hashtags[0]

                for h in tweet_hashtags[1:]:
                    if g.es[e][h] > g.es[e][max]:
                        max = h

                pr = g.es[e][max] * balance_coeff
                if verbose:
                    print "[independent_cascade_process]     Probability of activation on the considered edge: ", pr

                # Random number to simulate the biased coin flip
                r = random.random()

                if verbose:
                    print "[independent_cascade_process]     Value obtained: ", r

                # If the result is head, activated the node
                if r <= pr:
                    u = g.es[e].target
                    # If the node was already active, do nothing
                    if g.vs[u][ACTIVE] is False:
                        if verbose:
                            print  "[independent_cascade_process]     Node ", u, " activated."
                        g.vs[u][ACTIVE] = True
                        it_cur_n.append(u)
                        result.append(u)

        # Move to the next  iteration
        it_cur = it_cur_n
        it_cur_n = []
        iteration += 1
    if verbose:
        print "[independent_cascade_process]   ------------------------------------------------------"
        print "[independent_cascade_process]   Done."
    return result


# Estimate the expected outcome of an independent cascade run
def estimate_expected_outcome(g, source, hashtags, runs, expected_outcome, verbose=False):
    # This is the increment each node can get from a single run,
    # At the end, the number of increments received will be an estimation of the
    # probability of the node being activated.
    # Hence we will have an estimation of the expected outcome of the process.
    # This value can be used also to average the number of nodes activated in the different runs of the process
    inc = 1.0 / runs

    avg_number_activated = 0

    if verbose:
        print "[estimate_expected_outcome]   Computing Independent Cascade Process expected outcome.."

    # Repeate the process "runs" times
    for i in range(runs):
        if verbose:
            print "[estimate_expected_outcome]   Starting run ", i
        activations = 0
        result = independent_cascade_process(g, source, hashtags)
        for i in result:
            activations += 1
            g.vs[i][EXPECTED_VALUE] += inc

        avg_number_activated += activations * inc

        deactivate(g)
        if verbose:
            print "[estimate_expected_outcome]   Run ", i, " completed."

    # Collect results
    for v in g.vs:
        expected_outcome.append(v[EXPECTED_VALUE])

    # Clean up
    reset_graph(g)

    if verbose:
        print "[estimate_expected_outcome]   Done."

    return avg_number_activated


# Retrieve the most suitable hashtags, given as input  the set of hashtags currently adopted
def get_close_hahstags(hashtags_in, k=5):
    ranking = jaccard_top_k_similar_hashtags(hashtags_all_pairs_similarity, hashtags_in, k)
    result = [tup[1] for tup in ranking]
    return result


# Maximize the expected outcome of an independent cascade run
def maximize_expected_outcome(g, source, current_hashtags, runs, current_outcome, verbose=False):
    outcomes = {}
    if verbose:
        print "[maximize_expected_outcome]   Maximizing expected outcome.."

    if verbose:
        print "[maximize_expected_outcome]   Retrieving most suitable hashtags.."
    suggested_hashtags = get_close_hahstags(current_hashtags)
    if verbose:
        print "[maximize_expected_outcome]   Hashtags retrieved."

    if verbose:
        print  "[maximize_expected_outcome]   Starting simulations.."

    for h in suggested_hashtags:
        current_hashtags = []
        current_hashtags.extend(current_hashtags)
        current_hashtags.append(h)

        outcome = []
        n = estimate_expected_outcome(g, source, current_hashtags, runs, outcome)
        positivity = difference(outcome, current_outcome)
        if verbose:
            print "[maximize_expected_outcome]   Hashtag: ", h, " positivity: ", positivity
        if positivity >= 0:
            tup = (n, positivity)
            outcomes[h] = tup

    if verbose:
        print "[maximize_expected_outcome]   Done."

    return outcomes


# Retrieve the top-k hashtags according to the the vertex interests
def most_interested_in_hashtags(g, id, k=3, tweet_hashtags=None, verbose=False):
    result = []
    weighted_heap = []

    hashtags_weight = {}
    edges = g.incident(id, mode=IN)
    if verbose:
        print "[most_interested_in_hashtags]   Retrieve top k hashtags according to vertex interests.."
    for h in hashtags:
        if verbose:
            print "[most_interested_in_hashtags]   Trying hashtag: ", h
        cur_hashtags = []
        if tweet_hashtags is not None:
            cur_hashtags.extend(tweet_hashtags)
        cur_hashtags.append(h)
        hmg = homogeneity(cur_hashtags)
        if verbose:
            print "[most_interested_in_hashtags]   Homogeneity of current hashtag set: ", hmg
        for e in edges:
            edge = g.es[e]
            if edge[h] > 0:
                weight = 1 / (edge[h] * hmg)
            else:
                weight = MAX_WEIGHT
            if verbose:
                print "[most_interested_in_hashtags]   Edge probability on hashtag", h, ": ", edge[h]
                print "[most_interested_in_hashtags]   Weight: ", weight
            if h in hashtags_weight:
                hashtags_weight[h] += weight
            else:
                hashtags_weight[h] = weight
            if verbose:
                print "[most_interested_in_hashtags]   Updated hashtag weight: ", hashtags_weight[h]

    for e in hashtags_weight.keys():
        tup = (hashtags_weight[e], e)
        weighted_heap.append(tup)

    heapq.heapify(weighted_heap)

    l = min(len(weighted_heap), k)
    for i in range(0, l):
        tup = heapq.heappop(weighted_heap)
        result.append(tup[1])

    if verbose:
        print "[most_interested_in_hashtags]   Done."

    return result


# Weight edges according to the input hashtag
def weight_edges(g, field, homogeneity=1, verbose=False):
    if verbose:
        print "[weight_edges]   Weighting edges.."
    for edge in g.es:
        weight = MAX_WEIGHT
        if field in edge.attributes():
            den = (edge[field] * homogeneity)
            if den > 0:
                weight = 1 / den

        edge[WEIGHT] = weight
        if verbose:
            print "[weight_edges]   Edge:", edge.source, " ", edge.target, "  weights ", edge[WEIGHT]
    if verbose:
        print "[weight_edges]   Done."

# Check whether the suggested side track edges can be inserted into a shortest path with no loops
def is_straight_path(g, source, target, path, verbose=True):
    deactivate(g, verbose=verbose)
    d_path = {}
    count = 0

    if verbose:
        print "[is_path]   Checking if path: ", path, " is  indeed a path.."
    for t in path:
        key = int(t[1])
        d_path[key] = int(t[2])

    if len(path) == 0:
        if verbose:
            print "[is_path]   Done."
        return False

    '''if len(path) == 1:
        if verbose:
            print "[is_path]   Done."
        if path[0][1] == target:
            if verbose:
                print "[is_path] Result:", False
            return False
        n = path[0][1]
        edges = g.incident(n)
        for e in edges:
            if g.es[e][MAIN] == True:
                if verbose:
                    print "[is_path] Result:", True
                return True
        if verbose:
            print "[is_path] Result:", False
        return False'''



    if verbose:
        print "[is_path]   Edges: ", d_path
    cur = source
    while cur != target:

        v = g.vs[cur]
        if v[ACTIVE] is True:
            return False
        v[ACTIVE] = True

        if verbose:
            print "[is_path]   Current node:", cur
        if d_path.has_key(cur):
            if verbose:
                print "[is_path]   Taking side edge from: ", cur
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

    if verbose:
        print "[is_path]   Done."
        print "[is_path]   Result: ", count == len(path)
    return count == len(path)

# Check whether the current node belongs to the inverse Shortest Paths Tree
def is_valid_edge(g, node, verbose=False):
    if verbose:
        print "[is_valid_edge]   Checking if node:", node, " belongs to the Shortest Paths Tree.."
    edges = g.incident(g.vs[node])
    for e in edges:
        if g.es[e][MAIN] is True:
            if verbose:
                print "[is_valid_edge]   Done."
                print "[is_valid_edge]   Result:",True
            return True
    if verbose:
        print "[is_valid_edge]   Done."
        print "[is_valid_edge]   Result:", False
    return False

# Remove the edges incident to the target node and return them in a list
def remove_incidents(g, target, verbose=True):
    if verbose:
        print "[remove_incidents]   Temporary removing useless edges.."

    removed = {}
    out_edges = g.incident(target)
    if verbose:
        print "[remove_incidents]   Removing edges: "
    for id in out_edges:
        edge = g.es[id]
        key = edge.target
        # Dictionary to keep the  attributes
        dict = {}
        dict[MAIN] = edge[MAIN]
        dict[WEIGHT] = edge[WEIGHT]
        dict[INC] = edge[INC]
        for h in hashtags:
            dict[h] = edge[h]

        # Save the dictionary
        removed[key] = dict
        if verbose:
            print "[remove_incidents]   Edge: ", edge.source, " ", edge.target

    g.delete_edges(out_edges)

    if verbose:
        print "[remove_incidents]   Done."

    return removed


# Add edges in the list to the target node
def add_edges(g, target, edges_list, verbose=True):
    if verbose:
        print "[add_edges]   Inserting edges:"

    for k in edges_list.keys():
        g.add_edge(target, k)
        if verbose:
            print "[add_edges]   Inserted edge:", target, " ", k

    if verbose:
        print "[add_edges]   Done. Loading now attibutes.."

    edges = g.incident(target)
    for e in edges:
        edge = g.es[e]
        if verbose:
            print "[add_edges]   Loading attributes on edge: ", edge.source, " ", edge.target
        key = edge.target
        dict = edges_list[key]
        for k in dict.keys():
            edge[k] = dict[k]

    if verbose:
        print "[add_edges]   Done."


# Compute the shortest paths from every node to target
def compute_shortest_paths(g, target, weights=WEIGHT, mode=IN, verbose=True):
    if verbose:
        print "[compute_shortest_paths]   Computing inverse shortest paths.. "
    shortest_paths = g.get_shortest_paths(target, weights=weights, mode=mode, output="epath")
    for p in shortest_paths:
        for e in p:
            g.es[e][MAIN] = True
    if verbose:
        print "[compute_shortest_paths]   Done."


# Reconstruct cost of shortest paths to target
def reconstruct_paths_cost(g, target, verbose=True):
    if verbose:
        print "[reconstruct_paths_cost]   Reconstructing paths costs.."

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
                if verbose:
                    print "[reconstruct_paths_cost]   Edge: ", g.es[e].source, " ", g.es[e].target, \
                        " is in some shortest path with cost", g.es[e][WEIGHT]
                g.vs[v][COST] = g.es[e][WEIGHT] + g.vs[u][COST]
                break

        edges = g.incident(v, mode=IN)
        if verbose:
            print "[reconstruct_paths_cost]   Considering  outer neighbors of ", v
        for e in edges:
            if g.es[e][MAIN] is True:
                u = g.es[e].source
                if verbose:
                    print "[reconstruct_paths_cost]   Considering node ", u
                if g.vs[u][ACTIVE] is False:
                    if verbose:
                        print "[reconstruct_paths_cost]   Node ", u, " is now active."
                    g.vs[u][ACTIVE] = True
                    v_queue.append(u)

    for v in g.vs:
        if v[ACTIVE] is False:
            v[ACTIVE] is True
            v[COST] = MAX_WEIGHT

    if verbose:
        print "[reconstruct_paths_cost]   Done."


# Compute the increment in cost of the possible paths when taking sidetrack edges
def compute_sidetrack_edges_increment(g, verbose=True):
    sidetrack_edges = []

    # count = 0

    if verbose:
        print "[compute_sidetrack_edges_increment]   Computing increment in cost of sidetrack edges.."

    # costs = []
    # heapq.heapify(costs)

    # Can be improved
    for edge in g.es:
        if edge[MAIN] is False:
            # count += 1
            target = g.vs[edge.target]
            if target[COST] >= MAX_WEIGHT:
                continue
            else:
                edge[INC] = edge[WEIGHT] + g.vs[edge.target][COST] - g.vs[edge.source][COST]
                tup = (edge[INC], edge.source, edge.target)
                sidetrack_edges.append(tup)
                if verbose:
                    print "[compute_sidetrack_edges_increment]   Edge: ", edge.source, " " \
                        , edge.target, \
                        " Side_track_cost= edge[WEIGHT] + g.vs[edge.target][COST] - g.vs[edge.source][COST] =", \
                        edge[WEIGHT], "+", g.vs[edge.target][COST], "-", g.vs[edge.source][COST], "=", \
                        edge[INC]
    if verbose:
        print "[compute_sidetrack_edges_increment]   Ordering sidetrack edges.."

    heapq.heapify(sidetrack_edges)

    if verbose:
        print "[compute_sidetrack_edges_increment]   Done."

    # return ordered_s_e
    return sidetrack_edges


# Compute k least cost simple paths from source to target
def get_k_shortest_paths(g, source, target, result, k=5, verbose=True):
    # Need first to remove outgoing edges from target, edges will be restored at the end of the computation
    removed = remove_incidents(g, target, verbose=verbose)

    if verbose:
        print "[get_k_shortest_paths]   Computing ", k, "-least cost paths.."
        print "[get_k_shortest_paths]   Source: ", source
        print "[get_k_shortest_paths]   Target: ", target

    compute_shortest_paths(g, target, verbose=verbose)

    reconstruct_paths_cost(g, target, verbose=verbose)

    deactivate(g, verbose=False)

    # Cost of the optimal path
    OPT = g.vs[source][COST]

    if verbose:
        print "[get_k_shortest_paths]   Computing side edges increment in cost.."

    sidetrack_edges = compute_sidetrack_edges_increment(g, verbose=verbose)

    if verbose:
        print "[get_k_shortest_paths]   Done."
        print "[get_k_shortest_paths]   Computing candidate shortest paths side edges.. "

    ordered_s_e = []
    # The least cost path is already known
    candidates_found = 1
    while len(sidetrack_edges) > 0 & candidates_found < k:
        p = []
        tup = heapq.heappop(sidetrack_edges)
        p.append(tup)
        if is_valid_edge(g, tup[1], verbose=verbose):
            ordered_s_e.append(tup)
            candidates_found += 1

    # Update the number of paths
    k = min(k,candidates_found)

    if verbose:
        print "[get_k_shortest_paths]   Done."
        print "[get_k_shortest_paths]   Computing paths.."

    candidate_paths = []
    paths = []
    s = ()
    tup = (OPT, s)
    heapq.heapify(paths)
    heapq.heappush(paths, tup)

    if k == 1:
        result.extend(paths)
        return OPT

    for l in range(1, k):
        for tup in itertools.combinations(ordered_s_e, l):
            candidate_cost = 0
            for edge in tup:
                candidate_cost += edge[0]
            # Check if path might be in the k-least cost paths
            candidate_paths.append(tup)
            if verbose:
                print "[get_k_shortest_paths]   Tuple: ", tup
                print "[get_k_shortest_paths]   Cost: ", candidate_cost

    if verbose:
        print "[get_k_shortest_paths]   Candidates: ", candidate_paths
    # Can be improved
    for p in candidate_paths:
        cost = 0
        if verbose:
            print "[get_k_shortest_paths]   Examinating path: ", p
        for t in p:
            cost += t[0]

        if is_straight_path(g, source, target, p):
            if verbose:
                print "[get_k_shortest_paths]   Path is valid: ", p
            tup = (cost + OPT, p)
            heapq.heappush(paths, tup)
        else:
            if verbose:
                print "[get_k_shortest_paths]   Path is NOT valid: ", p
    if verbose:
        print "[get_k_shortest_paths]   Done."
        print "[get_k_shortest_paths]   Result:"
        for p in paths:
            print "[get_k_shortest_paths]   Path: ", p

    total = 0
    for i in range(0, k):
        tup = heapq.heappop(paths)
        total += tup[0]
        result.append(tup)

    heapq.heapify(result)

    add_edges(g, target, removed)

    return total


# TOTEST
# Maximize the probability of reaching target node
def maximize_target_outcome(g, source, target, tweet_hashtags, k=5, verbose=True):
    outcomes = []
    if verbose:
        print "[maximize_target_outcome]   Maximizing outcome on node: ", target
    pref_hashtags = most_interested_in_hashtags(g, target, k, tweet_hashtags, verbose=verbose)
    count = 0
    if verbose:
        print "[maximize_target_outcome]   Computing score for the k most favourite hashtags"
    for h in pref_hashtags:
        if count == k:
            break
        count += 1
        if verbose:
            print "[maximize_target_outcome]   Hashtag: ", h

        cur_hashtags = []
        cur_hashtags.extend(tweet_hashtags)
        cur_hashtags.append(h)

        homogeneity = homogeneity(cur_hashtags, verbose=verbose)

        weight_edges(g, h, homogeneity, verbose=verbose)
        outcome = []
        tot = get_k_shortest_paths(g, source, target, outcome, k, verbose=verbose)
        outcomes.append(tot, outcome)
        if verbose:
            print "[maximize_target_outcome]   Outcome: ", (tot,outcome)
    heapq.heapify(outcomes)
    if verbose:
        print "[maximize_target_outcome]   Done."
    return outcomes

# UTILS

# Deactivate nodes
def deactivate(g, verbose=False):
    if verbose:
        print "[deactivate]   Deactivating nodes.."
    # Deactivate all nodes
    for v in g.vs:
        v[ACTIVE] = False

    if verbose:
        print "[deactivate]   Done."


# Reset edge weights
def reset_weights(g, verbose=False):
    if verbose:
        print "[reset_weights]   Resetting weights.."
    for e in g.es:
        e[WEIGHT] = 0.0
    if verbose:
        print "[reset_weights]   Done."


# Reset the graph to default settings
def reset_graph(g, verbose=False):
    if verbose:
        print "[reset_graph]   Resetting graph.."
    # Reset nodes to their default settings
    for v in g.vs:
        v[ACTIVE] = False
        v[EXPECTED_VALUE] = 0.0
        if verbose:
            print "[reset_graph]   v"

    # Reset edges to their default settings
    for e in g.es:
        e[WEIGHT] = 0.0
        e[MAIN] = False
        e[INC] = 0.0
        if verbose:
            print "[reset_graph]   e"

    if verbose:
        print "[reset_graph]   Done."


if __name__ == "__main__":
    #
    # g = setup()
    # print hashtags[2], hashtags[1]
    # print most_interested_in_hashtags(g,7)
    '''cur_outcome = []
    n = estimate_expected_outcome(g, 0, [hashtags[2], hashtags[1]], 5, cur_outcome)
    print n
    print cur_outcome
    result = maximize_expected_outcome(g, 0, [hashtags[2], hashtags[1]], 5, cur_outcome)
    print result
    print translate("matteosalvinimi")
    # r = g.get_shortest_paths(0,4)
    # print r'''
    g = load_graph("k_paths_test_graph.tsv")
    print g

    # print get_close_hahstags([hashtags[2], hashtags[1]])
    '''print [hashtags[0],hashtags[1]]
    result = []
    print "Average number of nodes activated: ", \

    print result
    print "Nodes:"
    for n in g.vs:
        print n
    print "Edges:"
    for e in g.es:
        print e.source, e.target, e'''
    # weight_edges(g, "sale")
    # get_k_shortest_paths(g, 0, 4, [],1)

    # result = []
    # estimate_expected_outcome(g,0,["acqua"],50,result)
    # print result
    # most_interested_hashtags(g,0,0)
