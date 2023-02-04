#%%
import requests
import requests.auth
import pyttsx3

class reddit_grabber():
    def __init__(self):
        self.get_auth_token()
        
    def get_auth_token(self):
        CLIENT_AUTH = requests.auth.HTTPBasicAuth('r5CgWuFB6P7XcZoiPZgLGA', 'UpY25X1_lKRqY9I9rJDkb-FCpt1mGw')
        POST_DATA = {"grant_type": "password", "username": "voltomate", "password": "Reddit003465!"}
        HEADERS = {"User-Agent": "CW/0.1 by CW"}
        response = requests.post("https://www.reddit.com/api/v1/access_token", auth=CLIENT_AUTH, data=POST_DATA, headers=HEADERS)
        response.json()
        self.token = response.json()['access_token']

    def get_content_for_subreddit(self, subreddit, filter='hot'):
        HEADERS = {**{"User-Agent": "CW/0.1 by CW"}, **{'Authorization': f"bearer {self.token}"}}
        # while the token is valid (~2 hours) we just add HEADERS=HEADERS to our requests
        requests.get('https://oauth.reddit.com/api/v1/me', headers=HEADERS)
        res = requests.get(f"https://oauth.reddit.com/r/{subreddit}/{filter}",
                        headers=HEADERS)
        self.result = res.json()

    def save_content_as_mp3_file(self,title):
        print("WAT")
        engine = pyttsx3.init()
        voices = engine.getProperty('voices')       #getting details of current voice
        engine.setProperty('voice', voices[1].id)   #changing index, changes voices. 1 for female
        engine.save_to_file(title, 'test2.mp3')
        engine.runAndWait()


reddit_content = reddit_grabber()
print(reddit_content.token)
reddit_content.get_content_for_subreddit('TodayILearned')

reddit_content.save_content_as_mp3_file(reddit_content.result['data']['children'][4]['data']['title'])

# engine = pyttsx3.init()
# speakthis = reddit_content.result['data']['children'][0]['data']['title']
# engine.save_to_file(speakthis, 'test.mp3')
# engine.runAndWait()

#%%
# add authorization to our HEADERS dictionary

engine = pyttsx3.init()
voices = engine.getProperty('voices')       #getting details of current voice
engine.setProperty('voice', voices[1].id)   #changing index, changes voices. 1 for female


for post in res.json()['data']['children']:
    print(post['data']['title'])
    speakthis = post['data']['title']
    engine.say(speakthis)
    engine.save_to_file(speakthis, 'test.mp3')

    engine.runAndWait()
# %%
# %%
#%%
engine = pyttsx3.init()
speakthis = res.json()['data']['children'][0]['data']['title']
engine.say(speakthis)
engine.runAndWait()

# %%
engine.say("test")
engine.runAndWait()

# %%
voices = engine.getProperty('voices')       #getting details of current voice
print(voices)
#engine.setProperty('voice', voices[0].id)  #changing index, changes voices. o for male
engine.setProperty('voice', voices[1].id)   #changing index, changes voices. 1 for female

# %%
