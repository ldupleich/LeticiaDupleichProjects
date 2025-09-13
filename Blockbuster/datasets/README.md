**Directory Description**
- `1000_movies_dataset_original.csv`: This is the original dataset that was provided at the beginning of the month. This was not used for the rest of the project.
- `12000_movies_dataset.csv`: Dataset resulting from all changes made to 54000_movies_dataset.csv during eda.ipynb
- `54000_movies_dataset.csv`: Dataset resulting from aux_files/merge_datasets_post.py combining latest webscraper checkpoints.
- `54000_movies_dataset_prelim.csv`: Dataset resulting from combining title.basics and title.ratings in aux_files/merge_datasets_pre.py and filtering out all non-movie entries and all entries released pre 2020. This is the dataset we use for scraping using aux_files/webscraper.py.
- `title.basics.zip`: Zip file containing title.basics.csv, a dataset which contains basic information on 11.5 million movies.
- `title.ratings.zip`: Zip file containing title.ratings.csv, a dataset which contains the number of votes and average IMDB rating of 1.5 million movies.
- `movie_dataset_preprocessed.csv`: Overall dataset containing all data. It is a result of the preprocessing notebook, and is imported into the model notebook.
- `train_preprocessed.csv`: Dataset containing our training data. It is a result of the preprocessing notebook, and is imported into the model notebook.
- `test_preprocessed.csv`: Dataset containing our testing data. It is a result of the preprocessing notebook, and is imported into the model notebook.