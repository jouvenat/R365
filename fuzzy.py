import pandas as pd
import numpy as np
from thefuzz import process, fuzz

# Load your two CSV files
df1 = pd.read_csv('blue.csv')
df2 = pd.read_csv('r365.csv')

# Let's say we want to match on 'company_name' in df1 and 'organization' in df2
def fuzzy_match_dataframes(df1, df2, col1, col2, threshold=80):
    """
    Match rows from two dataframes based on fuzzy string matching.
    
    Parameters:
    -----------
    df1, df2 : pandas DataFrames
        The dataframes to match
    col1, col2 : str
        The column names to match on
    threshold : int
        The minimum similarity score (0-100) to consider a match
        
    Returns:
    --------
    pandas DataFrame
        A merged dataframe with matches above the threshold
    """
    # Create a dictionary to store matches
    matches = {}
    
    # For each name in the first dataframe
    for name in df1[col1].unique():
        # Find the best match in the second dataframe
        match, score = process.extractOne(name, df2[col2].unique(), scorer=fuzz.token_sort_ratio)
        
        # If the match score is above our threshold, store it
        if score >= threshold:
            matches[name] = match
    
    # Create a mapping dictionary
    name_mapping = pd.DataFrame(list(matches.items()), columns=[col1, col2])
    
    # Merge the dataframes using the mapping
    result = pd.merge(df1, name_mapping, on=col1)
    result = pd.merge(result, df2, on=col2)
    
    return result

# Example usage
result = fuzzy_match_dataframes(
    df1, df2, 
    'Name', 'Commissary Item', 
    threshold=80
)
result.to_csv('matched_data.csv', index=False)