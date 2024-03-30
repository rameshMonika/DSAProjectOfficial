from flask import Blueprint,render_template,request,flash,redirect,url_for
from .models import User
from werkzeug.security import generate_password_hash, check_password_hash
from . import db   
from flask_login import login_user,login_required,logout_user,current_user

auth=Blueprint('auth',__name__)


@auth.route('/login', methods=['GET', 'POST'])
def login():
    error_message = None
    if request.method == 'POST':
        print("Login request received")
        email = request.form.get('email')
        password = request.form.get('password')
        user = User.query.filter_by(email=email).first()
        if user:
            if check_password_hash(user.password, password):
                print("Login successful")
                login_user(user,remember=True)
                return redirect(url_for('views.home'))
            else:
                error_message = "Error Please Try Again."
        else:
            error_message = "Error Please Try Again."
        return render_template("login.html", user=current_user, error_message=error_message)


             
                   
         
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
    print("Sign up request received")
    if request.method == 'POST':
            error_message = None
            email = request.form.get('email')
            first_name = request.form.get('firstName')
            password1 = request.form.get('password1')
            password2 = request.form.get('password2')
            print(email)
            print(first_name)

            print(password1)
            print(password2)

            user = User.query.filter_by(email=email).first()

            if user:
                 
                 error_message = "Email already exists"
                 print("Email already exists")
                 return render_template("sign_up.html", user=current_user, error_message=error_message)

            elif len(email)<4:
                 error_message = "Incorrect email format"
                 print("Incorrect email format")
                 return render_template("sign_up.html", user=current_user, error_message=error_message)
                 
            elif len(first_name)<2:
                 
                 error_message = "Incorrect name format"
                 print("Incorrect name format")
                 return render_template("sign_up.html", user=current_user, error_message=error_message)
            elif password1!=password2:
                 
                 error_message = "Passwords don\'t match"
                 print("Passwords don\'t match")
                 return render_template("sign_up.html", user=current_user, error_message=error_message)
            elif len(password1)<6:
                 
                 error_message = "Password does not meet requirement of more than 6 characters"
                 print("Password does not meet requirement of more than 6 characters")
                 return render_template("sign_up.html", user=current_user, error_message=error_message)
            else:
                
                 new_user = User(email=email, first_name=first_name, password=generate_password_hash(password1, method='scrypt'))
                 db.session.add(new_user)
                 db.session.commit()
                 login_user(new_user, remember=True)
                    
                 print("Account created")
                 return redirect(url_for("views.home"))

                # flash("Account created",category="success")
            

    return render_template("sign_up.html",user=current_user)
