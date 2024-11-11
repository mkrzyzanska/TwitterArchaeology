# TwitterArchaeology

Code to accompany the article:

# Introduction:

This repository contains codes used for the collection and management of data and for the analysis undertaken for the article 'Positive sentiment and expertise predict the diffusion of archaeological content on social media'. The code was run in R, python and mongo database shell. 

# Data collection:

Historical data from [Twitter](https://twitter.com) was extracted via the [Academic API](https://developer.twitter.com/en/products/twitter-api/academic-research) using the [full-archive search endpoint](https://developer.twitter.com/en/docs/twitter-api/tweets/search/quick-start/full-archive-search). We extracted tweets containing hashtag #archaeology for the period from 01.02.2023 to 08.02.2023, inclusive. The data was collected using the [academictwitteR](https://github.com/cjbarrie/academictwitteR) library and as part of the set up, [Twitter App was created within the approved academic project](http://127.0.0.1:25801/library/academictwitteR/doc/academictwitteR-auth.html) and the [bearer token was set as an R environmental variable](https://github.com/cjbarrie/academictwitteR#authorization). It  included both tweets and additional files with user data. The code is available [here](R/Data_collection-tweets_with_keywords.R).

# Data processing:

Subsequently, data was [imported into](mongo/Import_to_mongo.txt) [Mongo Database](https://www.mongodb.com/) and cleaned. This involved checking for duplicates, separating the replies from original tweets and setting indexes on text fields (see [here](mongo/data_cleaning.js)). 

# Analysis:

## Sentiment analysis:

Sentiment scores were calculated using [Valence Aware Dictionary and sEntiment Reasoner](http://eegilbert.org/papers/icwsm14.vader.hutto.pdf) and assigned to each tweet in the database (see [here](R/Sentiment_analysis.R)).

## Threat:

Threat words were identified based on the dictionary provided in [Table S2](https://www.pnas.org/doi/suppl/10.1073/pnas.2113891119/suppl_file/pnas.2113891119.sapp.pdf) in the supplementary material to [Choi et al. 2022](https://www.pnas.org/doi/suppl/10.1073/pnas.2113891119). The dictionary was [imported](mongo/Import_to_mongo.txt) into the mongo database and used to [identify threat level in tweets](mongo/threat.js). 

## Topic models:

The LDA topic models were run on the text of the tweets with topic number (n) between 2 and 29 (see [here](python/lda.py)) and [coherence scores](Notebooks/Sentiment_scores.ipynb) were calculated for each n. The model with the highest score was selected and an [interactive visualisation](outputs/TopicModels/tweets/tm_vis29.html) was constructed to help with the analysis of the topics. Subsequently, the [topic probabilities were assigned to the tweets](python/topic_assignement.py) in the database. The same procedure was repeated for user categories with the visualisation available [here](outputs/TopicModels/users/users_topic_model29.html).

## Bayesian model:

The Zero-Inflated model which inlcudes threat, sentiment topcis, and tweet topics and user categories as variables was constructed in [stan](stan/m.archaeology.stan)) and [run on the collected data](R/Bayesian_model.R). Subsequently, the model results were analysed and plotted [here](Notebooks/Bayesian_model.ipynb), and the model itself is available [here](outputs/BayesianModels/m.archaeology.rds). Additionally, a model which includes additional variables with associated files is available in [extra_variables](extra_variables) folder.
 
