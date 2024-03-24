from flask import Blueprint,render_template,request,flash,redirect,url_for
from .models import User
from werkzeug.security import generate_password_hash, check_password_hash
from . import db   
from flask_login import login_user,login_required,logout_user,current_user

auth=Blueprint('auth',__name__)


@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        user = User.query.filter_by(email=email).first()
        if user:
            if check_password_hash(user.password, password):
                print("Login successful")
                login_user(user,remember=True)
                return redirect(url_for('views.home'))
            else:
                print("Incorrect credentials")


             
                   
         
    data= request.form
    print(data)
    return render_template("login.html",user=current_user)

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))

@auth.route('/sign-up', methods=['GET', 'POST'])
def sign_up():
    if request.method == 'POST':
            email = request.form.get('email')
            first_name = request.form.get('firstName')
            password1 = request.form.get('password1')
            password2 = request.form.get('password2')
            print("Password1: "+password1)
            print("Password2: "+password2)

            user = User.query.filter_by(email=email).first()

            if user:
                 print("Email already exists")
                 pass

            elif len(email)<4:
                 print("Incorrect email format")
                 #flash("Incorrect email format",category='error')
            elif len(first_name)<2:
                 print("Incorrect name format")
                 #flash("Incorrect name format",category='error')
            elif password1!=password2:
                 print("Passwords don\'t match")
                # flash("Passwords don\'t match ",category='error')
            elif len(password1)<6:
                 print("Password does not meet requirement")
                 #flash("Password does not meet requirement",category='error')
            else:
                
                 new_user = User(email=email, first_name=first_name, password=generate_password_hash(password1, method='scrypt'))
                 db.session.add(new_user)
                 db.session.commit()
                 login_user(user,remember=True)
                    
                 print("Account created")
                 return redirect(url_for("views.home"))

                # flash("Account created",category="success")
            

    return render_template("sign_up.html",user=current_user)
