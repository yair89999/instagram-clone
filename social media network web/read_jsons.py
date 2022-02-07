import json,os

if os.getcwd().split("\\")[-1] != "social media network web": # os.getcwd() gets the folder the file runs on
    try:
        os.chdir("social media network web") # change the diractory it works on to discord bot(now it start it from the "games and projects" directory)
    except: # can cause a error if it starts it from the folder
        pass

# this is a file with helpfull functions with json reading files

username_and_passwords_file_path = "static/users data/usernames_and_passwords.json"
def return_usernames_and_passwords_in_dict():
    with open(username_and_passwords_file_path) as file:
        data = json.load(file)
        data = data["people"][0]
        return data

def save_usernames_and_passwords(users_dict):
     # saves the dict it gets of the username:password and save it in the json file
    what_to_save = {"people":[users_dict]}
    with open(username_and_passwords_file_path, "w") as file:
        json.dump(what_to_save, file,  indent=4)

users_info_path = "static/users data/users_info.json"
def return_users_information():
    with open(users_info_path) as file:
        data = json.load(file)
        data = data["info"][0]
        return data

def save_users_information(users_info_dict):
    # gets a dict and saves it
    what_to_save = {"info":[users_info_dict]}
    with open(users_info_path, "w") as file:
        json.dump(what_to_save, file,  indent=4)


posts_path = "static/users data/posts.json"
def return_posts():
    with open(posts_path) as file:
        data = json.load(file)
        data = data["posts"][0]
        return data

def save_posts(posts_dict):
    what_to_save = {"posts":[posts_dict]}
    with open(posts_path, "w") as file:
        json.dump(what_to_save, file,  indent=4)