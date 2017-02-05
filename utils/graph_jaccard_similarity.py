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


# J(A, B) = |A *intersect* B| / |A *union* B|
# H = [{'N1': BitVector1, ..., 'Nm': BitVectorm}, ...]
def graph_jaccard_similarity(hashtags, mask_size):
    union_bitmask = BitVector(intVal=0, size=mask_size)
    intersec_bitmask = ~BitVector(intVal=0, size=mask_size)

    for bm in hashtags.values():
        union_bitmask |= bm
        intersec_bitmask &= bm

    return float(intersec_bitmask.count_bits()) / union_bitmask.count_bits()

