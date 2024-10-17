##### Data collection - tweets with keywords #####
# This file containt the code used for the extraction of tweets from the Twitter Archive with the Academic Access API

#### Load required library
library(here)
library(academictwitteR) # To get all tweets from the archive
library(data.table) # For rbindlist - to get the binded tweets for reference ids

#### Set Bearer Token as an environmental variable according to instructions in:
#https://github.com/cjbarrie/academictwitteR#authorization

##### Extract tweets from Twitter Archive #####

#### Get tweets with the specific keywords:

## Search for tweets from January2023 to get the sample of data and test the code:

# Define the search query:
search_query <- c("stonehenge","\"hadrian's wall\"","\"hadrians wall\"","\"sutton hoo\"","#archaeology","\"antonine wall\"")

# Set the output directory:
outputs_path <- here("data","January2023")

# Get all tweets with the define keywords for January 2023
tweets <-
  get_all_tweets(
    query = search_query,
    start_tweets = "2023-01-01T00:00:00Z",
    end_tweets = "2023-02-01T00:00:00Z",
    data_path = outputs_path,
    n = Inf,            # allow infinite tweets
    bind_tweets = FALSE, #bind them late,
    export_query = TRUE
  )

## Set up extraction for the past 2 years:

# Define years and months to iterate over
years<-c("2022","2021")
years<-c("2020")
months<-c("January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December")

# Loop through years and months and extract tweets
for(year in years){
    for(month in rev(months)){
        if(which(months==month)==12){
            y<-as.numeric(year)+1
            m<-1
                  }else{ 
        y<-year
        m<-which(months==month)+1
        }
        
        outputs_path<-here("data","archive_search",paste(month,year,sep=""))
        start_date<-paste(year,"-",which(months==month),"-","01T00:00:00Z",sep="")
        end_date<-paste(y,"-",m,"-","01T00:00:00Z",sep="")
        print(outputs_path)
        print(start_date) 
        print(end_date)
        tweets <-
            get_all_tweets(
            query = search_query,
            start_tweets = start_date,
            end_tweets = end_date,
            data_path = outputs_path,
            n = Inf,            # allow infinite tweets
            bind_tweets = FALSE, #bind them late,
            export_query = TRUE
  )
    }
}