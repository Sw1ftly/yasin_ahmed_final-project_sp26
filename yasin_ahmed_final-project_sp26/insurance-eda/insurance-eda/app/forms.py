from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, DateField, HiddenField, SubmitField
from wtforms.validators import DataRequired, Optional, Length


BENEFIT_CHOICES = [
    ('Health', 'Health'),
    ('Life', 'Life'),
    ('Accident', 'Accident'),
    ('Disability', 'Disability'),
]

GENDER_CHOICES = [
    ('', '-- Select --'),
    ('Male', 'Male'),
    ('Female', 'Female'),
    ('Other', 'Other'),
]

STATE_CHOICES = [
    ('', '-- Select --'),
    ('AL','AL'),('AK','AK'),('AZ','AZ'),('AR','AR'),('CA','CA'),
    ('CO','CO'),('CT','CT'),('DE','DE'),('FL','FL'),('GA','GA'),
    ('HI','HI'),('ID','ID'),('IL','IL'),('IN','IN'),('IA','IA'),
    ('KS','KS'),('KY','KY'),('LA','LA'),('ME','ME'),('MD','MD'),
    ('MA','MA'),('MI','MI'),('MN','MN'),('MS','MS'),('MO','MO'),
    ('MT','MT'),('NE','NE'),('NV','NV'),('NH','NH'),('NJ','NJ'),
    ('NM','NM'),('NY','NY'),('NC','NC'),('ND','ND'),('OH','OH'),
    ('OK','OK'),('OR','OR'),('PA','PA'),('RI','RI'),('SC','SC'),
    ('SD','SD'),('TN','TN'),('TX','TX'),('UT','UT'),('VT','VT'),
    ('VA','VA'),('WA','WA'),('WV','WV'),('WI','WI'),('WY','WY'),
]


class QuoteForm(FlaskForm):
    # Lookup existing
    customer_id = StringField('Existing Customer ID (leave blank to create new)',
                              validators=[Optional()])
    # New customer fields
    name        = StringField('Full Name', validators=[Optional(), Length(max=100)])
    dob         = DateField('Date of Birth', validators=[Optional()])
    gender      = SelectField('Gender', choices=GENDER_CHOICES, validators=[Optional()])
    state_code  = SelectField('State', choices=STATE_CHOICES, validators=[Optional()])
    zip_code    = StringField('ZIP Code', validators=[Optional(), Length(max=10)])
    # Policy fields
    account_id  = StringField('Employer Account ID', validators=[DataRequired()])
    company_code = StringField('Company Code', validators=[DataRequired()])
    benefit_type = SelectField('Benefit Type', choices=BENEFIT_CHOICES,
                               validators=[DataRequired()])
    submit = SubmitField('Get Quote')


class AcceptQuoteForm(FlaskForm):
    customer_id  = HiddenField()
    account_id   = HiddenField()
    company_code = HiddenField()
    benefit_type = HiddenField()
    premium      = HiddenField()
    submit       = SubmitField('Accept & Issue Policy')
