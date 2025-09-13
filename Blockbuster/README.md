# Assemble the Next Blockbuster Film
Julia, Leon, Leticia, and Mehmet

## Research Question
- Original research question: Assemble the next blockbuster film.
- Modified research question: Can we predict whether or not a movie will be a blockbuster, based on its pre-release characteristics?

## Project Description
This project aimed to classify movies as blockbusters or non-blockbusters, two classifications which we defined using gross income and IMDb rating. The primary goal is to predict blockbuster status based on a movie's actors, directors, runtime, etc. Although the original dataset was derived from Kaggle, more data was acquired by scraping information directly from the IMDb website. This dataset was analyzed during the exploratory data analysis (EDA) to determine that a supervised classification model will work optimally to determine whether movies fit the blockbuster features. After preprocessing the data, we used LightGBM, a pre-trained gradient boosting classifier known for its accuracy and robustness evaluate movies. For a more detailed recap of the project, view `results_discussion.ipynb`.

## Data
The original dataset contained 1,000 entries of the top movies with features:
- `Series_Title`, `Released_Year`, `Certificate`, `Runtime`, `Genre`,
- `IMDB_Rating`, `Overview`, `Meta_Score`, `Director`,
- `Star1`, `Star2`, `Star3`, `Star4`, 
- `No_of_Votes`, `Gross`, `Link`
- Target variables: `IMDB_Rating` (range: 7.6 - 9.3) and `Gross`(range: 1,300 - 900,000,000)

More data was scraped in order to have more entries and representatives columns. The new dataset contained 54,000 movies with features:
- `Column_1`, `tconst`, `averageRating`, `numVotes`, `titleType`,
- `primaryTitle`, `originalTitle`, `isAdult`, `startYear`,
- `endYear`, `runtimeMinutes`, `genres`, `storyline`,
- `themes`, `director`, `actors`, `gross_worldwide`
- Target variable: custom variable `movieType`, which was based off of`averageRating` (range: 1.0 - 9.8) and `gross_worldwide`(range: 1 - 2,300,000,000)

### Cleaning & Feature Engineering:
- Dropped the columns that were not going to be used for the model (`Column_1`, `tconst`, `numVotes`, `titleType`, `originalTitle`, `endYear`)
- Removed the rows that did not contain data for the `gross_worldwide` column which brought the data down to 12,000 entries

## Modelling Methods
A good approach when it comes to modelling this data is to try to compare classification and regression results to determine which one works better for our purpose and research question. Because of this, we wanted our model to follow specific criteria:
- Can perform classification and regression
- Handles mixed data types
- Is accurate and efficient
- Is interpretable

Our initial verdict was to use XGBoost since it met most of this criteria, and as a bonus, it was very interpretable. 
However, a challenge that arose when trying to use this model for our data is that we had many categorical values and XGBoost does not handle mixed datatypes well. We would have had to do a lot of preprocessing and create one-hot encoding matrices for our categorical data values. Although this would have been possible, we looked for a similar model that had all the advantages of XGBoost, but was good at mixed datatypes.

A solution we found for this issue was using LightGBM, which is a gradient boosting algorithm that handles categorical values by itself through tree splitting rather than one-hot encoding. This not only made the model much faster and more efficient, but it also meant that less preprocessing of the data was required before features were fed into the model.

Predicting whether a movie is a blockbuster or not required us to create a threshold that separates blockbuster from non-blockbuster categories. The realistic value for this would be 100 million dollars; however this made the data distribution very skewed, leading to a class imbalance. To solve this, we were more flexible with our threshold, lowering it to 1 million dollars. Therefore, we had two target variables: one for predicting blockbusters at the 100 million threshold, and one at the 1 million threshold. LightGBM was used as a classification and regression model to categorise the movies. 

## Project Files/Directories
- `aux_docs`: Directory that includes other types of auxillary files (not code) that help to track the progress that has been done throughtout the development of the project.
- `aux_files`: Directory that includes auxillary python files that would be too convoluted to include in the `eda.ipynb` or `model.ipynb`. Rather than overcrowding the notebook, the viewer will be guided to this folder if they wish to view the entire implementation.
- `datasets`: Directory that contains the past dataset with 1,000 movies, and the new dataset with 54,000 movies.
- `eda.ipynb`: Jupyter notebook for data exploration and visualization.
- `preprocessing.ipynb`: Jupyter notebook for preprocessing the data in preparation of the model.
- `model.ipynb`: Jupyter notebook for model implementation and hyperparameter tuning.
- `results_discussion.ipynb`: Jupyter notebook containing a small recap of our project, and a discussion of the results.