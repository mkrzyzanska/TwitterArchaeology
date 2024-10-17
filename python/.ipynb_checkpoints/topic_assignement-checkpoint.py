import pymongo
import gensim
import re # modifying texts
import nltk # natural language processing tools
from nltk.corpus import stopwords
from nltk.stem.wordnet import WordNetLemmatizer
from gensim.models import Phrases
from gensim.corpora import Dictionary
from collections import OrderedDict
from gensim.corpora.mmcorpus import MmCorpus
import gc
from gensim.models import CoherenceModel, LdaModel
from gensim.models import ldamulticore
import pyLDAvis.gensim


# Set working directory
os.chdir('/home/InfluentialPast/InfluentialPast')

# Define output paths:
path2dictionary = 'outputs/TopicModels/tweets/inputs/dictionary_archaeology'
path2corpus = 'outputs/TopicModels/tweets/inputs/corpus_archaeology'
path2model = 'outputs/TopicModels/tweets/models/model_archaeology'

# Define output paths:
path2dictionary = 'outputs/TopicModels/users/inputs/dictionary_archaeology'
path2corpus = 'outputs/TopicModels/users/inputs/corpus_archaeology'
path2model = 'outputs/TopicModels/users/models/model_archaeology'

from pymongo import MongoClient
client = MongoClient()
client = MongoClient('localhost', 27017)
client = MongoClient('mongodb://localhost:27017/')

# Define the database as InfluentialPasts
db = client.InfluentialPast

# Get collection:
collection = db.tweets

# Define query:
# For tweets
query = {"$and":[{"$or":[{"$and":[{"referenced_tweets.type":None},{"collection_stage":{"$in":[1,2]}}]},{"$and":[{"referenced_tweets.type":"quoted"},{"collection_stage":1}]}]},{"lang":"en"},{"keywords":"#archaeology"}]}

# Define fields to search:
fields = {"text":1,"id":1,"author_id":1}

# Make empty list
texts = []
ids = []
users = []


        
# Iterate over mongodb cursor with relevant query and fields and append the texts to the list of texts
for item in collection.find(query,fields):
        t = item['text']
        tid = item['id']
        uid = item['author_id']
        print(tid)
        texts.append(t)
        ids.append(tid)
        users.append(uid)
        
# While making the topic model we deleted duplicate texts, which made it through, so now we need to trandform the texts into corpus again:

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
        
dictionary = Dictionary.load_from_text(path2dictionary)
corpus = [dictionary.doc2bow(text) for text in texts]
mm = MmCorpus(path2corpus)

# Load model
n=22
lm = LdaModel.load(path2model+str(n))
tm = pyLDAvis.gensim.prepare(lm, mm, dictionary) # Prepare the visualisation


# Change the topics order to be consistent with the to be consistent with the pyLDAvis topic model (ordered from the most
# frequent one to the least frequent one) and assign dominant topic to each tweet:

# Get the topic order
to=tm.topic_order

for i in range(0,len(corpus)):
    print(i)
    topics = lm.get_document_topics(corpus[i]) # Get topic probabilities for the document
    topics=list(topics)    
    topics=[list(topic) for topic in topics] # Reformat topics probabilities for the analysis
    # reorder topics according to pyLDAvis numbering
    topics=[[to.index(topic[0]+1)+1,topic[1]] for topic in topics]
    topics = sorted(topics)
    # Need to change numeric value to float because mongo does not read numpy formats
    topics=[[str(topic[0]),float(topic[1])] for topic in topics] 
    topics = dict(topics)   
    # Setting filter for mongo
    filter = { 'id': ids[i] }
    # Values to be updated.
    newvalues = { "$set": {'topics_archaeology': topics} }
    # Using update_one() method for single
    collection.update_one(filter, newvalues)
    # Get dominant value and dominant topic (the highest probability and the topic with the highest probability) for the tweet.
    main_topic = int(max(topics,key=topics.get))
    value = topics[str(main_topic)]
    newvalues = { "$set": {'main_topic_archaeology': {'topic': main_topic, 'value': value} }}
    collection.update_one(filter, newvalues)    
    


users=list(set(users))


# For users - assuming the tweets are done:
query = {"id":{"$in":users}}
# Define fields to search:
fields = {"description":1,"id":1}

collection = db.users

# Make empty list
texts = []
ids = []

# Iterate over mongodb cursor with relevant query and fields and append the texts to the list of texts
for item in collection.find(query,fields):
        t = item['description']
        tid = item['id']
        print(tid)
        texts.append(t)
        ids.append(tid)
        
        
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
        
dictionary = Dictionary.load_from_text(path2dictionary)
corpus = [dictionary.doc2bow(text) for text in texts]

# Load model
n=4
lm = LdaModel.load(path2model+str(n))
tm = pyLDAvis.gensim.prepare(lm, mm, dictionary) # Prepare the visualisation
mm = MmCorpus(path2corpus)

# Change the topics order to be consistent with the to be consistent with the pyLDAvis topic model (ordered from the most
# frequent one to the least frequent one) and assign dominant topic to each tweet:

# Get the topic order
to=tm.topic_order

for i in range(0,len(corpus)):
    print(i)
    topics = lm.get_document_topics(corpus[i]) # Get topic probabilities for the document
    topics=list(topics)    
    topics=[list(topic) for topic in topics] # Reformat topics probabilities for the analysis
    # reorder topics according to pyLDAvis numbering
    topics=[[to.index(topic[0]+1)+1,topic[1]] for topic in topics]
    topics = sorted(topics)
    # Need to change numeric value to float because mongo does not read numpy formats
    topics=[[str(topic[0]),float(topic[1])] for topic in topics] 
    topics = dict(topics)   
    # Setting filter for mongo
    filter = { 'id': ids[i] }
    # Values to be updated.
    newvalues = { "$set": {'topics_archaeology': topics} }
    # Using update_one() method for single
    collection.update_one(filter, newvalues)
    # Get dominant value and dominant topic (the highest probability and the topic with the highest probability) for the tweet.
    main_topic = int(max(topics,key=topics.get))
    value = topics[str(main_topic)]
    newvalues = { "$set": {'main_topic_archaeology': {'topic': main_topic, 'value': value} }}
    collection.update_one(filter, newvalues)    
    

