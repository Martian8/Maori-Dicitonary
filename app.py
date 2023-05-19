from flask import Flask, render_template, request, redirect, session
import sqlite3
from flask_bcrypt import Bcrypt
from datetime import datetime

app = Flask(__name__)
DB = "dictionary.sqlite3"
app.secret_key = "5als3bKd4Sasjf6969lrkvn"
bcrypt = Bcrypt(app)
# These are used to check which characters can be used for english/maori terms
MAORI_CHARACTERS = ['q','w','e','r','t','y','u','i','o','p','a','s','d','f','g','h','j','k','l','z','x','c','v','b','n',
                    'm','Q','W','E','R','T','Y','U','I','O','P','A','S','D','F','G','H','J','K','L','Z','X','C','V','B',
                    'N','M','ā','ē','ī','ō','ū','Ā','Ē','Ī','Ō','Ū', "'", '-', ' ', '(', ')',',']
ENGLISH_CHARACTERS = ['q','w','e','r','t','y','u','i','o','p','a','s','d','f','g','h','j','k','l','z','x','c','v','b',
                      'n','m','Q','W','E','R','T','Y','U','I','O','P','A','S','D','F','G','H','J','K','L','Z','X','C',
                      'V','B','N','M', "'", '-', ' ', '(', ')'',']

# This function establishes a connection to the database
def create_connection(sql):
    try:
        return sqlite3.connect(sql)
    except sqlite3.Error:
        print(sqlite3.Error)
    return (None)

# All database interactions are compressed into this one function
# The arguments inside each data request are: The query, the tuple (false if no tuple), and whether it should fetchone 
# fetchall or commit
def db_interact(data_requests):
    db = create_connection(DB)
    cur = db.cursor()
    results = []
    # Allows for multiple database interactions just by calling the function once
    for data_request in data_requests:
        # If there is an tuple input to sanitise or not
        if data_request[1]:
            temp = cur.execute(data_request[0], data_request[1])
        else:
            temp = cur.execute(data_request[0])
        # Fetch one or all, or commit (delete or add)
        print(data_request)
        if data_request[2] == "fetchone":
            results.append(temp.fetchone())
        elif data_request[2] == "fetchall":
            results.append(temp.fetchall())
        elif data_request[2] == "commit":
            db.commit()
            print("commited")
    # Closes the database
    db.close()
    return results

# This stores the user information in the session so that they stay logged in when navigating different pages
def get_user():
    if ("username" in session):
        # This moves the data from the session into the webpage
        display_name = session["username"]
        permission = session["permission"]
        if display_name is None:
            # if there is no user information, it returns the user as false (nonexistent)
            return False
        return [display_name, permission]
    # if there is no user information, it returns the user as false (nonexistent)
    return False

# logs the user out by removing their information from the session
def logout():
    session.pop("username", None)
    session.pop("email", None)
    session.pop("permission", None)
    session.pop("id", None)

# This function checks the validity of various terms
def validity(type, value):
    match(type):
        # A password should: 
        case "password":
            # Match with the confirm password variable
            if value[0] != value[1]:
                return "\signup?error=Passwords+do+not+match"
            # Be at least 8 characters, 
            if len(value[0]) < 8:
                return "\signup?error=Passwords+must+be+at+least+8+characters"
            # Have at least one letter, number, and special character
            hasLetter = True in [i.isalpha() for i in value[0]]
            hasNumber = True in [i.isnumeric() for i in value[0]]
            hasSpecialChar = False in [i.isalnum() for i in value[0]]
            if hasLetter and hasNumber and hasSpecialChar:
                return None
            else:
                return "\signup?error=Passwords+must+have+a+letter+a+number+and+a+special+character"
        # Word levels should be an integer between 1 and 10
        case "level":
            try:
                if 1<=(int(value))<=10:
                    return None
            except:
                0
            return("\?error=Level+must+be+between+1+and+10")
        # Maori words should only contain certain charcacers (Listed in the constant MAORI_CHARACTERS)
        case "maori":
            for char in value:
                if char not in MAORI_CHARACTERS:
                    return("\?error=Unaccepted+characters+used+in+the+maori+word")
            return None
        # English words should only contain certain charcacers (Listed in the constant ENGLISH_CHARACTERS)
        case "english":
            for char in value:
                if char not in ENGLISH_CHARACTERS:
                    return("\?error=Unaccepted+characters+used+in+the+english+word")
            return None
        # Usernames need to be between 3 and 20 characters long
        case "username":
            if len(value)>20 or len(value)<3:
                return("\?error=Username+must+be+between+3+and+20+characters")
            return None

# Renders the home page
@app.route("/")
def render_home():
    user = get_user()
    categories, terms, term_detailed = db_interact([["SELECT * FROM categories", False, "fetchall"], [
                                                   "SELECT * FROM maori_dictionary", False, "fetchall"], 
                                                   ["SELECT * FROM maori_dictionary WHERE id=?", (0, ), "fetchone"]])
        #passes through any errors sent to the page
    error = request.args.get("error")
    return render_template("home.html", categories=categories, terms=terms, user=user, error=error)

# Renders the category page, where only words from a certain category are displayed
@app.route("/cat/<category_id>")
def render_category(category_id):
    user = get_user()
    categories, terms = db_interact([["SELECT * FROM categories", False, "fetchall"], [
                                                   "SELECT * FROM maori_dictionary WHERE category_id=?", (category_id, )
                                                   , "fetchall"]])
    error = request.args.get("error")
    return render_template("home.html", categories=categories, terms=terms, user=user, error=error)

# Renders the term page, where detailed information about a certain term is displayed
@app.route("/term/<termid>")
def render_term(termid):
    user = get_user()
    categories, term_detailed = db_interact([["SELECT * FROM categories", False, "fetchall"], 
                                             ["SELECT * FROM maori_dictionary WHERE id=?", (termid, ), "fetchone"]])
    term_category, editing_user  = db_interact([["SELECT category_name FROM categories WHERE id=?", (term_detailed[3], ), 
                                                 "fetchone"], ["SELECT username FROM user WHERE id=?", (term_detailed[8], ), "fetchone"]])
    error = request.args.get("error")
    return render_template("term.html", categories=categories,  term_category=term_category, term_detailed=term_detailed
                           , user=user, error=error, editing_user=editing_user)

# Renders the login page, where users can log in
@app.route("/login", methods=["POST", "GET"])
def render_login():
    user = get_user()
    categories,  = db_interact(
        [["SELECT * FROM categories", False, "fetchall"]])
    # This page is also used to log users out if they are logged in
    if user:
        logout()
        return redirect("/")
    # If they have submitted the form, the method is post, and this section logs them in
    if request.method == "POST":
        # Assigns to variable and formats the email and password
        email = request.form["email"].lower().strip()
        password = request.form["password"].strip()
        # Gets the user data to check they submitted the right email and password and to get their other information
        user_data,  = db_interact(
            [["SELECT * FROM user WHERE email=?", (email, ), "fetchone"]])
        # Checks they used the right email
        try:
            db_id = user_data[0]
            db_username = user_data[1]
            db_email = user_data[2]
            db_password = user_data[3]
            db_permission = user_data[4]
        except IndexError:
            return redirect("\login?error=Email+or+password+incorrect")
        # Checks they used the right password
        if not bcrypt.check_password_hash(db_password, password):
            return redirect("\login?error=Email+or+password+incorrect")
        # Login successful, assigns the user information to the new values
        session["email"] = db_email
        session["username"] = db_username
        session["permission"] = db_permission
        session["id"] = db_id
        return redirect("/")
    # If they have not completed the form and are just trying to view the page, this renders it for them
    error = request.args.get("error")
    return render_template("login.html", user=user, categories=categories, error=error)

# Renders the signup page, where users can sign up
@app.route("/signup", methods=["POST", "GET"])
def render_signup():
    user = get_user()
    categories,  = db_interact(
        [["SELECT * FROM categories", False, "fetchall"]])
    # If they submitted the form
    if request.method == "POST":
        # Retrieves the data, and formats it correctly
        username = request.form.get("username").title().strip()
        email = request.form.get("email").lower().strip()
        password = request.form.get("password")
        password2 = request.form.get("password2")
        is_teacher = request.form.get("is_teacher")
        # Checks the validity of the password
        passwordSecurity = validity("password", [password, password2])
        if passwordSecurity != None:
            return redirect(passwordSecurity)
        # Checks the validity of the username
        usernameValidity = validity("username", username)
        if usernameValidity != None:
            return redirect(usernameValidity)
        # Hashes the password befor inserting it into the database
        password = bcrypt.generate_password_hash(password)
        try:
            db_interact([["INSERT INTO user (username, email, password, is_teacher) VALUES(?,?,?, ?)",
                        (username, email, password, is_teacher), "commit"]])
        # Checks the email hasnt already been used
        except sqlite3.IntegrityError:
            return redirect("\signup?error=Email+has+already+been+used")
        return redirect("login")
    # Shows the page if they are just viewing, not submitting the form yet
    error = request.args.get("error")
    return render_template("signup.html", user=user, categories=categories, error=error)

# Handles all database editing. edit_type is add, update, or delete, cat_or_term says whether it is a category or a term
@app.route("/edit/<edit_type>/<cat_or_term>/<id>")
def render_edit(edit_type, cat_or_term, id):
    user = get_user()
    # Redirects away if they dont have editing permission or aren't logged in
    if not user:
        return redirect("\?You+dont+have+permission+to+edit")
    if not user[1]:
        return redirect("\?You+dont+have+permission+to+edit")
    # If they are viewing the form to add or update a term, additional information needs to 
    # be retrieved from the database
    if (edit_type == "add" or edit_type == "update") and (cat_or_term == "term"):
        categories, terms, term_detailed = db_interact([["SELECT * FROM categories", False, "fetchall"], [
                                                       "SELECT * FROM maori_dictionary ORDER BY maori ASC", False, 
                                                       "fetchall"], ["SELECT * FROM maori_dictionary WHERE id=?", 
                                                                     (id, ), "fetchone"]])
        # To help the auto complete when updating a term, this fetches the category name
        if edit_type=="update":
            term_category,  = db_interact([["SELECT category_name FROM categories WHERE id=?", (term_detailed[3], ),
                                             "fetchone"]])
            return render_template("edit.html", user=user, categories=categories, terms=terms, 
                                   term_category=term_category,edit_type=edit_type, cat_or_term=cat_or_term, 
                                   id=id, term_detailed=term_detailed)
        return render_template("edit.html", user=user, categories=categories, terms=terms, edit_type=edit_type, 
                               cat_or_term=cat_or_term, id=id, term_detailed=term_detailed)
    categories, terms = db_interact([["SELECT * FROM categories", False, "fetchall"], [
                                    "SELECT * FROM maori_dictionary ORDER BY maori ASC", False, "fetchall"]])
    error = request.args.get("error")
    return render_template("edit.html", user=user, categories=categories, terms=terms, edit_type=edit_type, 
                           cat_or_term=cat_or_term, id=id, error=error)

# if they are submitting the form to edit the database it goes through here
@app.route("/edit/<edit_type>/<cat_or_term>", methods=["POST"])
def edit(edit_type, cat_or_term):
    user = get_user()
    # Redirects away if they dont have editing permission
    if not user:
        return redirect("\?You+dont+have+permission+to+edit")
    if not user[1]:
        return redirect("\?You+dont+have+permission+to+edit")
    # Fetches the id, since that is used no matter what
    id = request.form.get("id")
    # If it's a category or term
    print(cat_or_term, edit_type)
    match(cat_or_term):
        case "cat":
            match(edit_type):
                # Adding a category
                case "add":
                    category_name = request.form.get("category_name")
                    db_interact(
                        [["INSERT INTO categories (category_name) VALUES (?)", (category_name, ), "commit"]])
                case "update":
                # Updating a category deletes it than readds it with the new name
                    db_interact(
                        [["DELETE FROM categories WHERE (id) = ?", (id, ), "commit"]])
                    category_name = request.form.get("category_name")
                    db_interact(
                        [["INSERT INTO categories (id,category_name) VALUES (?, ?)", (id, category_name), "commit"]])
                # Deleting a category also deletes all terms in the category
                case "delete":
                    db_interact([["DELETE FROM maori_dictionary WHERE (category_id) = ?", (id, ), "commit"], [
                                "DELETE FROM categories WHERE (id) = ?", (id, ), "commit"]])
        case "term":
            match(edit_type):
                # If adding or updating a term this retrieves data, and checks validity
                case "add" | "update":
                    maori, english, category_id, definition, level, image = request.form.get("maori"), 
                    request.form.get("english"), request.form.get("category_id"), request.form.get("definition"), 
                    request.form.get("level"), request.form.get("image")
                    maoriValid, englishValid, levelValid = validity("maori", maori), validity("english", english), 
                    validity("level", level)
                    if maoriValid is not None:
                        return redirect(maoriValid)
                    if englishValid is not None:
                        return redirect(englishValid)
                    if levelValid is not None:
                        return redirect(levelValid)
                    # Gets the date and the user that edited it
                    editing_user = session["id"]
                    now = str(datetime.now())
                    # Removes the seconds and millisconds from the edit time
                    now = now[:len(now)-10]
                    match(edit_type):
                        # adds a term
                        case "add":
                            db_interact([["INSERT INTO maori_dictionary (maori, english, category_id, definition,"/
                                          "level, image, last_edited, edited_by) VALUES (?,?,?,?,?,?,?,?)", 
                                          (maori, english, category_id, definition, level, image, now, editing_user), 
                                          "commit"]])
                        # updates a term by deleting then reading it with the new information
                        case "update":
                            db_interact(
                                [["DELETE FROM maori_dictionary WHERE (id) = ?", (id, ), "commit"]])
                            db_interact([["INSERT INTO maori_dictionary (id, maori, english, category_id, definition,"/
                                          "level,image,last_edited, edited_by) VALUES (?,?,?,?,?,?,?,?,?)", (
                            id,maori, english, category_id, definition, level, image, now, editing_user),"commit"]])
                # deletes a term
                case "delete":
                    db_interact([["DELETE FROM maori_dictionary WHERE (id) = ?", (id, ), "commit"]])
    # Once the editing is finished, go back home
    return redirect("/")

# If the url wasn't recognised, this allows for quickly going back home.
@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html"), 404

# Runs the program
if __name__ == "__main__":
    app.run(port=6969, debug=True)