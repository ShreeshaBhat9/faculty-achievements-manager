#Imports
from flask import Flask, render_template, flash, redirect, url_for, session, request, logging
from flask_mysqldb import MySQL
from wtforms import Form, StringField, TextAreaField, PasswordField, validators, DateField, IntegerField, RadioField
from passlib.hash import sha256_crypt
from functools import wraps
from flask_mail import Mail, Message


#instance of flask
app=Flask(__name__)

app.config['MAIL_SERVER']='smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = ''
app.config['MAIL_PASSWORD'] = ''
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
app.config['MAIL_DEFAULT_SENDER'] = 'shreesha.bht@gmail.com'

mail = Mail(app)

#Config MySQL
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'root'
app.config['MYSQL_DB'] = 'faculty'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'

#init MYSQL
mysql = MySQL(app)

#to check if any user is logged in
def is_logged_in(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return f(*args,**kwargs)
        else:
            flash('Unautorized. Please login to continue','danger')
            return redirect(url_for('login'))
    return wrap

def is_admin(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        cur = mysql.connection.cursor()
        result = cur.execute("select id from users where username = %s",[session['username']])
        if result>0:
            data = cur.fetchone()
            idfromdb = data['id']
            result2 = cur.execute("select id from ADMIN where id = %s",[idfromdb])
            if result2>0:
                return f(*args,**kwargs)
            else:
                flash('Unautorized','danger')
                return redirect(url_for('dashboard'))
        else:
            flash('Unautorized. Please login to continue','danger')
            return redirect(url_for('login'))
        cur.close()
    return wrap

class FeedbackForm(Form):
    feedback = StringField('Enter your Feedback', [validators.DataRequired(),validators.Length(min=1,max=1000)])

class RegisterForm(Form):
    name = StringField('Name', [validators.DataRequired(),validators.Length(min=3,max=50)])
    userid = StringField('Staff-Id', [validators.DataRequired(),validators.Length(min=5,max=20)])
    username = StringField('Username', [validators.DataRequired(),validators.Length(min=4,max=25)])
    email = StringField('Email', [validators.DataRequired(),validators.Length(min=4,max=30), validators.Email(message='Not a valid email address')])
    password = PasswordField('Password', [
        validators.DataRequired(),
        validators.EqualTo('confirm',message='Passwords do not match')
    ])
    confirm=PasswordField('Confirm Password')

class ProjectForm(Form):
    pname = StringField('Project Name', [validators.DataRequired(),validators.Length(min=3,max=50)])
    pincopi = StringField('PI & Co PI', [validators.DataRequired(),validators.Length(min=4,max=25)])
    psubto = StringField('Proposal Submitted to', [validators.DataRequired(),validators.Length(min=4,max=25)])
    budamt = StringField('Budgeted Amount', [validators.DataRequired(),validators.Length(min=4,max=25)])
    pstat = StringField('Proposal Status', [validators.DataRequired(),validators.Length(min=4,max=25)])
    month = StringField('Month', [validators.DataRequired(),validators.Length(min=3,max=10)])
    year = StringField('Year', [validators.DataRequired(message = 'Cannot be left blank')])

class ProjectGrantForm(Form):
    pname = StringField('Project Name', [validators.DataRequired(),validators.Length(min=3,max=50)])
    pincopi = StringField('PI & Co PI', [validators.DataRequired(),validators.Length(min=4,max=25)])
    fundage = StringField('Funding Agency', [validators.DataRequired(),validators.Length(min=4,max=25)])
    amounts = StringField('Sanctioned Amount in lakhs', [validators.DataRequired(),validators.Length(min=4,max=25)])
    syear = StringField('Sanctioned Year', [validators.DataRequired(),validators.Length(min=4,max=25)])
    amountr = StringField('Amount Recieved in lakhs', [validators.DataRequired(),validators.Length(min=4,max=25)])
    remarks = StringField('Remarks (1st/2nd/3rd year grant)', [validators.DataRequired(),validators.Length(min=4,max=25)])
    month = StringField('Month', [validators.DataRequired(),validators.Length(min=3,max=10)])
    year = StringField('Year', [validators.DataRequired(message = 'Cannot be left blank')])

class TrainingForm(Form):
    work = StringField('Training/Consultancy work', [validators.DataRequired(),validators.Length(min=3,max=50)])
    facin = StringField('Faculty Invlolved', [validators.DataRequired(),validators.Length(min=4,max=25)])
    fundage = StringField('Funding Agency', [validators.DataRequired(),validators.Length(min=4,max=25)])
    amount = StringField('Amount Recieved', [validators.DataRequired(),validators.Length(min=4,max=25)])
    month = StringField('Month', [validators.DataRequired(),validators.Length(min=3,max=10)])
    year = StringField('Year', [validators.DataRequired(message = 'Cannot be left blank')])

class WorkshopForm(Form):
    det = StringField('Details of Workshops/Seminars/Conference/Events', [validators.DataRequired(),validators.Length(min=3,max=50)])
    dateofe = DateField('Date of Event', [validators.DataRequired(message='Enter the date in dd/mm/yyyy format')],format='%d/%m/%Y')
    noofstu = IntegerField('Number of students')
    nooffac = IntegerField('Number of faculty')
    industry = StringField('Industry', [validators.DataRequired(),validators.Length(min=1,max=100)])
    orgby = StringField('Organized By', [validators.DataRequired(),validators.Length(min=1,max=100)])
    month = StringField('Month', [validators.DataRequired(),validators.Length(min=3,max=10)])
    year = StringField('Year', [validators.DataRequired(message = 'Cannot be left blank')])

class InvtalkForm(Form):
    topic = StringField('Topic', [validators.DataRequired(),validators.Length(min=3,max=50)])
    venue = StringField('Venue', [validators.DataRequired(),validators.Length(min=3,max=50)])
    dateoft = DateField('Date', [validators.DataRequired(message='Enter the date in dd/mm/yyyy format')],format='%d/%m/%Y')
    noofstu = IntegerField('Number of students')
    nooffac = IntegerField('Number of faculty')
    industry = StringField('Industry', [validators.DataRequired(),validators.Length(min=1,max=100)])
    month = StringField('Month', [validators.DataRequired(),validators.Length(min=3,max=10)])
    year = StringField('Year', [validators.DataRequired(message = 'Cannot be left blank')])

class ExplectForm(Form):
    topic = StringField('Topic', [validators.DataRequired(),validators.Length(min=3,max=50)])
    rname = StringField('Name of resource person', [validators.DataRequired(),validators.Length(min=3,max=50)])
    onameaddr = StringField('Organization name and address', [validators.DataRequired(),validators.Length(min=3,max=50)])
    dateoft = DateField('Date', [validators.DataRequired(message='Enter the date in dd/mm/yyyy format')],format='%d/%m/%Y')
    noofstu = IntegerField('Number of students')
    nooffac = IntegerField('Number of faculty')
    industry = StringField('Industry', [validators.DataRequired(),validators.Length(min=1,max=100)])
    month = StringField('Month', [validators.DataRequired(),validators.Length(min=3,max=10)])
    year = StringField('Year', [validators.DataRequired(message = 'Cannot be left blank')])

class WscForm(Form):
    wsc = StringField('Workshop/Seminar/Conference attended', [validators.DataRequired(),validators.Length(min=3,max=50)])
    venue = StringField('Venue', [validators.DataRequired(),validators.Length(min=3,max=50)])
    dateoft = DateField('Date attended', [validators.DataRequired(message='Enter the date in dd/mm/yyyy format')],format='%d/%m/%Y')
    month = StringField('Month', [validators.DataRequired(),validators.Length(min=3,max=10)])
    year = StringField('Year', [validators.DataRequired(message = 'Cannot be left blank')])

class JournalForm(Form):
    title = StringField('Title', [validators.DataRequired(),validators.Length(min=3,max=50)])
    jname = StringField('Journal Name', [validators.DataRequired(),validators.Length(min=3,max=50)])
    natorint = StringField('National or International')
    volno = StringField('Volume & No', [validators.DataRequired(),validators.Length(min=3,max=50)])
    issue = StringField('Issue', [validators.DataRequired(),validators.Length(min=3,max=50)])
    pageno = StringField('Page No', [validators.DataRequired(),validators.Length(min=3,max=50)])
    scoind = StringField('Scopus Index', [validators.DataRequired(),validators.Length(min=1,max=100)])
    wos = StringField('Web of Sciences', [validators.DataRequired(),validators.Length(min=1,max=100)])
    gscho = StringField('Google Scholar', [validators.DataRequired(),validators.Length(min=1,max=100)])
    noofcert = IntegerField('No. of Citifications')
    month = StringField('Month', [validators.DataRequired(),validators.Length(min=3,max=10)])
    year = StringField('Year', [validators.DataRequired(message = 'Cannot be left blank')])

class ConferenceForm(Form):
    title = StringField('Title', [validators.DataRequired(),validators.Length(min=3,max=50)])
    conf = StringField('Conference', [validators.DataRequired(),validators.Length(min=3,max=50)])
    natorint = StringField('National or International', [validators.DataRequired(),validators.Length(min=1,max=50)])
    volno = StringField('Volume and No', [validators.DataRequired(),validators.Length(min=3,max=50)])
    issue = StringField('Issue', [validators.DataRequired(),validators.Length(min=3,max=50)])
    pageno = StringField('Page no', [validators.DataRequired(),validators.Length(min=3,max=50)])
    month = StringField('Month', [validators.DataRequired(),validators.Length(min=3,max=10)])
    year = StringField('Year', [validators.DataRequired(message = 'Cannot be left blank')])

class BookForm(Form):
    bname = StringField('Book Name', [validators.DataRequired(),validators.Length(min=3,max=50)])
    pubname = StringField('Publisher', [validators.DataRequired(),validators.Length(min=3,max=50)])
    isbn = IntegerField('ISBN number')
    title = StringField('Title', [validators.DataRequired(),validators.Length(min=3,max=50)])
    pageno = StringField('Page no', [validators.DataRequired(),validators.Length(min=3,max=50)])
    month = StringField('Month', [validators.DataRequired(),validators.Length(min=3,max=10)])
    year = StringField('Year', [validators.DataRequired(message = 'Cannot be left blank')])

class MouForm(Form):
    org = StringField('Orgenization', [validators.DataRequired(),validators.Length(min=3,max=50)])
    moc = StringField('Mode of Collaboration', [validators.DataRequired(),validators.Length(min=3,max=50)])
    moue = DateField('MOU executed date', [validators.DataRequired(message='Enter the date in dd/mm/yyyy format')],format='%d/%m/%Y')
    validity = StringField('validity of the MoU/MoA', [validators.DataRequired(),validators.Length(min=3,max=50)])
    month = StringField('Month', [validators.DataRequired(),validators.Length(min=3,max=10)])
    year = StringField('Year', [validators.DataRequired(message = 'Cannot be left blank')])

class PatentForm(Form):
    title = StringField('Title', [validators.DataRequired(),validators.Length(min=3,max=50)])
    author = StringField('Author', [validators.DataRequired(),validators.Length(min=3,max=50)])
    pdate = DateField('Patent filed on', [validators.DataRequired(message='Enter the date in dd/mm/yyyy format')],format='%d/%m/%Y')
    status = StringField('Status', [validators.DataRequired(),validators.Length(min=3,max=50)])
    month = StringField('Month', [validators.DataRequired(),validators.Length(min=3,max=10)])
    year = StringField('Year', [validators.DataRequired(message = 'Cannot be left blank')])

class IvbysForm(Form):
    sem = IntegerField('Semester')
    inameaddr = StringField('Industry Name and Address', [validators.DataRequired(),validators.Length(min=3,max=50)])
    nostu = IntegerField('Number of students visited')
    purpose = StringField('Purpose', [validators.DataRequired(),validators.Length(min=3,max=50)])
    month = StringField('Month', [validators.DataRequired(),validators.Length(min=3,max=10)])
    year = StringField('Year', [validators.DataRequired(message = 'Cannot be left blank')])

class FacmemForm(Form):
    ass = StringField('Association', [validators.DataRequired(),validators.Length(min=3,max=50)])
    memdet = StringField('Membership detail', [validators.DataRequired(),validators.Length(min=3,max=50)])
    term = StringField('Term', [validators.DataRequired(),validators.Length(min=3,max=50)])
    month = StringField('Month', [validators.DataRequired(),validators.Length(min=3,max=10)])
    year = StringField('Year', [validators.DataRequired(message = 'Cannot be left blank')])

class UfacmemForm(Form):
    desi = StringField('Designation', [validators.DataRequired(),validators.Length(min=3,max=50)])
    body = StringField('Body', [validators.DataRequired(),validators.Length(min=3,max=50)])
    oname = StringField('Organization Institution Name', [validators.DataRequired(),validators.Length(min=3,max=50)])
    month = StringField('Month', [validators.DataRequired(),validators.Length(min=3,max=10)])
    year = StringField('Year', [validators.DataRequired(message = 'Cannot be left blank')])

class AwardsForm(Form):
    adeti = StringField('Award/Achievement details', [validators.DataRequired(),validators.Length(min=3,max=50)])
    oname = StringField('Awarded by Organization name', [validators.DataRequired(),validators.Length(min=3,max=50)])
    month = StringField('Month', [validators.DataRequired(),validators.Length(min=3,max=10)])
    year = StringField('Year', [validators.DataRequired(message = 'Cannot be left blank')])

class AnyothForm(Form):
    event = StringField('Event', [validators.DataRequired(),validators.Length(min=3,max=50)])
    month = StringField('Month', [validators.DataRequired(),validators.Length(min=3,max=10)])
    year = StringField('Year', [validators.DataRequired(message = 'Cannot be left blank')])





######################### NEW ROUTE ############################

@app.route('/')
def home():
    return render_template('home.html')

######################### NEW ROUTE ############################

@app.route('/feedback',methods=['GET','POST'])
def feedback():
    form = FeedbackForm(request.form)
    if request.method == 'POST' and form.validate():
        fb = form.feedback.data
        mes = session['username'] + ':\n\n\t' +fb
        msg = Message('Feedback Recieved from ' + session['username'], recipients = ['shreeshabhat.cs17@rvce.edu.in','shravanyr.cs17@rvce.edu.in'])
        msg.body = mes
        mail.send(msg)
        flash('Feedback Sent', 'success')
        return redirect(url_for('dashboard'))
    return render_template('feedback.html',form=form)

######################### NEW ROUTE ############################



@app.route('/register',methods=['GET','POST'])
def register():
    form = RegisterForm(request.form)
    if request.method == 'POST' and form.validate():
        name = form.name.data
        id = form.userid.data
        email = form.email.data
        username = form.username.data
        password = sha256_crypt.encrypt(str(form.password.data))

        #Create cursor
        cur = mysql.connection.cursor()
        cur.execute("insert into users (id, name, username, mailid, password) values (%s, %s ,%s, %s, %s)", (id, name, username, email, password))

        #Commit to DB
        mysql.connection.commit()

        #close connection
        cur.close()

        flash('You have registered successfully', 'success')

        return redirect(url_for('login'))
    return render_template('register.html',form=form)

######################### NEW ROUTE ############################

#User login/reg
@app.route('/login',methods=['GET','POST'])
def login():
    if request.method=='POST':
        #Get Form Fields
        username = request.form['username']
        password = request.form['password'] #hash

        #Create cursor
        cur = mysql.connection.cursor()
        result = cur.execute("select * from users where username = %s",[username])

        if result>0:
            data = cur.fetchone()
            passwordfromdb = data['password']

            #Compare passwords
            if sha256_crypt.verify(password,passwordfromdb):
                #success
                session['logged_in'] = True
                session['username'] = username

                idfromdb = data['id']
                result1 = cur.execute("select * from ADMIN where id = %s",[idfromdb])


                flash('You have logged in successfully','success')

                if result1>0:
                    return redirect(url_for('dashboardadmin'))
                else:
                    return redirect(url_for('dashboard'))

            else:
                error = 'The password is incorrect'
                return render_template('login.html',error=error)

            cur.close()

        else:
            error = '''Username doesn't exist'''
            return render_template('login.html',error=error)

    return render_template('login.html')


######################### NEW ROUTE ############################

@app.route('/logout')
@is_logged_in
def logout():
    session.clear()
    flash('You are now logged out','success')
    return redirect(url_for('login'))

######################### NEW ROUTE ############################

@app.route('/dashboard')
@is_logged_in
def dashboard():
    return render_template('dashboard.html')

######################### NEW ROUTE ############################

@app.route('/dashboardadmin')
@is_logged_in
@is_admin
def dashboardadmin():
    return render_template('dashboardadmin.html')

######################### NEW ROUTE ############################

@app.route('/monthly_report')
@is_logged_in
@is_admin
def monthly():
    return render_template('dashboardadmin.html')

######################### NEW ROUTE ############################

@app.route('/edit_achievement', methods=['GET','POST'])
@is_logged_in
def edit_achievement():
    #Create cursor
    cur = mysql.connection.cursor()
    result = cur.execute("select * from users where username = %s",[session['username']])
    flag = 0

    if result>0:
        data = cur.fetchone()
        idfromdb = data['id']
    else:
        redirect(url_for('login'))

    l = ['PROJECTS','PROGRANTS','TRAINING','WSCE','INVTALK','EXPLECT','WSCEA','JOURNAL','CONF','BOOK','MOU','PATENT','IVBYS','FACMEM','UFACMEM','AWARDS','ANYOTH']
    cname = []
    aname = []
    for tname in list(l):
        temp=[]
        result = cur.execute("select * from {} where userid = %s".format(tname),[idfromdb])
        ach = cur.fetchall()
        if result==0:
            l.remove(tname)
        else :
            flag=1
            for k in ach[0]:
                temp.append(k)
            aname.append(ach)
            cname.append(temp)
            app.logger.info('\n%s', tname)
            app.logger.info('\n%s', len(ach))

    if flag==0:
        msg = 'No Achievements found'
        return render_template('dashboard.html',msg = msg)
    else:
        return render_template('edit_achievement.html', l=l, aname = aname, cname = cname)


######################### NEW ROUTE ############################

#Do different for each
@app.route('/edit/PROJECTS-<string:id>', methods=['GET','POST'])
@is_logged_in
def edit_individual_projects(id):

    form = ProjectForm(request.form)
    #Create cursor
    cur = mysql.connection.cursor()

    #Get the id
    result = cur.execute("select * from users where username = %s",[session['username']])

    if result>0:
        data = cur.fetchone()
        idfromdb = data['id']
    else:
        redirect(url_for('login'))

    #Get the achievement
    result = cur.execute("select * from PROJECTS where userid = %s and id = %s",[idfromdb,id])
    instance = cur.fetchone()
    cur.close()

    #Fill form with existing data
    form.pname.data = instance['pname']
    form.pincopi.data = instance['pincopiname']
    form.psubto.data = instance['propsub']
    form.budamt.data = instance['amount']
    form.pstat.data = instance['prostat']
    form.year.data = instance['year']
    form.month.data = instance['month']

    if request.method == 'POST' and form.validate():
        pname = request.form['pname']
        pincopi = request.form['pincopi']
        psubto = request.form['psubto']
        budamt = request.form['budamt']
        pstat = request.form['pstat']
        year = request.form['year']
        month = request.form['month']

        #Create cursor
        cur = mysql.connection.cursor()
        result = cur.execute("select * from users where username = %s",[session['username']])

        if result>0:
            data = cur.fetchone()
            idfromdb = data['id']
        else:
            redirect(url_for('login'))
        cur.execute("update PROJECTS set pname=%s, pincopiname=%s, propsub=%s, amount=%s, prostat=%s, year = %s, month = %s where userid = %s and id = %s", (year, month, pname, pincopi, psubto, budamt, pstat,idfromdb,id))
        #Commit to DB
        mysql.connection.commit()

        #close connection
        cur.close()

        flash('You have edited successfully', 'success')
        return redirect(url_for('dashboard'))

    return render_template('projects.html',form=form,edit=1)

#########################  NEW ROUTE  ############################

@app.route('/edit/PROGRANTS-<string:id>', methods=['GET','POST'])
@is_logged_in
def edit_individual_progrants(id):

    form = ProjectGrantForm(request.form)
    #Create cursor
    cur = mysql.connection.cursor()

    #Get the id
    result = cur.execute("select * from users where username = %s",[session['username']])

    if result>0:
        data = cur.fetchone()
        idfromdb = data['id']
    else:
        redirect(url_for('login'))

    #Get the achievement
    result = cur.execute("select * from PROGRANTS where userid = %s and id = %s",[idfromdb,id])
    instance = cur.fetchone()
    cur.close()

    #Fill form with existing data
    form.pname.data = instance['pname']
    form.pincopi.data = instance['pincopiname']
    form.fundage.data = instance['funagency']
    form.amounts.data = instance['sainl']
    form.syear.data = str(instance['syear'])
    form.amountr.data = instance['amount']
    form.remarks.data = instance['remarks']
    form.year.data = str(instance['year'])
    form.month.data = instance['month']

    if request.method == 'POST' and form.validate():
        pname = request.form['pname']
        pincopi = request.form['pincopi']
        fundage = request.form['fundage']
        amounts = request.form['amounts']
        yearx = request.form['syear']
        amountr= request.form['amountr']
        remarks = request.form['remarks']
        year = request.form['year']
        month = request.form['month']

        #Create cursor
        cur = mysql.connection.cursor()
        result = cur.execute("select * from users where username = %s",[session['username']])

        if result>0:
            data = cur.fetchone()
            idfromdb = data['id']
        else:
            redirect(url_for('login'))
        cur.execute("update PROGRANTS set year = %s, month = %s, pname = %s, pincopiname = %s, funagency = %s, sainl = %s, syear = %s, amount = %s, remarks = %s where userid = %s and id = %s", (year, month, pname, pincopi, fundage, amounts, yearx, amountr, remarks, idfromdb,id))
        #Commit to DB
        mysql.connection.commit()

        #close connection
        cur.close()

        flash('You have edited successfully', 'success')
        return redirect(url_for('dashboard'))

    return render_template('projectgrants.html',form=form,edit=1)

#########################  NEW ROUTE  ############################

@app.route('/edit/TRAINING-<string:id>', methods=['GET','POST'])
@is_logged_in
def edit_individual_training(id):

    form = TrainingForm(request.form)
    #Create cursor
    cur = mysql.connection.cursor()

    #Get the id
    result = cur.execute("select * from users where username = %s",[session['username']])

    if result>0:
        data = cur.fetchone()
        idfromdb = data['id']
    else:
        redirect(url_for('login'))

    #Get the achievement
    result = cur.execute("select * from TRAINING where userid = %s and id = %s",[idfromdb,id])
    instance = cur.fetchone()
    cur.close()

    #Fill form with existing data
    form.work.data = instance['work']
    form.facin.data = instance['facin']
    form.fundage.data = instance['funagency']
    form.amount.data = instance['amount']
    form.year.data = instance['year']
    form.month.data = instance['month']


    if request.method == 'POST' and form.validate():
        work = request.form['work']
        facin = request.form['facin']
        fundage = request.form['fundage']
        amount = request.form['amount']
        year = request.form['year']
        month = request.form['month']

        #Create cursor
        cur = mysql.connection.cursor()
        result = cur.execute("select * from users where username = %s",[session['username']])

        if result>0:
            data = cur.fetchone()
            idfromdb = data['id']
        else:
            redirect(url_for('login'))
        cur.execute("update TRAINING set year = %s, month = %s, work = %s, facin = %s funagency = %s, amount = %s where userid = %s and id = %s", (year, month, work, facin, fundage, amount, idfromdb,id))
        #Commit to DB
        mysql.connection.commit()

        #close connection
        cur.close()

        flash('You have edited successfully', 'success')
        return redirect(url_for('dashboard'))

    return render_template('training.html',form=form,edit=1)

#########################  NEW ROUTE  ############################

@app.route('/edit/WSCE-<string:id>', methods=['GET','POST'])
@is_logged_in
def edit_individual_wsce(id):

    form = WorkshopForm(request.form)
    #Create cursor
    cur = mysql.connection.cursor()

    #Get the id
    result = cur.execute("select * from users where username = %s",[session['username']])

    if result>0:
        data = cur.fetchone()
        idfromdb = data['id']
    else:
        redirect(url_for('login'))

    #Get the achievement
    result = cur.execute("select * from WSCE where userid = %s and id = %s",[idfromdb,id])
    instance = cur.fetchone()
    cur.close()

    #Fill form with existing data
    form.det.data = instance['details']
    form.dateofe.data = instance['dateofe']
    form.noofstu.data = instance['noofstu']
    form.nooffac.data = instance['nooffac']
    form.industry.data = instance['industry']
    form.orgby.data = instance['orgby']
    form.year.data = instance['year']
    form.month.data = instance['month']

    if request.method == 'POST' and form.validate():
        det = request.form['det']
        dateofe = request.form['dateofe']
        noofstu = request.form['noofstu']
        nooffac = request.form['nooffac']
        industry = request.form['industry']
        orgby= request.form['orgby']
        year = request.form['year']
        month = request.form['month']

        #Create cursor
        cur = mysql.connection.cursor()
        result = cur.execute("select * from users where username = %s",[session['username']])

        if result>0:
            data = cur.fetchone()
            idfromdb = data['id']
        else:
            redirect(url_for('login'))
        cur.execute("update WSCE set year = %s, month = %s, details = %s, dateofe = %s, noofstu = %s, nooffac = %s, industry = %s, orgby = %s where userid = %s and id = %s", (year, month, details, dateofe, noofstu, nooffac, industry, orgby, idfromdb,id))
        #Commit to DB
        mysql.connection.commit()

        #close connection
        cur.close()

        flash('You have edited successfully', 'success')
        return redirect(url_for('dashboard'))

    return render_template('workshopsorganized.html',form=form,edit=1)

#########################  NEW ROUTE  ############################

@app.route('/edit/INVTALK-<string:id>', methods=['GET','POST'])
@is_logged_in
def edit_individual_invtalk(id):

    form = InvtalkForm(request.form)
    #Create cursor
    cur = mysql.connection.cursor()

    #Get the id
    result = cur.execute("select * from users where username = %s",[session['username']])

    if result>0:
        data = cur.fetchone()
        idfromdb = data['id']
    else:
        redirect(url_for('login'))

    #Get the achievement
    result = cur.execute("select * from INVTALK where userid = %s and id = %s",[idfromdb,id])
    instance = cur.fetchone()
    cur.close()

    #Fill form with existing data
    form.topic.data = instance['topic']
    form.venue.data = instance['venue']
    form.dateoft.data = instance['dateoft']
    form.noofstu.data = instance['noofstu']
    form.nooffac.data = instance['nooffac']
    form.industry.data = instance['industry']
    form.year.data = instance['year']
    form.month.data = instance['month']


    if request.method == 'POST' and form.validate():
        topic = request.form['topic']
        venue = request.form['venue']
        dateoft = request.form['dateoft']
        noofstu = request.form['noofstu']
        nooffac = request.form['nooffac']
        industry = request.form['industry']
        year = request.form['year']
        month = request.form['month']

        #Create cursor
        cur = mysql.connection.cursor()
        result = cur.execute("select * from users where username = %s",[session['username']])

        if result>0:
            data = cur.fetchone()
            idfromdb = data['id']
        else:
            redirect(url_for('login'))
        cur.execute("update INVTALK set year = %s, month = %s, topic = %s, venue = %s, dateoft = %s, noofstu = %s, nooffac = %s, industry = %s where userid = %s and id = %s", (year, month, topic, venue, dateoft, noofstu, nooffac, industry, idfromdb,id))
        #Commit to DB
        mysql.connection.commit()

        #close connection
        cur.close()

        flash('You have edited successfully', 'success')
        return redirect(url_for('dashboard'))

    return render_template('talks.html',form=form,edit=1)

#########################  NEW ROUTE  ############################

@app.route('/edit/EXPLECT-<string:id>', methods=['GET','POST'])
@is_logged_in
def edit_individual_explect(id):

    form = ExplectForm(request.form)
    #Create cursor
    cur = mysql.connection.cursor()

    #Get the id
    result = cur.execute("select * from users where username = %s",[session['username']])

    if result>0:
        data = cur.fetchone()
        idfromdb = data['id']
    else:
        redirect(url_for('login'))

    #Get the achievement
    result = cur.execute("select * from EXPLECT where userid = %s and id = %s",[idfromdb,id])
    instance = cur.fetchone()
    cur.close()

    #Fill form with existing data
    form.topic.data = instance['topic']
    form.rname.data = instance['nameofrp']
    form.onameaddr.data = instance['onameaddr']
    form.dateoft.data = instance['dateofel']
    form.noofstu.data = instance['noofstu']
    form.nooffac.data = instance['nooffac']
    form.industry.data = instance['industry']
    form.year.data = instance['year']
    form.month.data = instance['month']


    if request.method == 'POST' and form.validate():
        topic = request.form['topic']
        rname = request.form['rname']
        onameaddr = request.form['onameaddr']
        dateoft = request.form['dateoft']
        noofstu = request.form['noofstu']
        nooffac = request.form['nooffac']
        industry = request.form['industry']
        year = request.form['year']
        month = request.form['month']

        #Create cursor
        cur = mysql.connection.cursor()
        result = cur.execute("select * from users where username = %s",[session['username']])

        if result>0:
            data = cur.fetchone()
            idfromdb = data['id']
        else:
            redirect(url_for('login'))
        cur.execute("update EXPLECT set year = %s, month = %s, topic = %s, nameofrp = %s, onameaddr = %s, dateofel = %s, noofstu = %s, nooffac = %s, industry = %s where userid = %s and id = %s", (year, month, topic, rname, onameaddr, dateoft, noofstu, nooffac, industry, idfromdb,id))
        #Commit to DB
        mysql.connection.commit()

        #close connection
        cur.close()

        flash('You have edited successfully', 'success')
        return redirect(url_for('dashboard'))

    return render_template('lectures.html',form=form,edit=1)

#########################  NEW ROUTE  ############################

@app.route('/edit/WSCEA-<string:id>', methods=['GET','POST'])
@is_logged_in
def edit_individual_wscea(id):

    form = WscForm(request.form)
    #Create cursor
    cur = mysql.connection.cursor()

    #Get the id
    result = cur.execute("select * from users where username = %s",[session['username']])

    if result>0:
        data = cur.fetchone()
        idfromdb = data['id']
    else:
        redirect(url_for('login'))

    #Get the achievement
    result = cur.execute("select * from WSCEA where userid = %s and id = %s",[idfromdb,id])
    instance = cur.fetchone()
    cur.close()

    #Fill form with existing data
    form.wsc.data = instance['wsc']
    form.venue.data = instance['venue']
    form.dateoft.data = instance['dateofw']
    form.year.data = instance['year']
    form.month.data = instance['month']

    if request.method == 'POST' and form.validate():
        wsc = request.form['wsc']
        venue = request.form['venue']
        dateoft = request.form['dateoft']
        year = request.form['year']
        month = request.form['month']

        #Create cursor
        cur = mysql.connection.cursor()
        result = cur.execute("select * from users where username = %s",[session['username']])

        if result>0:
            data = cur.fetchone()
            idfromdb = data['id']
        else:
            redirect(url_for('login'))
        cur.execute("update WSCEA set year = %s, month = %s, wsc = %s, venue = %s, dateofw = %s where userid = %s and id = %s", (year, month, wsc, venue, dateoft, idfromdb,id))
        #Commit to DB
        mysql.connection.commit()

        #close connection
        cur.close()

        flash('You have edited successfully', 'success')
        return redirect(url_for('dashboard'))

    return render_template('workshopsattended.html',form=form,edit=1)

#########################  NEW ROUTE  ############################

@app.route('/edit/JOURNAL-<string:id>', methods=['GET','POST'])
@is_logged_in
def edit_individual_journal(id):

    form = JOURNALForm(request.form)
    #Create cursor
    cur = mysql.connection.cursor()

    #Get the id
    result = cur.execute("select * from users where username = %s",[session['username']])

    if result>0:
        data = cur.fetchone()
        idfromdb = data['id']
    else:
        redirect(url_for('login'))

    #Get the achievement
    result = cur.execute("select * from JOURNAL where userid = %s and id = %s",[idfromdb,id])
    instance = cur.fetchone()
    cur.close()

    #Fill form with existing data
    form.title.data = instance['title']
    form.jname.data = instance['jname']
    form.natorint.data = instance['natint']
    form.volno.data = instance['volno']
    form.issue.data = instance['issue']
    form.pageno.data = instance['pageno']
    form.scoind.data = instance['scoind']
    form.wos.data = instance['wos']
    form.gscho.data = instance['gsco']
    form.noofcert.data = instance['nocit']
    form.year.data = instance['year']
    form.month.data = instance['month']

    if request.method == 'POST' and form.validate():
        title = request.form['title']
        jname = request.form['jname']
        natorint = request.form['natorint']
        volno = request.form['volno']
        issue = request.form['issue']
        pageno = request.form['pageno']
        scoind = request.form['scoind']
        wos = request.form['wos']
        gscho = request.form['gscho']
        noofcert = request.form['noofcert']
        year = request.form['year']
        month = request.form['month']


        #Create cursor
        cur = mysql.connection.cursor()
        result = cur.execute("select * from users where username = %s",[session['username']])

        if result>0:
            data = cur.fetchone()
            idfromdb = data['id']
        else:
            redirect(url_for('login'))
        cur.execute("update JOURNAL set year = %s, month = %s, title = %s, jname = %s, natint = %s, volno = %s, issue = %s, pageno = %s, scoind = %s, wos = %s, gsco = %s, nocit = %s where userid = %s and id = %s", (year, month, title, jname, natorint, volno, issue, pageno, scoind, wos, gscho, nocert, idfromdb,id))
        #Commit to DB
        mysql.connection.commit()

        #close connection
        cur.close()

        flash('You have edited successfully', 'success')
        return redirect(url_for('dashboard'))

    return render_template('journal.html',form=form,edit=1)

#########################  NEW ROUTE  ############################

@app.route('/edit/CONF-<string:id>', methods=['GET','POST'])
@is_logged_in
def edit_individual_conf(id):

    form = CONFForm(request.form)
    #Create cursor
    cur = mysql.connection.cursor()

    #Get the id
    result = cur.execute("select * from users where username = %s",[session['username']])

    if result>0:
        data = cur.fetchone()
        idfromdb = data['id']
    else:
        redirect(url_for('login'))

    #Get the achievement
    result = cur.execute("select * from CONF where userid = %s and id = %s",[idfromdb,id])
    instance = cur.fetchone()
    cur.close()

    #Fill form with existing data
    form.title.data = instance['title']
    form.conf.data = instance['cname']
    form.natorint.data = instance['natint']
    form.volno.data = instance['volno']
    form.issue.data = instance['issue']
    form.pageno.data = instance['pageno']
    form.year.data = instance['year']
    form.month.data = instance['month']

    if request.method == 'POST' and form.validate():
        title = request.form['title']
        conf = request.form['cname']
        natorint = request.form['natorint']
        volno = request.form['volno']
        issue = request.form['issue']
        pageno = request.form['pageno']
        year = request.form['year']
        month = request.form['month']

        #Create cursor
        cur = mysql.connection.cursor()
        result = cur.execute("select * from users where username = %s",[session['username']])

        if result>0:
            data = cur.fetchone()
            idfromdb = data['id']
        else:
            redirect(url_for('login'))
        cur.execute("update CONF set year = %s, month = %s, title = %s, cname = %s, natint = %s, volno = %s, issue = %s, pageno = %s where userid = %s and id = %s", (year, month, title, conf, natorint, volno, issue, pageno, idfromdb,id))
        #Commit to DB
        mysql.connection.commit()

        #close connection
        cur.close()

        flash('You have edited successfully', 'success')
        return redirect(url_for('dashboard'))

    return render_template('conferences.html',form=form,edit=1)

#########################  NEW ROUTE  ############################

@app.route('/edit/BOOK-<string:id>', methods=['GET','POST'])
@is_logged_in
def edit_individual_book(id):

    form = BookForm(request.form)
    #Create cursor
    cur = mysql.connection.cursor()

    #Get the id
    result = cur.execute("select * from users where username = %s",[session['username']])

    if result>0:
        data = cur.fetchone()
        idfromdb = data['id']
    else:
        redirect(url_for('login'))

    #Get the achievement
    result = cur.execute("select * from BOOK where userid = %s and id = %s",[idfromdb,id])
    instance = cur.fetchone()
    cur.close()

    #Fill form with existing data
    form.bname.data = instance['bname']
    form.pubname.data = instance['pubname']
    form.isbn.data = instance['isbn']
    form.title.data = instance['titlechap']
    form.pageno.data = instance['pageno']
    form.year.data = instance['year']
    form.month.data = instance['month']

    if request.method == 'POST' and form.validate():
        bname = request.form['bname']
        pubname = request.form['pubname']
        isbn = request.form['isbn']
        title = request.form['title']
        pageno = request.form['pageno']
        year = request.form['year']
        month = request.form['month']

        #Create cursor
        cur = mysql.connection.cursor()
        result = cur.execute("select * from users where username = %s",[session['username']])

        if result>0:
            data = cur.fetchone()
            idfromdb = data['id']
        else:
            redirect(url_for('login'))
        cur.execute("update BOOK set year = %s, month = %s, bname = %s, pubname = %s, isbn = %s, titlechap = %s, pageno = %s where userid = %s and id = %s", (year, month, bname, pubname, isbn, title, pageno, idfromdb,id))
        #Commit to DB
        mysql.connection.commit()

        #close connection
        cur.close()

        flash('You have edited successfully', 'success')
        return redirect(url_for('dashboard'))

    return render_template('books.html',form=form,edit=1)

#########################  NEW ROUTE  ############################

@app.route('/edit/MOU-<string:id>', methods=['GET','POST'])
@is_logged_in
def edit_individual_mou(id):

    form = MouForm(request.form)
    #Create cursor
    cur = mysql.connection.cursor()

    #Get the id
    result = cur.execute("select * from users where username = %s",[session['username']])

    if result>0:
        data = cur.fetchone()
        idfromdb = data['id']
    else:
        redirect(url_for('login'))

    #Get the achievement
    result = cur.execute("select * from MOU where userid = %s and id = %s",[idfromdb,id])
    instance = cur.fetchone()
    cur.close()

    #Fill form with existing data
    form.org.data = instance['org']
    form.moc.data = instance['moc']
    form.moue.data = instance['moue']
    form.validity.data = instance['validity']
    form.year.data = instance['year']
    form.month.data = instance['month']

    if request.method == 'POST' and form.validate():
        org = request.form['org']
        moc = request.form['moc']
        moue = request.form['moue']
        validity = request.form['validity']
        year = request.form['year']
        month = request.form['month']

        #Create cursor
        cur = mysql.connection.cursor()
        result = cur.execute("select * from users where username = %s",[session['username']])

        if result>0:
            data = cur.fetchone()
            idfromdb = data['id']
        else:
            redirect(url_for('login'))
        cur.execute("update MOU set year = %s, month = %s, org = %s, moc = %s, moue = %s, validity = %s where userid = %s and id = %s", (year, month, org, moc, moue, validity, idfromdb,id))
        #Commit to DB
        mysql.connection.commit()

        #close connection
        cur.close()

        flash('You have edited successfully', 'success')
        return redirect(url_for('dashboard'))

    return render_template('mous.html',form=form,edit=1)

#########################  NEW ROUTE  ############################

@app.route('/edit/PATENT-<string:id>', methods=['GET','POST'])
@is_logged_in
def edit_individual_patent(id):

    form = PatentForm(request.form)
    #Create cursor
    cur = mysql.connection.cursor()

    #Get the id
    result = cur.execute("select * from users where username = %s",[session['username']])

    if result>0:
        data = cur.fetchone()
        idfromdb = data['id']
    else:
        redirect(url_for('login'))

    #Get the achievement
    result = cur.execute("select * from PATENT where userid = %s and id = %s",[idfromdb,id])
    instance = cur.fetchone()
    cur.close()

    #Fill form with existing data
    form.title.data = instance['title']
    form.author.data = instance['author']
    form.status.data = instance['status']
    form.pdate.data = instance['pdate']
    form.year.data = instance['year']
    form.month.data = instance['month']


    if request.method == 'POST' and form.validate():
        title = request.form['title']
        author = request.form['authoe']
        pdate = request.form['pdate']
        status = request.form['status']
        year = request.form['year']
        month = request.form['month']

        #Create cursor
        cur = mysql.connection.cursor()
        result = cur.execute("select * from users where username = %s",[session['username']])

        if result>0:
            data = cur.fetchone()
            idfromdb = data['id']
        else:
            redirect(url_for('login'))
        cur.execute("update PATENT year = %s, month = %s, set title = %s, author = %s, pdate = %s, status = %s where userid = %s and id = %s", (year, month, title, author, pdate, status, idfromdb,id))
        #Commit to DB
        mysql.connection.commit()

        #close connection
        cur.close()

        flash('You have edited successfully', 'success')
        return redirect(url_for('dashboard'))

    return render_template('patents.html',form=form,edit=1)

#########################  NEW ROUTE  ############################

@app.route('/edit/IVBYS-<string:id>', methods=['GET','POST'])
@is_logged_in
def edit_individual_ivbys(id):

    form = IvbysForm(request.form)
    #Create cursor
    cur = mysql.connection.cursor()

    #Get the id
    result = cur.execute("select * from users where username = %s",[session['username']])

    if result>0:
        data = cur.fetchone()
        idfromdb = data['id']
    else:
        redirect(url_for('login'))

    #Get the achievement
    result = cur.execute("select * from IVBYS where userid = %s and id = %s",[idfromdb,id])
    instance = cur.fetchone()
    cur.close()

    #Fill form with existing data
    form.sem.data = instance['sem']
    form.inameaddr.data = instance['inameaddt']
    form.nostu.data = instance['nostu']
    form.purpose.data = instance['purpose']
    form.year.data = instance['year']
    form.month.data = instance['month']

    if request.method == 'POST' and form.validate():
        sem = request.form['sem']
        inameaddr = request.form['inameaddr']
        nostu = request.form['nostu']
        purpose = request.form['purpose']
        year = request.form['year']
        month = request.form['month']

        #Create cursor
        cur = mysql.connection.cursor()
        result = cur.execute("select * from users where username = %s",[session['username']])

        if result>0:
            data = cur.fetchone()
            idfromdb = data['id']
        else:
            redirect(url_for('login'))
        cur.execute("update IVBYS set year = %s, month = %s, sem = %s, inameaddr= %s, nostu = %s, purpose = %s where userid = %s and id = %s", (year, month, sem, inameaddr, nostu, purpose, idfromdb,id))
        #Commit to DB
        mysql.connection.commit()

        #close connection
        cur.close()

        flash('You have edited successfully', 'success')
        return redirect(url_for('dashboard'))

    return render_template('visits.html',form=form,edit=1)

#########################  NEW ROUTE  ############################

@app.route('/edit/FACMEM3-<string:id>', methods=['GET','POST'])
@is_logged_in
def edit_individual_facmem(id):

    form = FacmemForm(request.form)
    #Create cursor
    cur = mysql.connection.cursor()

    #Get the id
    result = cur.execute("select * from users where username = %s",[session['username']])

    if result>0:
        data = cur.fetchone()
        idfromdb = data['id']
    else:
        redirect(url_for('login'))

    #Get the achievement
    result = cur.execute("select * from FACMEM where userid = %s and id = %s",[idfromdb,id])
    instance = cur.fetchone()
    cur.close()

    #Fill form with existing data
    form.ass.data = instance['ass']
    form.memdet.data = instance['memdet']
    form.term.data = instance['term']
    form.year.data = instance['year']
    form.month.data = instance['month']


    if request.method == 'POST' and form.validate():
        ass = request.form['ass']
        memdet = request.form['memdet']
        term = request.form['term']
        year = request.form['year']
        month = request.form['month']


        #Create cursor
        cur = mysql.connection.cursor()
        result = cur.execute("select * from users where username = %s",[session['username']])

        if result>0:
            data = cur.fetchone()
            idfromdb = data['id']
        else:
            redirect(url_for('login'))
        cur.execute("update FACMEM set year = %s, month = %s, ass = %s, memdet = %s, term = %s where userid = %s and id = %s", (year, month, ass, memdet, term, idfromdb,id))
        #Commit to DB
        mysql.connection.commit()

        #close connection
        cur.close()

        flash('You have edited successfully', 'success')
        return redirect(url_for('dashboard'))

    return render_template('membership-professional.html',form=form,edit=1)

#########################  NEW ROUTE  ############################

@app.route('/edit/UFACMEM-<string:id>', methods=['GET','POST'])
@is_logged_in
def edit_individual_ufacmem(id):

    form = UfacmemForm(request.form)
    #Create cursor
    cur = mysql.connection.cursor()

    #Get the id
    result = cur.execute("select * from users where username = %s",[session['username']])

    if result>0:
        data = cur.fetchone()
        idfromdb = data['id']
    else:
        redirect(url_for('login'))

    #Get the achievement
    result = cur.execute("select * from UFACMEM where userid = %s and id = %s",[idfromdb,id])
    instance = cur.fetchone()
    cur.close()

    #Fill form with existing data
    form.desi.data = instance['desi']
    form.body.data = instance['body']
    form.oname.data = instance['oname']
    form.year.data = instance['year']
    form.month.data = instance['month']

    if request.method == 'POST' and form.validate():
        desi = request.form['desi']
        body = request.form['body']
        oname = request.form['oname']
        year = request.form['year']
        month = request.form['month']

        #Create cursor
        cur = mysql.connection.cursor()
        result = cur.execute("select * from users where username = %s",[session['username']])

        if result>0:
            data = cur.fetchone()
            idfromdb = data['id']
        else:
            redirect(url_for('login'))
        cur.execute("update UFACMEM set year = %s, month = %s, desi = %s, body = %s, oname = %s where userid = %s and id = %s", (year, month, desi, body, oname, idfromdb,id))
        #Commit to DB
        mysql.connection.commit()

        #close connection
        cur.close()

        flash('You have edited successfully', 'success')
        return redirect(url_for('dashboard'))

    return render_template('membership-other.html',form=form,edit=1)

#########################  NEW ROUTE  ############################

@app.route('/edit/AWARDS-<string:id>', methods=['GET','POST'])
@is_logged_in
def edit_individual_awards(id):

    form = AwardsForm(request.form)
    #Create cursor
    cur = mysql.connection.cursor()

    #Get the id
    result = cur.execute("select * from users where username = %s",[session['username']])

    if result>0:
        data = cur.fetchone()
        idfromdb = data['id']
    else:
        redirect(url_for('login'))

    #Get the achievement
    result = cur.execute("select * from AWARDS where userid = %s and id = %s",[idfromdb,id])
    instance = cur.fetchone()
    cur.close()

    #Fill form with existing data
    form.adeti.data = instance['adeti']
    form.oname.data = instance['oname']
    form.year.data = instance['year']
    form.month.data = instance['month']

    if request.method == 'POST' and form.validate():
        adeti = request.form['adeti']
        oname = request.form['oname']
        year = request.form['year']
        month = request.form['month']

        #Create cursor
        cur = mysql.connection.cursor()
        result = cur.execute("select * from users where username = %s",[session['username']])

        if result>0:
            data = cur.fetchone()
            idfromdb = data['id']
        else:
            redirect(url_for('login'))
        cur.execute("update AWARDS set year = %s, month = %s, adeti = %s, oname = %s where userid = %s and id = %s", (year, month, adeti, oname, idfromdb,id))
        #Commit to DB
        mysql.connection.commit()

        #close connection
        cur.close()

        flash('You have edited successfully', 'success')
        return redirect(url_for('dashboard'))

    return render_template('awards.html',form=form,edit=1)

#########################  NEW ROUTE  ############################

@app.route('/edit/ANYOTH-<string:id>', methods=['GET','POST'])
@is_logged_in
def edit_individual_anyoth(id):

    form = AnyothForm(request.form)
    #Create cursor
    cur = mysql.connection.cursor()

    #Get the id
    result = cur.execute("select * from users where username = %s",[session['username']])

    if result>0:
        data = cur.fetchone()
        idfromdb = data['id']
    else:
        redirect(url_for('login'))

    #Get the achievement
    result = cur.execute("select * from ANYOTH where userid = %s and id = %s",[idfromdb,id])
    instance = cur.fetchone()
    cur.close()

    #Fill form with existing data
    form.event.data = instance['event']
    form.year.data = instance['year']
    form.month.data = instance['month']

    if request.method == 'POST' and form.validate():
        event = request.form['event']
        year = request.form['year']
        month = request.form['month']

        #Create cursor
        cur = mysql.connection.cursor()
        result = cur.execute("select * from users where username = %s",[session['username']])

        if result>0:
            data = cur.fetchone()
            idfromdb = data['id']
        else:
            redirect(url_for('login'))
        cur.execute("update ANYOTH set year = %s, month = %s, event = %s where userid = %s and id = %s", (year, month, event, idfromdb, id))
        #Commit to DB
        mysql.connection.commit()

        #close connection
        cur.close()

        flash('You have edited successfully', 'success')
        return redirect(url_for('dashboard'))

    return render_template('anyother.html',form=form,edit=1)


@app.route('/delete/<string:tname>-<string:id>', methods=['POST'])
@is_logged_in
def delete(tname,id):


    #Create cursor
    cur = mysql.connection.cursor()

    #Get the id
    result = cur.execute("select * from users where username = %s",[session['username']])

    if result>0:
        data = cur.fetchone()
        idfromdb = data['id']
    else:
        redirect(url_for('login'))

    #Get the achievement
    result = cur.execute("delete from {} where userid = %s and id = %s".format(tname),[idfromdb,id])


    #Commit to DB
    mysql.connection.commit()

    #close connection
    cur.close()
    flash('You have deleted successfully', 'success')
    return redirect(url_for('dashboard'))









@app.route('/add_achievement', methods=['GET','POST'])
@is_logged_in
def add_achievement():
    return render_template('add_achievement.html')



@app.route('/projects',methods=['GET','POST'])
def project():
    form = ProjectForm(request.form)
    if request.method == 'POST' and form.validate():
        pname = form.pname.data
        pincopi = form.pincopi.data
        psubto = form.psubto.data
        budamt = form.budamt.data
        pstat = form.pstat.data
        year = form.year.data
        month = form.month.data

        #Create cursor
        cur = mysql.connection.cursor()
        result = cur.execute("select * from users where username = %s",[session['username']])

        if result>0:
            data = cur.fetchone()
            idfromdb = data['id']
        else:
            redirect(url_for('login'))

        cur.execute("insert into PROJECTS (year, month, userid, pname, pincopiname, propsub, amount, prostat) values (%s, %s ,%s, %s, %s, %s, %s, %s)", (year, month, idfromdb, pname, pincopi, psubto, budamt, pstat))

        #Commit to DB
        mysql.connection.commit()

        #close connection
        cur.close()

        flash('You have added successfully', 'success')

        return redirect(url_for('add_achievement'))
    return render_template('projects.html',form=form,edit=0)




@app.route('/projectgrants',methods=['GET','POST'])
def projectgrant():
    form = ProjectGrantForm(request.form)
    if request.method == 'POST' and form.validate():
        pname = form.pname.data
        pincopi = form.pincopi.data
        fundage = form.fundage.data
        amounts = form.amounts.data
        year = form.year.data
        amountr= form.amountr.data
        remarks = form.remarks.data
        year = form.year.data
        month = form.month.data

        #Create cursor
        cur = mysql.connection.cursor()
        result = cur.execute("select * from users where username = %s",[session['username']])

        if result>0:
            data = cur.fetchone()
            idfromdb = data['id']
        else:
            redirect(url_for('login'))

        cur.execute("insert into PROGRANTS (year, month, userid, pname, pincopiname, funagency, sainl, syear, amount, remarks) values (%s, %s ,%s, %s, %s, %s, %s, %s, %s, %s)", [year, month, idfromdb, pname, pincopi, fundage , amounts, year, amountr, remarks])

        #Commit to DB
        mysql.connection.commit()

        #close connection
        cur.close()

        flash('You have added successfully', 'success')

        return redirect(url_for('add_achievement'))
    return render_template('projectgrants.html',form=form)



@app.route('/training',methods=['GET','POST'])
def training():
    form = TrainingForm(request.form)
    if request.method == 'POST' and form.validate():
        work = form.work.data
        facin = form.facin.data
        fundage = form.fundage.data
        amount = form.amount.data
        year = form.year.data
        month = form.month.data

        #Create cursor
        cur = mysql.connection.cursor()
        result = cur.execute("select * from users where username = %s",[session['username']])

        if result>0:
            data = cur.fetchone()
            idfromdb = data['id']
        else:
            redirect(url_for('login'))

        cur.execute("insert into TRAINING (year, month, userid, work, facin, funagency, amount) values (%s, %s ,%s, %s, %s, %s, %s)", (year, month, idfromdb, work, facin, fundage , amount))

        #Commit to DB
        mysql.connection.commit()

        #close connection
        cur.close()

        flash('You have added successfully', 'success')

        return redirect(url_for('add_achievement'))
    return render_template('training.html',form=form)






@app.route('/workshopsorganized',methods=['GET','POST'])
def workshop():
    form = WorkshopForm(request.form)
    if request.method == 'POST' and form.validate():
        det = form.det.data
        dateofe = form.dateofe.data
        noofstu = form.noofstu.data
        nooffac = form.nooffac.data
        industry = form.industry.data
        orgby = form.orgby.data
        year = form.year.data
        month = form.month.data

        #Create cursor
        cur = mysql.connection.cursor()
        result = cur.execute("select * from users where username = %s",[session['username']])

        if result>0:
            data = cur.fetchone()
            idfromdb = data['id']
        else:
            redirect(url_for('login'))

        cur.execute("insert into WSCE (year, month, userid, details, dateofe, noofstu, nooffac, industry, orgby) values (%s, %s ,%s, %s, %s, %s, %s, %s, %s)", (year, month, idfromdb, det, dateofe, noofstu, nooffac, industry, orgby))

        #Commit to DB
        mysql.connection.commit()

        #close connection
        cur.close()

        flash('You have added successfully', 'success')

        return redirect(url_for('add_achievement'))
    return render_template('workshopsorganized.html',form=form)



@app.route('/talks',methods=['GET','POST'])
def invitedtalk():
    form = InvtalkForm(request.form)
    if request.method == 'POST' and form.validate():
        topic = form.topic.data
        venue = form.venue.data
        dateoft = form.dateoft.data
        noofstu = form.noofstu.data
        nooffac = form.nooffac.data
        industry = form.industry.data
        year = form.year.data
        month = form.month.data

        #Create cursor
        cur = mysql.connection.cursor()
        result = cur.execute("select * from users where username = %s",[session['username']])

        if result>0:
            data = cur.fetchone()
            idfromdb = data['id']
        else:
            redirect(url_for('login'))

        cur.execute("insert into INVTALK (year, month, userid, topic, venue , dateoft , noofstu , nooffac , industry) values (%s, %s ,%s, %s, %s, %s, %s, %s, %s)", (year, month, idfromdb, topic, venue, dateoft, noofstu, nooffac, industry))

        #Commit to DB
        mysql.connection.commit()

        #close connection
        cur.close()

        flash('You have added successfully', 'success')

        return redirect(url_for('add_achievement'))
    return render_template('talks.html',form=form)



@app.route('/lectures',methods=['GET','POST'])
def expertlect():
    form = ExplectForm(request.form)
    if request.method == 'POST' and form.validate():
        topic = form.topic.data
        rname = form.rname.data
        onameaddr = form.onameaddr.data
        dateoft = form.dateoft.data
        noofstu = form.noofstu.data
        nooffac = form.nooffac.data
        industry = form.industry.data
        year = form.year.data
        month = form.month.data

        #Create cursor
        cur = mysql.connection.cursor()
        result = cur.execute("select * from users where username = %s",[session['username']])

        if result>0:
            data = cur.fetchone()
            idfromdb = data['id']
        else:
            redirect(url_for('login'))

        cur.execute("insert into EXPLECT (year, month, userid, topic, nameofrp , onameaddr , dateofel , noofstu , nooffac , industry) values (%s, %s ,%s, %s, %s, %s, %s, %s, %s, %s)", (year, month, idfromdb, topic, rname, onameaddr, dateoft, noofstu, nooffac, industry))

        #Commit to DB
        mysql.connection.commit()

        #close connection
        cur.close()

        flash('You have added successfully', 'success')

        return redirect(url_for('add_achievement'))
    return render_template('lectures.html',form=form)



@app.route('/workshopsattended',methods=['GET','POST'])
def wsc():
    form = WscForm(request.form)
    if request.method == 'POST' and form.validate():
        wsc = form.wsc.data
        venue = form.venue.data
        dateoft = form.dateoft.data
        year = form.year.data
        month = form.month.data

        #Create cursor
        cur = mysql.connection.cursor()
        result = cur.execute("select * from users where username = %s",[session['username']])

        if result>0:
            data = cur.fetchone()
            idfromdb = data['id']
        else:
            redirect(url_for('login'))

        cur.execute("insert into WSCEA (year, month, userid, wsc, venue, dateofw) values (%s, %s ,%s, %s, %s, %s)", (year, month, idfromdb, wsc, venue, dateoft))

        #Commit to DB
        mysql.connection.commit()

        #close connection
        cur.close()

        flash('You have added successfully', 'success')

        return redirect(url_for('add_achievement'))
    return render_template('workshopsattended.html',form=form)


@app.route('/journal',methods=['GET','POST'])
def journal():
    form = JournalForm(request.form)
    if request.method == 'POST' and form.validate():
        title = form.topic.data
        jname = form.rname.data
        natorint = form.onameaddr.data
        volnp = form.dateoft.data
        issue = form.noofstu.data
        pageno = form.nooffac.data
        scoind = form.industry.data
        wos = form.wos.data
        gscho = form.gscho.data
        noofcert = form.noofcert.data
        year = form.year.data
        month = form.month.data

        #Create cursor
        cur = mysql.connection.cursor()
        result = cur.execute("select * from users where username = %s",[session['username']])

        if result>0:
            data = cur.fetchone()
            idfromdb = data['id']
        else:
            redirect(url_for('login'))

        cur.execute("insert into JOURNAL (year, month, userid, title, jname , natint , volno , issue , pageno , scoind, wos, gsco, nocit) values (%s, %s ,%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)", (year, month, idfromdb, title, jname, natint, volno, issue, pageno, scoind, wos, gscho, noofcert))

        #Commit to DB
        mysql.connection.commit()

        #close connection
        cur.close()

        flash('You have added successfully', 'success')

        return redirect(url_for('add_achievement'))
    return render_template('journal.html',form=form)



@app.route('/conferences',methods=['GET','POST'])
def conference():
    form = ConferenceForm(request.form)
    if request.method == 'POST' and form.validate():
        title = form.title.data
        conf = form.conf.data
        natorint = form.natorint.data
        volno = form.volno.data
        issue = form.issue.data
        pageno = form.pageno.data
        year = form.year.data
        month = form.month.data

        #Create cursor
        cur = mysql.connection.cursor()
        result = cur.execute("select * from users where username = %s",[session['username']])

        if result>0:
            data = cur.fetchone()
            idfromdb = data['id']
        else:
            redirect(url_for('login'))

        cur.execute("insert into CONF (year, month, userid, title, cname, natint, volno, issue, pageno) values (%s, %s ,%s, %s, %s, %s, %s, %s, %s)", (year, month, idfromdb, title, conf, natorint, volno, issue, pageno))

        #Commit to DB
        mysql.connection.commit()

        #close connection
        cur.close()

        flash('You have added successfully', 'success')

        return redirect(url_for('add_achievement'))
    return render_template('conferences.html',form=form)




@app.route('/books',methods=['GET','POST'])
def book():
    form = BookForm(request.form)
    if request.method == 'POST' and form.validate():
        bname = form.bname.data
        pubname = form.pubname.data
        isbn = form.isbn.data
        title = form.title.data
        pageno = form.pageno.data
        year = form.year.data
        month = form.month.data

        #Create cursor
        cur = mysql.connection.cursor()
        result = cur.execute("select * from users where username = %s",[session['username']])

        if result>0:
            data = cur.fetchone()
            idfromdb = data['id']
        else:
            redirect(url_for('login'))

        cur.execute("insert into BOOK (year, month, userid, bname , pubname , isbn , titlechap , pageno) values (%s, %s ,%s, %s, %s, %s, %s, %s)", (year, month, idfromdb, bname, pubname, isbn, title, pageno))

        #Commit to DB
        mysql.connection.commit()

        #close connection
        cur.close()

        flash('You have added successfully', 'success')

        return redirect(url_for('add_achievement'))
    return render_template('books.html',form=form)



@app.route('/mous',methods=['GET','POST'])
def mou():
    form = MouForm(request.form)
    if request.method == 'POST' and form.validate():
        org = form.org.data
        moc = form.moc.data
        moue = form.moue.data
        validity = form.validity.data
        year = form.year.data
        month = form.month.data

        #Create cursor
        cur = mysql.connection.cursor()
        result = cur.execute("select * from users where username = %s",[session['username']])

        if result>0:
            data = cur.fetchone()
            idfromdb = data['id']
        else:
            redirect(url_for('login'))

        cur.execute("insert into MOU (year, month, userid, org, moc, moue, validity) values (%s, %s ,%s, %s, %s, %s, %s)", (year, month, idfromdb, org, moc, moue, validity))

        #Commit to DB
        mysql.connection.commit()

        #close connection
        cur.close()

        flash('You have added successfully', 'success')

        return redirect(url_for('add_achievement'))
    return render_template('mous.html',form=form)


@app.route('/patents',methods=['GET','POST'])
def patent():
    form = PatentForm(request.form)
    if request.method == 'POST' and form.validate():
        title = form.title.data
        author = form.author.data
        pdate = form.pdate.data
        status = form.status.data
        year = form.year.data
        month = form.month.data

        #Create cursor
        cur = mysql.connection.cursor()
        result = cur.execute("select * from users where username = %s",[session['username']])

        if result>0:
            data = cur.fetchone()
            idfromdb = data['id']
        else:
            redirect(url_for('login'))

        cur.execute("insert into PATENT (year, month, userid, title , author , pdate , status) values (%s, %s ,%s, %s, %s, %s, %s)", (year, month, idfromdb, title , author , pdate , status))

        #Commit to DB
        mysql.connection.commit()

        #close connection
        cur.close()

        flash('You have added successfully', 'success')

        return redirect(url_for('add_achievement'))
    return render_template('patents.html',form=form)


@app.route('/visits',methods=['GET','POST'])
def ivbys():
    form = IvbysForm(request.form)
    if request.method == 'POST' and form.validate():
        sem = form.sem.data
        inameaddr = form.inameaddr.data
        nostu = form.nostu.data
        purpose = form.purpose.data
        year = form.year.data
        month = form.month.data

        #Create cursor
        cur = mysql.connection.cursor()
        result = cur.execute("select * from users where username = %s",[session['username']])

        if result>0:
            data = cur.fetchone()
            idfromdb = data['id']
        else:
            redirect(url_for('login'))

        cur.execute("insert into IVBYS (year, month, userid, sem , inameaddr , nostu , purpose) values (%s, %s ,%s, %s, %s, %s, %s)", (year, month, idfromdb, sem , inameaddr , nostu , purpose))

        #Commit to DB
        mysql.connection.commit()

        #close connection
        cur.close()

        flash('You have added successfully', 'success')

        return redirect(url_for('add_achievement'))
    return render_template('visits.html',form=form)


@app.route('/membership-professional',methods=['GET','POST'])
def facmem():
    form = FacmemForm(request.form)
    if request.method == 'POST' and form.validate():
        ass = form.ass.data
        memdet = form.memdet.data
        term = form.term.data
        year = form.year.data
        month = form.month.data

        #Create cursor
        cur = mysql.connection.cursor()
        result = cur.execute("select * from users where username = %s",[session['username']])

        if result>0:
            data = cur.fetchone()
            idfromdb = data['id']
        else:
            redirect(url_for('login'))

        cur.execute("insert into FACMEM (year, month, userid, ass, memdet, term) values ( %s ,%s, %s, %s, %s, %s)", (year, month, idfromdb, ass, memdet, term))

        #Commit to DB
        mysql.connection.commit()

        #close connection
        cur.close()

        flash('You have added successfully', 'success')

        return redirect(url_for('add_achievement'))
    return render_template('membership-professional.html',form=form)


@app.route('/membership-other',methods=['GET','POST'])
def ufacmem():
    form = UfacmemForm(request.form)
    if request.method == 'POST' and form.validate():
        desi = form.desi.data
        body = form.body.data
        oname = form.oname.data
        year = form.year.data
        month = form.month.data

        #Create cursor
        cur = mysql.connection.cursor()
        result = cur.execute("select * from users where username = %s",[session['username']])

        if result>0:
            data = cur.fetchone()
            idfromdb = data['id']
        else:
            redirect(url_for('login'))

        cur.execute("insert into UFACMEM (year, month, userid, desi, body, oname) values ( %s ,%s, %s, %s, %s, %s)", (year, month, idfromdb, desi, body, oname))

        #Commit to DB
        mysql.connection.commit()

        #close connection
        cur.close()

        flash('You have added successfully', 'success')

        return redirect(url_for('add_achievement'))
    return render_template('membership-other.html',form=form)


@app.route('/awards',methods=['GET','POST'])
def awards():
    form = AwardsForm(request.form)
    if request.method == 'POST' and form.validate():
        adeti = form.adeti.data
        oname = form.oname.data
        year = form.year.data
        month = form.month.data

        #Create cursor
        cur = mysql.connection.cursor()
        result = cur.execute("select * from users where username = %s",[session['username']])

        if result>0:
            data = cur.fetchone()
            idfromdb = data['id']
        else:
            redirect(url_for('login'))

        cur.execute("insert into AWARDS (year, month, userid, adeti, oname) values ( %s , %s, %s, %s, %s)", (year, month, idfromdb, adeti, oname))

        #Commit to DB
        mysql.connection.commit()

        #close connection
        cur.close()

        flash('You have added successfully', 'success')

        return redirect(url_for('add_achievement'))
    return render_template('awards.html',form=form)


@app.route('/anyother',methods=['GET','POST'])
def anyoth():
    form = AnyothForm(request.form)
    if request.method == 'POST' and form.validate():
        event = form.event.data
        year = form.year.data
        month = form.month.data

        #Create cursor
        cur = mysql.connection.cursor()
        result = cur.execute("select * from users where username = %s",[session['username']])

        if result>0:
            data = cur.fetchone()
            idfromdb = data['id']
        else:
            redirect(url_for('login'))

        cur.execute("insert into ANYOTH (year, month, userid, event) values ( %s %s, %s, %s, %s)", (year, month, idfromdb, event))

        #Commit to DB
        mysql.connection.commit()

        #close connection
        cur.close()

        flash('You have added successfully', 'success')

        return redirect(url_for('add_achievement'))
    return render_template('anyother.html',form=form)


if __name__ =='__main__':
    app.secret_key='secret123'
    app.run(debug=True)
