from odoo import models, fields, api
# from datetime import datetime, timedelta


class StudentFeedback(models.Model):
    _name = 'student.feedback'
    _description = 'Student Feedback'

    student_id = fields.Many2one('tc.student',
                                 string='Learner Name')

    channel_id = fields.Many2one('slide.channel',
                                 string='Course', domain=[('intro', '=', False)])

    feedback_file = fields.Binary(string="feedback Document")
