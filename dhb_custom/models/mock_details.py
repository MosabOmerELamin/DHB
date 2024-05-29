from odoo import fields, models, api
from odoo.exceptions import ValidationError


class MockDetails(models.Model):
    _name = "mock.details"
    _description = 'Mock Details'

    student_id = fields.Many2one('tc.student',
                                 string='Student')

    answer_file = fields.Binary(string="Answer")

    task1 = fields.Text(
        string="Task 1: Discussing moral reasons for managing health and safety")
    task2 = fields.Text(
        string="Task 2: Why near misses should be investigated ")
    task3 = fields.Text(
        string="Task 3: Effective health and safety policy arrangements ")
    task4 = fields.Text(string="Task 4: improving formal consultation ")
    task5 = fields.Text(string="task 5: Safety culture ")
