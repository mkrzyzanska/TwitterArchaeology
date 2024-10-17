// Locate threat words in the tweets and measure threat levels:

// Look up words, but only if they have 'no letters' boundaries around them.
db.threat_dictionary.find().forEach(function(doc){                                
    var threat = doc['_id']
     db.tweets.updateMany({text:{$regex: "/b"+threat+"/b", $options: 'i'}},
                          {$addToSet:{threat_terms:threat}})});


db.tweets.updateMany({"threat_terms":{"$exists":true}},[
    // Aggregation pipeline
    { "$set": { "threat_level": {"$size":"$threat_terms"}}}],
                     {
    // Options
    "multi": true // false when a single doc has to be updated
  })