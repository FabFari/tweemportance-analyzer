import csv

import graph_analyzer

TEST_GRAPH_1 = "test_weight_1.tsv"
TEST_PATH_1 = "test_path_1.tsv"
TEST_PATH_2 = "test_path_2.tsv"

#Passed
def test_weight_edges(g, field, homogeneity=1):
    print "     Graph before weighting: "
    for e in g.es:
        print "     ", e
    print "     ===================================================="
    graph_analyzer.weight_edges(g, field, homogeneity)
    print "     Graph after weighting:"
    for e in g.es:
        print "     ", e

def load_path(file):
    print "Loading path.."
    path = []
    with open(file, 'rb') as tsvin:
        tsvin = csv.reader(tsvin, delimiter='\t')

        i= 0
        for row in tsvin:
            t = (row[0], row[1], row[2])
            path.append(t)
            i += 1

    print "Path: ", path
    print "Done."
    return path

def test_is_path(g,source,target,path):
    print "Testing path.."
    if graph_analyzer.is_path(g, source, target, path) is True:
        print "The path ", path, "is a valid path from ", source, " to ", target
    else :
        print "The path ", path, "is NOT a valid path from ", source, " to ", target

    print "Done."

def is_path_all_tests():
    g = graph_analyzer.load_graph(TEST_GRAPH_1)
    graph_analyzer.weight_edges(g, "sale")
    graph_analyzer.compute_shortest_paths(g, 5)
    p = load_path(TEST_PATH_2)
    test_is_path(g, 0, 5, p)
    p = load_path(TEST_PATH_1)
    test_is_path(g, 0, 5, p)

def test_reconstruct_paths_cost():
    g = graph_analyzer.load_graph(TEST_GRAPH_1)
    graph_analyzer.weight_edges(g, "sale")
    graph_analyzer.compute_shortest_paths(g,1, debug=False)
    print "Testing path cost reconstruction.."
    graph_analyzer.reconstruct_paths_cost(g,1)
    print "Done"
    print "Result:"
    for v in g.vs:
        print "         ", v


if __name__ == "__main__":
    print "Testing.."
    #is_path_all_tests()
    test_reconstruct_paths_cost()
    print "Done."