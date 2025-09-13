"""
This script combines the datasets from title.basics.zip and title.ratings.zip into one dataset
which only contains movies made post 2019. Resulting dataset is saved to 54000_movies_dataset_prelim.csv.
"""
import pandas as pd
import zipfile

with zipfile.ZipFile("../datasets/title.basics.zip", "r") as movie_basics_zip:
    with zipfile.ZipFile("../datasets/title.ratings.zip", "r") as movie_ratings_zip:
        with movie_basics_zip.open("title.basics.tsv") as movie_basics_file:
            with movie_ratings_zip.open("title.ratings.tsv") as movie_ratings_file:
                # These datasets also contain media that aren't movies, such as episodes, tv shows, etc.
                movie_basics_dataset = pd.read_csv(movie_basics_file, sep = "\t")
                movie_ratings_dataset = pd.read_csv(movie_ratings_file, sep = "\t")
                
                # Merging both together
                movie_dataset = pd.merge(movie_ratings_dataset, movie_basics_dataset, on = "tconst")
                
                # Filtering only the movies that were released after 2019
                movie_dataset = movie_dataset[(movie_dataset["titleType"] == "movie") & (pd.to_numeric(movie_dataset["startYear"], errors = 'coerce') >= 2020)]
                
                movie_dataset.to_csv("../datasets/54000_movies_dataset_prelim.csv", index = False)
                
"""
References:
    ChatGPT: https://chatgpt.com/share/6841f4d6-eb48-800d-ac4c-fa30d887b98a
"""