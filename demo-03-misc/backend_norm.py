from analyzer_process import format_locations


scores_dict = {'brooklyn': [0.005, 0.0, 0.1253925143078571, 0.012024897803105153], '285b. kent': [0.005, 0.0, 0.0, 0.012024897803105153], 'new york city': [0.005, 0.0, 0.12529076068013525, 0.0], 'oakland': [0.005, 0.0, 0.07611395553799709, 0.005921655547702681], 'philly': [0.005, 0.0, 0.12702354837731367, 0.0], 'bay bridge': [0.005, 0.0, 0.12905775981420187, 0.0], '8th street': [0.005, 0.0, 0.07263356737794611, 0.0038520983979995504], 'san francisco': [0.015, 0.0, 0.07589090465111534, 0.019200769556953115], 'west berkeley': [0.04, 0.0, 0.07608543508214356, 0.012651495714183362], "mr. t's bowl": [0.005, 0.0, 0.0, 0.012024897803105153], 'disneyland': [0.005, 0.0, 0.08279857884772694, 0.0], 'u. s.': [0.005, 0.0, 0.10959688732174987, 0.0], 'palestine': [0.005, 0.0, 0.11863307522349152, 0.011538461538461539], 'los angeles': [0.005, 0.0, 0.08229891350278558, 0.012024897803105153], '924 gilman street': [0.135, 0.0, 0.0, 0.027453198065955163], 'east bay': [0.01, 0.0, 0.07625743013680104, 0.0], 'columbay': [0.01, 0.0, 0.0, 0.011538461538461539], 'yuppie street': [0.005, 0.0, 0.0, 0.0038520983979995504], 'bay area': [0.024999999999999998, 0.0, 0.0758848415192974, 0.00589217002986293]}

for word, scores in scores_dict.items():
    scores_dict[word] = [scores]

# Initialize the new shape dictionary
new_shape = {}

# Loop over the word keys and their corresponding score lists
for word, scores in scores_dict.items():
    for i, score_list in enumerate(scores):
        # We create keys for each weight index
        weight_key = f"weight{i+1}"
        # If the weight key is not yet in the dictionary, we add it
        if weight_key not in new_shape:
            new_shape[weight_key] = [{"component1": {}}, {"component2": {}}, {"component3": {}}, {"component4": {}}]
        
        # Add scores for each component (component1, component2, etc.)
        for component_idx, score in enumerate(score_list):
            component_key = f"component{component_idx + 1}"
            new_shape[weight_key][component_idx][component_key][word] = score

# Now `new_shape` contains the transformed dictionary
# print(new_shape)
# print()

res = []
for wname, wval in new_shape.items():
    for c in wval:
        for cname, cval in c.items():
            r = []
            for wname, wval in cval.items():
                # print(wval)
                r.append((wname, wval))
            res.append(r)
        # print()

# print(res)

for sub in res:
    new = format_locations(sub)
    # print(new)
    # print()
    for loc, score in new:
        print(score)
    print()