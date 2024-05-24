# --------------------------- #
# Made by SAD_DUST            #
# Ported from rfoal/duolingo  #
# Version 1                   #
# --------------------------- #
import os
import requests
import json
import base64
import time
import shutil
from configparser import ConfigParser
from getpass import getpass
from datetime import datetime

# Define ANSI escape code, i don't want to use colorama since i cannot figure how to make it works on cross-platform
class colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    WHITE = '\033[97m'

try:
    token = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJleHAiOjYzMDcyMDAwMDAsImlhdCI6MCwic3ViIjo1MjM2MTgwNjB9.hc8fdQvA8LpBrZavMfWcA0dqkU-kN8rQRa1E8YCqgHg"
    lessons = 10000000
except:
    token = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJleHAiOjYzMDcyMDAwMDAsImlhdCI6MCwic3ViIjo1MjM2MTgwNjB9.hc8fdQvA8LpBrZavMfWcA0dqkU-kN8rQRa1E8YCqgHg"
    lessons = 10000000

# Configure headers for futher request
headers = {
    'Content-Type': 'application/json',
    'Authorization': f'Bearer {token}',
    'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36',
}

# Token processing 
try:
    jwt_token = token.split('.')[1]
except:
    print(f"{colors.WARNING}--------- Traceback log ---------{colors.ENDC}\n{colors.FAIL}❌ Invalid token{colors.ENDC}")
    exit(-1)

padding = '=' * (4 - len(jwt_token) % 4)
sub = json.loads(base64.b64decode(jwt_token + padding).decode())

# Collect date and insert to the API
date = datetime.now().strftime('%Y-%m-%d')
print(f"{colors.WARNING}Date: {date}{colors.ENDC}")
response = requests.get(
    f"https://www.duolingo.com/{date}/users/{sub['sub']}?fields=fromLanguage,learningLanguage,xpGains",
    headers=headers,
)
data = response.json()
# Take element required to make a request
fromLanguage = data['fromLanguage']
learningLanguage = data['learningLanguage']
try:
    xpGains = data['xpGains']
    skillId = xpGains[0]['skillId']
except:
    print(f"{colors.FAIL}Your Duolingo account has been banned or does not exist{colors.ENDC}")
    exit(-1)

skillId = next(
    (xpGain['skillId'] for xpGain in reversed(xpGains) if 'skillId' in xpGain),
    None,
)
print(f"From (Language): {fromLanguage}")
print(f"Learning (Language): {learningLanguage}")

if skillId is None:
    print(f"{colors.FAIL}{colors.WARNING}--------- Traceback log ---------{colors.ENDC}\nNo skillId found in xpGains\nPlease do at least 1 or some lessons in your skill tree\nVisit https://github.com/gorouflex/DuoXPy#how-to-fix-error-500---no-skillid-found-in-xpgains for more information{colors.ENDC}")
    exit(1)

# Do a loop and start make request to gain xp
for i in range(int(lessons)):
    session_data = {
        'challengeTypes': [
            'assist',
            'characterIntro',
            'characterMatch',
            'characterPuzzle',
            'characterSelect',
            'characterTrace',
            'completeReverseTranslation',
            'definition',
            'dialogue',
            'form',
            'freeResponse',
            'gapFill',
            'judge',
            'listen',
            'listenComplete',
            'listenMatch',
            'match',
            'name',
            'listenComprehension',
            'listenIsolation',
            'listenTap',
            'partialListen',
            'partialReverseTranslate',
            'readComprehension',
            'select',
            'selectPronunciation',
            'selectTranscription',
            'syllableTap',
            'syllableListenTap',
            'speak',
            'tapCloze',
            'tapClozeTable',
            'tapComplete',
            'tapCompleteTable',
            'tapDescribe',
            'translate',
            'typeCloze',
            'typeClozeTable',
            'typeCompleteTable',
        ],
        'fromLanguage': fromLanguage,
        'isFinalLevel': False,
        'isV2': True,
        'juicy': True,
        'learningLanguage': learningLanguage,
        'skillId': skillId,
        'smartTipsVersion': 2,
        'type': 'SPEAKING_PRACTICE',
    }

    session_response = requests.post(f'https://www.duolingo.com/{date}/sessions', json=session_data, headers=headers)
    if session_response.status_code == 500:
         print(f"{colors.FAIL}Session Error 500 / No skillId found in xpGains or Missing some element to make a request\nPlease do at least 1 or some lessons in your skill tree\nVisit https://github.com/gorouflex/DuoXPy#how-to-fix-error-500---no-skillid-found-in-xpgains for more information{colors.ENDC}")
         continue
    elif session_response.status_code != 200:
         print(f"{colors.FAIL}Session Error: {session_response.status_code}, {session_response.text}{colors.ENDC}")
         continue
    session = session_response.json()

    end_response = requests.put(
        f"https://www.duolingo.com/{date}/sessions/{session['id']}",
        headers=headers,
        json={
            **session,
            'heartsLeft': 0,
            'startTime': (time.time() - 60),
            'enableBonusPoints': False,
            'endTime': time.time(),
            'failed': False,
            'maxInLessonStreak': 9,
            'shouldLearnThings': True,
        },
    )

    try:
        end_data = end_response.json()
    except json.decoder.JSONDecodeError as e:
        print(f"{colors.FAIL}Error decoding JSON: {e}{colors.ENDC}")
        print(f"Response content: {end_response.text}")
        continue

    response = requests.put(f'https://www.duolingo.com/{date}/sessions/{session["id"]}', data=json.dumps(end_data), headers=headers)
    if response.status_code == 500:
         print(f"{colors.FAIL}Response Error 500 / No skillId found in xpGains or Missing some element to make a request\nPlease do at least 1 or some lessons in your skill tree\nVisit https://github.com/gorouflex/DuoXPy#how-to-fix-error-500---no-skillid-found-in-xpgains for more information{colors.ENDC}")
         continue
    elif response.status_code != 200:
         print(f"{colors.FAIL}Response Error: {response.status_code}, {response.text}{colors.ENDC}")
         continue
    print(f"{colors.OKGREEN}[{i+1}] - {end_data['xpGain']} XP{colors.ENDC}")

# Delete Config folder after running done on GitHub Actions (idk if it's useful or not)
if os.getenv('GITHUB_ACTIONS') == 'true':
    try:
      print(f"{colors.WARNING}Cleaning up..{colors.ENDC}")
    except Exception as e:
      print(f"{colors.FAIL}Error deleting config folder: {e}{colors.ENDC}")
      exit(-1)

print("Closing DuoXPy ✅")
