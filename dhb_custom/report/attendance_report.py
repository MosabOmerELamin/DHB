from odoo import api, fields, models


class ReportAttendance(models.AbstractModel):
    _name = 'report.dhb_custom.attendance_report_template'
    _description = 'Get attendance result as PDF.'

    @api.model
    def _get_report_values(self, docids, data=None):

        # Assuming 'batch_id' is a field of the wizard model, access it directly through 'self'
        batch = self.env['tc.batch'].browse(data['batch'])
        students = batch.student_ids  # Fetch students in the batch
        stud = []

        for student in students:

            attendance_status = []
            lectures = []
            attendance_rec = batch.course_id.slide_ids.filtered(
                lambda r: r.slide_category == 'video')
            for rec in attendance_rec.attendance_ids.filtered(lambda r: r.student_id == student):
                attendance_status.append(
                    {'status': '✓' if rec.is_offline_attended else '✗',
                     'lecture': rec.id})

            stud.append({
                'name': student.name,
                'attendance': attendance_status
            })
        print("ssssssssss", stud)

        # Fetch attendance records for each student
        attendance_records = batch.course_id.slide_ids.filtered(
            lambda r: r.slide_category == 'video')
        for attendance in attendance_records:
            lectures.append(attendance.name)

        # print("sasas", att)

        data.update({'stud': stud})
        data.update({'lectures': lectures})

        return{
            'doc_ids': docids,
            'doc_model':  'student.attendance',
            'docs': data,
            'data': data,

        }
    # att = []
        # for student in students:
        #     student_data = {
        #         'name': student.name,
        #     }
        #     stud.append(student_data)
        # print(stud)
        # print(batch)
