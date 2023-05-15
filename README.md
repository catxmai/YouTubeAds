# YouTubeAdStudy

Collecting video and ads on YouTube through Selenium. 

### Setup

Have Python. Run in cmd or git bash `pip install -r requirements.txt`

Download a driver for chrome found here https://chromedriver.chromium.org/downloads. Make sure the driver matches your chrome version (check in Chrome Settings)
Put `chromedriver.exe` in the same folder where `create_driver()` is (currently in `utils.py`, so main folder for this repo)

(Optional)
To browse with an account, create a file called `config.json`. Example file: `config_example.json`
If using a Google account, change the username and password in `config.json` to your google acount. To setup the driver to launch using your account:
1. Open chrome
2. Log in to the account
3. Fully exit chrome
4. Copy the "User Data" folder found in your computer's chrome directory (For Windows, `C:\Users\username\AppData\Local\Google\Chrome\User Data`), and paste it into the main folder for this repo 
5. Change the 'user_data' entry in the config file to the copied directory (works best if you delete the spaces from the "User Data")

### Running 

Change variables in `main.py` to reflect current setup. Most of the info collection is done in `get_video_info()` in `get_video_info.py`. Outputs of the program are written in `.json` format with multiple dicts per file, each dict represents a video. Truncated example of an output file:

```
{
    "video_id": "xR57WHDLSFo",
    "video_title": "Season 7 ep 18",
    "video_url": "https://www.youtube.com/watch?v=xR57WHDLSFo",
    "channel_name": "Chec_ Boss",
    "channel_id": "-1",
    "video_genre": "Comedy",
    "video_description": "Comedy , funny , series",
    "date_uploaded": "2021-07-12",
    "id": 0
}
{
    "video_id": "y1-zGegHjVc",
    "video_title": "i HATE DanTDM!",
    "video_url": "https://www.youtube.com/watch?v=y1-zGegHjVc",
    "channel_name": "DanTDM",
    "channel_id": "-1",
    "video_genre": "Entertainment",
    "video_description": "today, i'm seeing who out there hates dantdm..\n\n\u25ba Subscribe and join TeamTDM! :: http://bit.ly/TxtGm8\n\u25ba Follow Me on Twitter :: http://www.twitter.com/dantdm\n\u25ba Previous Video :: https://youtu.be/sMvBMx486pU\n\n\u25ba DanTDM MERCH :: http://www.dantdmshop.com\n\n\u25ba Powered by Chillblast :: http://www.chillblast.com\n\n#DanTDM",
    "date_uploaded": "2019-01-20",
    "id": 1
}
```

