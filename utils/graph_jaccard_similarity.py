import os
import heapq

from collections import defaultdict
from BitVector import BitVector


# G = {'N1': ['N2',..., 'Nl'], ..., 'Nm': ['N3',..., 'Nn']}
def compare_graphs(g1, g2):
    for n1 in g1.keys():
        for n2 in g2.keys():
            if len(g1[n1]) != len(g2[n2]):
                return False
            for reply in g1[n1]:
                if reply not in g2[n2]:
                    return False
    return True


def bitmask_file_parser(filename="hashtags_bitmasks.tsv", path="..\\data"):
    ht_bitmask = dict()

    with open(os.path.join(path, filename), 'r') as f:
        for line in f:
            hashtag = line.strip("\n").split("\t")
            ht_bitmask[hashtag[0]] = BitVector(bitstring=hashtag[1])

    return ht_bitmask


# J(A, B) = |A *intersect* B| / |A *union* B|
# H = [{'N1': BitVector1, ..., 'Nm': BitVectorm}, ...]
def graph_jaccard_similarity(hashtags, mask_size=None):
    if mask_size is None:
        mask_size = len(hashtags.values()[0])

    union_bitmask = BitVector(intVal=0, size=mask_size)
    intersec_bitmask = ~BitVector(intVal=0, size=mask_size)

    for bm in hashtags.values():
        union_bitmask |= bm
        intersec_bitmask &= bm

    return float(intersec_bitmask.count_bits()) / union_bitmask.count_bits()


def jaccard_all_pairs_similarity_file_parser(filename="jaccard_all_pairs_similarity.tsv", path="..\\data"):
    ht_pair_sim = dict()

    with open(os.path.join(path, filename), 'r') as f:
        for line in f:
            all_pair_list = line.strip("\n").split("\t")
            ht = all_pair_list.pop(0)
            all_pair_list_splitted = [pair.split(":") for pair in all_pair_list]
            ht_pair_sim[ht] = [(float(pair[1]), pair[0]) for pair in all_pair_list_splitted]

    return ht_pair_sim


def jaccard_top_k_similar_hashtags(ht_pair_sim, hashtags, k=2):
    all_pairs_dict = defaultdict(lambda: 0)

    for ht in hashtags:
        pos = 1
        for p in ht_pair_sim[ht]:
            if p[1] in hashtags:
                continue
            all_pairs_dict[p[1]] += pos
            pos += 1

    all_pairs_list = [(val, key) for (key, val) in all_pairs_dict.iteritems()]
    heapq.heapify(all_pairs_list)

    top_k_similar_hashtags = []
    for i in range(k):
        top_k_similar_hashtags.append(heapq.heappop(all_pairs_list))

    return top_k_similar_hashtags


if __name__ == "__main__":
    ht_bitmask = bitmask_file_parser()
    for (ht, bm) in ht_bitmask.iteritems():
        print "{}: {}".format(ht, bm)
    graph_jaccard_similarity(ht_bitmask)

    ht_pair_sim = jaccard_all_pairs_similarity_file_parser()
    print jaccard_top_k_similar_hashtags(ht_pair_sim, ['A', 'C'])


