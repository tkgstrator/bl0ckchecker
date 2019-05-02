from requests_oauthlib import OAuth1Session
import json
import csv
import time
import random

CK = "" # Consumer Key
CS = "" # Consumer Secret
AT = "" # Access Token
AS = "" # Access Token Secert

conn = OAuth1Session(CK, CS, AT, AS)

try:
    f = open("status.csv", "r", newline="")
    csv1 = csv.reader(f, delimiter=",", quotechar="'")
    done = []
    for id in csv1:
        done.append(id)
    done.sort()
    f.close()
except FileNotFoundError:
    done = []

f = open("status.csv", "a", newline="")
w = csv.writer(f)

file = open("userslist.csv", "r") 
csv = csv.reader(file, delimiter=",", quotechar="'")

user = []
for id in csv:
    if id not in done:
        user.append(id[0])
user.sort()

user = random.sample(user, 1500)

for id in user:
    url = "https://api.twitter.com/1.1/statuses/user_timeline.json?user_id=" + str(id)
    req = conn.get(url)
    # print(req.text)
    # 制限に引っかかったら10秒待って繰り返す
    while 1:
        try:
            code = req.status_code
            break
        except KeyError:
            print("Limit Error!")
            time.sleep(900)

    # print(req.text)
    # ステータスコードが401ならばアクセスが許可されていない
    if code == 401:
        try:
            error = json.loads(req.text)["error"]
            print(id, "status : protected")
            w.writerow([id, "protected"])
        except KeyError:
            print(id, "status : blocked")
            w.writerow([id, "blocked"])
    else:
        print(id, "status : normal")
        w.writerow([id, "normal"])
    if len(user) > 1500:
        time.sleep(0.6)
f.close()