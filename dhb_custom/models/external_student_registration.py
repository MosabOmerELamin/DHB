from odoo import models, fields, api
from datetime import datetime, timedelta


class ExternalStudentRegistration(models.Model):
    _name = 'external.student.registration'
    _description = 'External Student Registration'

    student_id = fields.Many2one('tc.student',
                                 string='Student')

    # fields
    learner_number = fields.Char(string='Learner Number')
    learner_first_name = fields.Char(string='Learner First Name')
    learner_surname = fields.Char(string='Learner Surname')
    qualification = fields.Char(string='Qualification')
    mode_of_study = fields.Char(string='Mode of Study')
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

    # mode_of_study = fields.Selection([
    #     ('full_time', 'Full-time'),
    #     ('part_time', 'Part-time'),
    #     ('distance_learning', 'Distance Learning')
    # ], string='Mode of Study')
