#%%
import requests
import requests.auth
import pyttsx3
import urllib
import openai
import time
import re
from moviepy.editor import *
from moviepy.config import change_settings
import time 
from PIL import Image
from boto3 import Session
from botocore.exceptions import BotoCoreError, ClientError
from contextlib import closing
import os
import sys
import subprocess
from tempfile import gettempdir

change_settings({"IMAGEMAGICK_BINARY": r"C:\\Program Files\\ImageMagick-7.1.0-Q16-HDRI\\magick.exe"})

def get_file_contents(filename):
    """ Given a filename,
        return the contents of that file
    """
    try:
        with open(filename, 'r') as f:
            # It's assumed our file contains a single line,
            # with our API key
            return f.read().strip()
    except FileNotFoundError:
        print("'%s' file not found" % filename)

class reddit_grabber():
    def __init__(self):
        self.get_auth_token()
        self.linked_media_url = None
        self.time_id = str(time.strftime("%Y%m%d_%H%M%S"))
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

    def save_polly_mp3_file(self,spoken_text,video_part):

        if video_part == "intro":
            self.mp3_intro_name = self.time_id+"_"+video_part+".mp3"
        if video_part == "main":
            self.mp3_main_name = self.time_id+"_"+video_part+".mp3"
        if video_part == "outro":
            self.mp3_outro_name = self.time_id+"_"+video_part+".mp3"

        session = Session(profile_name="default")
        polly = session.client("polly")

        try:
            response = polly.synthesize_speech(Text=spoken_text, OutputFormat="mp3",
                                                VoiceId="Joey")
        except (BotoCoreError, ClientError) as error:
            # The service returned an error, exit gracefully
            print(error)
            sys.exit(-1)

        # Access the audio stream from the response
        if "AudioStream" in response:
            # Note: Closing the stream is important because the service throttles on the
            # number of parallel connections. Here we are using contextlib.closing to
            # ensure the close method of the stream object will be called automatically
            # at the end of the with statement's scope.
            with closing(response["AudioStream"]) as stream:
                output = os.path.join(self.time_id+"_"+video_part+".mp3")

                try:
                    # Open a file for writing the output as a binary stream
                    with open(output, "wb") as file:
                        file.write(stream.read())
                except IOError as error:
                    # Could not write to file, exit gracefully
                    print(error)
                    sys.exit(-1)

        else:
            # The response didn't contain audio data, exit gracefully
            print("Could not stream audio")
            sys.exit(-1)

    def save_content_as_pyttsx3_mp3_file(self,title):

        self.title = title 
        self.title = self.title.replace("TIL", "Today I learned")

        print(self.title)       

        engine = pyttsx3.init()
        engine.setProperty("rate", 160)

        voices = engine.getProperty('voices')       #getting details of current voice
        engine.setProperty('voice', voices[1].id)   #changing index, changes voices. 1 for female
        self.mp3name = str(time.strftime("%Y%m%d_%H%M%S"))+".mp3"
        engine.save_to_file(self.title, self.mp3name)
        engine.runAndWait()

    def get_image_from_dalle(self):

        openai.api_key = "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"
        openai.organization = "org-9kOJ7yh966xJKuo7UXKVfVzn"

        openai.api_key = get_file_contents(r"C:\Users\Chris\Documents\credentials\oai_api_key.txt")
        openai.organization = get_file_contents(r"C:\Users\Chris\Documents\credentials\oai_api_org.txt")

        openai.Model.list()

        regex_pattern = r"[,.]"
        self.prompt_title_part= re.split(regex_pattern, self.title)[0]

        try:
            if len(self.prompt_title_part) < 30:
                self.prompt_title_part = self.title[0:40]
        except:
            pass

        print('requested for: '+str(self.prompt_title_part))

        response = openai.Image.create(
        prompt=self.prompt_title_part,
        n=1,
        size="1024x1024"
        )
        image_url = response['data'][0]['url']
        self.image_name = str(time.strftime("%Y%m%d_%H%M%S"))+".png"
        urllib.request.urlretrieve(image_url, self.image_name)

    def create_intro(self):
        # Load the audio file using moviepy
        print("Extract voiceover and get duration...")
        duration = 2

        img = Image.open(self.image_name)
        img_cropped = img.crop((224, 0, 800, 1024))
        self.image_name_cropped = self.image_name+"cropped.png"
        img_cropped.save(self.image_name_cropped, format=img.format)

        audio_clip = AudioFileClip(self.mp3_intro_name)

        print("Extract Image Clip and Set Duration...")
        image_clip = ImageClip(self.image_name_cropped).set_duration(duration)
        screensize = (576,800)

        credits = (TextClip("Did you know?", color='red',stroke_color= 'white',
                            stroke_width = 12,
                font="Berlin-Sans-FB-Bold", kerning=-2, interline=-1, size = 
        screensize, method='caption')
            .set_duration(duration)
            .set_start(0)
            )
        clip = image_clip.set_audio(audio_clip)

        video = CompositeVideoClip([clip, credits])

        self.intro_name = self.time_id+"_intro.mp4"
        video = video.write_videofile(self.intro_name, fps=24)
        print(f"The Video Has Been Created Successfully!")

    def create_video(self):
        # Load the audio file using moviepy
        print("Extract voiceover and get duration...")
        audio_clip = AudioFileClip(self.mp3_main_name)
        audio_duration = audio_clip.duration


        img = Image.open(self.image_name)
        img_cropped = img.crop((224, 0, 800, 1024))
        self.image_name_cropped = self.image_name+"cropped.png"
        img_cropped.save(self.image_name_cropped, format=img.format)

        # Load the image file using moviepy
        print("Extract Image Clip and Set Duration...")
        image_clip = ImageClip(self.image_name_cropped).set_duration(audio_duration)

        # # Use moviepy to create a text clip from the text
        # print("Customize The Text Clip...")
        # text_clip = TextClip("TIL Bats and dolphins evolved echolocation in the same way (down to the molecular level). An analysis revealed that 200 genes had independently changed in the same way", fontsize=50, color="white")
        # print("here")

        #text_clip = text_clip.set_pos('center').set_duration(audio_duration)
        # Use moviepy to create a final video by concatenating
        # the audio, image, and text clips
        print("Concatenate Audio, Image, Text to Create Final Clip...")
        clip = image_clip.set_audio(audio_clip)

        screensize = (576,900)

        credits = (TextClip(self.title, color='white',stroke_color= 'black',
                font="Berlin-Sans-FB-Bold", kerning=-2, interline=-1, size = 
        screensize, method='caption')
            .set_duration(audio_duration)
            .set_start(0)
            )


        video = CompositeVideoClip([clip, credits])
        # video = CompositeVideoClip([clip, text_clip.set_pos(('center', 'bottom'))])
        # Save the final video to a file
        self.main_name = self.time_id+"_main.mp4"
        video = video.write_videofile(self.main_name, fps=24)
        print(f"The Video Has Been Created Successfully!")

    def merge_video(self):
        intro = VideoFileClip(self.intro_name)
        main = VideoFileClip(self.intro_name)
        final = concatenate_videoclips([intro, main])
        self.video_name = self.time_id+"_video.mp4"

        final = final.write_videofile(self.video_name, fps=24)

        with open(self.video_name+'.txt', 'w') as f:
            f.write(reddit_content.linked_media_url+'\n'+reddit_content.title)     


#%%
reddit_content = reddit_grabber()
reddit_content.get_content_for_subreddit('TodayILearned')

k = 0

title = reddit_content.result['data']['children'][k]['data']['title']
reddit_content.title = title 
reddit_content.title = reddit_content.title.replace("TIL", "Today I learned")

reddit_content.save_polly_mp3_file("Did you know?","intro")
reddit_content.save_polly_mp3_file(reddit_content.title,"main")

# reddit_content.get_image_from_dalle()
reddit_content.image_name = '20230206_222456.png'

reddit_content.linked_media_url = reddit_content.result['data']['children'][k]['data']['url_overridden_by_dest']

reddit_content.create_intro()
reddit_content.create_video()
reddit_content.merge_video()



#%%
#
#
reddit_content = reddit_grabber()
print(reddit_content.token)
reddit_content.get_content_for_subreddit('TodayILearned')

for i in range(len(reddit_content.result['data']['children'])):
    print(i)
    print(reddit_content.result['data']['children'][i]['data']['title'])
    #%%

    
reddit_content = reddit_grabber()
print(reddit_content.token)
reddit_content.get_content_for_subreddit('TodayILearned')

k = 0

# reddit_content.save_content_as_polly_mp3_file(reddit_content.result['data']['children'][k]['data']['title'])
# reddit_content.save_content_as_polly_mp3_file("Today I learned about the London bus driver Albert Gunter. He found his bus on the London Bridge just when it was opening for a ship. He slammed the gas and jumped the gap! For this, he was given a bonus of £10 (about £290 in today’s money).")
# reddit_content.linked_media_url = reddit_content.result['data']['children'][k]['data']['url_overridden_by_dest']

# reddit_content.get_image_from_dalle()
reddit_content.image_name = '20230206_222456.png'
reddit_content.create_intro()
#%%
k = 7
reddit_content.save_content_as_mp3_file(reddit_content.result['data']['children'][k]['data']['title'])
reddit_content.linked_media_url = reddit_content.result['data']['children'][k]['data']['url_overridden_by_dest'])

reddit_content.get_image_from_dalle()
#reddit_content.image_name = '20230205_010857.png'

reddit_content.create_video()

print(reddit_content.video_name)




#%%
reddit_content = reddit_grabber()
reddit_content.title = "dali style: wooden penguin statue on a wooden rectangle base in an office"
reddit_content.get_image_from_dalle()



# reddit_content.save_content_as_mp3_file("This is a test. Let's see how fast you talk now")


#%%

CLIENT_AUTH = requests.auth.HTTPBasicAuth('r5CgWuFB6P7XcZoiPZgLGA', 'UpY25X1_lKRqY9I9rJDkb-FCpt1mGw')
POST_DATA = {"grant_type": "password", "username": "voltomate", "password": "Reddit003465!"}
HEADERS = {"User-Agent": "CW/0.1 by CW"}
response = requests.post("https://www.reddit.com/api/v1/access_token", auth=CLIENT_AUTH, data=POST_DATA, headers=HEADERS)
response.json()
token = response.json()['access_token']

HEADERS = {**{"User-Agent": "CW/0.1 by CW"}, **{'Authorization': f"bearer {token}"}}
# while the token is valid (~2 hours) we just add HEADERS=HEADERS to our requests
requests.get('https://oauth.reddit.com/api/v1/me', headers=HEADERS)
res = requests.get(f"https://oauth.reddit.com/r/TodayILearned/top",
                headers=HEADERS)
result = res.json()
#%%

print(result['data']['children'][13])
print(result['data']['children'][13]['data']['url_overridden_by_dest'])













#%%
# %%



# %%




#%%
# from PIL import Image
# formatter = {"PNG": "RGBA", "JPEG": "RGB"}
# img = Image.open("20230204_172158.png")
# rgbimg = Image.new(formatter.get(img.format, 'RGB'), img.size)
# rgbimg.paste(img)
# rgbimg.save("20230204_172158_edited.png", format=img.format)



filename = "20230204_235944"
img = Image.open(filename+".png")
img_cropped = img.crop((224, 0, 800, 1024))
img_cropped.save(filename+"cropped.png", format=img.format)
img_cropped.show()

# %%
from moviepy.editor import TextClip
print ( TextClip.list("font") )

# %%
from gtts import gTTS
import playsound

para = "yo buddy"
tts = gTTS(text=para, lang='de', slow=False)
filename = "abc2.mp3"
tts.save(filename)
playsound.playsound(filename)




#%%
"""
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
"""