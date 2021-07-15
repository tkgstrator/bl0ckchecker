from logging import error
from requests_oauthlib import OAuth1Session
import json
import time
import random
from enum import Enum
import collections


class Type(Enum):
    BLOCKED = 1
    PROTECTED = 2
    NORMAL = 3


class Bl0ckChecker:
    def __init__(self):
        with open("env.json", mode="r") as f:
            env = json.load(f)
            try:
                CK = env["CK"]
                CS = env["CS"]
                AT = env["AT"]
                AS = env["AS"]
                self.conn = OAuth1Session(CK, CS, AT, AS)
            except:
                print(error)

    def makeUserList(self, screenName):
        userList = []
        url = f"https://api.twitter.com/1.1/friends/ids.json?screen_name={screenName}&count=5000"
        req = self.conn.get(url)
        try:
            userIds = json.loads(req.text)["ids"]
            userCount = len(userIds)
            with open("userList.csv", "w") as f:
                for index, userId in enumerate(userIds):
                    url = f"https://api.twitter.com/1.1/friends/ids.json?user_id={userId}&count=5000"
                    req = self.conn.get(url)
                    try:
                        userIds = json.loads(req.text)["ids"]
                        userList = userList + userIds
                        print(f"\rUserList:{len(userList)} {index + 1}/{userCount}", end="")
                    except KeyError:
                        print(req.text)
                    time.sleep(60)
                userList = collections.Counter(sorted(userList)).items()
                userList = list(map(lambda userId: f"{userId[0]}\n", list(filter(lambda userId: userId[1] >= userCount * 0.05, userList))))
                f.writelines(userList)
        except KeyError:
            print(req.text)

    def getBlockList(self):
        blockedList = []
        userTypes = [0, 0, 0]
        try:
            with open("userList.csv", "r") as f:
                with open("blockedList.csv", "w") as w:
                    userList = f.readlines()
                    for index, user in enumerate(userList):
                        userId = user.strip()
                        userType = self.checkStatusType(userId)
                        if userType == Type.NORMAL:
                            userTypes[0] += 1
                        if userType == Type.BLOCKED:
                            userTypes[1] += 1
                            w.write(user)
                            blockedList = user
                        if userType == Type.PROTECTED:
                            userTypes[2] += 1
                        print(
                            f"\rNormal:{str(userTypes[0]).zfill(6)}, Blocked:{str(userTypes[1]).zfill(6)}, Protected:{str(userTypes[2]).zfill(6)} {str(index + 1).zfill(8)}/{str(len(userList)).zfill(8)}", end="")
                        time.sleep(1)
        except KeyboardInterrupt:
            with open("blockedList.csv", "w") as w:
                w.writelines(blockedList)

    def checkStatusType(self, userId):
        url = f"https://api.twitter.com/1.1/statuses/user_timeline.json?user_id={userId}"
        req = self.conn.get(url)
        try:
            code = req.status_code
            if code == 401:
                try:
                    _ = json.loads(req.text)["error"]
                    return Type.PROTECTED
                except KeyError:
                    return Type.BLOCKED
            else:
                return Type.NORMAL
        except KeyError:
            time.sleep(900)


if __name__ == "__main__":
    screenName = "tkgling"

    checker = Bl0ckChecker()
    # checker.makeUserList(screenName)
    checker.getBlockList()
