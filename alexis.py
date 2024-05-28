# Alexis - YOUR PERSONAL ROBOT BUTLER
import datetime
from datetime import date
import random
import webbrowser
import wikipedia
#import speech_recognition as sr
import pytube
import random
from html import unescape

# For request errors
import requests
# For email
import smtplib
# For system stats
import psutil
# For getting password anonymously
import getpass
# For translator
from googletrans import Translator, LANGUAGES

from utils import response_consts as resconst
from utils.tictactoe import TicTacToe
from utils.rock_paper_scissors import RockPaperScissors
from utils.connect_four import ConnectFour
#For currency
from forex_python.converter import CurrencyRates

import pytz



finished = False
speechRecog = False


# Inputs
agreeInput = ["yes", "y", "sure", "yep", "ok", "why not"]
disagreeInput = ["no", "n", "nope", "rather not"]


def greet() -> str:
    """
    Function to greet differently depending on the time of day
    :return: A color formatted string containing a response
    """
    # Get the current time 
    hour = datetime.datetime.now().hour
    greeting = "\033[36m\nHello, I am Alexis, your personal robot butler"

    # "\033[36m" shows the string in Cyan in the terminal
    # 12am to 11:59am
    if hour >= 0 and hour < 12 :
        greeting = "\033[36m\nGood Morning, I am Alexis, your personal robot butler"

    # 12pm to 5:59pm 
    if hour >= 12 and hour < 18:
        greeting = "\033[36m\nGood Afternoon, I am Alexis, your personal robot butler"

    # 6pm to 11:59pm 
    if hour >= 18 and hour != 0:
        greeting = "\033[36m\nGood Evening, I am Alexis, your personal robot butler"  
    
    return greeting

# This function  takes a string as an input and if the input string is fully in uppercase, 
# returns a new string lowercased and capitalized. If not returns string unchanged.
def upperToCapitalize(txtAct):
    if not txtAct.isupper():
        return txtAct
    txtAct = (txtAct.lower()).capitalize()
    return txtAct


# --------- Start of "Back-end" commands ---------


def obtain_aliases(file = "res/aliases.txt") -> str:
    """
    This function returns every saved command alias.
    Args:
        file (str, optional): The file where the aliases are stored. Defaults to "res/aliases.txt".

    Returns:
        list:dict:str A list of dictionaries where the keys are the aliases and the valus ar the command that the alias points to.
    """
    with open(file, "r") as f:
        lines = f.readlines()
    returnDictionnary = {}
    for line in lines:
        returnDictionnary[line.split("=")[0]] = line.split("=")[1]
    return returnDictionnary

def save_aliases(aliases, file = "res/aliases.txt") -> str:
    """
    This subroutine saves command aliases.
    Args:
        aliases (list of dictionnaries): the aliases to be stored
        file (str, optional): The file where the aliases are to be stored. Defaults to "res/aliases.txt".
    """
    with open(file, "w") as f:
        for k, v in aliases.items():
            f.write(f"{k}={v}")

def apply_aliases(command, file = "res/aliases.txt") -> str:
    """
    This function returns the command passed as an argument with all aliases apllied
    Args:
        command (str): The user command to aplly aliases to.
        file (str, optional): The file in which the alliases are stored. Defaults to "res/aliases.txt".
    Returns:
        str: The command with all aliasess apllied
    """
    aliases = obtain_aliases()
    for k, v in aliases.items():
        command = command.replace(k, v)
    return command 

def get_setting(setting: str, file = "res/settings.txt") -> str:
    """
    This function obtains a specific setting's value from the specified file.
    Args:
        setting (str): The seting you are looking for the value of.
        file (str, optional): Settings file to consult (relative filepath as string required). Defaults to "res/setings.txt".

    Returns:
        str: The value of the queried setting.
    """
    with open(file, "r") as f:
        settings = f.readlines()
    for line in settings:
        if line.split("=")[0] == setting.upper():
            return line.split("=")[1].strip("\n")
    return None

def set_background_color(settingsFile = "res/settings.txt") -> str:
    backgroundColor = "\033[1;32;40m"
    colorMode = get_setting("COLORMODE", settingsFile)
    if colorMode == "dark":
        backgroundColor = "\033[1;32;40m"
    elif colorMode == "light":
        backgroundColor = "\033[1;32;255m"
    elif colorMode == "purple":
        backgroundColor = "\033[1;32;45m"
    elif colorMode == "red":
        backgroundColor = "\033[1;32;41m"
    elif colorMode == "green":
        backgroundColor = "\033[1;32;42m"
    elif colorMode == "blue":
        backgroundColor = "\033[1;32;44m"
    return backgroundColor

def execute_user_macro(macroNameAndArgs: str, file = "res/macros.txt"):
    """
    This function executes a user-written macro as specified in the passed file.
    Args:
        macroName (str): The name of the macro to execute.
        file (str, optional): The location of the macros file. Defaults to "res/macros.txt".

    Returns:
        any: The macro's return value if applicable or a string error message
    """
    macroName = macroNameAndArgs[0]
    arguments = macroNameAndArgs[1:]
    with open(file, "r") as f:
        text = f.read().split("</MACRO>")
    macros = {}
    # This large for loop tries to read the macros.txt file into macro names and arguments and macro code in a single dictionnary.
    for code in text:
        currentMacroName =""
        currentMacroContent = ""
        nameObtained = False
        for char in code:
            if char == ">":
                nameObtained = True
            elif char != "<" and not nameObtained:
                currentMacroName += char
            elif char != "<":
                currentMacroContent += char
        macroHeaders = currentMacroName.strip("\n").split(" ")
        macros[macroHeaders[0].lower()] = currentMacroContent.strip("\n"), macroHeaders[1:]
    if macroName in macros.keys():
        # This is the part that handles passing the arguments to the macro.
        macroArgs = {}
        for argumentIndex in range(len(arguments)):
            macroArgs[macros[macroName][1][argumentIndex]] = arguments[argumentIndex]
        return exec(macros[macroName][0], macroArgs)
    else:
        return "Sorry, I don't seem to remember what this macro is."



# --------- Start of "Font-end" commands ---------



# Function to perform language translation
def translate_text(*command, target_language='en'):
    translator = Translator()
    translation = translator.translate(command[0], dest=target_language)
    return translation.text

# Function to print available languages
def print_available_languages(*command):
    print("\033[36mAvailable Languages:")
    for code, language in LANGUAGES.items():
        print(f"{code}: {language}")

news_api_key = '102ebf59c0124b54a9c2e239549bf2a3'

def get_latest_news(*command): #api_key, country='us', category='general'
   country = command[0].split(" ")[1]
   category = command[0].split(" ")[2]
   base_url = "https://newsapi.org/v2/top-headlines"
   params = {
       'country': country,
       'category': category,
       'apiKey': api_key
   }
   response = requests.get(base_url, params=params)
   if response.status_code == 200:
       articles = response.json()['articles']
       return articles[:5]  # Return top 5 news articles
   else:
       return f"Error: {response.status_code}"


def dealias(*command):
    aliases = obtain_aliases()
    alias = command[0].split(" ")[1]
    if alias not in aliases.values():
        print("\033[36mThis alias does not exist.")
    else:
        newAliases = {}
        for k, v in aliases.items():
            if v == alias:
                continue
            else:
                newAliases[k] = v
        save_aliases(newAliases)
        print("\033[36mAlias removed successfuly.")

def alias(*command):
    aliases = obtain_aliases()
    alias = command[0].split(" ")[1]
    aliasing_target = command[0].split(" ")[-1]
    if alias in aliases.keys():
        print("\033[36mThis word already binds to a command.")
    else:
        aliases[alias] = aliasing_target
        save_aliases(aliases)
        print("\033[36mAlias applied.")

def run(*command):
    returnValue = f"\033[36m{execute_user_macro(command[0].split(' ')[1:])}"
    if returnValue == "\033[36mNone":
        print("\033[36mDone with execution.")
    else:
        print(returnValue)

def greet_user(*command):
    print(random.choice(resconst.helloResponse))

def ask_how_are_you(*command):
    print(random.choice(resconst.howAreYouResponse))

def ask_whats_up(*command):
    print(random.choice(resconst.whatsUpResponse))

def who_are_you(*command):
    print("\033[36mI am Alexis, your personal robot butler!")

def get_time(*command):
    format = get_setting("HOUR_FORMAT")
    time_now = datetime.datetime.now()
    if format == "12h":
        current_time = time_now.strftime("%I:%M %p")
    else:
        current_time = time_now.strftime("%H:%M")
    print("\033[36mIt's currently", current_time)

def get_date(*command):
    date_today = date.today()
    date_today = date_today.strftime("%B %d, %Y")
    print("\033[36mIt's", date_today)

def get_news(*command):
    news = get_latest_news(news_api_key)
    for article in news:
        print(article['title'], "-", article['description'])

def get_vitals(*command):
    try:
        print("Diagnosing system to collect vital stats")
        # Get CPU usage
        print(f"The CPU usage is: {psutil.cpu_percent(4)} %") # We get the CPU usage for the past 4 seconds
        # Get memory usage
        print(f"RAM memory used: {psutil.virtual_memory()[2]} %")
        # Get battery percentage
        battery_status = psutil.sensors_battery()
        print(f"Percentage of battery: {battery_status.percent} %")
    except:
        print("An error occurred while collecting system vitals")

def play_tic_tac_toe(*command):
    game_instance = TicTacToe()
    game_instance.start_game()

def play_rock_paper_scissors(*command):
    game_instance = RockPaperScissors()
    game_instance.start_game()

def play_connect_four(*command):
    game_instance = ConnectFour()
    game_instance.start_game()

def download_youtube_video(*command):
    url = input("\033[33mEnter the URL of the video you want to download: ")
    try:
        yt = pytube.YouTube(url)
        ys = yt.streams.filter(progressive=True, file_extension="mp4").order_by('resolution').desc().first()
        path = input("\033[33mEnter the path to save the video: ")
        ys.download(path)
        print("\033[36mVideo downloaded successfully!")
    except Exception as e:
        print("\033[36mVideo download failed! Error: ", e)

def get_youtube_video_info(*command):
    url = input("\033[33mEnter the URL of the video you want to get information about: ")
    try:
        yt = pytube.YouTube(url)
        print("\033[36mTitle:          ", yt.title)
        print("Views:          ", yt.views)
        print("Length:         ", yt.length)
        print("Publish Date:   ", yt.publish_date)
        print("Author:         ", yt.author)
        print("Age Restricted: ", yt.age_restricted)
    except Exception as e:
        print("\033[36mVideo information retrieval failed! Error: ", e)

def world_clock(*command):
    dispTimezone = input("Enter the location of time zone in like (Canada/Eastern, Europe/Brussels, Etc/GMT-2): ")
    try: 
        dispTime = datetime.datetime.now(pytz.timezone(dispTimezone))
        print(f"current time in {dispTimezone}: {dispTime}")
    except pytz.UnknownTimeZoneError:
        print("Can't find the place, try checking for typos or extra spaces")

def open_site(*command):
    if "http" in command[0]:
        webbrowser.open(command[0][5:])
    elif "tempmail" in command[0]:
        webbrowser.open("https://temp-mail.org/en/")
    elif "youtube" in command[0] or "yt" in command[0]:
        webbrowser.open("https://youtube.com")
    elif "spotify" in command[0] or "song" in command[0]:
        webbrowser.open("https://spotify.com")
    elif "github" in command[0] or "gh" in command[0]:
        webbrowser.open("https://github.com")
    elif "gmail" in command[0]:
        webbrowser.open("https://mail.google.com/")
    elif "netflix" in command[0]:
        webbrowser.open("https://netflix.com")
    elif "amazon" in command[0]:
        webbrowser.open("https://amazon.com")
    elif "google classroom" in command[0] or "classroom" in command[0]:
        webbrowser.open("https://edu.google.com/intl/en-GB/workspace-for-education/classroom/")
    elif "twitter" in command[0] or command[0].endswith("x") or command[0].endswith("x."):
        webbrowser.open("https://twitter.com")
    else:
        webbrowser.open("https://" + command[0][5:])

def google_search(*command):
    print(random.choice(resconst.agreeResponse))
    webbrowser.open('https://www.google.com/search?q=' + command[0][7:])

def amazon_search(*command):
    print(random.choice(resconst.agreeResponse))
    webbrowser.open('https://www.amazon.com/s?k=' + command[0][7:])

def ebay_search(*command):
    print(random.choice(resconst.agreeResponse))
    webbrowser.open('https://www.ebay.com/sch/i.html?_nkw=' + command[0][5:])

def definition_of_word(*command):
    print(random.choice(resconst.agreeResponse))
    webbrowser.open('https://www.dictionary.com/browse/' + command[0][14:])    

def synonym_of_word(*command):
    print(random.choice(resconst.agreeResponse))
    webbrowser.open('https://www.thesaurus.com/browse/' + command[0][11:])  

def google_map_of_place(*command):
    print(random.choice(resconst.agreeResponse))
    webbrowser.open('https://www.google.com/maps/search/' + command[0][9:])

def wikipedia_search(*command):
    try:
        searchTerm = command[0][7:]
        print(wikipedia.summary(searchTerm))
    except:
        print("An error occurred")
        print(f"Googling {command[0]}")
        webbrowser.open('https://www.google.com/search?q=' + command[0][7:])

def send_email(*command):
    session = smtplib.SMTP('smtp.live.com', 587)
    session.starttls()
    try:
        mailID = input("\033[33mEnter your Outlook/Hotmail E-mail address\n").lower()
        password = getpass.getpass("Enter Password\n")
        recipient = input("\033[33mEnter email of recipient\n").lower()
        msg = input("\033[33mEnter message\n")
        message = f"\n {msg}"
        session.login(mailID, password)
        session.sendmail(mailID, recipient, message)
        session.quit()
        print("\033[36mSent!")
    except:
        print(random.choice(resconst.errorResponse))

def translate_text_command(*command):
    try:
        text_to_translate = input("\033[33mEnter the text to be translated: ")
        target_language_input = input("\033[33mEnter the target language code or type 'help' to see the list of available languages: ").lower()
        if target_language_input == "help":
            print_available_languages()
        else:
            target_language = target_language_input
            translated_text = translate_text(text_to_translate, target_language)
            print("\033[36mTranslated Text:", translated_text)
    except Exception as e:
        print("\033[36mTranslation failed! Error: ", e)
        
def get_bored_activity(*command):
    try:
        r = requests.get('https://www.boredapi.com/api/activity').json()
        activity = r['activity']
        print("\033[36mTry this:\n" + activity)
        if r['link']:
            open_browser = input("\033[36mLearn more? (Yes/No)\n").lower()
            if open_browser in agreeInput:
                webbrowser.open(r['link'])
    except:
        print(random.choice(resconst.errorResponse))

def get_joke(*command):
    try:
        r = requests.get('https://sv443.net/jokeapi/v2/joke/Miscellaneous,Pun,Spooky,Christmas&type=single').json()
        activity = r['joke']
        print("\033[34m" + activity)
        askForInput = True
        while askForInput:
            anotherOne = input("\033[36mAnother one?(Yes/No)\n").lower()
            if anotherOne in agreeInput:
                r = requests.get('https://sv443.net/jokeapi/v2/joke/Any?blacklistFlags=nsfw,racist,sexist&type=single').json()
                activity = r['joke']
                print("\033[34m" + activity)
            else:
                askForInput = False
    except:
        print(random.choice(resconst.errorResponse))

def show_image(*command):
    try:
        obj = command[5:]
        if obj == 'dog':
            print(random.choice(resconst.agreeResponse))
            r = requests.get('https://dog.ceo/api/breeds/image/random').json()
            picture_url = r['message']
            webbrowser.open(picture_url)
        elif obj == 'cat':
            print(random.choice(resconst.agreeResponse))
            r = requests.get('https://api.thecatapi.com/v1/images/search').json()
            picture_url = r[0]['url']
            webbrowser.open(picture_url)
        else:
            print("\033[34m" + "The list available to show is: " + "\033[36m" + "dog, cat")
    except:
        print(random.choice(resconst.errorResponse))

def get_fact(*command):
    try:
        r = requests.get('https://asli-fun-fact-api.herokuapp.com/').json()
        activity = upperToCapitalize(r['data']['fact'])
        print("\033[34m" + activity)
        askForInput = True
        while askForInput:
            anotherOne = input("\033[36mAnother one?(Yes/No)\n").lower()
            if anotherOne in agreeInput:
                r = requests.get('https://asli-fun-fact-api.herokuapp.com/').json()
                activity = upperToCapitalize(r['data']['fact'])
                print("\033[34m" + activity)
            else:
                askForInput = False
    except:
        print(random.choice(resconst.errorResponse))

def get_advice(*command):
    try:
        r = requests.get("https://api.adviceslip.com/advice").json()
        print(r['slip']['advice'])
    except:
        print(random.choice(resconst.errorResponse))

def get_trivia(*command):
    try:
        response = requests.get("https://opentdb.com/api.php?amount=1&category=9&difficulty=easy&type=multiple")
        data = response.json()
        if response.status_code == 200:
            result = data["results"][0]
            question = unescape(result["question"])
            print(f"\033[36m{question}")
            correct_answer = unescape(result["correct_answer"])
            options = [unescape(option) for option in result["incorrect_answers"]]
            options.append(correct_answer)
            random.shuffle(options)
            for i, option in enumerate(options):
                print(f"\033[36m\t({i+1}) {option}")
            my_answer_id = int(input("\033[33mEnter your answer (A number from 1-4): "))
            if my_answer_id not in range(1, 5):
                print("\033[36mEnter a valid number between 1 and 4 next time...")
            elif correct_answer == options[my_answer_id - 1]:
                print("\033[36mCongratulations, you are correct!!!")
            else:
                print(f"\033[36mGood attempt, the correct answer was \"{correct_answer}\". Try again next time")
        else:
            print('\033[36mError retrieving trivia data')
    except Exception as e:
        print("\033[36mError in trivia execution!:", e)

def get_weather(*command):
    api_key = '42dd8eece458d27eca3c295e916b6c79'
    city = input("\033[33mEnter the city for weather information: ")
    try:
        params = {"q": city, "appid": api_key, "units": "metric"}
        response = requests.get('https://api.openweathermap.org/data/2.5/weather', params=params)
        data = response.json()
        if response.status_code == 200:
            temperature = data["main"]["temp"]
            weather_description = data["weather"][0]["description"]
            print(f'\033[36mWeather in {city}: {weather_description}, Temperature: {temperature}°C')
        else:
            print(f'\033[36mError retrieving weather data for {city}')
    except:
        print(random.choice(resconst.errorResponse))

def get_stock_price(*command):
    stock_symbol = input("\033[33mEnter the stock symbol (e.g., AAPL): ").upper()
    api_key = "GT33YXVN95VQ810P"
    base_url = "https://www.alphavantage.co/query"
    try:
        response = requests.get(f'{base_url}?function=GLOBAL_QUOTE&symbol={stock_symbol}&apikey={api_key}')
        data = response.json()
        stock_info = data.get('Global Quote', {})
        if stock_info:
            stock_price = stock_info.get('05. price')
            print(f'\033[36mCurrent stock price of {stock_symbol}: ${stock_price}')
        else:
            print(f'\033[36mStock information not found for {stock_symbol}')
    except Exception as e:
        print(f'\033[36mError retrieving stock data: {e}')

def get_zip_info(*command):
    try:
        zip_code = input("Type your zip code:\n")
        r = requests.get(f'https://api.zippopotam.us/us/{zip_code}').json()
        activity = r["places"][0]['place name'] + " " + r["places"][0]["state abbreviation"] + " " + r["country"]
        print("\033[34m" + activity)
        askForInput = True
        while askForInput:
            anotherOne = input("\033[36mDo you want to check another zip code?(Yes/No)\n").lower()
            if anotherOne == "yes":
                zip_code = input("Type your zip code:\n")
                r = requests.get(f'https://api.zippopotam.us/us/{zip_code}').json()
                activity = r["places"][0]['place name'] + " " + r["places"][0]["state abbreviation"] + " " + r["country"]
                print("\033[34m" + activity)
            else:
                askForInput = False
    except:
        print(random.choice(resconst.errorResponse))

def convert_currency(*command):
    try:
        source_currency = input("\033[33mEnter the source currency code (e.g., USD): ").upper()
        target_currency = input("\033[33mEnter the target currency code (e.g., EUR): ").upper()
        amount = float(input("\033[33mEnter the amount to convert: "))
        c = CurrencyRates()
        exchange_rate = c.get_rate(source_currency, target_currency)
        converted_amount = amount * exchange_rate
        print(f"\033[36m{amount} {source_currency} is equal to {converted_amount} {target_currency}")
    except Exception as e:
        print("\033[36mCurrency conversion failed! Error:", e)

def list_commands(*command):
    with open('res/AllCommands.txt', 'r') as f:
        print(f.read())

def turn_on_speech_recognition(*command):
    global speechRecog
    print("Turning on Speech Recognition...")
    speechRecog = True

def exit_program(*command):
    print(random.choice(resconst.exitResponse))
    global finished
    finished = True
    exit()

actions = {
    ("dealias", "de-alias"): dealias,
    ("alias",): alias,
    ("run",): run,
    ("hi", "hey", "hello", "hai"): greet_user,
    ("how are you", "hows it going", "how's it going", "how r u"): ask_how_are_you,
    ("whats up", "what's up", "ssup", "what up"): ask_whats_up,
    ("who are you", "what are you"): who_are_you,
    ("time",): get_time,
    ("date",): get_date,
    ("news",): get_news,
    ("vitals",): get_vitals,
    ("tic tac toe", "x and o", "xo", "x n o", "x and 0", "tictactoe"): play_tic_tac_toe,
    ("rock paper scissors", "rockpaperscissors"): play_rock_paper_scissors,
    ("connect four", "connectfour"): play_connect_four,
    ("download youtube video", "download video", "mp4"): download_youtube_video,
    ("video stats", "video info", "video information", "video statistics"): get_youtube_video_info,
    ("world clock",): world_clock,
    ("open ",): open_site,
    ("google ",): google_search,
    ("amazon ",): amazon_search,
    ("ebay ",): ebay_search,
    ("definition of ",): definition_of_word,
    ("synonym of ",): synonym_of_word,
    ("where is ",): google_map_of_place,
    ("search ",): wikipedia_search,
    ("send mail", "send e-mail", "send email"): send_email,
    ("translate",): translate_text_command,
    ("bored",): get_bored_activity,
    ("joke",): get_joke,
    ("fact",): get_fact,
    ("advice",): get_advice,
    ("trivia",): get_trivia,
    ("weather",): get_weather,
    ("stocks",): get_stock_price,
    ("zip code", "postal code"): get_zip_info,
    ("currency",): convert_currency,
    ("commands", "help"): list_commands,
    ("speech",): turn_on_speech_recognition,
    ("exit",): exit_program,
    
}


def executeCommand(command):
    for keyword, order in actions.items():
        for word in keyword:
            if word in command:
                order(command)
                return True
    return False
            


# MAIN LOOP
if __name__ == '__main__':
    # This prints one of the above three greetings before taking user input
    print(greet())
    backgroundColor = set_background_color()
    while not finished:
        while speechRecog:
            with sr.Microphone() as source:
                # Recognisers for speech recognition
                r1 = sr.Recognizer()
                r2 = sr.Recognizer()

                # This will prompt user for speech input in green color and not go to the next line
                print(f"\n{backgroundColor}Speak Command: ", end="")

                # Try to get speech input from user
                try:
                    audio = r1.listen(source)
                    recognised = r2.recognize_google(audio)
                    # Make the speech lowercase for simplicity
                    command = recognised.lower()
                    # Print exactly what user said
                    print(recognised)

                except sr.UnknownValueError:
                    # This will prompt user for text input in green color and not go to the next line
                    print(f"\n{backgroundColor}Speech not recognised to Type Commands, say 'type' or enter it here: ", end="")

                except sr.RequestError as e:
                    # This will prompt user for text input in green color and not go to the next line
                    print(f"\n{backgroundColor}Speech not recognised to Type Commands, say 'type' or enter it here: ", end="")

        # This is the default setting - typing commands
        # This is for when voice commands are disabled
        while not speechRecog:
            # This will prompt user for text input in green color and not go to the next line
            print(f"\n{backgroundColor}Type Command: ", end="")
            # Take input from user in yellow color
            command = input("\033[33m").lower()
            # Apllies aliases
            command = apply_aliases(command)  

            # API BASED
            # Bored
            
            if not executeCommand(command):
                print(f"{random.choice(resconst.unrecognisedCommandResponse)}. Type 'help' to see the list of commands")


#  MADE BY:_            _   _____                        _ 
#  \ \    / (_)        (_) |  __ \                      (_)
#   \ \  / / _ _ __ ___ _  | |  | | __ _ ___  __ _ _ __  _ 
#    \ \/ / | | '__/ _ \ | | |  | |/ _` / __|/ _` | '_ \| |
#     \  /  | | | |  __/ | | |__| | (_| \__ \ (_| | | | | |
#      \/   |_|_|  \___| | |_____/ \__,_|___/\__,_|_| |_|_|
#                     _/ |                                 
#                    |__/                                  
