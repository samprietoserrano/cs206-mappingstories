import pandas as pd
import os

# Original scores dictionary (assuming only one weight option)
# scores_dict = {
#     'word1': [[0.075, 0.1875, 0.1125, 0.25]],
#     'word2': [[0.099, 0.2475, 0.1485, 0.0]],
#     'word3': [[0.09, 0.375, 0.045, 0.1]],
#     'word4': [[0.09, 0.15, 0.135, 0.0]]
# }

def create_spreadsheet(scores_dict):
    # Create a list to store rows
    rows = []

    # Process each word and extract its components
    for word, scores in scores_dict.items():
        # Since there is only one weight option, take the first (and only) list of scores
        # components = scores[0]
        components = scores
        rows.append([word] + components)

    # Define column names
    columns = ["word", "component1", "component2", "component3", "component4"]

    # Create a DataFrame
    df = pd.DataFrame(rows, columns=columns)

    # Save to Excel file
    log_filename = "scores_output.xlsx"
    base_name, ext = os.path.splitext(log_filename)
    counter = 1
    while os.path.exists(log_filename):
        log_filename = f"{base_name}_{counter}{ext}"
        counter += 1
    df.to_excel(log_filename, index=False)
    # df.to_excel("/Users/samxp/Documents/Coding and Software/EJ-BayCurious/scores_output.xlsx", index=False)

    # Print the DataFrame to verify the structure
    print(df)