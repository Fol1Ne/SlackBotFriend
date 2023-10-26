import slack, os, random, json, apscheduler.schedulers.blocking
from pathlib import Path
from dotenv import load_dotenv
from datetime import datetime

def get_users_friendship_dict():
    with open("users_info.json", "r") as my_file:
        try:
            return json.load(my_file)
        except:
            return {}

def set_users_friendship_dict(users_friendship_dict):
    with open("users_info.json", "w") as my_file:
        json.dump(users_friendship_dict, my_file)

def get_bot_friend_info():
    with open("bot_friend_info.json", "r") as my_file:
        try:
            return json.load(my_file)
        except:
            return {}

def set_bot_friend_info(bot_friend_info):
    with open("bot_friend_info.json", "w") as my_file:
        json.dump(bot_friend_info, my_file)

def get_users(users_array): # Функция для просмотра списка пользователей в канале
    for user_id in users_array["members"]:
        if user_id != bot_id:
            users_dict[user_id] = client.users_info(user=user_id)["user"]["real_name"]
    users = list(users_dict.keys())
    random.shuffle(users)
    return users

def schedule_messages(): # Функция для отправки сообщений в заданное время
    today_time = datetime.today().strftime("%d.%m.%Y")
    bot_friend_info = get_bot_friend_info()

    if "last_send_time" not in bot_friend_info or today_time != bot_friend_info["last_send_time"]:
        print(today_time + ": Отправка сообщений")

        bot_friend_info["last_send_time"] = today_time
        users_array = client.conversations_members(channel=os.environ["CHANNEL_ID"])
        users = get_users(users_array)

        while len(users) > 1:
            user1 = users.pop(0)
            users_friendship_dict = get_users_friendship_dict()
            for user2 in users:
                if user1 not in users_friendship_dict or user2 not in users_friendship_dict[user1]:
                    if user1 not in users_friendship_dict:
                        users_friendship_dict[user1] = []
                    if user2 not in users_friendship_dict:
                        users_friendship_dict[user2] = []
                    users_friendship_dict[user1].append(user2)
                    users_friendship_dict[user2].append(user1)
                    users.remove(user2)
                    client.chat_postMessage(channel=user1, text=os.environ["SEND_TEXT"].format(user2))
                    client.chat_postMessage(channel=user2, text=os.environ["SEND_TEXT"].format(user1))
                    break

        set_bot_friend_info(bot_friend_info)
        set_users_friendship_dict(users_friendship_dict)

env_path = Path(".") / ".env"
load_dotenv(dotenv_path=env_path)

client = slack.WebClient(token=os.environ["SLACK_TOKEN"])

users_dict = {}
bot_id = client.auth_test()["user_id"]

scheduler = apscheduler.schedulers.blocking.BlockingScheduler()
scheduler.add_job(schedule_messages, "cron", day_of_week="wed", hour="12-22", minute="0-59")
scheduler.start()