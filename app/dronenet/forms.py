from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, Length

# Settings form class
class SettingsForm(FlaskForm):
  name = StringField('Name', validators=[DataRequired(), Length(min=2, max=46)])
  update = SubmitField('Update')
