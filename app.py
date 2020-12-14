# Thinks to do first when somebody use "," create bugs
""" 1. Main/Home page
 2. About page
 3. History page
 4. Register
 4.1 Register form class
 4.2 Register Main
 4.2 Check that you are logged in so you can't go to register page
 4.3 Register Main
 5. Login
 5.1 Check that user is logged in so user have access to some pages (dashboard and history)
 5.2 Logout
 6. Dashboard
 7. Payment
 7.1 PaymentForm
 7.2 Add payment
 7.3 Edit payment
 7.4 Delete payment from History
 7.5 Delete payment from dashboard


 """



from flask import Flask, render_template, flash, redirect, url_for, session, logging, request
#from data import payments
from flask_mysqldb import MySQL
from wtforms import Form, StringField, SelectField, IntegerField, PasswordField, validators
from passlib.hash import sha256_crypt
from functools import wraps #autorization


import pymysql
from datetime import datetime



app = Flask(__name__)

connection = pymysql.connect(host = 'localhost', user= 'root', passwd = '', database = 'tracker', cursorclass=pymysql.cursors.DictCursor)


#1. Main/Home page
@app.route('/')
def index():
    return render_template("home.html")
#2. About page
@app.route('/about')
def about():
    return render_template("about.html")


#3. History page
@app.route('/history')
def history():
    reverse = []
    payment_in_time = []
    name_type = ["food", "clothes", "entertainment", "other"]
    for i in range(12):
        payment_in_time.append(0)
    comprasion = []



    time = datetime.now()
    print(time)


        #Create cursor
    cur = connection.cursor()

    # Get payments
    result = cur.execute("SELECT * FROM payments WHERE user = %s", [session['username']])

    payments = cur.fetchall()

    if result > 0:
        for i in range(len(payments)):
            reverse.append(payments[-i-1])
        #Another loop
        for payment in payments:
            new_time=(datetime.now() - payment["date"])
            #print(type(new_time.days))
            # Przepisać to na 1 tablice dzięki czemu będzie się dało to wrzucić do słownika poprzez pętle


            if new_time.days<30:
                if payment["type"] == "Food":
                    payment_in_time[0] += payment["amount"]
                if payment["type"] == "Clothes":
                    payment_in_time[3] += payment["amount"]
                if payment["type"] == "Entertainment":
                    payment_in_time[6]+= payment["amount"]
                if payment["type"] == "Other":
                    payment_in_time[9] += payment["amount"]
            if new_time.days<182:
                if payment["type"] == "Food":
                    payment_in_time[1] += payment["amount"]
                if payment["type"] == "Clothes":
                    payment_in_time[4] += payment["amount"]
                if payment["type"] == "Entertainment":
                    payment_in_time[7]+= payment["amount"]
                if payment["type"] == "Other":
                    payment_in_time[10] += payment["amount"]
            if new_time.days<365:
                if payment["type"] == "Food":
                    payment_in_time[2] += payment["amount"]
                if payment["type"] == "Clothes":
                    payment_in_time[5] += payment["amount"]
                if payment["type"] == "Entertainment":
                    payment_in_time[8]+= payment["amount"]
                if payment["type"] == "Other":
                    payment_in_time[11] += payment["amount"]
        index = 0
        #print(payment_in_time)
        for i in range(4):

                #p
            sum_history = {
            "type": name_type[i],
            "sum_month":  (-payment_in_time[index]),
            "sum_6_month": (-payment_in_time[index+1]),
            "sum_year": (-payment_in_time[index+2])
            }
            index+=3
            comprasion.append(sum_history)



        return render_template("history.html", payments=reverse, comprasion = comprasion)
    else:
        msg = "No payments found"
        return render_template("history.html", msg=msg)

    # Close connection
    cur.close()


    return render_template("history.html")
# 4. Register
#r 4.1 Register form class
class RegisterForm(Form):
    name = StringField('Name',[validators.Length(min=1,max=50)])
    username = StringField('Username',[validators.Length(min=4,max=25)])
    email = StringField('Email',[validators.Length(min=6,max=50)])
    password = PasswordField('Password',[validators.DataRequired(),
    validators.EqualTo('confirm',message="Passwords do not match")
    ])
    confirm = PasswordField('Confirm Password')


#4.2 Check that you are logged in so you can't go to register page
def is_logged_in_reg(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            flash("You can't regiser account when you are logged in", 'danger')
            return redirect(url_for('dashboard'))
        else:
            return f(*args, **kwargs)
    return wrap
# 4.3 Register Main
@app.route("/register", methods=["GET","POST"])
@is_logged_in_reg
def register():
    form = RegisterForm(request.form)
    if request.method == "POST" and form.validate():
        name = form.name.data
        email = form.email.data
        username = form.username.data
        password = sha256_crypt.encrypt(str(form.password.data))

        #Create cursor
        cur = connection.cursor()

        #Get user by Username
        result = cur.execute("SELECT * FROM users WHERE username = %s", [username])
        cur.close()
        if result>0:
            error = "This username already exist, please another one "
            return render_template("register.html", error=error, form=form)
        else:

            # Create cursor

            cur = connection.cursor()

            # Execute query
            cur.execute("INSERT INTO users(name, email, username, password) VALUES(%s, %s, %s, %s)", (name, email, username, password))

            # Commit to DB
            connection.commit()

            # Close connection
            cur.close()
            flash('You are now registered and can log in ','success')
            redirect(url_for("index"))



    return render_template("register.html", form=form)


#5. Login
@app.route('/login',methods=['GET','POST'])
def login():
    if request.method == 'POST':
        #get Form fields
        username = request.form['username']
        password_candidate = request.form['password']

        #Create cursor
        cur = connection.cursor()

        #Get user by Username
        result = cur.execute("SELECT * FROM users WHERE username = %s", [username])

        if result > 0:
            # Get stored hash
            data = cur.fetchone()
            password = data["password"]


            #compare Passwords
            if sha256_crypt.verify(password_candidate,password):
                #Password and user correct
                session["logged_in"] = True
                session['username'] = username
                flash('You are logged in', 'success')
                return redirect(url_for("dashboard"))
                #app.logger.info('Pasword matched')## informacja wyskakuje w konsoli

            else:
                error = 'Invalid login'
                return render_template("login.html", error=error)
            #close connection
            cur.close()
        else:
            error = "Username not found"
            return render_template("login.html", error=error)


    return render_template("login.html")


#5.1 Check that user is logged in so user have access to some pages (dashboard and history)
def is_logged_in(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return f(*args, **kwargs)
        else:
            flash('Unauthorized, Please login', 'danger')
            return redirect(url_for('login'))
    return wrap


#  5.2 Logout
@app.route("/logout")
@is_logged_in
def logout():
    session.clear()
    flash("You are logout", 'success')
    return redirect(url_for('login'))

#6. Dashboard
@app.route('/dashboard')
@is_logged_in
def dashboard():
    last_10=[]
    safety_pillow=0
    current_savings=0
    all_savings=0

    #Create cursor
    cur = connection.cursor()

    # Get payments
    result = cur.execute("SELECT * FROM payments WHERE user = %s", [session['username']])

    payments = cur.fetchall()
    for payment in payments:
        all_savings+=payment["amount"]
        if payment["savings"]=="Current saving":
            current_savings+=payment["amount"]
        if payment["savings"]== "Safety pillow":
            safety_pillow+=payment["amount"]

    if result < 10:

        return render_template("dashboard.html", payments=payments,all_savings=all_savings,safety_pillow=safety_pillow,current_savings=current_savings)
    else:
        for i in range(10):
            last_10.append(payments[-i-1])
        return render_template("dashboard.html", payments = last_10)



    return render_template("dashboard.html")
# 7. Payment
#7.1 PaymentForm
class PaymentForm(Form):
    type = SelectField('type',choices = [("Food","Food"),("Clothes","Clothes"),("Rent","Rent"),
    ("Entertainment","Entertainment"),("Other","Other"),("Income","Income")])
    amount = StringField('amount')
    savings = SelectField('savings',choices = [("Current saving","Current saving"),("Safety pillow","Safety pillow")])

#7.2 Add payment
@app.route('/add_payment',methods=['GET','POST'])
@is_logged_in
def add_payment():
    form = PaymentForm(request.form)
    if request.method =="POST" and form.validate():
        type = form.type.data
        amount = form.amount.data
        savings = form.savings.data

        try:

            #Create cursor
            cur = connection.cursor()

            #execute
            cur.execute("INSERT INTO payments(type, amount, savings,user) VALUES(%s, %s, %s,%s)",(type, amount, savings, session['username']))
            #Commit
            connection.commit()
            #close connection
            cur.close()


            flash('Payment Created', 'success')

            return redirect(url_for('dashboard'))
        except:
            flash('Wrong format try use . when you use float number','danger')
            return render_template("add_payment.html", form=form)



    return render_template("add_payment.html", form=form)

# 7.3 Edit payment

@app.route('/edit_payment/<string:id>',methods=['GET','POST'])
@is_logged_in
def edit_payment(id):
    # create cursor
    cur =connection.cursor()
    #Get payment by id
    result = cur.execute("SELECT * FROM payments WHERE id = %s", [id])

    payment = cur.fetchone()

    #Get Form
    form = PaymentForm(request.form)

    #Populate payment form fields

    form.type.data = payment['type']
    form.amount.data = payment['amount']
    form.savings.data = payment['savings']


    # close connection
    cur.close()
    if request.method =="POST" and form.validate():
        type = request.form['type']
        amount = request.form['amount']
        savings = request.form['savings']
        try:

            #Create cursor
            cur = connection.cursor()

            #execute
            cur.execute("UPDATE payments SET type=%s, amount=%s,savings=%s WHERE id=%s",(type, amount,savings, id))
            #Commit
            connection.commit()
            #close connection
            cur.close()

            flash('Payment Updated', 'success')

            return redirect(url_for('history'))
        except:
            flash('Wrong format try use . when you use float number','danger')
            return render_template("edit_payment.html", form=form)
    return render_template("edit_payment.html", form=form)

# 7.4 Delete payment from History
@app.route('/payment/<string:id>', methods=['POST'])
@is_logged_in
def delete_payment(id):
    # Create cursor
    cur = connection.cursor()

    # Execute
    cur.execute("DELETE FROM payments WHERE id = %s", [id])

    # Commit to DB
    connection.commit()

    #Close connection
    cur.close()

    flash('Payment Deleted', 'success')

    return redirect(url_for('history'))

# 7.5 Delete payment from dashboard
@app.route('/payment/<string:id>', methods=['POST'])
@is_logged_in
def delete_payment_dash(id):
    # Create cursor
    cur = connection.cursor()

    # Execute
    cur.execute("DELETE FROM payments WHERE id = %s", [id])

    # Commit to DB
    connection.commit()

    #Close connection
    cur.close()

    flash('Payment Deleted', 'success')

    return redirect(url_for('dashboard'))

#8. Search in history
#8.1 SearchForm
class SearchForm(Form):
    search_type = SelectField('type',choices = [("Food","Food"),("Clothes","Clothes"),("Rent","Rent"),
    ("Entertainment","Entertainment"),("Other","Other"),("Income","Income")])
    number_search = SelectField('number',choices = [("10","10"),("20","20"),("30","30"),
    ("40","40")])

#8.2 Search main
@app.route("/search_history", methods=['GET','POST'])
@is_logged_in
def search_history():
    form = SearchForm(request.form)
    number = 0
    reverse = []
    payments_list= []
    if request.method =="POST" and form.validate():
        search_type = form.search_type.data
        number_search = form.number_search.data
        print(number_search)

        #Create cursor
        cur = connection.cursor()
        # Get all payments
        result = cur.execute("SELECT * FROM payments WHERE user = %s", [session['username']])

        payments = cur.fetchall()


        if result > 0:
            for i in range(len(payments)):

                reverse.append(payments[-i-1])
                #print(reverse[i]["type"])
                if number< int(number_search):
                    if reverse[i]["type"] == search_type:
                        payments_list.append(reverse[i])
                        number+=1

                        
            return render_template("search_history.html", form=form, payments_list = payments_list)


        else:
            msg = "No payments in type"+search_type + " found"
            return render_template("search_history.html", form=form, msg=msg)



    return render_template("search_history.html", form=form)

if __name__ == "__main__":
    app.secret_key="secret123"
    app.run(debug=True)
