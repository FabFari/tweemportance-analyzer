import csv

import graph_analyzer

TEST_GRAPH_1 = "test_weight_1.tsv"
TEST_GRAPH_SIDE_TRACK = "toy_graph_3.tsv"
TEST_PATH_1 = "test_path_1.tsv"
TEST_PATH_2 = "test_path_2.tsv"

# Utils
def load_path(file):
    print "[load_path]   Loading path.."
    path = []
    with open(file, 'rb') as tsvin:
        tsvin = csv.reader(tsvin, delimiter='\t')

        i= 0
        for row in tsvin:
            t = (row[0], row[1], row[2])
            path.append(t)
            i += 1

    print "[load_path]   Path: ", path
    print "[load_path]   Done."
    return path


# Passed
def test_weight_edges(g, field, homogeneity=1):
    print "[test_weight_edges]   Graph before weighting: "
    for e in g.es:
        print "[test_weight_edges]     ", e
    print "[test_weight_edges]    ===================================================="
    graph_analyzer.weight_edges(g, field, homogeneity)
    print "[test_weight_edges]    Graph after weighting:"
    for e in g.es:
        print "[test_weight_edges]   ", e

    print "[test_weight_edges]   Done."

# Passed
def test_is_path(g,source,target,path):
    print "[test_is_path]   Testing path.."
    if graph_analyzer.is_straight_path(g, source, target, path) is True:
        print "[test_is_path]   The path ", path, "is a valid path from ", source, " to ", target
    else :
        print "[test_is_path]   The path ", path, "is NOT a valid path from ", source, " to ", target

    print "[test_is_path]   Done."

# Passed
def is_path_all_tests():
    g = graph_analyzer.load_graph(TEST_GRAPH_1)
    graph_analyzer.weight_edges(g, "sale")
    graph_analyzer.compute_shortest_paths(g, 5)
    p = load_path(TEST_PATH_2)
    test_is_path(g, 0, 5, p)
    p = load_path(TEST_PATH_1)
    test_is_path(g, 0, 5, p)

# Passed
def test_reconstruct_paths_cost():
    g = graph_analyzer.load_graph(TEST_GRAPH_1)
    graph_analyzer.weight_edges(g, "sale")
    graph_analyzer.compute_shortest_paths(g, 5, verbose=False)
    print "[test_reconstruct_paths_cost]   Testing path cost reconstruction.."
    graph_analyzer.reconstruct_paths_cost(g,5)
    print "[test_reconstruct_paths_cost]   Done."
    print "[test_reconstruct_paths_cost]   Result:"
    for v in g.vs:
        print "[test_reconstruct_paths_cost]   ", v

# Passed
def test_compute_sidetrack_edges_increment():
    print "[test_compute_k_sidetrack_edges]   Testing compute k sidetrack edges.."
    g = graph_analyzer.load_graph(TEST_GRAPH_SIDE_TRACK, verbose=False)
    removed = graph_analyzer.remove_incidents(g,4, verbose=False)
    graph_analyzer.weight_edges(g, "sale", verbose=False)
    graph_analyzer.compute_shortest_paths(g, 4, verbose=False)
    graph_analyzer.reconstruct_paths_cost(g,4, verbose=False)
    s_e = graph_analyzer.compute_sidetrack_edges_increment(g)
    graph_analyzer.add_edges(g,4,removed, verbose=False)
    print "[test_compute_k_sidetrack_edges]   Done."
    print "[test_compute_k_sidetrack_edges]   Result: "
    for e in s_e:
        print "[test_compute_k_sidetrack_edges]   ",e


def test_get_k_shortest_paths():
    g = graph_analyzer.load_graph("k_paths_test_graph.tsv")
    graph_analyzer.weight_edges(g, "#A")
    # for e in g.es:
    #    print e.source, e.target
    #    print e
    result = []
    tot =  graph_analyzer.get_k_shortest_paths(g,0,5, result, k=3)
    print result
    print tot

if __name__ == "__main__":
    print "Testing.."
    #is_path_all_tests()
    #test_reconstruct_paths_cost()
    #test_compute_sidetrack_edges_increment()
    test_get_k_shortest_paths()
    print "Done."