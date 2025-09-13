"""
This script combines all scraped dataset checkpoints into the final dataset of 54000 movies which now includes
scraped data. This dataset is saved to 54000_movies_dataset.csv
"""
import pandas as pd

session_1 = pd.read_csv("../datasets/webscraper_checkpoints/checkpoint1.4.csv")
session_2 = pd.read_csv("../datasets/webscraper_checkpoints/checkpoint2.16.csv")
session_3 = pd.read_csv("../datasets/webscraper_checkpoints/checkpoint3.16.csv")
session_4 = pd.read_csv("../datasets/webscraper_checkpoints/checkpoint4.15.csv")
session_5 = pd.read_csv("../datasets/webscraper_checkpoints/checkpoint5.4.csv")

final_movies_dataset = pd.concat([session_1, session_2, session_3, session_4, session_5], ignore_index=True)

final_movies_dataset.to_csv("../datasets/54000_movies_dataset.csv", index = False)