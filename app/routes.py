from app import app
from flask import render_template, request, redirect, url_for, session, g, flash
from werkzeug.urls import url_parse
from app.forms import LoginForm, RegistrationForm, QuestionForm
from app.models import User, Questions , Admin
from app import db


@app.before_request
def before_request():
    g.user = None
    g.admin = None

    # admin = Admin.query.filter_by(id=session['user_id']).first()
    if 'user_id' in session:
        user = User.query.filter_by(id=session['user_id']).first()
        g.user = user

@app.route('/')
def home():
    # form = QuestionForm()
    q = Questions.query.first()
    session['count'] =0
    return render_template('index.html', title='Home',q=q)


@app.route('/admin', methods=['GET', 'POST'])
def admin():
    form = LoginForm()
    if form.validate_on_submit():
        admin = Admin(username=form.username.data)
        admin.set_password(form.password.data)
        db.session.add(admin)
        db.session.commit()

    if g.user:
        return redirect(url_for('home'))
    return redirect(url_for('add_edit_delete'))

@app.route('/add_edit_delete', methods=['GET', 'POST'])
def add_edit_delete():
    form = QuestionForm()
    q = Questions.query.all()
    return render_template('add_edit_delete.html', form=form, q=q, title='Question {}'.format(id))


@app.route('/edit_question/<int:id>', methods=['GET', 'POST'])
def edit_question(id):
    data = Questions.query.filter_by(q_id=id).first()
    ques = data
    if ques:
        form = QuestionForm(formdata=request.form, obj=ques)
        if request.method == 'POST' and form.validate():
            # save edits
            # save_changes(album, form)
            flash('Album updated successfully!')
            return redirect(url_for('add_edit_delete'))
        return render_template('edit.html', form=form)


@app.route('/delete_question/<int:id>', methods=['GET', 'POST'])
def delete_question(id):
    data = Questions.query.filter_by(q_id=id).first()
    if request.method == 'GET':
        if data:
            db.session.delete(data)
            db.session.commit()
            return redirect(url_for('add_edit_delete'))
    return redirect(url_for('add_edit_delete'))

@app.route('/add_question', methods=['GET', 'POST'])
def add_question():
    form = QuestionForm()

    if request.method == 'POST':
        question_data = request.form['question']
        option_a = request.form['optionA']
        option_b = request.form['optionB']
        option_c = request.form['optionC']
        option_d = request.form['optionD']
        ans = request.form['ans']

        question = Questions(ques=question_data,a=option_a , b=option_b, c=option_c, d=option_d, ans=ans)
        db.session.add(question)
        db.session.commit()

    return render_template('add_edit.html', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid Credential')
            return redirect(url_for('login'))
        session['user_id'] = user.id
        session['marks'] = 0
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('home')
        return redirect(next_page)
        return redirect(url_for('home'))
    if g.user:
        return redirect(url_for('home'))
    return render_template('login.html', form=form, title='Login')

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.password.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        session['user_id'] = user.id
        session['marks'] = 0
        return redirect(url_for('home'))
    if g.user:
        return redirect(url_for('home'))
    return render_template('register.html', title='Register', form=form)



@app.route('/question/<int:id>', methods=['GET', 'POST'])
def question(id):
    form = QuestionForm()
    q = Questions.query.filter_by(q_id=id).first()
    q_ids= Questions.query.all()
    data=[i.q_id for i in q_ids]

    
    if not q:
        return redirect(url_for('score'))
    if not g.user:
        return redirect(url_for('login'))
    if request.method == 'POST':
            session['count'] += 1
            print('----->', session['count'])
            q = Questions.query.filter_by(q_id=id).first()

            option = request.form['options']
            if option == q.ans:
                session['marks'] += 10
            return redirect(url_for('question', id=(data[session['count']])))
    form.options.choices = [(q.a, q.a), (q.b, q.b), (q.c, q.c), (q.d, q.d)]
    return render_template('question.html', form=form, q=q, title='Question {}'.format(id))


@app.route('/score')
def score():
    if not g.user:
        return redirect(url_for('login'))
    g.user.marks = session['marks']
    # db.session.commit()
    return render_template('score.html', title='Final Score')

@app.route('/logout')
def logout():
    if not g.user:
        return redirect(url_for('login'))
    session.pop('user_id', None)
    session.pop('marks', None)
    return redirect(url_for('home'))
