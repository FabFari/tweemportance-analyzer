import csv
import heapq
import random
from collections import deque

import itertools
from igraph import *
from translate.lang.ja import ja

from utils.graph_jaccard_similarity import graph_jaccard_similarity
from utils.vector_utils import compare_positivity

GRAPH_FILE = "toy_graph2.tsv"
TRANSLATION_FILE = "ID_translation.tsv"

WEIGHT = "weight"
INC = "increase"
MAIN = "main"
#TODO
#Collection of all the hashtags
HASHTAGS = ["acqua", "sale"]

ACTIVE = "active"
EXPECTED_VALUE = "e_v"
COST = "cost"
BALANCE_FACTOR = 1
SOURCE = 0
MST = Graph(directed=True)
#Flag to check whether the MST has been already computed
MST_FLAG = False






#LOAD GRAPH
def load_graph(graph_in, translation_out, g):
    print "Loading  graph.."

    #Open the graph file, and a  new file:
    #the new file will contain a mapping between the tweeter accounts and the nodes' IDs in the graph.
    with open(graph_in, 'rb') as tsvin, open(translation_out, 'wb') as tsvout:
        tsvin = csv.reader(tsvin, delimiter='\t')
        tsvout = csv.writer(tsvout, delimiter='\t')

        translator = {}
        current_id = 0
        current_edge = 0

        for row in tsvin:
            #Check if each of the twitter accounts of the current edge
            #have already a corresponding vertex in the graph.
            for i in range(0,2):
                twitter_id = row[i]
                #If not create a new vertex and update the mapping
                if translator.has_key(twitter_id) is False:
                    translator[twitter_id] = current_id
                    tsvout.writerow([twitter_id, translator[twitter_id]])

                    g.add_vertex()
                    g.vs[current_id][ACTIVE]= False
                    g.vs[current_id][EXPECTED_VALUE] = 0.0
                    g.vs[current_id][COST]=0.0

                    current_id += 1

            #Add the edge to the graph
            g.add_edge(translator.get(row[0]), translator.get(row[1]))

            #Add the edge attributes
            lenght = len(row)
            for i in range(2,lenght,2):
                g.es[current_edge][row[i]]=float(row[i+1])

            g.es[current_edge][WEIGHT] = 0.0
            g.es[current_edge][INC] = 0.0
            g.es[current_edge][MAIN] = False

            current_edge += 1

    print "Graph loaded."


#MODEL SIMULATION
def independent_cascade_process(g, source, hashtags, result, debug=True):

    #TODO
    #Topic neighbourness
    #Need runtime Jaccard Similarity
    #jaccard = graph_jaccard_similarity(hashtags)
    #diss = 1 - jaccard
    balance_coeff = 1 #-diss*BALANCE_FACTOR

    #Stack containing the nodes activated in the previous iteration
    #First iteration has only the source node
    it_cur= []
    g.vs[source][ACTIVE] = True
    it_cur.append(source)

    result.append(source)

    #Stack containing the nodes activated in the current iteration
    it_cur_n = []

    iter = 1

    #Each new iteration of this cycle is a new iteration of the process
    while len(it_cur) > 0:

        if debug:
            print "------------------------------------------------------"
            print "Iteration: ", iter

        #Simulate the process for each newly active node
        while len(it_cur) > 0:
            v = it_cur.pop()
            if debug:
                print "     Considering current active node: ", v

            edges = g.incident(v)
            for e in edges:

                #We consider only the hastag parameter that maximizes the probability,
                #this probability will then adjusted according to the jaccard similarity of the hashtags.
                #The Jaccard similarity is an indicator of how close the hashtags are.
                pr = 0.0
                max = hashtags[0]

                for h in hashtags[1:]:
                    if g.es[e][h] > g.es[e][max]:
                        max = h

                pr = g.es[e][max]*balance_coeff
                if debug:
                    print "     Probability of activation on the considered edge: ", pr

                #Random number to simulate the biased coin flip
                r = random.random()

                if debug:
                    print "     Value obtained: ", r

                #If the result is head, activated the node
                if r<=pr:
                    u = g.es[e].target
                    #If the node was already active, do nothing
                    if g.vs[u][ACTIVE] is False:
                        if debug:
                            print  "            Node ", u, " activated."
                        g.vs[u][ACTIVE] = True
                        it_cur_n.append(u)
                        result.append(u)

        #Move to the next  iteration
        it_cur = it_cur_n
        it_cur_n = []
        iter += 1
    if debug:
        print "------------------------------------------------------"
        print "Done."



#ESTIMATION
def estimate_expected_outcome(g, source, hashtags, runs, expected_outcome):
    #This is the increment each node can get from a single run,
    #At the end, the number of increments received will be an estimation of the
    #probability of the node being activated.
    #Hence we will have an estimation of the expected outcome of the process.
    #This value can be used also to average the number of nodes activated in the different runs of the process
    inc = 1.0/runs

    avg_acts = 0

    #Repeate the process "runs" times
    for i in range(runs):
        activations = 0
        result = []
        independent_cascade_process(g, source, hashtags, result)
        for i in result:
            activations += 1
            g.vs[i][EXPECTED_VALUE] += inc

        avg_acts += activations*inc

        deactivate(g)


    #Collect results
    for v in g.vs:
        expected_outcome.append(v[EXPECTED_VALUE])

    #Clean up
    reset_graph(g)

    return avg_acts





#GENERAL MAXIMIZATION HEURISTIC
def maximize_expected_outcome(g,source, hashtags, runs, current_outcome, outcomes):

    suggested_hashtags = []
    get_close_hahstags(hashtags, suggested_hashtags)
    for h in suggested_hashtags:
        current_hashtags = []
        current_hashtags.extend(hashtags)
        current_hashtags.append(h)
        outcome = []
        n = estimate_expected_outcome(g, source, current_hashtags, runs, outcome)
        positivity = compare_positivity(outcome, current_outcome)
        if positivity > 0:
            tup = (n, positivity)
            outcomes[h] = tup



def get_close_hahstags(hashtags_in, hashtags_out):
    # TODO
    hashtags_out.append("sale")


def most_interested_hashtags(g, id, k, result):
    heapq.heapify(result)

    #Assume id already translated
    v = g.vs[id]
    length = len(g.vs[id])

    e_id = 0
    e = g.es[e_id]

    length = len(e)

    #print e

    for h in HASHTAGS:
        weight = 1/e[h]
        tup = (weight, h)
        heapq.heappush(result, tup)
    #print result


#TARGET MAXIMIZATION HEURISTIC
def maximize_target_outcome(g, source, target, hashtags, runs, current_outcome, outcomes, k = 1):
    pref_h = []
    most_interested_hashtags(g,target,k,pref_h)
    #TODO


def weight_edges(g,field):
    #TODO
    #Stub method
    g.es[0][WEIGHT] = 1
    g.es[1][WEIGHT] = 3
    g.es[2][WEIGHT] = 1
    g.es[3][WEIGHT] = 6
    g.es[4][WEIGHT] = 1
    g.es[5][WEIGHT] = 1
    g.es[6][WEIGHT] = 2
    g.es[7][WEIGHT] = 1
    #for e in g.es:
    #    print e

def get_k_shortest_paths(g, source, target, k, result,  weight=None, debug=True):

    #Need first to remove outgoing edges from target, edges will be restored at the end of the computation
    if debug:
        print "Temporary removing useless edges.."

    removed = {}
    out_edges = g.incident(target)
    for id in out_edges:
        edge = g.es[id]
        key = edge.target
        #Dictionary to keep the  attributes
        dict = {}
        dict[MAIN] = edge[MAIN]
        dict[WEIGHT] = edge[WEIGHT]
        dict[INC] = edge[INC]
        for h in HASHTAGS:
            dict[h] = edge[h]

        #Save the dictionary
        removed[key] = dict

    g.delete_edges(out_edges)

    if debug:
        print "Done."
        print
        print "Edges removed: ", removed

    if debug:
        print "Computing ", k, "-least cost paths.."
        print "Source: ", source
        print "Target: ", target

    if debug:
        print "Computing inverse shortest paths.. "
    paths = g.get_shortest_paths(target, weights=WEIGHT, mode=IN,output = "epath")
    for p in paths:
        for e in p:
            g.es[e][MAIN] = True
            #print g.es[e]
    if debug:
        print "Done."
        print "-----------------------------------------"

    if debug:
        print "Reconstructing paths costs.."
    v_queue = deque()
    v_queue.append(target)
    g.vs[target][ACTIVE]=True
    while len(v_queue) >  0:
        v = v_queue.popleft()
        #Reuse ACTIVE field as VISITED flag
        edges = g.incident(v)
        for e in edges:
            if g.es[e][MAIN] is True:
                u = g.es[e].target
                if debug:
                    print "     Edge: ", g.es[e].source, " ", g.es[e].target, \
                        " is in some shortest path with cost", g.es[e][WEIGHT]
                g.vs[v][COST]  = g.es[e][WEIGHT] + g.vs[u][COST]
                break

        edges = g.incident(v,mode=IN)
        if debug:
            print "     Considering  outer neighbors of ", v
        for e in edges:
            if g.es[e][MAIN] is True:
                u = g.es[e].source
                if debug:
                    print "         Considering node ", u
                if g.vs[u][ACTIVE] is False:
                    if debug:
                        print "         Node ",u, " is now active."
                    g.vs[u][ACTIVE] =  True
                    v_queue.append(u)
        if debug:
            print

    if debug:
        print "Done."

    #Cost of the optimal path
    OPT = g.vs[source][COST]

    if debug:
        print "-----------------------------------------"
        print "Computing side edges increment in cost.."

    sidetrack_edges  = []

    count = 0
    max = 0

    #Can be improved
    for edge in g.es:
        if edge[MAIN] is False:
            count += 1
            edge[INC] = edge[WEIGHT] + g.vs[edge.target][COST] - g.vs[edge.source][COST]
            if debug:
                print "Edge: ", edge.source, " ", edge.target, " Side_track_cost: ", edge[INC]
            if count <= k-1:
                if edge[INC] > max:
                    max = edge[INC]
                    tup  = (edge[INC], edge.source, edge.target)
                sidetrack_edges.append(tup)
            if count > k-1:
                if edge[INC] < max:
                    tup = (edge[INC], edge.source, edge.target)
                sidetrack_edges.append(tup)

    if debug:
        print "Done."

    heapq.heapify(sidetrack_edges)

    ordered_s_e = []
    for i in range(0,k-1):
        ordered_s_e.append(heapq.heappop(sidetrack_edges))

    if debug:
        print "Candidate shortest paths side edges: ", ordered_s_e
    #Best paths already found, the shortest one is already known
    paths_found = 1
    paths = []
    candidate_paths = []
    s = ()
    tup = (OPT,s)
    heapq.heapify(paths)
    heapq.heappush(paths,tup)

    cur_max = 0
    for i in ordered_s_e:
        if i[0] > cur_max:
            cur_max = i[0]

    for l in range(1,k):
        for subset in itertools.combinations(ordered_s_e,l):
            candidate_paths.append(subset)
            print "Subset: ", subset


    #Can be improved
    for p in candidate_paths:
        cost = 0
        for t in p:
            cost += t[0]

        #Check if path might be in the k-least cost paths
        if cost <= cur_max:
            # TODO
            #Check if candidate is a path
            tup=(cost+OPT,p)
            heapq.heappush(paths,tup)

    for p in paths:
        print p

    # We will reuse this flag
    deactivate(g)



    if debug:
        print "Reinserting removed edges.."

    for k in removed.keys():
        g.add_edge(target, k)

    edges = g.incident(target)
    for id in edges:
        key = g.es[id].target
        dict = removed[key]
        edge = g.es[id]
        for k in dict.keys():
            edge[k] = dict[k]

    if debug:
        print "Done."

    #We now use WEIGHT field of the sidetrack edges as increase cost of alternative paths



    #print MST.vs[0]
    #p1 = g.get_all_shortest_paths(source,target)

    #while len(p1) > 0:
    #    n = p1.pop()

    #result.append(p1)

    #print p1
    #TODO


def get_mst(g, weight=None):
    global MST,MST_FLAG
    print "Computing MST.."
    MST = g.spanning_tree(weight)
    MST_FLAG = True
    print "Done"



#UTILS
def deactivate(g):
    #Deactivate all nodes
    for v in g.vs:
        v[ACTIVE] = False

def reset_weights(g):
    for e in g.es:
        e[WEIGHT] = 0.0


def reset_graph(g):
    print "Resetting graph.."
    #Reset nodes to their default settings
    for v in g.vs:
        v[ACTIVE] = False
        v[EXPECTED_VALUE] = 0.0
        print v

    #Reset edges to their default settings
    for e in g.es:
        e[WEIGHT] = 0.0
        e[MAIN] =  False
        e[INC] = 0.0
        print e

    print "Done."
















if __name__ == "__main__":
    g = Graph(directed=True)
    load_graph(GRAPH_FILE, TRANSLATION_FILE,g)
    #r = g.get_shortest_paths(0,4)
    #print r
    #print g
    weight_edges(g, "weight")
    get_k_shortest_paths(g,0,4,3,[],weight=WEIGHT)

    #result = []
    #estimate_expected_outcome(g,0,["acqua"],50,result)
    #print result
    #most_interested_hashtags(g,0,0)



