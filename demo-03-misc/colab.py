import sys
sys.dont_write_bytecode = True

from collections import Counter
import numpy as np

weights = [0.25, 0.25, 0.25, 0.25]
weights2 = [0.33, 0.33, 0.33, 0] # <--- THIS ONE
weights3 = [0.3, 0.5, 0.1, 0.1]
weights4 = [0.3, 0.2, 0.3, 0]
weights5 = [0.33, 0.33, 0.33]


# w = [weights, weights2, weights3, weights4, weights5]

scores = [0.3, 0.75, 0.45, 1]

# USING ARRAYS DEFINED IN CELL ABOVE
w = [weights, weights2, weights3, weights4]
scores = [0.3, 0.75, 0.45, 1]

scores_dict = {}
for i in range(1, 6): # six identical words
    # print(np.array(scores))
    # scores_calc = [np.dot(np.array(wi),  np.array(scores[:len(weights)])) for wi in w]
    # info = scores + list(np.array(wi)*np.array(scores[:len(weights)]))
    scores_calc = [list(np.array(wi)*np.array(scores[:len(weights)])) for wi in w]
    scores_dict[f"word{i}"] = scores_calc

print(scores_dict)
print()
# tmp = [Counter(dict(zip(scores_dict.keys(), values))).most_common(3) for values in zip(*scores_dict.values())]
# tmp = [Counter(dict(zip(scores_dict.keys(), values))).most_common(3) for values in zip(*scores_dict.values())]
# print(tmp)

# [array([0.075 , 0.1875, 0.1125, 0.25  ]), array([0.099 , 0.2475, 0.1485, 0.    ]), array([0.09 , 0.375, 0.045, 0.1  ]), array([0.09 , 0.15 , 0.135, 0.   ])]