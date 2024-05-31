from flask import Flask, request, render_template, url_for, redirect, get_flashed_messages, jsonify, flash, session
from flask_bcrypt import Bcrypt
from flask_wtf import FlaskForm
from flask_login import current_user, LoginManager, login_user, logout_user, login_required, UserMixin
from wtforms import StringField, PasswordField, SubmitField, BooleanField, DateField, RadioField, IntegerField
from wtforms.validators import DataRequired, Email, EqualTo, Length, ValidationError, NumberRange
from flask_sqlalchemy import SQLAlchemy
import requests
import secrets



# Initializing Flask App
app = Flask(__name__)
app.config['SECRET_KEY'] = 'f0581e8a6a286b32168928b17f8a31d8'

# Initializing bcrypt 
bcrypt = Bcrypt(app)


# Initializing database
db = SQLAlchemy(app)
username='ronnierflask'
password= 'Tootsie@1430'
port = '3306'
host = 'localhost'
database_name= 'eeadmin'
app.config['SQLALCHEMY_DATABASE_URI'] = f'mysql+pymysql://{username}:{password}@{host}:{port}/{database_name}?charset=utf8mb4' # Modify MySQL database configuration to include the charset=utf8mb4 parameter to support unicode text


# Creating class for User Admin using db.Model and UserMixin Resource
class UserAdmin(UserMixin, db.Model): 
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    firstname = db.Column(db.String(255))
    lastname = db.Column(db.String(255))
    username = db.Column(db.String(255))
    email = db.Column(db.String(255))
    password = db.Column(db.String(255))
    date_of_birth = db.Column(db.Date)
    gender = db.Column(db.String(10))



# Creating class for Register form using FlaskForm Resource
class RegisterForm(FlaskForm):
    firstname = StringField('Firstname', validators=[DataRequired(), Length(min=2, max=20)])
    lastname = StringField('Lastname', validators=[DataRequired(), Length(min=2, max=20)])
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[EqualTo('password', message='Passwords must match')])
    date_of_birth = DateField('Birthdate')
    gender = RadioField('Gender', choices=[('male', 'Male'), ('female', 'Female')])
    submit = SubmitField('Submit')


    def validate_username(self, username):
        user = UserAdmin.query.filter_by(username=username.data).first()

        if user:
            raise ValidationError('Username already exist. Please choose other username')
    

    def validate_email(self, email):
      
        email = UserAdmin.query.filter_by(email=email.data).first()

        if email:
            raise ValidationError('Email already exists. Please choose other email')
        

# Creating class for Add Question form using FlaskForm Resource
class AddQuestions(FlaskForm):
    question = StringField('Question', validators=[DataRequired()])
    opn_a = StringField('Option A', validators=[DataRequired()])
    opn_b = StringField('Option B', validators=[DataRequired()])
    opn_c = StringField('Option C', validators=[DataRequired()])
    opn_d = StringField('Option D', validators=[DataRequired()])
    correct_a = RadioField('Is option A correct?', validators=[DataRequired()], choices=[(True,'True'), (False,'False')])
    correct_b = RadioField('Is option B correct?', validators=[DataRequired()], choices=[(True,'True'), (False,'False')])
    correct_c = RadioField('Is option C correct?', validators=[DataRequired()], choices=[(True,'True'), (False,'False')])
    correct_d = RadioField('Is option D correct?', validators=[DataRequired()], choices=[(True,'True'), (False,'False')])
    course = RadioField('Course on which to add the question', validators=[DataRequired()], choices=[('elecs','Electronics'), ('comms','Communications'),('math','Math'), ('geas','GEAS')])
    submit = SubmitField('Add to database')

    def get_null_fields(self):
        null_fields = []
        for field_name, field in self._fields.items():
            if field.data is None:
                null_fields.append(field_name)
        return null_fields



# Creating class for Login Form using FlaskForm Resource
class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember me')
    submit = SubmitField('Login')



# Creating class for Update Question form using FlaskForm Resource
class UpdateQuestion(FlaskForm):
    question_id = IntegerField('ID of the question you want to update', validators=[DataRequired(), NumberRange(min=0, max=100)])
    content = StringField('Type the question', validators=[DataRequired()])
    submit = SubmitField('Update')



# Creating class for Update Options form using FlaskForm Resource
class UpdateOptions(FlaskForm): 
   question_id = IntegerField('Question ID', validators=[DataRequired(), NumberRange(min=1, max=100)])
   opn_a = StringField('Option A', validators=[DataRequired()])
   opn_b = StringField('Option B', validators=[DataRequired()])
   opn_c = StringField('Option C', validators=[DataRequired()])
   opn_d = StringField('Option D', validators=[DataRequired()])
   correct_a = RadioField('Is option A correct?', validators=[DataRequired()], choices=[(True,'True'), (False,'False')])
   correct_b = RadioField('Is option B correct?', validators=[DataRequired()], choices=[(True,'True'), (False,'False')])
   correct_c = RadioField('Is option C correct?', validators=[DataRequired()], choices=[(True,'True'), (False,'False')])
   correct_d = RadioField('Is option D correct?', validators=[DataRequired()], choices=[(True,'True'), (False,'False')])
   submit = SubmitField('Update')
   


# Initializing Login Manager 
login_manager = LoginManager(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return UserAdmin.query.get(int(user_id))



@app.route('/admin-register', methods=['GET', 'POST'])
def register():

    form = RegisterForm()
    if request.method == 'POST':
      if form.validate_on_submit():
             hashed_pw = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
             admin = UserAdmin(firstname=form.firstname.data, lastname=form.lastname.data, 
                             username=form.username.data, email=form.email.data, password=hashed_pw, 
                             date_of_birth=form.date_of_birth.data, gender=form.gender.data)
             db.session.add(admin)
             db.session.commit()
             return redirect(url_for('login'))
 
    
    return render_template('admin-register.html', form=form)



@app.route('/admin-login', methods=['GET', 'POST'])
def login():

    form = LoginForm()
    if request.method == 'POST': 
        if form.validate_on_submit():
            user = UserAdmin.query.filter_by(email=form.email.data).first()
            if user and bcrypt.check_password_hash(user.password, form.password.data):
                login_user(user)
                return redirect(url_for('add_question'))
            

    return render_template('admin-login.html', form=form)


@app.route('/admin-logout')
def logout():
    logout_user()
    return redirect(url_for('login'))



@app.route('/add-question', methods=['GET', 'POST'])
@login_required
def add_question():

    form = AddQuestions()
    messages = get_flashed_messages()
    

    if request.method == 'POST':
        question = {'content':request.form['question'], 'options':[
            {'letter': 'A', 'content': form.opn_a.data, 'is_correct':form.correct_a.data =='True'},
            {'letter': 'B', 'content': form.opn_b.data, 'is_correct':form.correct_b.data=='True'},
            {'letter': 'C', 'content': form.opn_c.data, 'is_correct':form.correct_c.data=='True'},
            {'letter': 'D', 'content': form.opn_d.data, 'is_correct':form.correct_d.data=='True'}
            ]}
        
        if form.validate_on_submit():  
             if form.course.data == 'elecs':
               url = 'http://127.0.0.1:5000/elecsqn-api'
               response = requests.post(url, json=question) 

               if response.status_code == 200:
                     print('Question added succesfully')

             elif form.course.data == 'comms':
               url = 'http://127.0.0.1:5000/commsqn-api'
               response = requests.post(url, json=question)   

               if response.status_code == 200:
                     print('Question added succesfully')  

             elif form.course.data == 'math':
               url = 'http://127.0.0.1:5000/mathqn-api'
               response = requests.post(url, json=question)   

               if response.status_code == 200:
                     print('Question added succesfully')   
             
             elif form.course.data == 'geas':
               url = 'http://127.0.0.1:5000/geasqn-api'
               response = requests.post(url, json=question)   

               if response.status_code == 200:
                     print('Question added succesfully') 

             flash('Question added succesfully') 
             return redirect(url_for('add_question'))
        
        else:
            form = AddQuestions(request.form)
            null_fields = form.get_null_fields() 
            fields = ['correct_a', 'correct_b', 'correct_c', 'correct_d', 'course']


            if null_fields == fields:
                flash_message = 'Please choose a course and complete the boolean option choices'

            elif 'correct_a' in null_fields or 'correct_b' in null_fields or 'correct_c' in null_fields or 'correct_d' in null_fields:
                flash_message = 'Complete the boolean option choices'
            
            elif 'course' in null_fields:
                flash_message = 'Please choose a course'

  
            
            flash(flash_message)
            return redirect(url_for('add_question'))
        
     
        
    return render_template('add_question.html', form=form, messages=messages)   


#Endpoint route for deleting questions
@app.route('/delete-question', methods=['GET', 'POST'])
@login_required
def delete_question():
   
   
   question_list = [] 
   course = ''
   if request.method == 'POST':
       
       session_id = secrets.token_hex(16)
       session['sid'] = session_id
       course = request.form.get('course')
       question_id = request.form.get('question_id', '') #question id for deletion

       if course == 'Electronics':
           url = 'http://127.0.0.1:5000/elecsqn-api' 
           session['subject'] = 'electronics'
           session['url'] = url
           response = requests.get(url)

           if response.status_code == 200:
               json_data = response.json()
               print(json_data)
               question_list = json_data.get("elecs_questions")
           else:
               print('Retrieval of questions is unsuccesful:', response.status_code)

       elif course == 'Communications':
           url = 'http://127.0.0.1:5000/commsqn-api' 
           session['subject'] = 'communications'
           session['url'] = url
           response = requests.get(url)

           if response.status_code == 200:
               json_data = response.json()
               print(json_data)
               question_list = json_data.get("comms_questions")
           else:
               print('Error:', response.status_code)

       elif course == 'Math':
           url = 'http://127.0.0.1:5000/mathqn-api' 
           session['subject'] = 'math'
           session['url'] = url
           response = requests.get(url)

           if response.status_code == 200:
               json_data = response.json()
               print(json_data)
               question_list = json_data.get("math_questions")
           else:
               print('Error:', response.status_code)
       
       elif course == 'GEAS':
           url = 'http://127.0.0.1:5000/geasqn-api' 
           session['subject'] = 'geas'
           session['url'] = url
           response = requests.get(url)

           if response.status_code == 200:
               json_data = response.json()
               print(json_data)
               question_list = json_data.get("geas_questions")
           else:
               print('Error:', response.status_code)
       


       subject = session.get('subject')
       if  subject == 'electronics':
           url = session.get('url')
           if question_id: 
               requests.delete(url, data={'question_id':question_id})
           
  
       elif subject == 'communications':
           url = session.get('url')
           if question_id: 
               requests.delete(url, data={'question_id':question_id})


       elif subject == 'math':
           url = session.get('url')
           if question_id: 
               requests.delete(url, data={'question_id':question_id})
           
       elif subject == 'geas':
           url = session.get('url')
           if question_id: 
               requests.delete(url, data={'question_id':question_id})


   return render_template('delete_questions.html', question_list=question_list, course=course)



# Endpoint Route for updating question
@app.route('/update-question', methods=['GET', 'POST'])
@login_required
def update_question():
   
   
   form = UpdateQuestion()
   question_list = [] 
   course = ''
   question_id = []
   message = get_flashed_messages()

   if request.method == 'GET':
       session['subject'] = ''

   if request.method == 'POST':
       
       session_id = secrets.token_hex(16)
       session['sid'] = session_id
       course = request.form.get('course')
     
       if course == 'Electronics':
           url = 'http://127.0.0.1:5000/elecsqn-api' 
           session['subject'] = 'electronics'
           session['url'] = url
           response = requests.get(url)
           

           if response.status_code == 200:
               json_data = response.json()
               question_list = json_data.get("elecs_questions")
               question_id = [q_id['question_id'] for q_id in question_list]
               session['question_id'] = question_id
               print(question_id)
               print(session['subject'])
           else:
               print('Retrieval of questions is unsuccesful:', response.status_code)


       elif course == 'Communications':
           url = 'http://127.0.0.1:5000/commsqn-api' 
           session['subject'] = 'communications'
           session['url'] = url
           response = requests.get(url)

           if response.status_code == 200:
               json_data = response.json()
               question_list = json_data.get("comms_questions")
               question_id = [q_id['question_id'] for q_id in question_list]
               session['question_id'] = question_id
               print(question_id)
               print(session['subject'])
           else:
               print('Retrieval of questions is unsuccesful:', response.status_code)
       

       elif course == 'Math':
           url = 'http://127.0.0.1:5000/mathqn-api' 
           session['subject'] = 'math'
           session['url'] = url
           response = requests.get(url)

           if response.status_code == 200:
               json_data = response.json()
               question_list = json_data.get("math_questions")
               question_id = [q_id['question_id'] for q_id in question_list]
               session['question_id'] = question_id
               print(question_id)
               print(session['subject'])
           else:
               print('Retrieval of questions is unsuccesful:', response.status_code)


       elif course == 'GEAS':
           url = 'http://127.0.0.1:5000/geasqn-api' 
           session['subject'] = 'geas'
           session['url'] = url
           response = requests.get(url)

           if response.status_code == 200:
               json_data = response.json()
               question_list = json_data.get("geas_questions")
               question_id = [q_id['question_id'] for q_id in question_list]
               session['question_id'] = question_id
               print(question_id)
               print(session['subject'])
           else:
               print('Retrieval of questions is unsuccesful:', response.status_code)


       subject = session.get('subject')
       if form.validate_on_submit():
              q_id = form.question_id.data 
              q_content = form.content.data
              url = session.get('url')
              print("form is validated")
              
              if not subject:
                  flash('Please choose a course first')
                  return redirect(url_for('update_question'))
            
              elif subject:
                  if q_id not in session.get('question_id'):
                     flash('Question ID not found in the database')
                     return redirect(url_for('update_question'))
                  
                  else:
                      updated_question = {'question_id':q_id, "q_content":q_content}
                      requests.put(url, json=updated_question)
                      flash('Question has been updated successfully')
           
                  return redirect(url_for('update_question'))

    

     

   return render_template('update_questions.html', course=course, form=form, question_list=question_list, message=message)


# Endpoint Route for updating options
@app.route('/update-option', methods=['GET','POST'])
@login_required
def update_option():
  
   form = UpdateOptions() 
   question_list = [] 
   question_id = []
   course = ''
   message = get_flashed_messages()

   if request.method == 'GET':
       session['subject'] = ''

   if request.method == 'POST':
       
        session_id = secrets.token_hex(16)
        session['sid'] = session_id
        course = request.form.get('course')
 
        if course == 'Electronics':
            url = 'http://127.0.0.1:5000/elecsopn-api' 
            session['subject'] = 'electronics'
            session['url'] = url
            response = requests.get(url)
            
            if response.status_code == 200:
                elecs_questions = response.json()
                question_list=elecs_questions
                question_id = [q_id['id'] for q_id in question_list]
                session['question_id'] = question_id
    
     
            else:
                print('Retrieval of questions is unsuccesful:', response.status_code)

        elif course == 'Communications':
            url = 'http://127.0.0.1:5000/commsopn-api' 
            session['subject'] = 'communications'
            session['url'] = url
            response = requests.get(url)

            if response.status_code == 200:
                comms_questions = response.json()
                question_list=comms_questions
                question_id = [q_id['id'] for q_id in question_list]
                session['question_id'] = question_id

            else:
                print('Error:', response.status_code)


        elif course == 'Math':
            url = 'http://127.0.0.1:5000/mathopn-api' 
            session['subject'] = 'math'
            session['url'] = url
            response = requests.get(url)

            if response.status_code == 200:
                math_questions = response.json()
                question_list=math_questions
                question_id = [q_id['id'] for q_id in question_list]
                session['question_id'] = question_id

            else:
                print('Error:', response.status_code)

         
        elif course == 'GEAS':
            url = 'http://127.0.0.1:5000/geasopn-api' 
            session['subject'] = 'geas'
            session['url'] = url
            response = requests.get(url)

            if response.status_code == 200:
                geas_questions = response.json()
                question_list=geas_questions
                question_id = [q_id['id'] for q_id in question_list]
                session['question_id'] = question_id
                
            else:
                print('Error:', response.status_code)
        
        

        subject = session.get('subject')
        if form.validate_on_submit():
              q_id = form.question_id.data 
              url = session.get('url')
              print("form is validated")
              
              if not subject:
                  flash('Please choose a course first')
                  return redirect(url_for('update_option'))
            
              elif subject:
                  if q_id not in session.get('question_id'):
                     flash('Question ID not found in the database')
                     return redirect(url_for('update_option'))
                  
                  else:
                      question = {'question_id':form.question_id.data, 'options':[
                      {'letter': 'A', 'content': form.opn_a.data, 'is_correct':form.correct_a.data =='True'},
                      {'letter': 'B', 'content': form.opn_b.data, 'is_correct':form.correct_b.data=='True'},
                      {'letter': 'C', 'content': form.opn_c.data, 'is_correct':form.correct_c.data=='True'},
                      {'letter': 'D', 'content': form.opn_d.data, 'is_correct':form.correct_d.data=='True'}
                      ]}
                      requests.put(url, json=question)
                      flash('Question has been updated successfully')
           
                  return redirect(url_for('update_option'))


   return render_template('update_options.html', message=message, form=form, question_list=question_list, course=course)

  


if __name__ == '__main__': 
    app.run(debug=True, port=5001)