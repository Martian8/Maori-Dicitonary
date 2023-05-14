from flask import Flask, render_template, request, redirect, session
import sqlite3
from flask_bcrypt import Bcrypt

app = Flask(__name__)
DB = "dictionary.sqlite3"
app.secret_key = "5als3bKd4Sasjf6969lrkvn"
bcrypt = Bcrypt(app)

def create_connection(sql):
    try:
        return sqlite3.connect(sql)
    except sqlite3.Error:
        print(sqlite3.Error)
    return(None)

@app.route("/cat/<CategoryId>")
def render_category(CategoryId):
    db = create_connection(DB)
    cur = db.cursor()
    query = "SELECT * FROM Categories"
    categories = cur.execute(query).fetchall()
    query = "SELECT * FROM MaoriDictionary WHERE CategoryId=?"
    terms = cur.execute(query, (CategoryId, )).fetchall()
    return render_template('base.html', categories=categories, terms=terms)


@app.route('/')
def render_home():
    return render_template("home.html")

"""
def logout():
    session.pop('username', None)
    session.pop('display_name', None)


def get_user():
    if ("email" in session) and ("display_name" in session):
        email = session["email"]
        display_name = session["display_name"]
        print(session)
        if email is None or display_name is None:
            return False
        return [display_name, email]
    else:
        print("oops")
    return False

def checkPasswordSecurity(password, password2):
    if password != password2:
        return "\signup?error=Passwords+do+not+match"
    if len(password)<8:
        return "\signup?error=Passwords+must+be+at+least+8+characters"
    hasLetter = True in [i.isalpha() for i in password]
    hasNumber = True in [i.isnumeric() for i in password]
    hasSpecialChar = False in [i.isalnum() for i in password]
    if hasLetter and hasNumber and hasSpecialChar:
        return None
    else:
        return "\signup?error=Passwords+must+have+a+letter+a+number+and+a+special+character"



@app.route('/')
def render_home():
    print("home")
    user = get_user()
    return render_template('home.html', user=user)

@app.route('/menu/<CategoryId>')
def render_menu(CategoryId):
    user = get_user()

    db = create_connection(DB)
    cur = db.cursor()
    if CategoryId == "0":
        menu = cur.execute(
            "SELECT * FROM SmileMenu ORDER BY Name ASC").fetchall()
    else:
        menu = cur.execute(
            "SELECT * FROM SmileMenu WHERE CategoryId=? ORDER BY Name ASC", (CategoryId)).fetchall()

    categories = cur.execute("SELECT * FROM Category").fetchall()
    return render_template('menu.html', menu=menu, categories = categories, user=user)

@app.route("/menu")
def render_cart():
    user = get_user()
    db = create_connection(DB)
    cur = db.cursor()
    cart = 2

@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html"), 404

@app.route('/admin')
def render_admin():
    user = get_user()
    if not user:
        return redirect('/?error=not+logged+in')
    db = create_connection(DB)
    cur = db.cursor()
    categories = cur.execute("SELECT * FROM Category").fetchall()
    menu = cur.execute('SELECT * FROM SmileMenu')
    return render_template('admin.html', user=user, categories=categories, menu=menu)

@app.route("/addCategory", methods=["POST"])
def addCategory():
    user = get_user()
    if not user:
        return redirect('/?error=not+logged+in')
    cat_name = request.form.get("categoryName")
    db = create_connection(DB)
    query = "INSERT INTO Category ('name') VALUES (?)"
    cur = db.cursor()
    cur.execute(query, (cat_name, ))
    db.commit()
    db.close()
    return redirect("/admin")


@app.route("/deleteCategory", methods=["POST"])
def deleteCategory():
    user = get_user()
    if not user:
        return redirect('/?error=not+logged+in')
    category = request.form.get("catId")
    print(category)
    category = category.split(", ")
    catId, catName = category[0], category[1]
    return render_template("/deleteConfirm.html", id=catId, name=catName, type="Category")

@app.route("/deleteCategoryConfirm/<catId>")
def deleteCategoryConfirm(catId):
    user = get_user()
    if not user:
        return redirect('/?error=not+logged+in')
    db = create_connection(DB)
    query = "DELETE FROM Category WHERE Id = ?"
    cur = db.cursor()
    cur.execute(query, (catId, ))
    db.commit()
    db.close()
    return redirect("/admin")


@app.route("/addItem", methods=["POST"])
def addItem():
    user = get_user()
    if not user:
        return redirect('/?error=not+logged+in')
    Name, Description, Size, Image, Price, Category = request.form.get("itemName"),request.form.get("itemDescription"),request.form.get("itemSize"),request.form.get("imageName"),request.form.get("itemPrice"),request.form.get("itemCategory")
    db = create_connection(DB)
    query = "INSERT INTO SmileMenu ('Name', 'Description', 'Size', 'Image', 'Price', 'CategoryId') VALUES (?,?,?,?,?,?)"
    cur = db.cursor()
    cur.execute(query, (Name, Description,Size, Image, Price, Category))
    db.commit()
    db.close()
    return redirect("/admin")

@app.route("/deleteItem", methods=["POST"])
def deleteItem():
    user = get_user()
    if not user:
        return redirect('/?error=not+logged+in')
    item = request.form.get("item")
    item = item.split(", ")
    itemId, itemName = item[0], item[1]
    return render_template("/deleteConfirm.html", id=itemId, name=itemName, type="Item")

@app.route("/deleteItemConfirm/<itemId>")
def deleteItemConfirm(itemId):
    user = get_user()
    if not user:
        return redirect('/?error=not+logged+in')
    db = create_connection(DB)
    query = "DELETE FROM SmileMenu WHERE Id = ?"
    cur = db.cursor()
    cur.execute(query, (itemId, ))
    db.commit()
    db.close()
    return redirect("/admin")


@app.route('/contact')
def render_contact():
    user = get_user()
    return render_template('contact.html', user=user)

@app.route('/login', methods=['POST', 'GET'])
def render_login():
    user = get_user()
    if user:
        logout()
        return redirect("/")
    if request.method == 'POST':
        email = request.form['email'].lower().strip()
        password = request.form['password'].strip()
        db = create_connection(DB)        
        cur = db.cursor()
        query = cur.execute("SELECT * FROM User WHERE email=?", (email,))
        user_data = query.fetchone()
        db.close()
        print(user_data)
        if user_data is None:
            return redirect("\login?error=Email+or+password+incorrect")
        try:    
            db_email = user_data[3]
            db_username = user_data[1]+user_data[2]
            db_password = user_data[4]
        except IndexError:
            return redirect("\login?error=Email+or+password+incorrect")
        if not bcrypt.check_password_hash(db_password, password):
            return redirect("\login?error=Email+or+password+incorrect")
        print("got here")
        session['email'] = db_email
        session['display_name']=db_username
        return redirect('/')
    return render_template("login.html", user=user)


@app.route('/signup', methods=['POST', 'GET'])
def render_signup():
    user = get_user()
    if request.method == 'POST':
        print(request.form)
        fname = request.form.get('fname').title().strip()
        lname = request.form.get('lname').title().strip()
        email = request.form.get('email').lower().strip()
        password = request.form.get('password')
        password2 = request.form.get('password2')
        passwordSecurity = checkPasswordSecurity(password,password2)
        if passwordSecurity!=None:
            return redirect(passwordSecurity)
        password = bcrypt.generate_password_hash(password)
        db = create_connection(DB)
        cur = db.cursor()
        query = "INSERT INTO user (fname, lname, email, password) VALUES(?,?,?,?)"

        try:
            cur.execute(query, (fname, lname, email, password))
        except sqlite3.IntegrityError:
            cur.close()
            return redirect("\signup?error=Email+has+already+been+used")
        db.commit()
        cur.close()
        return redirect('login')
    return render_template("signup.html", user=user)
"""

if __name__ == '__main__':
    app.run(debug=True)
