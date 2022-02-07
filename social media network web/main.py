# python modules imports
from flask import Flask,render_template,redirect,url_for,session,request,flash
import json,os,re,smtplib
from werkzeug.utils import secure_filename
from datetime import timedelta
# python my modules imports(functions i made)
from read_jsons import return_usernames_and_passwords_in_dict,save_usernames_and_passwords,   return_users_information,save_users_information,  return_posts,save_posts

if os.getcwd().split("\\")[-1] != "social media network web": # os.getcwd() gets the folder the file runs on
    try:
        os.chdir("social media network web") # change the diractory it works on to discord bot(now it start it from the "games and projects" directory)
    except: # can cause a error if it starts it from the folder
        pass

app = Flask(__name__)

app.secret_key = "Yair's social media web 123456789!@$%453&^!$#5"
app.permanent_session_lifetime = timedelta(hours=1) # saves things in the session for 1 hour

users = return_usernames_and_passwords_in_dict()
users_info = return_users_information()
posts = return_posts()
defult_profile_img_path = "users data/users_icons/default.PNG"

sending_email = os.environ.get("WEBSITES_EMAIL")
sending_email_password = os.environ.get("WEBSITES_EMAIL_PASSWORD")

"""
append options for the web:
like post option
delete comments(that a user will be able to delete a comment he posted on a post)"""

# create things functions
def create_a_user(username,password,email): # gets info and saves EVERYTHING
    users[username] = password # saves username+password
    users_info[username] = { # save username data: username password email and stuff
        "username":username,
        "password":password,
        "email":email,

        "profile pic path": "users data/users_icons/default.png",
        "profile description":"",

        "posts":[], # evert element looks like this: "post id","post id"
        # every post has a unique(יחודי) id(post information is in posts dict)
    }
    print(users_info)

    session["username"] = username
    session["password"] = password
    save_usernames_and_passwords(users)
    save_users_information(users_info)

def return_users_for_js():
    # doing the 123--suppurate user--321 between every user because javascript gets signs in other way
    return "123--suppurate user--321".join(sorted(list(users)))

@app.route("/home")
@app.route("/")
def home():
    profile_pic_path = None
    username = ""
    if "username" in session:
        login = True
        profile_pic_path = users_info[session["username"]]["profile pic path"]
        username = session["username"]
    else: login = False
    users_for_js = return_users_for_js()
    posts_info = {}
    index = 1
    for post_id in list(posts)[::-1]: # gets the last 10 posts
        posts_info[post_id] = posts[post_id]
        if index >= 10:
            break
        index += 1

    return render_template("home.html", login=login, profile_pic_path=profile_pic_path,username=username,users_for_js=users_for_js, posts_info=posts_info)

def allowed_file(filename): # using in edit_profile() in the upload file part
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in {"png","jpg","jpeg"}

def get_post_id():
    if len(posts) == 0:
        return "1"
    posts_id = list(posts)
    last_id = posts_id[-1]
    return_id = str(int(last_id)+1)
    return return_id

@app.route("/upload post", methods=["POST","GET"])
def upload_post():
    if "username" in session:
        login = True
        username = session["username"]
        profile_pic_path = users_info[session["username"]]["profile pic path"]
    else: return redirect(url_for("home"))

    if request.method == "POST":
        description = request.form["description"]
        if description == "": # cant leave the description empty
            flash("You must write a post description")
            return redirect(request.url)
        else:
            if 'file' not in request.files:
                flash('No file part')
                return redirect(request.url)
            file = request.files['file']
            if file.filename == '':
                flash("You must choose file")
                users_for_js = return_users_for_js()
                return render_template("upload post.html", description=description)
            if file and allowed_file(file.filename):
                
                # save post
                filename = secure_filename(file.filename)
                file_id = str(get_post_id()) # gives the post id(by numbers for example the first post will have the id: "1")
                try:
                    filetype = users_info[username]["profile pic path"].split(".")[1]
                    os.remove("static//users data//posts//"+username + "." + filetype)
                except: pass
                file.save("static//users data//posts//"+filename)
                os.rename("static//users data//posts//"+filename,"static//users data//posts//"+file_id + "." +filename.split(".")[1])
                
                # update dicts
                posts[file_id] = {"by":username, "pic path":"users data//posts//"+file_id + "." +filename.split(".")[1],  "description":description, "comments":{}}
                #comments: {"username":comment}
                users_info[username]["posts"].append(file_id)
                save_users_information(users_info)
                save_posts(posts)
                return redirect(url_for("show_post", post_id=file_id))
            else:
                flash('Illegal file type')

                users_for_js = return_users_for_js()
                return render_template("upload post.html", description=description,users_for_js=users_for_js) # return to the same url
    else:
        users_for_js = return_users_for_js()
        return render_template("upload post.html", login=login, profile_pic_path=profile_pic_path,username=username,users_for_js=users_for_js)


@app.route("/show post/<post_id>")
def show_post(post_id):
    profile_pic_path = None
    username = ""
    if "username" in session:
        login = True
        profile_pic_path = users_info[session["username"]]["profile pic path"]
        username = session["username"]
    else: login = False

    try:
        post_dict = posts[post_id]
        post_dict["id"] = post_id
    except: return redirect(url_for("post_not_exist"))
    user_uploaded = post_dict["by"]
    user_uploaded = users_info[user_uploaded].copy()
    try:
        user_uploaded.pop("password")
        user_uploaded.pop("email")
        user_uploaded.pop("profile description")
        user_uploaded.pop("posts")
    except: pass

    users_for_js = return_users_for_js()
    return render_template("show post.html", login=login, profile_pic_path=profile_pic_path,username=username,   post_dict=post_dict,user_uploaded=user_uploaded,users_for_js=users_for_js)


"""comments save like this:
comment<~-!@#$%^&*()--username:username
for every username can send a message someone else sent"""
def give_comments(id):
    comments = [] # {"username":username, comment:[]}
    for post_comments in posts[id]["comments"].items():
        print(post_comments)
        user_dict = {"username":post_comments[1], "comment":post_comments[0].split("<~-!@#$%^&*()--")[0]}
        comments.append(user_dict)
    print(comments)
    return comments

@app.route("/del comment/<post_id>/<comment>")
def del_comment(post_id,comment):
    if "username" in session: # user logged in
        username = session["username"]
        comment_username = posts[post_id]["comments"][comment+"<~-!@#$%^&*()--"+username]
        if username == comment_username: # if the user that wrote the comment
            posts[post_id]["comments"].pop(comment+"<~-!@#$%^&*()--"+username)
            save_posts(posts)
            return redirect(url_for("show_write_post_comments",post_id=post_id))
        else:
            return redirect(url_for("show_write_post_comments",post_id=post_id))
    else:
        return redirect(url_for("show_post",post_id=post_id))

@app.route("/comments/<post_id>", methods=["POST","GET"])
def show_write_post_comments(post_id):
    """to do:
    that a user can delete a post he uploaded"""
    if not post_id in posts: # if he searched for a post that not exists
        return redirect(url_for("post_not_exist"))
    profile_pic_path = None
    username = ""
    if "username" in session:
        login = True
        profile_pic_path = users_info[session["username"]]["profile pic path"]
        username = session["username"]
    else: login = False
    users_for_js = return_users_for_js()

    comments = give_comments(post_id)

    post_user = posts[post_id]["by"]

    if request.method == "POST":
        comment = request.form["comment"]
        if comment == "": # empty comment
            return render_template("show_write_comments.html", login=login, profile_pic_path=profile_pic_path,username=username,users_for_js=users_for_js,  comments=comments, post_by=post_user,post_id=post_id,
            error =  "can't send empty comment")
        else: # if he wrote something
            try:
                if comment != posts[post_id]["comments"][username][-1] and username != "":
                    # updates the post comments
                    posts[post_id]["comments"][comment+"<~-!@#$%^&*()--"+username] = username
            except:
                if username != "":
                    # updates the post comments
                    posts[post_id]["comments"][comment+"<~-!@#$%^&*()--"+username] = username

            comments = give_comments(post_id)
            
            save_posts(posts)
            return render_template("show_write_comments.html", login=login, profile_pic_path=profile_pic_path,username=username,users_for_js=users_for_js,  
            comments=comments, post_by=post_user,post_id=post_id)
    else:
        return render_template("show_write_comments.html", login=login, profile_pic_path=profile_pic_path,username=username,users_for_js=users_for_js,  comments=comments, post_by=post_user,post_id=post_id)

@app.route("/post not exist")
def post_not_exist():
    profile_pic_path = None
    username = ""
    if "username" in session:
        login = True
        profile_pic_path = users_info[session["username"]]["profile pic path"]
        username = session["username"]
    else: login = False

    users_for_js = return_users_for_js()
    return render_template("not exist.html", login=login, profile_pic_path=profile_pic_path,username=username,   what_not_exist="post",users_for_js=users_for_js)

def split_list(lst, n):
    returning_list = []
    for i in range(0, len(lst), n):
        returning_list.append(lst[i:i + n])
    return returning_list

@app.route("/show profile/<show_username>")
def show_user_profile(show_username): # show the profile of a user(not you, if you you go back to your page(my profile function))
    profile_pic_path = None
    username = ""
    if "username" in session:
        login = True
        profile_pic_path = users_info[session["username"]]["profile pic path"]
        username = session["username"]
        if session["username"] == show_username: # if the user go to his own profile
            return redirect(url_for("show_my_profile"))
    else: login=False

    try:
        user_info = users_info[show_username].copy()
    except: return redirect(url_for("user_not_exist"))
    user_info.pop("password")
    user_info.pop("email")
    user_info["posts divide to 3"] = split_list(user_info["posts"],3) # returning a list like this [[1,2,3],[4,5,6]]
    # user_info = {'username': 'yair', 'profile pic path': 'users data/users_icons/yair.PNG', 'profile description': 'This is my profile\r\nI made this web guys', 'posts': ['1']}
    posts_info = {}
    for post_id in user_info["posts"]:
        posts_info[post_id] = posts[post_id]

    users_for_js = return_users_for_js()
    return render_template("show other users profile.html", login=login, profile_pic_path=profile_pic_path,username=username,   user_info=user_info,posts_info=posts_info,users_for_js=users_for_js)

@app.route("/user not exist")
def user_not_exist():
    profile_pic_path = None
    username = ""
    if "username" in session:
        login = True
        profile_pic_path = users_info[session["username"]]["profile pic path"]
        username = session["username"]
    else: login = False

    users_for_js = return_users_for_js()
    return render_template("not exist.html", login=login, profile_pic_path=profile_pic_path,username=username,   what_not_exist="user profile",users_for_js=users_for_js)

@app.route("/edit profile", methods=["POST","GET"])
def edit_profile():
    global users_info
    if "username" in session:
        login = True
        username = session["username"]
        profile_pic_path = users_info[session["username"]]["profile pic path"]
        user_info = users_info[username].copy()
        try:
            user_info.pop("password")
            user_info.pop("email")
        except: pass
    else: return redirect(url_for("home"))
    
    if request.method == "POST":
        # after updating the profile you go the show_profile page
        new_description = request.form["description"]
        old_description = users_info[username]["profile description"]
        users_info[username]["profile description"] = new_description
        save_users_information(users_info)
        users_info = return_users_information()

        if new_description == old_description: # will get the files
            if 'file' not in request.files:
                flash('No file part')
                return redirect(request.url)
            file = request.files['file']
            if file.filename == '':
                return redirect(url_for("show_my_profile"))
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                try:
                    filetype = users_info[username]["profile pic path"].split(".")[1]
                    os.remove("static//users data//users_icons//"+username + "." + filetype)
                except: pass
                file.save("static//users data//users_icons//"+filename)
                os.rename("static//users data//users_icons//"+filename,"static//users data//users_icons//"+username + "." +filename.split(".")[1])
                users_info[username]["profile pic path"] = "users data/users_icons/"+username + "." +filename.split(".")[1]
                save_users_information(users_info)
            else:
                flash('Illegal file type')
                return redirect(request.url) # return to the same url

        return redirect(url_for("show_my_profile"))
    else:

        users_for_js = return_users_for_js()
        return render_template("edit profile.html",login=login, profile_pic_path=profile_pic_path,username=username,  user_info=user_info,users_for_js=users_for_js)

@app.route("/remove profile image")
def remove_profile_image(): # set the user profile image to be the defult image
    global users_info
    if "username" in session:
        username = session["username"]
        users_info[username]["profile pic path"] = defult_profile_img_path
        save_users_information(users_info)
        return redirect(url_for("edit_profile"))
    else: return redirect(url_for("home"))

@app.route("/my profile")
def show_my_profile():
    if "username" in session:
        login = True
        username = session["username"]
        profile_pic_path = users_info[session["username"]]["profile pic path"]
        user_info = users_info[username].copy()
        try:
            user_info.pop("password")
            user_info.pop("email")
        except: pass
        user_info["posts divide to 3"] = split_list(user_info["posts"],3) # returning a list like this [[1,2,3],[4,5,6]]
        # user_info = {'username': 'yair', 'profile pic path': 'users data/users_icons/yair.PNG', 'profile description': 'This is my profile\r\nI made this web guys', 'posts': ['1']}
        posts_info = {}
        for post_id in user_info["posts"]:
            posts_info[post_id] = posts[post_id]

        users_for_js = return_users_for_js()
        return render_template("show profile.html",login=login, profile_pic_path=profile_pic_path,username=username,  user_info=user_info,posts_info=posts_info,users_for_js=users_for_js)

    else: return redirect(url_for("home"))


def delete_post(post_id,username):
    # delete from all of the dicts and delete the post photo
    users_info[username]["posts"].remove(post_id)
    os.remove("static//" + posts[post_id]["pic path"])
    posts.pop(post_id)

@app.route("/del/<post_id>")
def del_post(post_id):
    if not "username" in session or session["username"] != posts[post_id]["by"]: # if didnt log in or didnt upload the post
        return redirect(url_for("home"))
    username = session["username"]
    delete_post(post_id,username)
    save_users_information(users_info)
    save_posts(posts)
    return redirect(url_for("show_my_profile"))

@app.errorhandler(404)
def _404_page(e):
    profile_pic_path = None
    username = ""
    if "username" in session:
        login = True
        profile_pic_path = users_info[session["username"]]["profile pic path"]
        username = session["username"]
    else: login = False

    users_for_js = return_users_for_js()
    return render_template("404 page.html", login=login, profile_pic_path=profile_pic_path,username=username,users_for_js=users_for_js)

@app.route("/login", methods=["POST","GET"])
def login():
    if "username" in session:
        return  redirect(url_for("home"))
    else: login = False

    if request.method == "POST":
        username,password = request.form["username"],request.form["password"]
        if username == "" or password == "": # didnt enter username/password
            error = "You must fill in the username/password textboxes"
            users_for_js = return_users_for_js()
            return render_template("login logout create user files/login.html", login=login,  error=error,  username=username, password=password,users_for_js=users_for_js)
        else:
            # check if the username+password is true and exist if yes connect if not something else
            if username in users: # username exit
                if users[username] == password: # login
                    session["username"] = username
                    session["password"] = password
                    return redirect(url_for("home"))
                else:
                    error = "Wrong password"
                    users_for_js = return_users_for_js()
                    return render_template("login logout create user files/login.html", login=login,  error=error,  username=username, password=password,users_for_js=users_for_js)
            else: # username does not exist
                error = "Username does not exist"
                users_for_js = return_users_for_js()
                return render_template("login logout create user files/login.html", login=login,  error=error,  username=username, password=password,users_for_js=users_for_js)
    else:
        users_for_js = return_users_for_js()
        return render_template("login logout create user files/login.html", login=login,users_for_js=users_for_js)

def send_email(to,email):
    # sending email function
    with smtplib.SMTP("smtp.gmail.com",587) as smtp:
        smtp.ehlo()
        smtp.starttls()
        smtp.ehlo()

        smtp.login(sending_email,sending_email_password)
        
        subject = "Reset password in instagram clone"
        body = email

        msg = f"Subject: {subject}\n\n{body}"
        
        smtp.sendmail(sending_email, to,msg)

@app.route("/forgot password",methods=["POST","GET"])
def forgot_password():
    profile_pic_path = None
    username = ""
    if "username" in session:
        login = True
        profile_pic_path = users_info[session["username"]]["profile pic path"]
        username = session["username"]
    else: login = False

    if request.method == "POST":
        username1 = request.form["username"]
        if username1 == "":
            error = "You must fill in the textbox"
        else:
            if username1 in users_info:
                # will send an email
                user_email = users_info[username1]["email"]
                message = f"The user information you asked for is:\nUsername: {username1}\nPassword: {users_info[username1]['password']}\nEmail: {users_info[username1]['email']}"
                try:
                    send_email(user_email,message)
                    error = "An email has been send with the user information"
                except:
                    error = "There was an error while sending the email please try again later"
            else:
                error = "The username you entered does not exist"
        return render_template("login logout create user files/forgot password.html", login=login, profile_pic_path=profile_pic_path,username=username, error=error)
    else:
        return render_template("login logout create user files/forgot password.html", login=login, profile_pic_path=profile_pic_path,username=username)

regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b' # email format(using in check_email(email) function)
def check_email(email):
    # check if the email address is good
    if(re.fullmatch(regex, email)):
        return True
    else:
        return False

@app.route("/create user",methods=["POST","GET"])
def create_user():
    if "username" in session: # return to home page
        return  redirect(url_for("home"))
    else: login = False

    if request.method == "POST":
        username = request.form["username"]
        password,password_confirm = request.form["password"],request.form["password confirm"]
        email = request.form["email"]
        if username == "" or password == "" or password_confirm == "" or email == "": # 
            error = "You must fill in every textbox"
            users_for_js = return_users_for_js()
            return render_template("login logout create user files/create_user.html", login=login,error=error, username=username,password=password,password_confirm=password_confirm,email=email,users_for_js=users_for_js)
        else: # if he filled everything up
            if password != password_confirm:
                error = "password is not the same as password(confirm)"
                users_for_js = return_users_for_js()
                return render_template("login logout create user files/create_user.html", login=login,error=error, username=username,password=password,password_confirm=password_confirm,email=email,users_for_js=users_for_js)
            else: # password is good
                if check_email(email) == False: # email is not valid/good
                    error = "email is not valid"
                    users_for_js = return_users_for_js()
                    return render_template("login logout create user files/create_user.html", login=login,error=error, username=username,password=password,password_confirm=password_confirm,email=email,users_for_js=users_for_js)
                else: # check if the username is catch
                    if username in users or username == "defult": # username is catch(defult is using for other things such as defult icon and stuff)
                        error = "username is catch"
                        users_for_js = return_users_for_js()
                        return render_template("login logout create user files/create_user.html", login=login,error=error, username=username,password=password,password_confirm=password_confirm,email=email,users_for_js=users_for_js)
                    else: # everything is good and resume to the profile editing
                        create_a_user(username,password,email)
                        users_for_js = return_users_for_js()
                        return render_template("home.html",login=True,  show_js_profile_question = True) # show_js_profile_question if to tell the code to do the alert message(look at home.html to see)
    else:
        users_for_js = return_users_for_js()
        return render_template("login logout create user files/create_user.html", login=login,users_for_js=users_for_js)



@app.route("/logout")
def logout():
    try:
        session.pop("username")
        session.pop("password")
    except:
        pass
    return redirect(url_for("home"))

app.run(debug=True)