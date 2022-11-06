# Written by Graham Zemel, 2022

import json
import os
import threading
import time
from http import client
from sqlite3 import Date
from urllib import response
from urllib.parse import quote
from wsgiref import headers
from wsgiref.util import request_uri

import requests
import spotipy
from dotenv import load_dotenv
from flask import request
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support.select import Select
from spotipy.oauth2 import SpotifyOAuth
from telegram import MessageEntity, ParseMode, ReplyMarkup
from telegram.ext import CommandHandler, Filters, MessageHandler, Updater

load_dotenv(".env")
UPDATER_KEY = os.getenv("UPDATER_KEY")
NEWS_API_KEY = os.getenv("NEWS_API_KEY")
MEDIUMUSER = os.getenv("MEDIUMUSER")
GRIDPOINTS = os.getenv("GRIDPOINTS")
SPOTIFY_CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
SPOTIFY_CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")
SPOTIFY_USER_ID = os.getenv("SPOTIFY_USER_ID")
SPOTIFY_USER = os.getenv("SPOTIFY_USER")
SPOTIFY_PASS = os.getenv("SPOTIFY_PASS")
SPOTIFY_DEVICE = os.getenv("SPOTIFY_DEVICE")
# Error handling
def error(update, context):
    # print(f'Update {update} caused error {context.error}')
    update.message.reply_text("Error: " + str(context.error))

# Helper functions
def need_help(bot, update):
    bot.message.reply_text('--Help!--')
    bot.message.reply_text('Use /start to start the bot. \n')
    bot.message.reply_text('Use /stop to stop the bot (in development). \n')
    bot.message.reply_text('Use /force run the bot at any time. \n')
    bot.message.reply_text('---------')

# Automatic starting functions
def start_bot(bot, update):
    bot.message.reply_text("Hey " + bot.message.chat.first_name +
                           "! My name's SitRepBot (Situation Report Robot). \n")
    bot.message.reply_text('----BOT STARTED----')
    bot.message.reply_text('Use /status to see the status of the bot. \n')
    bot.message.reply_text('Use /force run the bot at any time. \n')
    bot.message.reply_text('Use /help to see all commands. \n')
    bot.message.reply_text('--------')
    # Creates thread to run waiting function while command listener is running for things like force and stop
    global waitThread
    waitThread = threading.Thread(target=waitTest, args=(bot, update))
    waitThread.name = "waitThread"
    waitThread.daemon = True
    waitThread.start()

# Work in progress for the stop function (not working)
def stop_bot(bot, update):
    bot.message.reply_text("Stopping bot...")
    waitThread.join()
    bot.message.reply_text("Bot stopped!")

# Get the status of the bot and the time until the next run
def status(bot, update):
    # Checks if the thread for the waitTest function is running
    if (waitThread.is_alive()):
        clockTime = time.localtime()
        bot.message.reply_text("Bot is running!")
        bot.message.reply_text("Time until 7am: " + str(31-clockTime.tm_hour) + ":" + str(60-clockTime.tm_min) + " (hh:mm)")
    else:
        bot.message.reply_text("Bot is not running, start it using '/start'.")

# /Force command that will run the bot at any time
def force_bot(bot, update):
    bot.message.reply_text("Overriding bot timing... \n")
    sitRep(bot, update)

# Function to wait until 7am to run the bot
def waitTest(bot, update):
    # Gets the current time at time of function run
    clockTime = time.localtime()
    if (clockTime.tm_hour == 7 and clockTime.tm_min == 00):
        isSeven = True
    else:
        isSeven = False
    firstRun = True
    # As long as isSeven is false, the bot will wait until 7am
    while not isSeven:
        clockTime = time.localtime()
        # If it's past midnight, the bot will run the 'until' 7:00am code
        if (clockTime.tm_hour < 7):
            if (firstRun):
                bot.message.reply_text("It's not 7:00am yet!")
                bot.message.reply_text(
                    "Time until 7:00am: " + str(31-clockTime.tm_hour) + ":" + str(60-clockTime.tm_min) + " (hh:mm)")
                firstRun = False
        # If it's after 7am, the bot will run the 'after' 7:00am code
        else:
            if (firstRun):
                bot.message.reply_text("It's past 7:00am!")
                bot.message.reply_text("Time since 7:00am: " + str(
                    abs(7 - clockTime.tm_hour)) + ":" + str(abs(clockTime.tm_min)) + " (hh:mm)")
                firstRun = False
        # Sleeps for 1 minute, then checks the time again and makes sure the bot only runs once each automated 7:00am loop
        time.sleep(60)
        if (clockTime.tm_hour == 7 and clockTime.tm_min == 00 and not isSeven):
            isSeven = True
        else:
            isSeven = False
    if (isSeven):
        sitRep(bot, update)

# Main function that runs the bot upon either forcing or waiting until 7am
def sitRep(bot, update):
    # Makes browser not open but run the graphics in the background as it is headless
    options = Options()
    options.add_argument('--headless')

    # #UNCOMMENT IN PRODUCTION (HEROKU RELEASE)
    #
    driver = webdriver.Firefox(firefox_binary=os.environ['FIREFOX_BIN'],
                               executable_path=os.environ['GECKODRIVER_PATH'],
                               options=options)
    
    # UNCOMMENT IN DEVELOPMENT MODE, LOCAL RUN
    #
    # driver = webdriver.Firefox(options=options)
    
    
    today = Date.today()
    bot.message.reply_text("------SITREP FOR " + str(today.month) +
                           "/" + str(today.day) + "/" + str(today.year) + "-------\n")

    # Medium followers via selenium automation
    #
    try:
        driver.get("https://{}.medium.com/followers".format(MEDIUMUSER))
        bot.message.reply_text("Current Medium follower count: " + driver.find_element(
            By.XPATH, '//*[@id="root"]/div/div[3]/div[1]/div[3]/div/div/h2').text + "\n")
    except NoSuchElementException:
        bot.message.reply_text("Medium follow count not found")
        return

    driver.quit()

    # Weather API
    #
    try:
        response = requests.get("https://api.weather.gov/gridpoints/OKX/{}/forecast".format(GRIDPOINTS))
        weatherResponse = response.json()
        bot.message.reply_text(
            "Today's weather: " + weatherResponse['properties']['periods'][0]['detailedForecast'] + "\n")
    except:
        bot.message.reply_text("Weather not found")
        return

    # Spotify API w/ OAUTH2 using spotipy
    #
    bot.message.reply_text("--------\n")
    # Bit of a mess, requires a specific kind of OAUTH2 token instead of regular client credentials in order to access /me endpoints. 
    # This is due to the fact that the Spotify API is not a public API, and requires a user to be logged in to access their own data.
    scope = "user-read-playback-state user-modify-playback-state user-library-read"
    sp = spotipy.oauth2.SpotifyOAuth(
        # Make sure to configure your localhost redirect URI here in your spotify developer app to the exact same string in the next line
        client_id=SPOTIFY_CLIENT_ID, client_secret=SPOTIFY_CLIENT_SECRET, redirect_uri="http://localhost:8080", scope=scope)
    auth_code = sp.get_access_token(as_dict=False)
    # IF the token is obtained through automation if you've inputted the correct plaintext username and password in the config.ini file, this will work
    try:
        # Grab your top 3 playlists
        playlistResp = requests.get("https://api.spotify.com/v1/users/" + os.environ['SPOTIFY_USER_ID'] + "/playlists?offset=0&limit=3", headers={'Authorization': 'Bearer {token}'.format(token=auth_code)})
        spotifyResponse = playlistResp.json()
        bot.message.reply_text("Here are your recent playlists: ")
        spotifyPlaylists = spotifyResponse['items']
        # List your top 3 playlists
        for i in range(0, 3):
            name = spotifyPlaylists[i]['name']
            desc = ""
            if(spotifyPlaylists[i]['description']):
                desc = ": " + spotifyPlaylists[i]['description']
            embedLink = spotifyPlaylists[i]['external_urls']['spotify']
            # Returns the name of the playlist, the description, and the link to the playlist in a nice format
            bot.message.reply_text(text="<a href='{}'><strong>".format(embedLink) + name + "</strong></a>" + desc, parse_mode=ParseMode.HTML, disable_web_page_preview=True)
        # Obtains bluetooth devices connected to your spotify account, NOT NECESSARY FOR THIS BOT
        blResp = requests.get("https://api.spotify.com/v1/me/player/devices", headers={'Accept': 'application/json', 'Content-Type': 'application/json', 'Authorization': "Bearer {}".format(auth_code)})
        bluetoothResponse = blResp.json()
        foundSpeaker = False
        for device in bluetoothResponse['devices']:
            # Search for a specific device name in the list of bluetooth devices defined by the device ID defined in the config.ini file
            # This is not necessary, but I have a specific bluetooth speaker I want to play music on. It will require a bit of tinkering to find the ID though, as it is not the plaintext name
            if (device['name'] == os.environ['SPOTIFY_DEVICE']):
                speakerID = device['id']
                foundSpeaker = True
                # Use my speaker if device is found
                requests.put("https://api.spotify.com/v1/me/player", headers={'Accept': 'application/json', 'Authorization': "Bearer {}".format(auth_code)}, json={'device_ids': [speakerID]})
                # Add my top 10 liked songs to the queue
                likedTracks = requests.get("https://api.spotify.com/v1/me/tracks?limit=10", headers={'Accept': 'application/json', 'Authorization': "Bearer {}".format(auth_code)})
                likedTracksResponse = likedTracks.json()
                for track in likedTracksResponse['items']:
                    track = track['track']
                    spotLink = track['uri']
                    # Post each to queue
                    requests.post("https://api.spotify.com/v1/me/player/queue", params={'uri': spotLink}, headers={'Accept': 'application/json', 'Authorization': "Bearer {}".format(auth_code)})
                #Start playing the first song in the liked songs queue by skipping any current song
                requests.post("https://api.spotify.com/v1/me/player/next", headers={'Accept': 'application/json', 'Authorization': "Bearer {}".format(auth_code)}) 
                bot.message.reply_text("Playing your top 10 liked songs on " + device['name'])
            # If the device is not found, use the default device
            else:
                foundSpeaker = False
        if (foundSpeaker == False):
            bot.message.reply_text("Cannot connect to bluetooth speaker, playing on default device")
            defaultID = bluetoothResponse['devices'][0]['id']
            requests.put("https://api.spotify.com/v1/me/player", headers={'Accept': 'application/json', 'Authorization': "Bearer {}".format(auth_code)}, json={'device_ids': [defaultID]})
            # Add my top 10 liked songs to the queue
            likedTracks = requests.get("https://api.spotify.com/v1/me/tracks?limit=10", headers={'Accept': 'application/json', 'Authorization': "Bearer {}".format(auth_code)})
            likedTracksResponse = likedTracks.json()
            for track in likedTracksResponse['items']:
                track = track['track']
                spotLink = track['uri']
                # Post each to queue
                requests.post("https://api.spotify.com/v1/me/player/queue", params={'uri': spotLink}, headers={'Accept': 'application/json', 'Authorization': "Bearer {}".format(auth_code)})
            #Start playing the first song in the liked songs queue by skipping any current song
            requests.post("https://api.spotify.com/v1/me/player/next", headers={'Accept': 'application/json', 'Authorization': "Bearer {}".format(auth_code)}) 
            bot.message.reply_text("Playing your recent liked songs on " + bluetoothResponse['devices'][0]['name'])
    # If configuration is incorrect, this will be thrown
    except:
        bot.message.reply_text("Spotify playlists / device not found, investigate further...")
        return

    # News API
    # Just a neat little feature to get the top 5 news articles from a news API I found, feel free to use your own
    try:
        techResponse = requests.get('https://newsapi.org/v2/top-headlines?country=us&category=technology&pageSize=2&apiKey={}'.format(NEWS_API_KEY)).json()
        scienceResponse = requests.get('https://newsapi.org/v2/top-headlines?country=us&category=science&pageSize=2&apiKey={}'.format(NEWS_API_KEY)).json()
        generalResponse = requests.get('https://newsapi.org/v2/top-headlines?country=us&category=general&pageSize=1&apiKey={}'.format(NEWS_API_KEY)).json()
        bot.message.reply_text("Here are your top headlines: \n")
        # Gets a certain number of the top articles from each category and parses them nicely into message replies
        for i in range(0, 2):
            url = techResponse['articles'][i]['url']
            name = techResponse['articles'][i]['title']
            bot.message.reply_text(text="Tech: <a href='{}'>".format(
                url) + name + "</a>", parse_mode=ParseMode.HTML, disable_web_page_preview=True)
        for i in range(0, 2):
            url = scienceResponse['articles'][i]['url']
            name = scienceResponse['articles'][i]['title']
            bot.message.reply_text(text="Science: <a href='{}'>".format(
                url) + name + "</a>", parse_mode=ParseMode.HTML, disable_web_page_preview=True)
        for i in range(0, 1):
            url = generalResponse['articles'][i]['url']
            name = generalResponse['articles'][i]['title']
            bot.message.reply_text(text="General: <a href='{}'>".format(
                url) + name + "</a>", parse_mode=ParseMode.HTML, disable_web_page_preview=True)
        bot.message.reply_text("--------")
    # If configuration is incorrect, this will be thrown again
    except:
        bot.message.reply_text("Website not found")
        return
    
    # End
    #
    bot.message.reply_text("That's all for today! Check back tomorrow for more updates.")


if __name__ == '__main__':
    print(UPDATER_KEY)
    updater = Updater(UPDATER_KEY, use_context=True)

    dp = updater.dispatcher
    dp.add_handler(CommandHandler('start', start_bot))
    # dp.add_handler(CommandHandler('stop', stop_bot))
    dp.add_handler(CommandHandler('status', status))
    dp.add_handler(CommandHandler('force', force_bot))

    dp.add_error_handler(error)
    updater.start_polling()

    updater.idle()
