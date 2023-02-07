#%%

"""Getting Started Example for Python 2.7+/3.3+"""
from boto3 import Session
from botocore.exceptions import BotoCoreError, ClientError
from contextlib import closing
import os
import sys
import subprocess
from tempfile import gettempdir

# Create a client using the credentials and region defined in the [adminuser]
# section of the AWS credentials file (~/.aws/credentials).
session = Session(profile_name="adminuser", 
        aws_access_key_id="ASIATDSFMB7QXCCUHRVN",
        aws_secret_access_key="6Jo2XkhAI5TMV64dQvl7I08m6hErtaNQ2LekaGoQ",
        aws_session_token="IQoJb3JpZ2luX2VjEN///////////wEaCXVzLWVhc3QtMSJIMEYCIQDsO5WXe93pH/5STJhRFp/GDQRo5PCSEmcvXRlgEuGQ6QIhAOrdfTAa1lu5LN9Pygk+ZLWLeAfdPcKob94/wcluEd5UKu8CCGgQABoMMjEzODIwMTE2OTYxIgz4GIvOF5EVuF4a6vkqzAJCVd0lgSGRLH8bhQtsq8ed4G3OVqEaum/udTHd7N9VylMAzFWyaHAeO2dzlZUENg9MjWbol6ieBj/c0eSJk2wlceRDg2oy4YTEzReDDDVqQ/TF5AvqfMd2hVBcuddLjCkkVw/YSXckEx6eIOUJ0H1nXrlb9WRIbc9zzNB4melrcdbjNBrr7iBenSKFkVZJxUeEpRvO41YcrlArJpzd9mWQLH9bZvtvWcbAgU/8/rHeckSMUUpQAKzB5ZAirQhWqFi37h2fyFRWXCmNJMPaZ4aqVPgs+WHkidq+pSG23kbmnNbnO/ywLi5DX8W989WxKi7fN3TNEg+8NaNTQzbtID2AHT+h9393pLs1rdv9KQJQB+zEk1VH04bLQHvithr+uw/F+ZRi6I4brIQllj2raE8gJAZUmajOy9pgr3Nyci9wkcUgYazDCrJNQoc41DC1oYufBjqmAdxgKaLUgB3D+cDbY4uCydiQkn/3aMBkwFyDS1aABgqvTI1Lh//0IoCr06rSBAdh44HgeEaaM+7zr0Z4i43sCBn6GLlnTb9OhhnzzJopqZy23n/W+fZEFpsYtZVXdzKMDL7PsfhRK3uZihaR+xAl7UdTu1wVKbqbDWx/Hji0+f5tC1+FU6klPAIYXtHrLxvbRAZDb2ww2TwYBReR1FKN4k8Lwm/kNGk=",
        region_name="eu-central-1"
)
polly = session.client("polly")
try:
    # Request speech synthesis
    prompt = "Today I learned Armadillos got their name from the Aztec word meaning turtle-rabbit"
    response = polly.synthesize_speech(Text=prompt, OutputFormat="mp3",
                                        VoiceId="Arthur", Engine="neural")
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
           output = os.path.join("speech.mp3")

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

# Play the audio using the platform's default player
if sys.platform == "win32":
    os.startfile(output)
else:
    # The following works on macOS and Linux. (Darwin = mac, xdg-open = linux).
    opener = "open" if sys.platform == "darwin" else "xdg-open"
    subprocess.call([opener, output])

# %%
