//////////// Tweets collection - import and data cleaning //////////

//// This was done after importing the tweets which were originally collected (archeive_search and January2023 folders) to the collection tweets (see data import)

// Define data collections stage:

db.tweets.updateMany({},{$set:{collection_stage:1}})

// Set index for easier parasing when cleaning 
db.tweets.createIndex( { "id": 1 } )

// Check for duplicates by aggregating by the tweet id
db.tweets.aggregate([
        {"$group" : {_id:"$id",
        count:{$sum:1}}},
        {$out: "count_tweet_ids"}
],{allowDiskUse:true})

db.count_tweet_ids.distinct("count") // If there are any ids wih count more than 1, these are the duplicates
var ids = db.count_tweet_ids.distinct("_id",{count:{ $gt: 1}}) // Get ids of those tweets in the database that have duplicates

// Now iterate over each id to get rid of the tweets collected in the second stage if there are any present (these were not used in the paper but added to the collection separately):
for (i = 0; i < ids.length; i++) { var id = ids[i]; print(id); db.tweets.deleteOne({ $and: [{ id: id }, { collection_stage: { $exists: false } }] }); } 

db.count_tweet_ids.drop() // Drop the collection with ids 

// Move those tweets which are replies to the separate collection:
db.tweets.aggregate([ { $match: { "referenced_tweets.type":"replied_to"}}, { $out: "replies" }])
db.tweets.deleteMany( { "referenced_tweets.type":"replied_to"} )

//// Indexing and keywords

// Set useful indexes:

// First drop the id index and re-set it as unique
db.tweets.dropIndex('id_1')
db.tweets.createIndex( { "id": 1 }, { unique: true } )
db.tweets.createIndex( { "author_id": 1 } ) // index user ids as well
db.tweets.createIndex( { "conversation_id": 1 } ) // index conversation ids as well
db.tweets.createIndex( { "referenced_tweets.id": 1 } ) // index conversation ids as well
db.tweets.createIndex({text:"text"},{background:true}) // Set the text index on the text field


//// Set the date field:

// Reformat date field as time variable

db.tweets.updateMany({},[
    // Aggregation pipeline
    { "$set": { "date": {$dateFromString: {dateString: '$created_at'}}}}],
                     {
    // Options
    "multi": true // false when a single doc has to be updated
  })

// Pull the keywords into the keywords field:
// Define keywords with regex in such a way that they get picked up if two terms within the same keyword are in the close proximity, so that they get picked up even if its e.g. hadrians-wall or hadirans_wall, not just Hadrian's wall. 

var keywords = [/stonehenge/,/hadrian\W{0,6}?\w{0,3}\W{0,6}?wall/,/sutton\W{0,6}?\w{0,3}\W{0,6}?hoo/,/antonine\W{0,6}\w{0,3}\W{0,6}wall/,/#archaeology/]
var names = ["stonehenge","hadrian's wall", "sutton hoo", "anotonine wall", "#archaeology"]

// Iterate over keywords to set them
for(k in keywords){  
    var keyword = keywords[k]
    var name = names[k]
    print(keyword)
    db.tweets.updateMany(
        {$or:[{text:{$regex:  keyword, $options: 'i'}},
              {"entities.annotations.normalized_text":{$regex:  keyword, $options: 'i'}},
              {"entities.urls.description":{$regex:  keyword, $options: 'i'}},
              {"entities.urls.title":{$regex:  keyword, $options: 'i'}},
              {"entities.urls.expanded_url":{$regex:  keyword, $options: 'i'}},
              {"entities.urls.unwound_url":{$regex:  keyword, $options: 'i'}}]},              
        {$addToSet:{
                     keywords:name
                    }}
        )
} 


// Now also make sure that keywords and #archaeology are also marked for retweets and quotes:
// For retweets just add them to the keywords section
// For quotes add them as quoted_keywords:


db.tweets.count({"keywords.0":{$exists:true}})
db.tweets.find({"keywords.0":{$exists:true}}).forEach(function(doc){
    var id = doc['id']
    print(id)
    var keywords = doc['keywords']
    db.tweets.updateMany({$and:[{"referenced_tweets.id":id},{"referenced_tweets.type":"retweeted"}]},{$set:{keywords:keywords}})
    db.tweets.updateMany({$and:[{"referenced_tweets.id":id},{"referenced_tweets.type":"quoted"}]},{$set:{quotedKeywords:keywords}})
})


//////// User data //////// 

// Reformat the users data from arrays to entries in the database

db.usersArray.find().forEach(function(doc){db.users2.insertMany(doc['users'])});

// Delete empty documnets
db.usersArray.deleteMany({users:null})
db.usersArray.find().forEach(function(doc){db.users.insertMany(doc['users'])});


// Set the index on the id field 
db.users.createIndex( { "id": 1 })

// Check for users duplicates
db.users.aggregate([
        {"$group" : {_id:"$id",
        count:{$sum:1}}},
        {$out: "count_users_ids"}
],{allowDiskUse:true})


db.count_users_ids.distinct("count") // If there are any ids wihh count more than 1, these are the duplicates

var user_ids = db.users.distinct("id")
db.count_users_ids.find({count:{ $gt: 1}}).forEach(function(doc){
    id=doc['_id']
    print(id)
    count=doc['count']
    for(i=1;i<count;i++){db.users.deleteOne({id:id})}
})

db.count_users_ids.drop()
// Now check if all the author ids from tweets are also in the users database
db.replies.aggregate([
        {"$group" : {_id:"$author_id",
        count:{$sum:1}}},
        {$out: "count_author_ids"}
],{allowDiskUse:true})

var authors = db.count_author_ids.distinct("_id")

// See if any are missing
missing=[]

for (author in authors){
    print(author)
var a = db.users.findOne({"id":authors[author]})
if(a==null){missing.push(authors[author])}
}

db.count_users_ids.drop() // Drop the collection with ids 
db.count_author_ids.drop() // Drop the collection with author ids

// Set the text index on the description field

db.users.createIndex({description:"text"},{background:true})
db.users.dropIndex("id_1")
db.users.createIndex( { "id": 1 },{ unique: true } )// make the id index unique