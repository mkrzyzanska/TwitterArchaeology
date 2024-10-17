# Load libraries:
library("here")
library("mongolite")
library("rethinking")

# Set path to model:

path2model<-here("outputs","BayesianModels","m.archaeology.rds")

# Prepare data:
# Define database and collection
col = mongo(collection = "tweets", db = "InfluentialPast")

# Define query and fields to retrive:
query = '{"$and":[{"$or":[{"referenced_tweets.type":null},{"$and":[{"referenced_tweets.type":"quoted"},{"collection_stage":1}]}]},{"lang":"en"},{"keywords":"#archaeology"}]}'
fields = '{"id":true,"author_id":true,"public_metrics":true,"sentiment":true,"_id":false,"topics_archaeology":true,"threat_level":true,"main_topic_archaeology":true,"entities":true,"attachements":true,"characterCount":true}'

tweets<-col$find(query,fields)

colnames(tweets)[colnames(tweets)=="topics_archaeology"]<-"topics"
colnames(tweets)[colnames(tweets)=="main_topic_archaeology"]<-"main_topic"

tweets$image<-NA
tweets$link<-NA


for (i in 1:nrow(tweets)){
    print(i)
    x<-tweets[i,]   
    urls<-x$entities$urls[[1]]$expanded_url
    for (url in urls){
        print(url)
        if(grepl("photo",url)==TRUE|grepl("video",url)==TRUE){tweets$image[i]<-TRUE}
        else{tweets$link[i]<-TRUE}
        
    }
}
    

# Change the topic order to be consistent with visualisation
col_order <- unlist(lapply(1:ncol(tweets$topics),toString))

tweets$topics<- tweets$topics[, col_order]
tweets$topics[is.na(tweets$topics)] <- 0

# Get the list of user ids:
ids<-unique(tweets$author_id)

# Define the users collection
colUsers = mongo(collection = "users", db = "InfluentialPast")

#colUsers = mongo(collection = "users", db = "InfluentialPast",url = "mongodb://129.215.193.63:27017/serverSelectionTimeoutMS=4000")
queryUsers<-paste('{"id":{"$in":[',(paste('\"',as.character(ids),'\"',collapse=", ",sep="")),"]}}",sep="")
fieldsUsers <- '{"id":1,"description":1,"public_metrics":1,"_id":0,"topics_archaeology":1,"main_topic_archaeology":1}'
users<-colUsers$find(queryUsers,fieldsUsers)

colnames(users)[colnames(users)=="topics_archaeology"]<-"topics"
colnames(users)[colnames(users)=="main_topic_archaeology"]<-"main_topic"

col_order <- unlist(lapply(1:ncol(users$topics),toString))

users$topics<- users$topics[, col_order]
users$topics[is.na(users$topics)] <- 0

# Merge user and tweet data
data <- merge(tweets, users, by.x ="author_id",by.y="id")

# Delete the few tweets which could not have sentiment identified
data<-data[!is.na(data$sentiment$compound),]

# Scale and centre the number of followers and sentiment
F=scale(data$public_metrics.y$followers_count)
S=scale(data$sentiment$compound)

# Set threat level for tweets without threat words
data$threat_level[is.na(data$threat_level)] <- 0

# Change threat variable to factor
data$threat_level<-as.factor(data$threat_level)

# Set delta priot
alphad = rep( 2 , length(unique(data$threat_level))-1 ) 

# Make a list of input data for the model

d<-list(R=data$public_metrics.x$retweet_count,
        N=length(data$public_metrics.x$retweet_count),
        topics=as.integer(data$main_topic.x$topic),
        users=as.integer(data$main_topic.y$topic),
        T=ncol(data$topics.x),
        U=ncol(data$topics.y),
        F=as.numeric(F),
        S=as.numeric(S),
        TL=as.integer(data$threat_level),
        L= length(unique(data$threat_level)),
        alphaD=alphad)
# Run the model
m.ZImultiCert <- stan(file="/home/InfluentialPast/InfluentialPast/stan/ZImultiCert_archaeology_simple.stan", data=d,iter=4000, chains=4,cores=4)


m.ZImultiCertTSFTU_final_correct_archaeology <- stan(file="/home/InfluentialPast/InfluentialPast/stan/ZImultiCertTSFTU.stan", data=d,iter=4000, chains=4,cores=4)

m.ZImultiCertTSFTU_final_archaeology <- stan(file="/home/InfluentialPast/InfluentialPast/stan/ZImultiCertTSFTU.stan", data=d,iter=4000, chains=4,cores=4)


saveRDS(m.ZImultiCertTSFTU,path2model)
saveRDS(m.ZImultiCert_archaeology_simple.stan,path2model)

saveRDS(m.ZImultiCert_final_archaeology.stan,path2model)


#This is the latest!
saveRDS(m.ZImultiCertTSFTU_final_correct_archaeology,path2model)

