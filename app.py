import json
from flask import Flask, flash, render_template, url_for, request, session, redirect, Response,jsonify 
from flask_mysqldb import MySQL, MySQLdb
import datetime as dt
from datetime import timedelta
import smtplib
from password_strength import PasswordPolicy, PasswordStats
import numpy as np
import joblib
import mediapipe as mp
from helpers import predict, helper_predict_speech
from werkzeug.utils import secure_filename
import cv2, os
import pandas as pd
import math
import pandas as pd
import time
from apscheduler.schedulers.background import BackgroundScheduler

def load_key():
    return open("secret.key", "rb").read()


def load_count():
    return open("participantcount.txt", "r").read()


app = Flask(__name__)
mysql = MySQL(app)

db_config = {
    'host': 'localhost',
    'user': 'root',
    'passwd': 'password',
    'db': 'parkinson_diagnosis_fyp',
    'port': 3306,
    'charset': 'utf8'
}

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'password'
app.config['MYSQL_DB'] = 'parkinson_diagnosis_fyp'
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=30)
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=30)
app.config['SECRET_KEY'] = "abc/djiejdei"

scheduler = BackgroundScheduler()
scheduler.start()

policy = PasswordPolicy.from_names(
    length=8,
    uppercase=1,
    numbers=1,
    strength=0.66
)


gait_model = joblib.load('gait_model.sav')
speech_model = joblib.load('knn_model.sav')


def allowed_file(filename):
    allowed_extensions = {'mp4', 'avi', 'mkv', 'mov', 'mp3', 'wav', 'flac', 'aiff'}  # Add more extensions if needed
    return '.' + filename and filename.rsplit('.', 1)[1].lower() in allowed_extensions

def sched_gait_predict(file_path, participant_mr, show_video=False):
    df = predict(file_path, show_video)
    print("These are columns ,",df.columns,len(df.columns))
    print("Participant MR: ", participant_mr)
    prediction = gait_model.predict(df)
    print("Prediction: ", prediction[0])
    cur = MySQLdb.connect(**db_config).cursor()
    cur.execute("INSERT INTO ensemble(participant_mr, gait) VALUES (%s, %s)", (participant_mr, prediction[0]))
    cur.connection.commit()
    cur.close()
    print("Processing Ended")
    return "success"

def sched_speech_predict(file_path, participant_mr):
    df = helper_predict_speech(file_path)
    print("These are columns ,",df.columns,len(df.columns))
    print("Participant MR: ", participant_mr)
    df.drop(['patient_type'], axis=1, inplace=True)
    prediction = speech_model.predict(df)
    print("Prediction: ", prediction[0])
    # cur = MySQLdb.connect(**db_config).cursor()
    # cur.execute("INSERT INTO ensemble(participant_mr, speech) VALUES (%s, %s)", (participant_mr, prediction[0]))
    # cur.connection.commit()
    # cur.close()
    print("Processing Ended")
    return "success"

@scheduler.scheduled_job('interval', minutes=1)
def pd_predict():
    cur = MySQLdb.connect(**db_config).cursor()
    cur.execute("SELECT * FROM ensemble where participant_mr is not null and gait is not null and speech is not null and tremor is not null and muscle is not null and finger_tap is not null")
    data = cur.fetchall()
    cur.close()
    print("Data: ", data)
    
@app.route('/predict_speech', methods=['POST','GET'])
def predict_speech():
    if "email" in session.keys() and "password" in session.keys():
        if request.method == 'POST':
            file = request.files['audio']
            print("File is ",file)
            if 'audio' not in request.files:
                pass
            
            if file.filename == '':
                pass

            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file.save(os.path.join('UPLOAD_FOLDER/', filename))
                print("Process Audio is called")
                scheduler.add_job(sched_speech_predict, 'date', run_date=dt.datetime.now() + timedelta(seconds=5), args=[os.path.join('UPLOAD_FOLDER', filename), session["participant_mr"]])
                return render_template('add/process_audio.html', user=session['name'], process=True)
        return render_template('add/process_audio.html', user=session['name'])
    else:
        flash('You must be login before accessing this page')
        return redirect(url_for('login'))
                

@app.route('/predict_gait', methods=['POST','GET'])
def predict_gait():

    if "email" in session.keys() and "password" in session.keys():
       
        if request.method == 'POST':
            file = request.files['video']
            print("File is ",file)
            if 'video' not in request.files:
                pass
            
            if file.filename == '':
                pass

            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file.save(os.path.join('UPLOAD_FOLDER/', filename))
                print("Process Video is called")
                scheduler.add_job(sched_gait_predict, 'date', run_date=dt.datetime.now() + timedelta(seconds=5), args=[os.path.join('UPLOAD_FOLDER', filename), session["participant_mr"], False]) #, 1, False
                return render_template('add/process_video.html', user=session['name'], process=True)
        return render_template('add/process_video.html', user=session['name'])    
    else:
        flash('You must be login before accessing this page')
        return redirect(url_for('login'))
    

main_df = pd.DataFrame(columns=["patient_type","Jitter_rel", "Jitter_abs", "Jitter_RAP", "Jitter_PPQ", "Shim_loc", "Shim_dB",
                                "Shim_APQ3", "Shim_APQ5", "Shi_APQ11", "hnr05", "hnr15",
                                "hnr25"])  


@app.route('/pres', methods=['GET', 'POST'])
def pres():
    if "doctoremail" and "doctorpassword" in session:
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT * FROM doctor WHERE name=%s ", (session['doctor_name'],))
        mysql.connection.commit()
        dat = cursor.fetchone()
        contact = dat[4]
        address = dat[11]
        spea = dat[2]
        drname = dat[1]

        cursor.close()

        if request.method == 'POST':
            data = request.form
            symp = data['toms']
            test = data['t']
            advice = data['ts']
            medicine = data['medici']
            mr = session['participant_mr']
            print(data['toms'])

            print(data['t'])
            print(data['ts'])
            print(data['medici'])
            print('Session of mr is' + session['participant_mr'])
            cursor = mysql.connection.cursor()
            cursor.execute(
                "INSERT INTO prescription(Patient_Mr,Doctor_Name,Speacialization,Symptoms,Test,Advice,Medicine) VALUES (%s,%s,%s,%s,%s,%s,%s) ",
                (mr, drname, spea, symp, test, advice, medicine))
            mysql.connection.commit()
            cursor.close()

        return render_template('add/pres.html', doctor=session['doctor_name'], address=address, contact=contact)
    else:
        flash('You must be login to access this page')
        return redirect(url_for('doctorlogin'))


@app.route('/makeprescription/<string:user>', methods=['GET', 'POST'])
def makeprescription(user):
    data = json.loads(user)
    print("The Mr Number of the user is" + str(data['name']))
    session['participant_mr'] = data['name']
    return "success"


@app.route('/home')
def home():
    if "email" in session.keys() and "password" in session.keys():
        return render_template('view/home.html', user=session['name'])

    else:
        flash('you must be login before accessing this page')
        return redirect(url_for('login'))


@app.route('/')
def homebase():
    return render_template('view/default.html')


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    error = None
    current_date = dt.datetime.now().strftime("%d/%m/%Y").split("/")
    year = current_date[2].split('0')[1]
    month = current_date[1]

    print(current_date)

    if request.method == 'POST':
        participantDetails = request.form
        name = participantDetails['pname']
        email = participantDetails['email']
        password = participantDetails['passw']
        RePassword = participantDetails['rePassword']
        parGender = str(participantDetails['gen'])
        participantDob = str(participantDetails['pardob'])
        phoneNum = str(participantDetails['pnum'])
        parAddress = participantDetails['Paddress']
        parCountry = participantDetails['country']
        parCity = participantDetails['parCity']

        stats = PasswordStats(password)
        check = policy.test(password)

        if (stats.strength() < 0.3):
            print(stats.strength())
            flash('Password not strong enough ! , Avoid using consecutive characters and easily guessed words ')
            return redirect(url_for('signup'))

        print(parGender)
        count = load_count()
        print(count)
        participantMr = str(year) + str(month) + count
        print(participantMr)
        count = int(count)

        if password != RePassword:
            flash('Both passwords should be same')
            return redirect(url_for('signup'))

        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO pendingParticipants VALUES (%s, %s,%s,%s,%s,%s,%s,%s,%s,%s)", (
        participantMr, name, email, parGender, participantDob, password, parAddress, parCountry, phoneNum, parCity))
        mysql.connection.commit()
        cur.close()

        count += 1
        with open("participantcount.txt", "w") as f:
            f.write(str(count))

        gmail_user = 'mohammadhammad9801@gmail.com'
        gmail_password = 'lmin wowt vqeq tuue'
        UrL = "http://127.0.0.1:5000/confirmParticipant";
        sent_from = gmail_user
        to = ['mohammadhammad9801@gmail.com', "mufaddalhatim53@gmail.com"]
        subject = 'Participant Confirmation mail '
        body = 'A new participant just registered in our hospital please accept or reject it' + "\n" + UrL

        email_text = """\
        From: %s
        To: %s
        Subject: %s

        %s
        """ % (sent_from, to, subject, body)
        print("Email Is Sending")
        try:
            smtp_server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
            smtp_server.ehlo()
            smtp_server.login(gmail_user, gmail_password)
            smtp_server.sendmail(sent_from, to, email_text)
            smtp_server.close()
            print("Email sent successfully!")

        except Exception as ex:
            print("Something went wrong….", ex)

        return redirect(url_for('homebase'))

    return render_template('add/register.html', error=error)


@app.route('/confirmParticipant')
def confirmParticipant():
    if "adminemail" and "adminpassword" in session:
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM pendingParticipants ")
        mysql.connection.commit()
        data = cur.fetchall()
        cur.close()

        return render_template('add/addParticipant.html', tup=data)
    else:
        flash('you must be login before accessing this page')
        return redirect(url_for('admin'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':

        details = request.form
        email = details['email']
        password = details['password']

        cursor = mysql.connection.cursor()
        cursor.execute("select * from participants where email = %s", (email,))
        mysql.connection.commit
        account = cursor.fetchone()
        print("This is patient account",account)
        cursor.close()

        cursor2 = mysql.connection.cursor()
        cursor2.execute("select * from doctor where email = %s", (email,))
        mysql.connection.commit
        account2 = cursor2.fetchone()
        print("This is doctor account",account2)
        cursor2.close()

        if account:

            if account[2] == email and account[5] == password:
                session.permanent = True
                session['email'] = email
                session['password'] = password
                session['name'] = account[1]
                session['participant_mr'] = account[0]
                name = session['name']

                return redirect(url_for('home', user=name))



        elif account2:

            if account2[5] == email and account2[6]==password:
                session.permanent=True
                session['doctoremail']=email
                session['doctorpassword']=password
                session['doctor_name']=account2[1]
                session['doctorsp']=account2[2]
                session['doctor_id']=account2[0]
                name=session['doctor_name']
                return redirect(url_for('doctorhome', user=name))



        else:
            flash('incorrect email or password')
            return redirect(url_for('login'))
    else:

        if "email" in session.keys() and "password" in session.keys():
            return redirect(url_for('home', user=session['name']))

        elif "doctoremail" in session.keys() and "doctorpassword" in session.keys():
            return redirect(url_for('doctorhome', user=session['doctor_name']))

    return render_template('add/login.html')


@app.route('/doctorappoint')
def doctorappoint():
    if "doctoremail" in session.keys() and "doctorpassword" in session.keys():
        print(session['doctorsp'])
        cursor = mysql.connection.cursor()
        cursor.execute(" SELECT s_no,participant_id,Name,appointment_date From appointment WHERE Speacialization = %s ",
                       (session['doctorsp'],))
        mysql.connection.commit
        data = cursor.fetchall()
        print(data)
        cursor.close()
        return render_template("add/doctorappointment.html", tup=data, user=session['doctor_name'])

    else:
        flash('You must be login before accessing this page')
        return redirect(url_for('doctorlogin'))


@app.route('/appointmentdelete/<string:user>', methods=['POST', 'GET'])
def appointmentDelete(user):
    data = json.loads(user)
    mr = data['mr']
    print("PATIENT MR: ")
    cursor = mysql.connection.cursor()
    cursor.execute("DELETE FROM appointment WHERE participant_id = %s ", (mr,))
    mysql.connection.commit()
    cursor.close()
    return {'success': 'success'}


@app.route('/Participantupdate', methods=['GET', 'POST'])
def Participantupdate():
    if "email" and "password" in session:
        if request.method == 'POST':
            participant_name = session['name']
            participantDetails = request.form
            name = participantDetails['pname']
            email = participantDetails['email']
            password = participantDetails['passw']
            RePassword = participantDetails['rePassword']
            parGender = participantDetails['gen']
            participantDob = participantDetails['pardob']
            phoneNum = participantDetails['pnum']
            parAddress = participantDetails['Paddress']
            parCountry = participantDetails['country']
            city = participantDetails['parCity']

            stats = PasswordStats(password)
            check = policy.test(password)

            if (stats.strength() < 0.3):
                print(stats.strength())
                flash('Password not strong enough ! , Avoid using consecutive characters and easily guessed words ')
                return redirect(url_for('Participantupdate'))

            if password != RePassword:
                flash('Both passwords must be same')
                return redirect(url_for('Participantupdate'))

            cursor = mysql.connection.cursor()
            cursor.execute(
                " UPDATE participants SET Name=%s,Email=%s,Gender=%s,Date_Of_Birth=%s,Password=%s,Address=%s,Country=%s,PhoneNumber=%s,City=%s WHERE Name=%s ",
                (name, email, parGender, participantDob, password, parAddress, phoneNum, parCountry, city,
                 participant_name))
            mysql.connection.commit()
            cursor.close()

            cursor = mysql.connection.cursor()
            cursor.execute(" UPDATE appointment SET name=%s WHERE Name=%s ", (name, participant_name))
            mysql.connection.commit()
            cursor.close()

            session['name'] = name

            session.pop('email', None)
            session.pop('password', None)
            session.pop('participant_mr', None)
            session.pop('name', None)
            return redirect(url_for('homebase'))

        return render_template('add/participantUpdate.html')

    else:

        flash('You must be login before accessing this page')
        return redirect(url_for('login'))


@app.route('/doctorlogin', methods=['GET', 'POST'])
def doctorlogin():
    if request.method == 'POST':

        email = request.form['email']
        password = request.form['password']
        session.permanent = True

        cursor = mysql.connection.cursor()
        cursor.execute("select * from doctor where email = %s", (email,))
        mysql.connection.commit
        account = cursor.fetchone()
        print(account)
        session['doctorsp'] = account[2]
        session['doctor_name']=""

        print(account)
        cursor.close()
        if account:

            if account[5] == email and account[6] == password:
                session.permanent = True
                session['doctoremail'] = email
                session['doctorpassword'] = password
                session['doctor_name'] = account[1]
                session['doctor_id'] = account[0]

                return redirect(url_for('doctorhome'))

            else:
                flash('incorrect email or password')
                return redirect(url_for('doctorlogin'))
        else:
            flash('incorrect email or password')
            return redirect(url_for('doctorlogin'))

    else:
        if "doctoremail" and "doctorpassword" in session:
            return redirect(url_for('doctorhome'))

    return render_template('add/doctorLogin.html')



@app.route('/makeroute')
def makeroute():

    cursor = mysql.connection.cursor()
    cursor.execute(
            "SELECT id,Name,Speacialization,Degree,Email,Gender,ContactNumber  FROM doctor")
    mysql.connection.commit()
    data = cursor.fetchall()
    cursor.close()
    if "email" and "password" in session:
        return render_template('view/MakeAppointment.html', tup=data)
    else:
        flash('You must be login before accessing this page')
        return redirect(url_for('login'))



@app.route('/addappointment/<string:user>', methods=['POST', 'GET'])
def addappointment(user):
    data = json.loads(user)
    doctor_id = data['name']

    print("The Id Of The Doctor Is : " + doctor_id)
    Participant_name = session['name']
    cursor = mysql.connection.cursor()
    cursor.execute(" SELECT * From doctor WHERE id = %s ", (doctor_id,))
    mysql.connection.commit()
    doctor_data = cursor.fetchone()
    doctor_sp = doctor_data[2]
    print(doctor_data)
    cursor.close()

    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM participants WHERE name = %s ", (Participant_name,))
    mysql.connection.commit
    participant_data = cursor.fetchone()
    cursor.close()
    participant_id = participant_data[0]

    print(participant_data)
    print(participant_id)

    cursor = mysql.connection.cursor()
    cursor.execute("INSERT INTO appointment(participant_id,name,doctor_id, Speacialization) VALUES(%s,%s,%s,%s)",
                   (participant_id, Participant_name, doctor_id, doctor_sp))
    mysql.connection.commit()
    cursor.close()
    flash('your appointment has been made')
    return redirect(url_for('home'))



@app.route('/participantvideo', methods=['POST', 'GET'])
def participantvideo():

    video_url = request.data
    vid = video_url.decode("UTF-8")
    print("The url of video is " + vid)
    mr = session['participant_mr']
    print(mr)

    cursor = mysql.connection.cursor()
    cursor.execute(" INSERT INTO participant_video(participant_id,video_link) VALUES (%s, %s) ", (mr, vid))
    mysql.connection.commit()
    cursor.close()

    dic = {"Apppointment": "Your Appointment has been made"}
    return jsonify(dic)


@app.route('/logout')
def logout():

    if "email" and "password" in session:
        session.pop('email', None)
        session.pop('password', None)
        session.pop('name', None)
        session.pop('participant_mr', None)
        return redirect(url_for('homebase'))

    else:
        flash('You must be login before accessing this page')
        return redirect(url_for('login'))


@app.route('/doctorhome')
def doctorhome():

    if "doctoremail" and "doctorpassword" in session:

        return render_template('view/doctorhome.html', user=session['doctor_name'])

    else:
        flash('You must be login before accessing this page')
        return redirect(url_for('doctorlogin'))


@app.route('/doctorupdate', methods=['POST', 'GET'])
def doctorupdate():

    if "doctoremail" and "doctorpassword" in session:

        if request.method == 'POST':
            doctor = session['doctor_name']
            doctorDetails = request.form
            name = doctorDetails['pname']
            speacialization = doctorDetails['spea']
            degree = doctorDetails['degree']
            email = doctorDetails['email']
            password = doctorDetails['passw']
            RePassword = doctorDetails['rePassword']
            parGender = doctorDetails['gen']
            participantDob = doctorDetails['pardob']
            phoneNum = doctorDetails['pnum']
            parAddress = doctorDetails['Paddress']
            parCountry = doctorDetails['country']
            city = doctorDetails['parCity']

            cursor = mysql.connection.cursor()
            cursor.execute(
                "UPDATE doctor SET Name=%s,Speacialization=%s,Degree=%s,ContactNumber=%s,Email=%s,Password=%s,DOB=%s,Gender=%s,Country=%s,City=%s,Address=%s WHERE Name=%s ",
                (name, speacialization, degree, phoneNum, email, password, participantDob, parGender, parCountry, city,
                 parAddress, doctor))
            mysql.connection.commit()
            cursor.close()

            session['doctor_name'] = name
            session['doctorsp'] = speacialization
            cursor = mysql.connection.cursor()
            cursor.execute("UPDATE appointment SET Speacialization=%s WHERE doctor_id=%s ",
                           (speacialization, session['doctor_id']))
            mysql.connection.commit()
            cursor.close()
            return "success"

        return render_template('add/doctorupdate.html')
    else:
        flash('You must be login before accessing this page')
        return redirect(url_for('doctorlogin'))


@app.route('/doctorlogout')
def doctorlogout():

    session.pop('doctoremail', None)
    session.pop('doctorpassword', None)
    session.pop('doctor_name', None)
    session.pop('doctorsp', None)
    return redirect(url_for('homebase'))


@app.route('/prescription')
def prescription():

    if "email" and "password" in session:
        cursor = mysql.connection.cursor()
        cursor.execute(" SELECT patient_mr,doctor_name,date,symptoms,test,advice,medicine FROM prescription WHERE Patient_Mr= %s ", (session['participant_mr'],))
        data = cursor.fetchall()
        cursor.close()
        return render_template("view/prescriptionHistory.html", tup=data)
    else:
        flash('You must be login to access this page')
        return redirect(url_for('login'))


@app.route('/addDoctors', methods=['GET', 'POST'])
def addDoctors():

    if "adminemail" and "adminpassword" in session:

        if (request.method == 'POST'):

            doctorDetails = request.form
            name = doctorDetails['pname']
            speacialization = doctorDetails['spea']
            degree = doctorDetails['degree']
            email = doctorDetails['email']
            password = doctorDetails['passw']
            RePassword = doctorDetails['rePassword']
            parGender = doctorDetails['gen']
            participantDob = doctorDetails['pardob']
            phoneNum = doctorDetails['pnum']
            parAddress = doctorDetails['Paddress']
            parCountry = doctorDetails['country']
            city = doctorDetails['parCity']

            if password != RePassword:
                flash('Both Passwords Must Be The Same')
                return redirect(url_for('addDoctors'))

            else:
                cursor = mysql.connection.cursor()
                cursor.execute(
                    " INSERT INTO doctor(Name,Speacialization,Degree,ContactNumber,Email,Password,DOB,Gender,Country,City,Address) VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s) ",
                    (name, speacialization, degree, phoneNum, email, password, participantDob, parGender, parCountry,
                     city, parAddress))
                mysql.connection.commit()
                cursor.close()

        return render_template('add/addDoctors.html', user=session['adminName'])
    else:
        flash('Admin must be login to access this page')
        return redirect(url_for('admin'))


@app.route('/admin', methods=['POST', 'GET'])
def admin():

    if (request.method == 'POST'):

        email = request.form.get('email')
        password = request.form.get('password')

        cursor = mysql.connection.cursor()
        cursor.execute("SELECT * FROM admin")
        mysql.connection.commit()
        data = cursor.fetchone()
        cursor.close()
        if email == data[2] and password == data[3]:
            session.permanent = True

            session['adminemail'] = email
            session['adminpassword'] = password
            session['adminName'] = data[1]

            return redirect(url_for('adminHome'))

        else:
            flash('You have entered incorrect email or password')
            return redirect(url_for('admin'))

    return render_template('add/AdminLogin.html')


@app.route('/showDoctors')
def showDoctors():

    if "adminemail" and "adminpassword" in session:

        cursor = mysql.connection.cursor()
        cursor.execute(
            "SELECT id,name,speacialization,degree,contactNumber,email,dob,gender,country,city,address FROM doctor")
        mysql.connection.commit()
        data = cursor.fetchall()
        cursor.close()
        return render_template('view/showDoctors.html', tup=data, user=session['adminName'])
    else:
        flash('You must be login to access this page')
        return redirect(url_for('doctorlogin'))


@app.route('/showparticipants')
def showparticipant():

    if "adminemail" and "adminpassword" in session:
        cursor = mysql.connection.cursor()
        cursor.execute(
            "SELECT Mr_no,name,email,parGender,participantDob,parAddress,parCountry,phoneNum,parCity FROM  participants")
        mysql.connection.commit()
        data = cursor.fetchall()
        cursor.close()
        return render_template('view/showPartcipant.html', tup=data, user=session['adminName'])
    else:
        flash('Admin must be login to access this page')
        return redirect(url_for('admin'))


@app.route('/adminHome')
def adminHome():

    if "adminemail" and "adminpassword" in session:
        return render_template('view/adminHome.html', user=session['adminName'])
    else:
        flash('You must be login before accessing this page')
        return redirect(url_for('admin'))


@app.route('/adminLogout')
def adminLogout():

    session.pop('adminemail', None)
    session.pop('adminpassword', None)
    session.pop('adminName', None)
    return redirect(url_for('homebase'))


@app.route('/docdelete/<string:user>', methods=['GET', 'POST'])
def docdelete(user):

    data = json.loads(user)
    cursor = mysql.connection.cursor()
    cursor.execute("DELETE FROM doctor WHERE  id=%s", (data['id'],))
    mysql.connection.commit()
    cursor.close()

    print(data['id'])


@app.route('/sendmail')
def sendmail():
    return "success"


@app.route('/accept/<string:user>', methods=['GET', 'POST'])
def accept(user):

    data = json.loads(user)
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM pendingParticipants WHERE name=%s ", (data['name'],))
    mysql.connection.commit()
    pardata = cur.fetchone()

    cur.execute("INSERT INTO participants VALUES (%s, %s,%s,%s,%s,%s,%s,%s,%s,%s)", (
    pardata[0], pardata[1], pardata[2], pardata[3], pardata[4], pardata[5], pardata[6], pardata[7], pardata[8],
    pardata[9]))
    mysql.connection.commit()

    cur.execute(" DELETE FROM pendingParticipants WHERE name=%s ", (data['name'],))
    mysql.connection.commit()
    cur.close()

    gmail_user = 'mohammadhammad9801@gmail.com'
    gmail_password = 'Incrediblemohammad'
    UrL = "http://127.0.0.1:5000/login";
    sent_from = gmail_user
    to = data['email']
    subject = 'Participant Confirmation mail '
    body = 'You are now registered in hospital\nFollow this link to login  ' + UrL

    email_text = """\
    From: %s
    To: %s
    Subject: %s

    %s
    """ % (sent_from, ", ".join(to), subject, body)

    try:
        smtp_server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        smtp_server.ehlo()
        smtp_server.login(gmail_user, gmail_password)
        smtp_server.sendmail(sent_from, to, email_text)
        smtp_server.close()
        print("Email sent successfully!")

    except Exception as ex:
        print("Something went wrong….", ex)

    return "success"


@app.route('/reject/<string:user>', methods=['GET', 'POST'])
def reject(user):

    data = json.loads(user)
    email = data['email']
    cur = mysql.connection.cursor()
    cur.execute(" DELETE FROM pendingParticipants WHERE name=%s ", (data['name'],))
    mysql.connection.commit()
    cur.close()

    gmail_user = 'mohammadhammad9801@gmail.com'
    gmail_password = 'Incrediblemohammad'
    UrL = "http://127.0.0.1:5000/signup";
    sent_from = gmail_user
    to = email
    subject = 'Participant Confirmation mail '
    body = 'Your regiustration has been rejected by the admin.\nFor Signup Follow the Link ' + UrL

    email_text = """\
    From: %s
    To: %s
    Subject: %s

    %s
    """ % (sent_from, ", ".join(to), subject, body)

    try:
        smtp_server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        smtp_server.ehlo()
        smtp_server.login(gmail_user, gmail_password)
        smtp_server.sendmail(sent_from, to, email_text)
        smtp_server.close()
        print("Email sent successfully!")

    except Exception as ex:
        print("Something went wrong….", ex)

    return "success"


if __name__ == '__main__':
    app.run(debug=True, port=5000)