from odoo import api, fields, models, _


class TcStudent(models.Model):
    _name = 'tc.student'

    serial_number = fields.Char(
        string='Student ID', copy=False, readonly=True,)
    name = fields.Char(string='Student Name')

    arabic_name = fields.Char(string='Name')

    # course_id = fields.Many2one('slide.channel',
    #                             string='Course')

    slide_id = fields.Many2one('slide.slide',
                               string='Content')

    user_id = fields.Many2one('res.users',
                              string='User')

    email = fields.Char(string='Email',)

    phone = fields.Char(string='Phone')

    att_num = fields.Integer(
        string='Attendance Count',
    )

    batch_ids = fields.Many2many('tc.batch',
                                 string='Batch')

    pre_center = fields.Boolean(
        string='Previous Center',
    )
    reason_you_left = fields.Text('The reason you left your previous center')
    previous_center_name = fields.Text('Previous Center Name')
    pervious_courses = fields.Text('Previous Courses')
    old_serial = fields.Text('Nibosh number')
    cant_remember = fields.Boolean(
        string='Cant remember the serial number'
    )
    result_img = fields.Binary(
        string='Result Image')

    student_types = fields.Selection([('internal', 'Internal'),
                                      ('external', 'External')],
                                     string='Student Type',
                                     compute='_onchange_student_type'
                                     )
    payment_id = fields.Many2one('student.payment',
                                 string='Payment')

    @api.model
    def create(self, vals):
        vals.update(
            {'serial_number': self.env['ir.sequence'].next_by_code('tc.student.serial')})
        return super(TcStudent, self).create(vals)

    @api.depends('pre_center')
    def _onchange_student_type(self):
        if self.pre_center == True:
            self.student_types = 'external'
        else:
            self.student_types = 'internal'

    # att_id = fields.Many2one('student.attendance',
    #                          string='Student att')

    # def name_get(self):
    #     result = []
    #     for record in self:
    #         # Customize this as per your requirement
    #         name = f"{record.user_id.name} - {record.course_id.name}"
    #         result.append((record.id, name))
    #     return result

    # slide_id = fields.Many2one('student.attendance',
    #                            string='Student')

    # is_attended = fields.Boolean(
    #     string='Attandence',
    # )

    # reason_of_absence = fields.Text(
    #     string='Reason Of Absence',
    # )
