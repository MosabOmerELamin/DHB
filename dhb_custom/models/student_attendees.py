from odoo import api, fields, models, _


class StudentAttendance(models.Model):
    _name = 'student.attendance'

    user_id = fields.Many2one('res.users',
                              string='Student')

    course_id = fields.Many2one('slide.channel',
                                string='Course', related='slide_id.channel_id', domain="[('slide_ids', 'in', slide_id)]")

    is_offline_attended = fields.Boolean(
        string='Offline Attandence',
    )

    is_manual_attended = fields.Boolean(
        string='F2f Attandence',
    )

    reason_of_absence = fields.Text(
        string='Reason Of Absence',
    )
    slide_id = fields.Many2one('slide.slide',
                               string='Content', domain="[('channel_id', '=', course_id),('slide_category', '=', 'video'),('is_intro', '=', False),('is_live', '=', False)]")
    student_id = fields.Many2one('tc.student',
                                 string='Student')
    date = fields.Datetime(
        string='Datetime',
        default=fields.Datetime.now,
    )
    batch_id = fields.Many2one('tc.batch',
                               string='Batch', domain="[('student_ids', 'in', student_id)]")

    @api.model
    def create(self, vals):
        # Call super to ensure course_id is populated
        record = super(StudentAttendance, self).create(vals)

        if 'batch_id' not in vals:
            student_id = record.student_id.id
            course_id = record.course_id.id
            if student_id and course_id:
                batch = self.env['tc.batch'].search([
                    ('student_ids', 'in', student_id),
                    ('course_id', '=', course_id)
                ], limit=1)
                if batch:
                    record.batch_id = batch.id

        return record


class StudentSlideAttendance(models.Model):
    _inherit = 'slide.slide'

    attendance_ids = fields.One2many(
        'student.attendance', 'slide_id', string="Student Attendance", )

    slide_seq = fields.Integer(
        string='Slide Seq', readonly=True,
        default=lambda self: self.env['ir.sequence'].next_by_code(
            'slide.seq')
    )

    is_intro = fields.Boolean(
        "Introductory courses", default=False)

    quiz_completed = fields.Boolean(
        "Quiz Completed", default=False)

    student_id = fields.Many2one('tc.student',
                                 string='Student')

    is_live = fields.Boolean(
        "Live stream", default=False)

    batch_id = fields.Many2one('tc.batch',
                               string='Batch')

    # @api.depends('batch_id')
    # def _batch_attendance(self):
    #     if self.batch_id:
    #         for student in self.batch_id.student_ids:
    #             print(student)
    #             # self.attendance_ids.write({})

    @api.onchange('batch_id')
    def onchange_batch_id(self):
        if self.batch_id:
            attendance_data = []
            for student in self.batch_id.student_ids:
                attendance_data.append((0, 0, {
                    'student_id': student.id,
                }))
            self.attendance_ids = attendance_data


class SlidePartnerQuiz(models.Model):
    _inherit = 'slide.slide.partner'

    quiz_completed = fields.Boolean(
        "Quiz Completed", default=False)


class SlideChannelintro(models.Model):
    _inherit = 'slide.channel'

    intro = fields.Boolean(
        "Intro", default=False)

    co_price = fields.Float(
        string="Price", related='product_id.lst_price')
