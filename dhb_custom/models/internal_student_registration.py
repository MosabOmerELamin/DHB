from odoo import models, fields, api
from datetime import datetime, timedelta


class InternalStudentRegistration(models.Model):
    _name = 'internal.student.registration'
    _description = 'Internal Student Registration'

    student_id = fields.Many2one('tc.student',
                                 string='Learner Name')
    # field
    student_no = fields.Char(string='Student Number')
    title = fields.Selection([
        ('Mr', 'Mr'),
        ('Mrs', 'Mrs'),
        ('Miss', 'Miss'),
        ('Ms', 'Ms'),
        ('Dr', 'Dr'),
        ('Eur-Ing', 'Eur-Ing'),
        ('Captain', 'Captain'),
        ('Professor', 'Professor'),
        ('Dept', 'Dept'),
        ('Sir', 'Sir'),
        ('Reverend', 'Reverend')
    ], string='Title')

    forenames_given_name = fields.Char(string='Forenames/Given Name')
    surname_family_name = fields.Char(string='Surname/Family Name')
    gender = fields.Selection([
        ('male', 'Male'),
        ('female', 'Female'),
        ('unspecified', 'Unspecified')
    ], string='Gender')
    dob = fields.Date(string='Date of Birth')
    # nationality = fields.Char(string='Nationality')
    mail_address = fields.Selection([
        ('home', 'Home'),
        ('work', 'Work'),
    ], string='Mailing Address')
    address_line1 = fields.Char(string='Address Line 1')
    address_line2 = fields.Char(string='Address Line 2', required=False)
    address_line3 = fields.Char(string='Address Line 3', required=False)
    address_line4 = fields.Char(string='Address Line 4', required=False)
    town_city = fields.Char(string='Town/City')
    county = fields.Char(string='County')
    postcode = fields.Char(string='Postcode')
    country_id = fields.Many2one(string="Country", comodel_name='res.country')
    work_phone = fields.Char(string='Work Phone')
    home_phone = fields.Char(string='Home Phone')
    mobile_phone = fields.Char(string='Mobile Phone')
    email = fields.Char(string='Email')

    Practical_exam = fields.Boolean(
        string='Practical exam'
    )
    Theoretical_exam = fields.Boolean(
        string='Theoretical exam'
    )
    both_exam = fields.Boolean(
        string='Both Exam'
    )

    NATIONALITIES = [
        ('afghan', 'Afghan'),
        ('albanian', 'Albanian'),
        ('algerian', 'Algerian'),
        ('american', 'American'),
        ('andorran', 'Andorran'),
        ('angolan', 'Angolan'),
        ('antiguans', 'Antiguans'),
        ('argentinean', 'Argentinean'),
        ('armenian', 'Armenian'),
        ('australian', 'Australian'),
        ('austrian', 'Austrian'),
        ('azerbaijani', 'Azerbaijani'),
        ('bahamian', 'Bahamian'),
        ('bahraini', 'Bahraini'),
        ('bangladeshi', 'Bangladeshi'),
        ('barbadian', 'Barbadian'),
        ('barbudans', 'Barbudans'),
        ('batswana', 'Batswana'),
        ('belarusian', 'Belarusian'),
        ('belgian', 'Belgian'),
        ('belizean', 'Belizean'),
        ('beninese', 'Beninese'),
        ('bhutanese', 'Bhutanese'),
        ('bolivian', 'Bolivian'),
        ('bosnian', 'Bosnian'),
        ('brazilian', 'Brazilian'),
        ('british', 'British'),
        ('bruneian', 'Bruneian'),
        ('bulgarian', 'Bulgarian'),
        ('burkinabe', 'Burkinabe'),
        ('burmese', 'Burmese'),
        ('burundian', 'Burundian'),
        ('cambodian', 'Cambodian'),
        ('cameroonian', 'Cameroonian'),
        ('canadian', 'Canadian'),
        ('cape verdean', 'Cape Verdean'),
        ('central african', 'Central African'),
        ('chadian', 'Chadian'),
        ('chilean', 'Chilean'),
        ('chinese', 'Chinese'),
        ('colombian', 'Colombian'),
        ('comoran', 'Comoran'),
        ('congolese', 'Congolese'),
        ('costa rican', 'Costa Rican'),
        ('croatian', 'Croatian'),
        ('cuban', 'Cuban'),
        ('cypriot', 'Cypriot'),
        ('czech', 'Czech'),
        ('danish', 'Danish'),
        ('djibouti', 'Djibouti'),
        ('dominican', 'Dominican'),
        ('dutch', 'Dutch'),
        ('east timorese', 'East Timorese'),
        ('ecuadorean', 'Ecuadorean'),
        ('egyptian', 'Egyptian'),
        ('emirian', 'Emirian'),
        ('equatorial guinean', 'Equatorial Guinean'),
        ('eritrean', 'Eritrean'),
        ('estonian', 'Estonian'),
        ('ethiopian', 'Ethiopian'),
        ('fijian', 'Fijian'),
        ('filipino', 'Filipino'),
        ('finnish', 'Finnish'),
        ('french', 'French'),
        ('gabonese', 'Gabonese'),
        ('gambian', 'Gambian'),
        ('georgian', 'Georgian'),
        ('german', 'German'),
        ('ghanaian', 'Ghanaian'),
        ('greek', 'Greek'),
        ('grenadian', 'Grenadian'),
        ('guatemalan', 'Guatemalan'),
        ('guinea-bissauan', 'Guinea-Bissauan'),
        ('guinean', 'Guinean'),
        ('guyanese', 'Guyanese'),
        ('haitian', 'Haitian'),
        ('herzegovinian', 'Herzegovinian'),
        ('honduran', 'Honduran'),
        ('hungarian', 'Hungarian'),
        ('icelander', 'Icelander'),
        ('indian', 'Indian'),
        ('indonesian', 'Indonesian'),
        ('iranian', 'Iranian'),
        ('iraqi', 'Iraqi'),
        ('irish', 'Irish'),
        ('israeli', 'Israeli'),
        ('italian', 'Italian'),
        ('ivorian', 'Ivorian'),
        ('jamaican', 'Jamaican'),
        ('japanese', 'Japanese'),
        ('jordanian', 'Jordanian'),
        ('kazakhstani', 'Kazakhstani'),
        ('kenyan', 'Kenyan'),
        ('kittian and nevisian', 'Kittian and Nevisian'),
        ('kuwaiti', 'Kuwaiti'),
        ('kyrgyz', 'Kyrgyz'),
        ('laotian', 'Laotian'),
        ('latvian', 'Latvian'),
        ('lebanese', 'Lebanese'),
        ('liberian', 'Liberian'),
        ('libyan', 'Libyan'),
        ('liechtensteiner', 'Liechtensteiner'),
        ('lithuanian', 'Lithuanian'),
        ('luxembourger', 'Luxembourger'),
        ('macedonian', 'Macedonian'),
        ('malagasy', 'Malagasy'),
        ('malawian', 'Malawian'),
        ('malaysian', 'Malaysian'),
        ('maldivan', 'Maldivan'),
        ('malian', 'Malian'),
        ('maltese', 'Maltese'),
        ('marshallese', 'Marshallese'),
        ('mauritanian', 'Mauritanian'),
        ('mauritian', 'Mauritian'),
        ('mexican', 'Mexican'),
        ('micronesian', 'Micronesian'),
        ('moldovan', 'Moldovan'),
        ('monacan', 'Monacan'),
        ('mongolian', 'Mongolian'),
        ('moroccan', 'Moroccan'),
        ('mosotho', 'Mosotho'),
        ('motswana', 'Motswana'),
        ('mozambican', 'Mozambican'),
        ('namibian', 'Namibian'),
        ('nauruan', 'Nauruan'),
        ('nepalese', 'Nepalese'),
        ('new zealander', 'New Zealander'),
        ('ni-vanuatu', 'Ni-Vanuatu'),
        ('nicaraguan', 'Nicaraguan'),
        ('nigerien', 'Nigerien'),
        ('north korean', 'North Korean'),
        ('northern irish', 'Northern Irish'),
        ('norwegian', 'Norwegian'),
        ('omani', 'Omani'),
        ('pakistani', 'Pakistani'),
        ('palauan', 'Palauan'),
        ('panamanian', 'Panamanian'),
        ('papua new guinean', 'Papua New Guinean'),
        ('paraguayan', 'Paraguayan'),
        ('peruvian', 'Peruvian'),
        ('polish', 'Polish'),
        ('portuguese', 'Portuguese'),
        ('qatari', 'Qatari'),
        ('romanian', 'Romanian'),
        ('russian', 'Russian'),
        ('rwandan', 'Rwandan'),
        ('saint lucian', 'Saint Lucian'),
        ('salvadoran', 'Salvadoran'),
        ('samoan', 'Samoan'),
        ('san marinese', 'San Marinese'),
        ('sao tomean', 'Sao Tomean'),
        ('saudi', 'Saudi'),
        ('scottish', 'Scottish'),
        ('senegalese', 'Senegalese'),
        ('serbian', 'Serbian'),
        ('seychellois', 'Seychellois'),
        ('sierra leonean', 'Sierra Leonean'),
        ('singaporean', 'Singaporean'),
        ('slovakian', 'Slovakian'),
        ('slovenian', 'Slovenian'),
        ('solomon islander', 'Solomon Islander'),
        ('somali', 'Somali'),
        ('south african', 'South African'),
        ('south korean', 'South Korean'),
        ('spanish', 'Spanish'),
        ('sri lankan', 'Sri Lankan'),
        ('sudanese', 'Sudanese'),
        ('surinamer', 'Surinamer'),
        ('swazi', 'Swazi'),
        ('swedish', 'Swedish'),
        ('swiss', 'Swiss'),
        ('syrian', 'Syrian'),
        ('taiwanese', 'Taiwanese'),
        ('tajik', 'Tajik'),
        ('tanzanian', 'Tanzanian'),
        ('thai', 'Thai'),
        ('togolese', 'Togolese'),
        ('tongan', 'Tongan'),
        ('trinidadian or tobagonian', 'Trinidadian or Tobagonian'),
        ('tunisian', 'Tunisian'),
        ('turkish', 'Turkish'),
        ('tuvaluan', 'Tuvaluan'),
        ('ugandan', 'Ugandan'),
        ('ukrainian', 'Ukrainian'),
        ('uruguayan', 'Uruguayan'),
        ('uzbekistani', 'Uzbekistani'),
        ('venezuelan', 'Venezuelan'),
        ('vietnamese', 'Vietnamese'),
        ('welsh', 'Welsh'),
        ('yemenite', 'Yemenite'),
        ('zambian', 'Zambian'),
        ('zimbabwean', 'Zimbabwean'),
    ]
    nationality = fields.Selection(
        NATIONALITIES, string='Nationality')

    time_period = fields.Selection([
        ('08:00 - 09:00', '08:00 - 09:00'),
        ('09:00 - 10:00', '09:00 - 10:00'),
        ('10:00 - 11:00', '10:00 - 11:00'),
        ('11:00 - 12:00', '11:00 - 12:00'),
        ('12:00 - 13:00', '12:00 - 13:00'),
        ('13:00 - 14:00', '13:00 - 14:00'),
        ('14:00 - 15:00', '14:00 - 15:00'),
        ('15:00 - 16:00', '15:00 - 16:00'),
        ('16:00 - 17:00', '16:00 - 17:00'),
        ('17:00 - 18:00', '17:00 - 18:00'),
        ('18:00 - 19:00', '18:00 - 19:00'),
        ('19:00 - 20:00', '19:00 - 20:00'),
        ('20:00 - 21:00', '20:00 - 21:00'),
        ('21:00 - 22:00', '21:00 - 22:00')
    ], string='Time Period of the Day', help="Select the time period of the day.")
