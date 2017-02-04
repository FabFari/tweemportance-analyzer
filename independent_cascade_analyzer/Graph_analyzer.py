import csv
import random

from igraph import *

GRAPH_FILE = "toy_graph"
TRANSLATION_FILE = "ID_translation.tsv"
WEIGHT = "weight"
ACTIVE = "active"
EXPECTED_VALUE = "e_v"






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

                    current_id += 1

            #Add the edge to the graph
            g.add_edge(translator.get(row[0]), translator.get(row[1]))

            #Add the edge attributes
            lenght = len(row)
            for i in range(2,lenght,2):
                g.es[current_edge][row[i]]=float(row[i+1])
                g.es[current_edge][WEIGHT]=0.0

            current_edge += 1

    print "Graph loaded."







def independent_cascade_process(g, source, hashtags, result, debug=True):

    #TODO
    #Topic neighbourness
    #Need runtime Jaccard Similarity
    jaccard = 1

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

                pr = g.es[e][max]*jaccard
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





def estimate_expected_outcome(g, source, hashtags, runs, expected_outcome):
    #This is the increment each node can get from a single run,
    #At the end, the number of increments received will be an estimation of the
    #probability of the node being activated.
    #Hence we will have an estimation of the expected outcome of the process.
    inc = 1.0/runs

    #Repeate the process "runs" times
    for i in range(runs):
        result = []
        independent_cascade_process(g, source, hashtags, result)
        for i in result:
            g.vs[i][EXPECTED_VALUE] += inc
        deactivate(g)

    #Collect results
    for v in g.vs:
        expected_outcome.append(v[EXPECTED_VALUE])

    #Clean up
    reset_graph(g)


def deactivate(g):
    #Deactivate all nodes
    for v in g.vs:
        v[ACTIVE] = False


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
        print e

    print "Done."


if __name__ == "__main__":
    g = Graph(directed=True)
    load_graph(GRAPH_FILE, TRANSLATION_FILE,g)
    result = []
    estimate_expected_outcome(g,0,["acqua"],50,result)
    print result

