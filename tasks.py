from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
import sqlite3
from pathlib import Path
from datetime import datetime


user = 'PlanMyLife'

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///'+user+'.db'
db = SQLAlchemy(app)

class Info(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50))
    password = db.Column(db.String(50))
    f_name = db.Column(db.String(50))
    l_name = db.Column(db.String(50))
    email = db.Column(db.String(50))
    gender = db.Column(db.String(50))
    date = db.Column(db.String(50))


class Stickers(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.String(50))
    text = db.Column(db.String(50))



class Targets(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.String(50))
    objective = db.Column(db.String(500))
    deadline = db.Column(db.String(50))



# for logging in
@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        Username = request.form.get('username')
        Password = request.form.get('password')

        path3 = Path('Tasks/'+Username+'.db')
        if path3.exists():
            conn = sqlite3.connect('Tasks/'+Username+'.db')
            c = conn.cursor()
            c.execute("SELECT * from Info")
            entire_list = c.fetchall()
            if Password == entire_list[0][2]:
                app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///'+Username+".db"
                # db = SQLAlchemy(app)
                return redirect('/view')
            else:
                return render_template('try_login.html')
        else:
            return render_template('try_login.html')

    return render_template('login.html')


# setting new account
@app.route('/setup', methods=['POST', 'GET'])
def setup():
    if request.method == 'POST':
        Username = request.form.get('username')
        
        path4 = Path('Tasks/'+Username+'.db')
        if path4.exists():
            return('Account already exist')

        else:
            Username = request.form.get('username')
            Password = request.form.get('password')
            f_name = request.form.get('f_name')
            l_name = request.form.get('l_name')
            email = request.form.get('email')
            gender = request.form.get('gender')
            date = request.form.get('dob')
 
            info = Info(username=Username, password=Password, f_name=f_name, l_name=l_name,
                        email=email, gender=gender, date=date)

            db.session.add(info)
            db.session.commit()

            path2 = Path("Tasks/"+user+".db")
            path2.rename("Tasks/"+Username+".db")

            return redirect('/')

    return render_template('setup.html')


@app.route('/edit_info', methods=['GET', 'POST'])
def edit_info():
    info = Info.query.all()
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        f_name = request.form.get('f_name')
        l_name = request.form.get('l_name')
        email = request.form.get('email')
        gender = request.form.get('gender')
        date = request.form.get('dob')

        for item in info:
            item.username = username
            item.password = password
            item.email = email
            item.gender = gender
            item.date = date
            item.f_name = f_name
            item.l_name = l_name
        db.session.commit()
        return render_template('edit_info.html', info=info)
    return render_template('edit_info.html', info=info)

@app.route('/view')
def view():
    targets = Targets.query.all()
    stickers = Stickers.query.all()
    return render_template('viewpage.html',targets=targets, stickers=stickers)


# for stickers
@app.route('/sticker', methods=['POST'])
def sticker():
    text = request.form.get('sticker')
    date = datetime.utcnow().strftime('%x')

    content = Stickers(text=text, date=date)
     
    db.session.add(content)
    db.session.commit()
    return redirect('/view')


@app.route('/stickers/delete/<int:id>')
def del_sticky(id):
    stickers = Stickers.query.filter_by(id=id).first()
    db.session.delete(stickers)
    db.session.commit()
    return redirect('/view')


@app.route('/stickers/edit/<int:id>', methods=['GET', 'POST'])
def edit_sticky(id):
    sticker = Stickers.query.filter_by(id=id).first()
    if request.method == 'POST':
        sticky = request.form.get('sticky')
        today = datetime.utcnow().strftime('%x')

        sticker.text = sticky
        sticker.date = today

        db.session.commit()
        return redirect('/view')
    return render_template('edit_sticky.html', sticker=sticker)


# for Objectives
@app.route('/target', methods=['POST'])
def target():
    objective = request.form.get('objective')
    deadline = request.form.get('deadline')
    now = datetime.utcnow().strftime('%x')

    target = Targets(objective = objective, deadline = deadline, date = now)
    
    db.session.add(target)
    db.session.commit()
    return redirect('/view')


@app.route('/targets/delete/<int:id>')
def del_target(id):
    targets = Targets.query.filter_by(id=id).first()
    db.session.delete(targets)
    db.session.commit()
    return redirect('/view')


@app.route('/targets/edit/<int:id>', methods=['POST', 'GET'])
def edit_target(id):
    target = Targets.query.filter_by(id=id).first()
    if request.method == 'POST':
        objective = request.form.get('objective')
        deadline = request.form.get('deadline')
        today = datetime.utcnow().strftime('%x')

        target.objective = objective
        target.deadline = deadline
        target.date = today
        
        db.session.commit()
        return redirect('/view')
    return render_template('edit_targets.html', target=target)


if __name__ == '__main__':
    db.create_all()
    app.run(debug=True)
