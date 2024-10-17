### Set up ###

# Import required packages:
import os # os functions
import pymongo # access to mongo
import gensim # topic modelling library
import re # modifying texts
import nltk # natural language processing tools
from nltk.corpus import stopwords
from nltk.stem.wordnet import WordNetLemmatizer
from gensim.models import Phrases
from gensim.corpora import Dictionary
from collections import OrderedDict
from gensim.corpora.mmcorpus import MmCorpus
import gc
import logging
from gensim.models import CoherenceModel, LdaModel, LsiModel, HdpModel
from gensim.models import ldamulticore
from gensim import models
import pyLDAvis.gensim
#import pyLDAvis.gensim_models
import csv
import faulthandler

faulthandler.enable()

# Set working directory
os.chdir('/home/InfluentialPast/InfluentialPast')

# Define output paths:

path2dictionary = 'outputs/TopicModels/tweets/inputs/dictionary_archaeology'
path2corpus = 'outputs/TopicModels/tweets/inputs/corpus_archaeology'
path2model = 'outputs/TopicModels/tweets/models/model_archaeology'
path2coherence =  "outputs/TopicModels/tweets/coherence_scores_archaeology.csv"
path2html = "outputs/TopicModels/tweets/tm_vis_archaeology"

# Alternatively Define output paths for users:
#path2dictionary = 'outputs/TopicModels/users/inputs/dictionary'
#path2corpus = 'outputs/TopicModels/users/inputs/corpus'
#path2model = 'outputs/TopicModels/users/models/model'
#path2coherence =  "outputs/TopicModels/users/coherence_scores.csv"
#path2html = "outputs/TopicModels/users/tm_vis"

### Data import ###

# Extract data from the database with pymongo
# Make a client:
from pymongo import MongoClient
client = MongoClient()
client = MongoClient('localhost', 27017)
client = MongoClient('mongodb://localhost:27017/')

# Define the database as InfluentialPasts
db = client.InfluentialPast

# Get collection:
collection = db.tweets

# Alternatively for users
#collection = db.users


# Define query:
query = {"$and":[{"$or":[{"referenced_tweets.type":None},{"$and":[{"referenced_tweets.type":"quoted"},{"collection_stage":1}]}]},{"lang":"en"},{"keywords":"#archaeology"}]}

# Define fields to search:
fields = {"text":1,"_id":0,"author_id":1}

# Alternatively for users
#fields = {"description":1,"_id":0}

# Iterate over mongodb cursor with relevant query and fields and append the texts to the list of texts
for text in collection.find(query,fields):
        t = text['text']
        texts.append(t)
        
# Alternatively for users

# Get relevant texts from the database:
# Make empty list
#texts = []
#ids = []

#for text in collection.find(query,fields):
#        i = text['author_id']
#        ids.append(i)


#ids= list(set(ids))

#query = {"id":{"$in":ids}}
#for text in collection.find(query,fields):
#        t = text['description']
#        texts.append(t)
                       
### Text processing###

# Get rid of links usernames, and (optionally) indication that the tweet is a retweet from the text:
i=0
j=len(texts)
while(i<j):
    texts[i] = re.sub('http\S+', '', texts[i])
    texts[i] = re.sub('@\S+', '', texts[i])
    #tweets[i] = re.sub('RT|cc', '', tweets[i])
    i=i+1
    
    
# Get only unique sets by 
texts = list(set(texts))

# Tokenize the texts
    
i=0
j=len(texts)
while(i<j):
    texts[i] = gensim.utils.simple_preprocess(texts[i], deacc=True, min_len=3)
    i=i+1
    

# Import and define stpowords:
nltk.download('stopwords')
stops = set(stopwords.words('english'))

# Optionaly add additional stopwords:
#stops.update(set(["",""]))

## Get rid of all stopwords
texts = [[word for word in text if word not in stops] for text in texts]

# Lemmatize all the words in the document:
nltk.download('wordnet')
lemmatizer = WordNetLemmatizer()
texts= [[lemmatizer.lemmatize(token) for token in text] for text in texts]

# Add bigrams and trigrams to docs (only ones that appear 50 times or more).
bigram = Phrases(texts, min_count=50)
for idx in range(len(texts)):
    for token in bigram[texts[idx]]:
        if '_' in token:
            # Token is a bigram, add to document.
            texts[idx].append(token)
            
            
# Make and save dictionary             
dictionary = Dictionary(texts)
dictionary.save_as_text(path2dictionary)

# Make and save corpus
corpus = [dictionary.doc2bow(text) for text in texts]
MmCorpus.serialize(path2corpus, corpus)


# Load corpus and (optionally) dictionary
mm = MmCorpus(path2corpus)
dictionary = Dictionary.load_from_text(path2dictionary)


### Prepare models with different numbers of topics
# Set up the list to hold coherence values for each topic:
c_v = []
# Set the max number of topics:

max_topics=30
# Loop over to create models with 2 to 30 topics, and caluclate coherence scores for it:

for num_topics in range(2, max_topics):
    print(num_topics)
    lm = models.LdaMulticore(corpus=mm, num_topics=num_topics,     id2word=dictionary,chunksize=9000,passes=100,eval_every=1,iterations=500,workers=4) # Create a model for num_topics topics
    print("Calculating coherence score...")
    cm = CoherenceModel(model=lm, texts=texts, dictionary=dictionary, coherence='c_v') # Calculate the coherence score for the topics
    print("Saving model...")
    lm.save(path2model+str(num_topics)) # Save the model
    lm.clear() # Clear the data from the model
    del lm # Delete the model
    gc.collect() # Clears data from the workspace to free up memory
    c_v.append(cm.get_coherence()) # Append the coherence score to the list
    
# Save the coherence scores to the file:    
with open(path2coherence, 'a') as csvFile:
    writer = csv.writer(csvFile)
    writer.writerow(["n_topics","coherence_score"])
    i=2
    for score in c_v:
        print(i)
        writer.writerow([i,score])
        i=i+1
        
        
n=c_v.index(max(c_v))+2 # Get the number of topics with the highest coherence score
lm = LdaModel.load(path2model+str(n)) # Load the number of topics with the highest coherence score into the workspace
tm = pyLDAvis.gensim.prepare(lm, mm, dictionary) # Prepare the visualisation
pyLDAvis.save_html(tm, path2html+str(n)+'.html') # Save the visualisation