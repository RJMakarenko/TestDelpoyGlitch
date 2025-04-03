import flask
from flask import jsonify, make_response
from flask_restful import Resource
from werkzeug.exceptions import NotFound
from werkzeug.security import generate_password_hash

from api_v2.reqparse_user import parser
from data import db_session
from data.jobs import Jobs
from data.users import User


def set_password(password):
    return generate_password_hash(password)


class UsersResource(Resource):
    def get(self, user_id):
        session = db_session.create_session()
        user = session.query(User).get(user_id)
        if not user:
            raise NotFound('Пользователь не существует!')
        return flask.jsonify(user.to_dict(
            only=('id', 'surname', 'name', 'age', 'position', 'speciality', 'address', 'email')))

    def post(self):
        ...


class UsersListResource(Resource):
    def get(self):
        session = db_session.create_session()
        users = session.query(User).all()
        return flask.jsonify({'users': ([item.to_dict(
            only=('id', 'surname', 'name', 'age', 'position', 'speciality', 'address', 'email'
                  )
        ) for item in users])})

    def post(self):
        args = parser.parse_args()
        session = db_session.create_session()
        user = User(
            name=args['name'],
            surname=args['surname'],
            age=args['age'],
            address=args['address'],
            email=args['email'],
            position=args['position'],
            speciality=args['speciality'],
            hashed_password=set_password(args['hashed_password'])
        )
        session.add(user)
        session.commit()
        return make_response(jsonify({
            'id': user.id,
            'surname': user.surname,
            'name': user.name,
            'email': user.email,
            'modified_date': user.modified_date.isoformat()
        }), 201)
