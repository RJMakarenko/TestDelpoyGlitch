import flask
from flask import make_response, request, jsonify
from werkzeug.exceptions import BadRequest, Conflict, NotFound

from data import db_session
from data.users import User


users_bp = flask.Blueprint('users_api', __name__, template_folder='templates')


@users_bp.route('/users', methods=['GET'])
def get_users():
    session = db_session.create_session()
    users = session.query(User).all()
    return flask.jsonify({'users': ([item.to_dict(
        only=('id', 'surname', 'name', 'age', 'position', 'speciality', 'address', 'email'
     )
    ) for item in users])})


@users_bp.route('/users/<int:user_id>', methods=['GET'])
def get_one_user(user_id):
    session = db_session.create_session()
    user = session.query(User).get(user_id)
    if not user:
        return make_response(flask.jsonify({'error': 'Not found'}), 404)
    return flask.jsonify(user.to_dict(
        only=('id', 'surname', 'name', 'age', 'position', 'speciality', 'address', 'email')))


@users_bp.route('/users', methods=['POST'])
def register_user():
    data = request.get_json()

    # Проверка обязательных полей
    required_fields = ['surname', 'name', 'age', 'position',
                       'speciality', 'address', 'email',
                       'password', 'repeat_password']
    if not all(field in data for field in required_fields):
        raise BadRequest("Отсутствуют необходимые поля!")

    # Проверка совпадения паролей
    if data['password'] != data['repeat_password']:
        raise BadRequest("Пароли не совпадают!")

    session = db_session.create_session()

    # Проверка существования пользователя
    if session.query(User).filter_by(email=data['email']).first():
        raise Conflict("Пользователь с указанным email уже существует!")

    try:
        # Создание пользователя
        user = User(
            surname=data['surname'],
            name=data['name'],
            age=data['age'],
            position=data['position'],
            speciality=data['speciality'],
            address=data['address'],
            email=data['email']
        )
        user.set_password(data['password'])
        session.add(user)
        session.commit()

        # Возвращаем созданный объект без пароля
        return jsonify({
            'id': user.id,
            'surname': user.surname,
            'name': user.name,
            'email': user.email,
            'modified_date': user.modified_date.isoformat()
        }), 201

    except Exception as e:
        session.rollback()
        raise BadRequest(f"Ошибка регистрации: {str(e)}")
    finally:
        session.close()


@users_bp.route('/users/<int:user_id>', methods=['PUT'])
def update_user(user_id):
    data = request.get_json()
    session = db_session.create_session()

    try:
        # Получаем пользователя
        user = session.get(User, user_id)
        if not user:
            raise NotFound("Пользователь не найден")

        # Поля, которые можно обновлять
        updatable_fields = ['surname', 'name', 'age',
                            'position', 'speciality', 'address']

        # Обновляем разрешенные поля
        for field in updatable_fields:
            if field in data:
                setattr(user, field, data[field])

        # Обновление пароля (если передано)
        if 'password' in data or 'repeat_password' in data:
            if data.get('password') != data.get('repeat_password'):
                raise BadRequest("Пароли не совпадают")
            user.set_password(data['password'])

        session.commit()

        # Возвращаем обновленные данные
        return jsonify({
            'id': user.id,
            'surname': user.surname,
            'name': user.name,
            'email': user.email,
            'modified_date': user.modified_date.isoformat()
        }), 200

    except Exception as e:
        session.rollback()
        raise BadRequest(f"Ошибка обновления: {str(e)}")
    finally:
        session.close()
