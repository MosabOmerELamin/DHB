from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
import pytz  # Import pytz module for timezone handling


class TcBatch(models.Model):
    _name = 'tc.batch'

    name = fields.Char(
        string='Name',
    )
    code = fields.Char('Code', size=8)
    begin_date = fields.Datetime('Begin Date', required=True)
    end_date = fields.Datetime('End Date', required=True)
    # last_date = fields.Datetime('last Date', required=True, timezone='UTC')

    batch_number = fields.Integer("Batch Number", required=True)
    course_id = fields.Many2one('slide.channel',
                                string='Course')

    student_ids = fields.Many2many('tc.student', string='Students')

    time_period = fields.Selection(
        string='Time Period',
        selection=[('morning', 'Morning'), ('night', 'Night')],


    )

    @api.constrains('student_ids')
    def _check_students_limit(self):
        for batch in self:
            if len(batch.student_ids) > 20:
                raise ValidationError(
                    "A batch can only have a maximum of 20 students!")

    @api.onchange('end_date')
    def onchange_end_date(self):
        if self.end_date:
            end_time = fields.Datetime.from_string(self.end_date).time()
            print("fffffffff", end_time)
            if end_time.hour < 12:
                self.time_period = 'morning'
            else:
                self.time_period = 'night'

    def name_get(self):
        new_format = []
        for rec in self:
            name = rec.name + "(" + str(rec.batch_number) + ")"
            new_format.append((rec.id, name))
        return new_format
