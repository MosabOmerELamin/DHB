from odoo import api, fields, models, _


class CourseAttendanceReport(models.TransientModel):
    _name = 'course.attendance.report'

    batch_id = fields.Many2one('tc.batch',
                               string='Batch')
    begin_date = fields.Date('From Date')
    end_date = fields.Date('End Date')
    course_id = fields.Many2one('slide.channel',
                                string='Course')

    def print_report(self):
        # students = self.env['tc.student'].search(
        #     [('serial_number', '=', False)])
        # print('ssds', students)
        # for student in students:
        #     # Generate a new serial number and update the record
        #     new_serial_number = self.env['ir.sequence'].next_by_code(
        #         'tc.student.serial')
        #     student.write({'serial_number': new_serial_number})

        #     # Optionally, print the updated record for verification
        #     print(
        #         f"Updated serial number for student {student.id}: {new_serial_number}")
        data = {
            'ids': [],
            'batch': self.batch_id.id}
        # print("sasaas", data['batch'])

        return self.env.ref('dhb_custom.course_attendance_report_action').report_action(self, data)
