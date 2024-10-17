# Load libraries

library(here)
library(mongolite)
library(vader) 

# Establish connection to the database
col = mongo(collection = "tweets", db = "InfluentialPast")

query = '{}'
fields = '{"id":true,"text":true}'
tweets<-col$find(query,fields)


# Calculate sentiments for all texts in the tweets collection
sentiments<-vader_df(tweets$text)

tweets<- cbind(tweets,sentiments[,names(sentiments) != "text"])
errors<-tweets[tweets$word_scores=="ERROR",]
errors<-tweets[tweets$word_scores=="ERROR",]
errors$text <- gsub("[^\x01-\x7F]", "",errors$text)
errors$text <- gsub("-", "",errors$text)
errors$text <- gsub("LMAO", "",errors$text)
new_sentiments<-vader_df(errors$text)
t2<- cbind(errors[,colnames(errors) %in% c("_id","id","text")],new_sentiments[,names(new_sentiments) != "text"])

tweets<-tweets[tweets$word_scores!="ERROR",]
tweets<-rbind(tweets,t2)

# Now iterate over rows of the data.frame and enter sentiment data into the database:

apply(t2, 1, function(x){
    id = x[['id']]
    query <- paste('{"id":"',id,'"}',sep="")
    print(id)
    s <- x[c("word_scores","compound","pos","neu","neg","but_count")]
    values = unname(unlist(s))
    n = which(names(s)=="word_scores")
    values[n] <- sub("\\{","[",values[n])
    values[n] <- sub("\\}","]",values[n])
    array <- paste('"',names(s),'":',values,sep="")
    array <-paste('{"$set":{"sentiment":{',paste(paste(array, collapse=',' ),'}}}',sep=""))    
    col$update(query, array)
        })