import requests
from flask import Flask, render_template, redirect, request, jsonify, url_for
from flask_login import LoginManager
from flask_login import login_user, login_required, logout_user
from werkzeug.exceptions import HTTPException
import logging

from api.jobs_api import get_jobs
from api.jobs_api import jobs_bp
from api.users_api import get_users
from api.users_api import users_bp
from api_v2.jobs_api_v2 import JobsListResource, JobsResource
from api_v2.users_api_v2 import UsersListResource, UsersResource
from data import db_session
from data.login_form import LoginForm
from data.register_form import RegisterForm
from data.users import User

from flask_restful import Api

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("app.log"),  # Запись в файл
        logging.StreamHandler()  # Вывод в консоль (если сервер позволяет)
    ]
)

app = Flask(__name__)
app.register_blueprint(jobs_bp, url_prefix='/api')
app.register_blueprint(users_bp, url_prefix='/api')

api_version2 = Api(app)
api_version2.add_resource(JobsListResource, '/api/v2/jobs')
api_version2.add_resource(JobsResource, '/api/v2/jobs/<int:job_id>')
api_version2.add_resource(UsersListResource, '/api/v2/users')
api_version2.add_resource(UsersResource, '/api/v2/users/<int:user_id>')

app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'
login_manager = LoginManager()
login_manager.init_app(app)

API_SERVER = 'http://localhost:5000/api'


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.get(User, user_id)


@app.route('/')
def index():
    jobs = get_jobs().json
    users = get_users().json
    return render_template("index.html", jobs=jobs, names=users)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        session = db_session.create_session()
        user = session.query(User).filter(User.email == form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect('/')
    return render_template('login_2.html', title='Авторизация', form=form)


# @app.route('/register', methods=['GET', 'POST'])
# def register():
#     form = RegisterForm()
#     if form.password.data != form.repeat_password.data:
#         return render_template('register.html', title="Регистрация пользователя",
#                                message="Пароли не совпадают!", form=form)
#     session = db_session.create_session()
#     if form.validate_on_submit():
#         if session.query(User).filter(User.email == form.email.data).first():
#             return render_template('register.html', title="Регистрация пользователя",
#                                    message="Такой пользователь уже существует!", form=form)
#         user = User(
#             surname=form.surname.data,
#             name=form.name.data,
#             age=form.age.data,
#             position=form.position.data,
#             speciality=form.speciality.data,
#             address=form.address.data,
#             email=form.email.data,
#         )
#         user.set_password(form.password.data)
#         session.add(user)
#         session.commit()
#         return redirect('/login')
#     return render_template('register.html', title="Регистрация пользователя", form=form)

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()

    if request.method == 'POST' and form.validate_on_submit():
        user_data = {
            'surname': form.surname.data,
            'name': form.name.data,
            'age': form.age.data,
            'position': form.position.data,
            'speciality': form.speciality.data,
            'address': form.address.data,
            'email': form.email.data,
            'password': form.password.data,
            'repeat_password': form.repeat_password.data,
        }
        response = requests.post(f'https://localhost/api/users', json=user_data)
        if response.status_code == 201:
            return redirect('/login')

        error_data = response.json()
        return render_template('register.html',
                               form=form,
                               message=error_data.get('error'))

    return render_template('register.html', title="Регистрация пользователя", form=form)


@app.route('/users/<int:user_id>', methods=['GET', 'POST'])
def edit_user(user_id):
    form = RegisterForm(is_editing=True)
    if request.method == 'GET':
        response = requests.get(f'{API_SERVER}/users/{user_id}')
        if response.status_code != 200:
            return render_template('register.html', title="Редактирование пользователя", form=form,
                                   message='Пользователь не найден!', edit=True)
        user_data = response.json()
        form = RegisterForm(data=user_data, is_editing=True)
    if request.method == 'POST' and form.validate_on_submit():
        user_data = {
            'surname': form.surname.data,
            'name': form.name.data,
            'age': form.age.data,
            'position': form.position.data,
            'speciality': form.speciality.data,
            'address': form.address.data,
            'email': form.email.data,
        }

        # Отправляем PUT-запрос в API
        response = requests.put(
            f'{API_SERVER}/users/{user_id}',
            json=user_data
        )
        if response.ok:
            return redirect(url_for('index'))

        error_data = response.json()
        return render_template('register.html',
                               title="Редактирование пользователя",
                               form=form,
                               edit=True,
                               message=error_data.get('error', 'Ошибка обновления'))

    return render_template('register.html', title="Редактирование пользователя", form=form, edit=True)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")


@app.errorhandler(HTTPException)
def handle_http_exception(error):
    """Обрабатывает стандартные HTTP-исключения Flask"""
    response = jsonify({
        'error': error.description,
        'status_code': error.code
    })
    response.status_code = error.code
    return response


@app.errorhandler(Exception)
def handle_generic_exception(error):
    """Обрабатывает все остальные исключения (например, базовые Exception)"""
    response = jsonify({
        'error': 'Internal Server Error',
        'message': str(error)
    })
    response.status_code = 500
    return response


def main():
    db_session.global_init('db/mars.db')
    app.run(host='0.0.0.0')


if __name__ == '__main__':
    main()
