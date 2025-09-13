def unique_values(dataframe, column_name):
    """
    Returns the unique values in a specified column of a pandas DataFrame, in this case our movie_dataset.
    """
    
    if column_name not in dataframe.columns:
        raise ValueError("Column does not exist in dataframe")
    
    column_data = dataframe[column_name].astype(str)
    unique = set()

    for entry in column_data:
        for item in entry.split(','):
            unique.add(item.strip())
            
    return unique

# ---------------------------------------------
def count_unique_values(dataframe, column_name):
    """
    Returns a dictionary with counts of unique values in a specified column.
    """
    
    if column_name not in dataframe.columns:
        raise ValueError("Column does not exist in dataframe")
    
    column_data = dataframe[column_name].dropna().astype(str)
    counts = {}

    for entry in column_data:
        for item in entry.split(','):
            item_clean = item.strip()
            counts[item_clean] = counts.get(item_clean, 0) + 1
            
    return counts

# ---------------------------------------------
def unique_combos(dataframe, column_name):
    """
    Returns the unique values in a specified column of a pandas DataFrame.
    """
    
    if column_name not in dataframe.columns:
        raise ValueError("Column does not exist in dataframe")
    
    # .unique() is a method that returns the unique values of a series in the Pandas library
    unique_combos = dataframe[column_name].unique()
    return unique_combos

# ---------------------------------------------
def first_n_unique(n, dataframe):
    """
    Prints the unique values set for the first n rows of the categorical columns in the movies dataset.
    """
    categorical_columns = dataframe.select_dtypes(include=['object', 'category']).columns
    
    for column in categorical_columns:
        unique_vals = unique_values(dataframe, column)
        first_n = list(unique_vals)[:n]  # get first n unique values
        print(f"\033[1mFirst {n} unique values for column '{column}':\033[0m")
        print(first_n)

# ---------------------------------------------
def print_amount_unique(dataframe):
    """
    Prints the amount of unique values in every column of the dataset.
    """
    for column in dataframe.columns:
        unique = unique_values(dataframe, column)
    
        print("The number of unique values for column", column, "is:", len(unique))
