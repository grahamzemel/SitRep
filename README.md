# Situation Report (Sit Rep) Bot by Graham Zemel
Written by Graham Zemel, using Selenium, Python, and Heroku
# NOTE: 
## UPDATE LINES 122-125 IN 'bot.py' IF RUNNING LOCALLY  
### Otherwise, if you're using Heroku, set these config vars:
```
FIREFOX_BIN:
/app/vendor/firefox/firefox
GECKODRIVER_PATH:
/app/vendor/geckodriver/geckodriver
LD_LIBRARY_PATH:
/usr/local/lib:/usr/lib:/lib:/app/vendor/firefox:/app/vendor
PATH:
/usr/local/bin:/usr/bin:/bin:/app/vendor/firefox:/app/vendor/
UPDATER_KEY:  
XXXXXXXXXX:XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX

```

## Here's the .env file with sample data copied and pasted:
```
NEWS_API_KEY=XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
MEDIUMUSER=grahamzemel
GRIDPOINTS=34,32
SPOTIFY_CLIENT_ID=XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
SPOTIFY_CLIENT_SECRET=XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
SPOTIFY_USER_ID=XXXXXXXXXXXXXXXXXXXXXXXXXXXX
SPOTIFY_USER=youremail@gmail.com
SPOTIFY_PASS=Password123
SPOTIFY_DEVICE=Sonos Speaker
```
### Otherwise, hardcode the config vars some way in your `bot.py`.  

### You should know how to create a telegram bot with the BotFather, and run a server instance to host your code using something like Heroku  
## Installation: (Do this in a server environment for best results)

### You will need to install Heroku's buildpack for geckodriver if that's what you decide to use:

```shell
--Create a new app--
$ heroku create --buildpack https://github.com/grahamzemel/heroku_geckodriver_firefox

--If the app is already created--
$ heroku buildpacks:add https://github.com/grahamzemel/heroku_geckodriver_firefox

--Use either the master or main branch depending on your project--
$ git push heroku master
```
## Commands to run on server or locally if you've modified the bot.py code as such:
```
$ cd SitRep  
$ pip3 install -r requirements.txt  
$ python3 bot.py
```
## Filesystem Tree:  
SitRep  
-bot.py  
-requirements.txt  
-Procfile  
-readme.md  

## TO-DO (Future improvements):
Implement volume controls/increasing function (for the song playing stuff in the morning)
