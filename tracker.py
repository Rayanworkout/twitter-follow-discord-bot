import json
import time

import requests
import tweepy
from discord_webhook import DiscordEmbed, DiscordWebhook
from datetime import datetime

###################################################################################################

webhook = DiscordWebhook(
    url='https://discord.com/api/webhooks/1037438920050360351/'
        '3vbCVu0RZfa4KjPm9G2xpC8v-eDzF5LBdvQ65g-rPJ-pNkB4rPEzuUAlElj4dvu_t_lD',
    username='Twitter following'
)

client = tweepy.Client(bearer_token="AAAAAAAAAAAAAAAAAAAAADhdUQEAAAAAaMGUYLBUc9APzkNTXIGNCPpDyF4%3DSFWrzBewEaWgRqDssuvfsQsKjpPMx1zR55QJSWratpDSejEb2T")

auth = tweepy.OAuthHandler('qi0FcmJWMv1T6x8WYhvD6M8d3', 'HI9gHHJNiTXwBWuJlsXzFUDjOhe2t7gBHXbptCNE1L9JvzhFU6')
api = tweepy.API(auth, wait_on_rate_limit=True)

number_following_per_request = 50
number_following_stored = 100

#######################################################################################################

def get_time():
    return datetime.now().strftime('%D %H:%M:%S')

def compare():  
    while True:
        with open('db.json', 'r') as f:
            db = json.load(f)

        try:
            for tracked_account in db.keys():
                lastFollowings = client.get_users_following(id=tracked_account, max_results=number_following_per_request)
                newly_following_users = lastFollowings.data
                
                old_follow_list = db[tracked_account]["follows"]

                differences = [value for value in newly_following_users if value.id not in old_follow_list]
            
                if differences:
                    del db[tracked_account]["follows"][len(old_follow_list) - len(differences):]
                    db[tracked_account]["follows"] = [value.id for value in differences] + db[tracked_account]["follows"]

                    for user in differences:
                        
                        twitter_user = api.get_user(user_id=user.id)
                        
                        if int(twitter_user.followers_count) < 2000:
                        
                            username = twitter_user.screen_name
                            followers_count = twitter_user.followers_count
                            friends_count = twitter_user.friends_count
                            bio = twitter_user.description
                            profile_picture = twitter_user.profile_image_url_https
                            created_at = twitter_user.created_at
                            
                            if twitter_user.url:
                                try:
                                    profile_bio_url = requests.get(f"https://unshort.herokuapp.com/api/?url={twitter_user.url}").json()["longUrl"]
                                except Exception:
                                    profile_bio_url = "None"
                            else:
                                profile_bio_url = "None"
                            
                            tag = db[tracked_account]['Tag'].upper()
                            
                            if tag == "ALPHA":
                                color = "e81224"
                            elif tag == "CONTRIBUTOR":
                                color = "f7630c"
                            elif tag == "OG":
                                color = "fff100"
                            elif tag == "SHITCOIN":
                                color = "16c60c"
                            elif tag == "DEFI":
                                color = "0078d7"
                            elif tag == "NFT":
                                color = "886ce4"
                            elif tag == "VC":
                                color = "ffffff"
                            else:
                                color = '000000'
                            
                            description = (f"\n:blue_circle:  **Followers:** {followers_count}\n\n:orange_circle:  **Following:**" 
                                        f" {friends_count}\n\n**Bio:** {bio}\n\n:link:  **Link in Bio**\n{profile_bio_url}\n\n"
                                        f":hourglass_flowing_sand: **Profile Creation Date**\n{created_at.strftime('%d/%m/%Y')}")
                            
                            embed = DiscordEmbed(title=username, description=description,
                                                url=f'https://twitter.com/{username}', color=color)
                            
                            embed.set_author(name=f"New Follow for {db[tracked_account]['username']}  [{db[tracked_account]['Tag'].upper()}]",
                                            icon_url=db[tracked_account]['profile_picture'], url=f"https://twitter.com/{username}")    
                            
                            embed.set_thumbnail(url=profile_picture)
                                
                            embed.set_timestamp()
                            
                            webhook.add_embed(embed)

                            with open('db.json', 'w') as f:
                                json.dump(db, f, indent=4)
                                
                            print(f"[{get_time()}] New follow for {db[tracked_account]['username']}: "
                                  f"{'/'.join([user.name for user in differences])}")
                    
                    webhook.execute()
                    webhook.remove_embeds()
                                
                else:
                    print(f"[{get_time()}] No new follow for {db[tracked_account]['username']}")
                    
                    time.sleep(400)
        except Exception as e:
            requests.get("https://api.telegram.org/bot1768068100:AAHVGEdeItHypLHBfqmMoqdqhX4KdgO08Gc/"
                    "sendMessage?chat_id=901170303&text={}".format("Error with Twitter Tracker: " + str(e)))
            
            time.sleep(900)


if '__main__' == __name__:
    compare()