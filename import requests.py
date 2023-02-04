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
        self.title = title        
        engine = pyttsx3.init()
        voices = engine.getProperty('voices')       #getting details of current voice
        engine.setProperty('voice', voices[1].id)   #changing index, changes voices. 1 for female
        engine.save_to_file(title, 'test2.mp3')
        engine.runAndWait()


reddit_content = reddit_grabber()
print(reddit_content.token)
reddit_content.get_content_for_subreddit('TodayILearned')

reddit_content.save_content_as_mp3_file(reddit_content.result['data']['children'][12]['data']['title'])

#%%

regex_pattern = r"[,.]"
import re
print(re.split(regex_pattern, reddit_content.title)[0])
















#%%
import numpy as np
from moviepy.editor import *
from moviepy.video.tools.segmenting import findObjects

# WE CREATE THE TEXT THAT IS GOING TO MOVE, WE CENTER IT.

screensize = (720,460)
txtClip = TextClip('Cool effect',color='white', font="Amiri-Bold",
                   kerning = 5, fontsize=100)
cvc = CompositeVideoClip( [txtClip.set_pos('center')],
                        size=screensize)

# THE NEXT FOUR FUNCTIONS DEFINE FOUR WAYS OF MOVING THE LETTERS


# helper function
rotMatrix = lambda a: np.array( [[np.cos(a),np.sin(a)], 
                                 [-np.sin(a),np.cos(a)]] )

def vortex(screenpos,i,nletters):
    d = lambda t : 1.0/(0.3+t**8) #damping
    a = i*np.pi/ nletters # angle of the movement
    v = rotMatrix(a).dot([-1,0])
    if i%2 : v[1] = -v[1]
    return lambda t: screenpos+400*d(t)*rotMatrix(0.5*d(t)*a).dot(v)
    
def cascade(screenpos,i,nletters):
    v = np.array([0,-1])
    d = lambda t : 1 if t<0 else abs(np.sinc(t)/(1+t**4))
    return lambda t: screenpos+v*400*d(t-0.15*i)

def arrive(screenpos,i,nletters):
    v = np.array([-1,0])
    d = lambda t : max(0, 3-3*t)
    return lambda t: screenpos-400*v*d(t-0.2*i)
    
def vortexout(screenpos,i,nletters):
    d = lambda t : max(0,t) #damping
    a = i*np.pi/ nletters # angle of the movement
    v = rotMatrix(a).dot([-1,0])
    if i%2 : v[1] = -v[1]
    return lambda t: screenpos+400*d(t-0.1*i)*rotMatrix(-0.2*d(t)*a).dot(v)



# WE USE THE PLUGIN findObjects TO LOCATE AND SEPARATE EACH LETTER

letters = findObjects(cvc) # a list of ImageClips


# WE ANIMATE THE LETTERS

def moveLetters(letters, funcpos):
    return [ letter.set_pos(funcpos(letter.screenpos,i,len(letters)))
              for i,letter in enumerate(letters)]

clips = [ CompositeVideoClip( moveLetters(letters,funcpos),
                              size = screensize).subclip(0,5)
          for funcpos in [vortex, cascade, arrive, vortexout] ]

# WE CONCATENATE EVERYTHING AND WRITE TO A FILE

final_clip = concatenate_videoclips(clips)
final_clip.write_videofile('coolTextEffects.avi',fps=25,codec='mpeg4')

# %%
from gtts import gTTS
tts = gTTS('Sweden has the highest rate of automatically created speech texts.')
tts.save('hello.mp3')
#%%
# %%
import urllib
import openai
import time
#openai.api_key = "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"
openai.api_key = "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"

openai.organization = "org-9kOJ7yh966xJKuo7UXKVfVzn"
openai.Model.list()

title = "Monet style picture of success"

response = openai.Image.create(
  prompt=title,
  n=1,
  size="1024x1024"
)
image_url = response['data'][0]['url']

urllib.request.urlretrieve(image_url, str(time.strftime("%Y%m%d_%H%M%S"))+".png")


# %%

from moviepy.editor import *
from moviepy.config import change_settings
import time 
change_settings({"IMAGEMAGICK_BINARY": r"C:\\Program Files\\ImageMagick-7.1.0-Q16-HDRI\\magick.exe"})

# Load the audio file using moviepy
print("Extract voiceover and get duration...")
audio_clip = AudioFileClip(f"test2.mp3")
audio_duration = audio_clip.duration

# Load the image file using moviepy
print("Extract Image Clip and Set Duration...")


image_clip = ImageClip("20230204_234716.png").set_duration(audio_duration)


# Use moviepy to create a text clip from the text
print("Customize The Text Clip...")
text_clip = TextClip("yeet", fontsize=50, color="white")
print("here")

text_clip = text_clip.set_pos('center').set_duration(audio_duration)
# Use moviepy to create a final video by concatenating
# the audio, image, and text clips
print("Concatenate Audio, Image, Text to Create Final Clip...")
clip = image_clip.set_audio(audio_clip)
print(clip)
print(text_clip)

video = CompositeVideoClip([clip, text_clip])
# video = CompositeVideoClip([clip, text_clip.set_pos(('center', 'bottom'))])
#final_clip = concatenate_videoclips([clip,clip], method="compose")


# Save the final video to a file
video = video.write_videofile(str(time.strftime("%Y%m%d_%H%M%S"))+"vid.mp4", fps=24)
print(f"The Video Has Been Created Successfully!")

#%%
# from PIL import Image
# formatter = {"PNG": "RGBA", "JPEG": "RGB"}
# img = Image.open("20230204_172158.png")
# rgbimg = Image.new(formatter.get(img.format, 'RGB'), img.size)
# rgbimg.paste(img)
# rgbimg.save("20230204_172158_edited.png", format=img.format)
