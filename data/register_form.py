from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, IntegerField, EmailField
from wtforms.validators import DataRequired, Optional


class RegisterForm(FlaskForm):
    surname = StringField("Фамилия", validators=[DataRequired()])
    name = StringField("Имя", validators=[DataRequired()])
    age = IntegerField("Возраст", validators=[DataRequired()])
    position = StringField("Должность", validators=[DataRequired()])
    speciality = StringField("Специальность", validators=[DataRequired()])
    address = StringField("Адрес проживания", validators=[DataRequired()])
    email = EmailField("Электронная почта", validators=[DataRequired()])

    password = PasswordField("Пароль", validators=[Optional()])
    repeat_password = PasswordField("Повторите пароль", validators=[Optional()])
    submit = SubmitField('Сохранить')

    def __init__(self, *args, is_editing=False, **kwargs):
        super(RegisterForm, self).__init__(*args, **kwargs)
        self.is_editing = is_editing

        if not self.is_editing:
            self.password.validators = [DataRequired()]
            self.repeat_password.validators = [DataRequired()]
            self.submit.label.text = 'Зарегистрировать'
        else:
            self.submit.label.text = 'Сохранить'
