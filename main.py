
from flask import Flask, render_template, request, session,redirect
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import json
from flask_mail import Mail
from datetime import datetime
import math

with open('config.json','r') as c:
    params=json.load(c)["params"]
local_server=True
app = Flask(__name__)
app.secret_key = 'islamicblogusers'
app.config.update(
    MAIL_SERVER='smtp.gmail.com',
    MAIL_PORT='465',
    MAIL_USE_SSL='True',
    MAIL_USER=params['gmail-user'],
    MAIL_PASSWORD=params['gmail-password']
)

mail=Mail(app)

if(local_server):
    app.config['SQLALCHEMY_DATABASE_URI'] = params['local_uri']
else:
     app.config['SQLALCHEMY_DATABASE_URI'] = params['prod_uri']

db = SQLAlchemy(app)


class icontacts(db.Model):
    '''
    sno, name phone_num, msg, date, email
    '''
    sno = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    phn = db.Column(db.String(15), nullable=False)
    mes = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(20), nullable=False)

class iblogs(db.Model):
    '''
    sno, name phone_num, msg, date, email
    '''
    sno = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(80), nullable=False)
    sub = db.Column(db.String(80), nullable=False)
    slug = db.Column(db.String(20), nullable=False)
    content= db.Column(db.String(100000), nullable=False)
    wrt = db.Column(db.String(20), nullable=False)
    dt = db.Column(db.String(12), nullable=True)
    img= db.Column(db.String(12), nullable=True)

@app.route("/home")
def home():
    posts = iblogs.query.filter_by().all()
    last=math.ceil(len(posts)/int(params['no_of_posts']))
    page=request.args.get('page')    
    if(not str(page).isnumeric()):
        page=1
    page=int(page)
    
    posts=posts[(page-1)*int(params['no_of_posts']):(page-1)*int(params['no_of_posts'])+int(params['no_of_posts'])]
    if(page==1):
        prev="#"
        pnext="home?page="+str(page+1)
    elif(page==last):
        prev="home?page="+str(page-1)
        pnext="#"
    else:
        prev="home?page="+str(page-1)
        pnext="home?page="+str(page+1)
    return render_template('home.html', params=params, posts=posts,next=pnext,prev=prev)

@app.route("/blogs")
def allblogs():
    posts = iblogs.query.filter_by().all()
    return render_template('allblogs.html', posts=posts)

@app.route("/logout")
def logout():
    session.pop('user')
    return redirect('home')

@app.route("/about")
def about():
    return render_template('about.html')
@app.route("/feedback")
def feedback():
    if ('user' in session and session['user'] == "naseebbdk@gmail.com" ) :
            posts =icontacts.query.filter_by().all()

    return render_template('feedback.html',posts=posts)
@app.route("/login",methods = ['GET', 'POST'])
def login():
    if ('user' in session and session['user'] == "naseebbdk@gmail.com" ) :
            posts = iblogs.query.filter_by().all()
            return render_template('dashboard.html', params=params,posts=posts)
    if request.method =='POST':
        username=request.form.get('user')
        psd=request.form.get('pass')
        print(username)
        print(psd)
        if(username=="naseebbdk@gmail.com" and psd=="nrk36731"):
            print("hi")
            session['user']=username
            print("hi")
            posts = iblogs.query.filter_by().all()
            return render_template('dashboard.html', params=params,posts=posts)
    return render_template('login.html',params=params)

@app.route("/contact", methods = ['GET', 'POST'])
def contact():
    if(request.method=='POST'):
        '''Add entry to the database'''
        name = request.form.get('name')
        email = request.form.get('email')
        phone = request.form.get('phone')
        message = request.form.get('message')
        entry = icontacts(name=name, phn = phone, mes = message,email = email )
        db.session.add(entry)
        db.session.commit()
        ''' mail.send_message('New Message from ' + name,
        sender=email,
        recipients=[params['gmail-user']],
        body=message+"\n-"+phone)'''
        return render_template('submit.html')
    return render_template('contact.html')

@app.route('/post/<string:post_slug>', methods=['GET'])
def post(post_slug):
    post = iblogs.query.filter_by(slug=post_slug).first()
    return render_template('post.html',post=post)
@app.route('/edit/<string:sno>', methods=['GET','POST'])
def edit(sno):
    if ('user' in session and session['user'] == "naseebbdk@gmail.com" ) :
        if request.method =="POST":
            new_title=request.form.get("title")
            new_sub=request.form.get("sub")
            new_content=request.form.get("content")
            new_image=request.form.get("img")
            new_writer=request.form.get("wrt")
            new_slug=request.form.get("slug")
            date=datetime.now()
            if sno=='0':
                post=iblogs(title=new_title,slug=new_slug,sub=new_sub,content=new_content,img=new_image,wrt=new_writer,dt=date)
                db.session.add(post)
                db.session.commit()
            else:
                post=iblogs.query.filter_by(sno=sno).first()
                post.title=new_title
                post.slug=new_slug
                post.sub=new_sub
                post.content=new_content
                post.img=new_image
                post.wrt=new_writer
                post.date=date
                db.session.commit()
                return redirect('/edit/'+sno)
        post=iblogs.query.filter_by(sno=sno).first()
        return render_template('edit.html',params=params,post=post,sno=sno)


@app.route("/delete/<string:sno>", methods=['GET','POST'])
def delete(sno):
    if ('user' in session and session['user'] == "naseebbdk@gmail.com" ) :
        post=iblogs.query.filter_by(sno=sno).first()
        db.session.delete(post)
        db.session.commit()
        print("deleted")
    return redirect("/login")


    
    

    

app.run(debug=True)