

#before u begin, install twitter_scraper library by opening anaconda prompt or command prompt in admin mode
# type this to install : pip install twitter_scraper

from twitter_scraper import get_tweets, Profile


# words that fetch lot of links in the tweets (for sample usage): checkout, free, immediately


def get_info(word=None):
    master_list = []

    for tweet in get_tweets(word, pages=1):
        
        link = tweet['entries']['urls']
        
        if len(link) != 0:
            
            
            profile_details_list = []
            
            profile_details_list.append(tweet['username'])
            
            username = tweet['username']
            
            profile_link = 'twitter.com/' + username
            
            profile_details_list.append(profile_link)
            
            tweet_link = 'twitter.com' + tweet['tweetUrl']
            
            profile_details_list.append(tweet_link)
            
            profile = Profile(username)
                
            profile_details_list.append(profile.location)
            
            profile_details_list.append(profile.name)  
            
            profile_details_list.append(link[0])

            master_list.append(profile_details_list)
            

    #print('---The entire list of profiles is ----')

    #print(master_list)


    # master list has mulitple lists. Each list has [@username, profileLink, link of the tweet, location of the user, Profile display Name, link the user has posted]

    
    return master_list
    
    #for each_value in master_list:
        
        #entry = each_value[-1]
        
        #print(entry)
        #pass the entry value to the model
        
        # if the output is malicious, then insert values in each_value list into a table (separate table for this)
        # if output is not malicious, validate for the next entry     

        
    #each row in the new table should have username, his profile link, his location and link that he posted
    # and should be available to public users as well as cyber security officials in the form of a table in UI
        
    
    
    
#print(get_info(word="#covid"))



