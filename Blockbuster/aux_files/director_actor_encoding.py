def data_explore(data, director_or_actor):
    """
    Checks if there are any missing values in the column, and whether these are NaN values that
    are being treated as floats.
    """

    missing = data[director_or_actor].apply(type).value_counts()
    type_missing = data[director_or_actor][data[director_or_actor].apply(type) == float].head(10)

    return missing, type_missing

# ---------------------------------------------  
def remove_non_string(data, director_or_actor):
    """
    Removes any rows from the directors or actors column where the datatype of that entry
    is not a string (i.e. it is a missing value).
    """

    data = data[data[director_or_actor].apply(type) == str]

    return data

# ---------------------------------------------
def group_gw_and_ar(train_data, director_or_actor):
    """
    Groups the training data by a the director or actor column and then computes and returns
    the mean of 'grossWorldwide' and 'averageRating' for each group. 
    """
    
    grouped_grossWorldwide = train_data.groupby(director_or_actor)["grossWorldwide"].mean()
    grouped_averageRating = train_data.groupby(director_or_actor)["averageRating"].mean()

    return grouped_grossWorldwide, grouped_averageRating

# ---------------------------------------------
def map_groups(train_data, director_or_actor, grouped_gross, grouped_rating):
    """
    Maps the average grossWorldwide and averageRating values (from grouped data)to each row in the
    training dataset based on the director or actor. It then returns this mapping.
    """
    
    map_gross = train_data[director_or_actor].map(grouped_gross)
    map_rating = train_data[director_or_actor].map(grouped_rating)

    return map_gross, map_rating

# ---------------------------------------------
def map_default_values(train_data, director_or_actor, test_data, grouped_gross, grouped_rating):
    """
    Maps grouped average values to the test dataset. For any unknown directors/actors 
    (i.e., not in training set), fills with default values calculated from individuals 
    with only one movie in the training data. 
    """
    
    # Finding all the director/actors that only made one movie
    frequency = train_data[director_or_actor].value_counts()
    one_movie = frequency[frequency == 1]

    # Need to get the directors/actors names, which are the indexes
    one_movie_names = one_movie.index
    
    # Finding all the movies from one_movie actors or directors
    movies = train_data[train_data[director_or_actor].isin(one_movie_names)]
    
    # Setting the default values
    default_grossWorldwide = movies["grossWorldwide"].mean()
    default_averageRating = movies["averageRating"].mean()
    print(f"The default grossWorldwide value for {director_or_actor} is: {default_grossWorldwide}")
    print(f"The default averageRating value for {director_or_actor} is: {default_averageRating}")

    # Mapping to test_data
    test_gross = test_data[director_or_actor].map(grouped_gross)
    test_rating = test_data[director_or_actor].map(grouped_rating)
    
    # Replacing null values
    test_gross = test_gross.fillna(default_grossWorldwide)
    test_rating = test_rating.fillna(default_averageRating)
    
    return test_gross, test_rating

