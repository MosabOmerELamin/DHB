from odoo import models, fields, api


class ResUsersAdd(models.Model):
    _inherit = 'res.users'

    # serial_number = fields.Char(string='Student ID',
    #                             copy=False, readonly=True,
    #                             index=True,
    #                             default=lambda self: self.env['ir.sequence'].next_by_code('tc.student.serial'))

#  is_studied = fields.Boolean(string='Have u studied in another center')
#  reason = fields.Text(string='The reason you left your previous position')

# student_id = fields.Many2one('tc.student', string='Student')

# @api.model
# def create(self, vals):
#     user = super(ResUsersExt, self).create(vals)

#     student_model = self.env['tc.student'].sudo()
#     email = user.partner_id.email
#     phone = user.partner_id.phone
#     student_data = {
#         'name': user.name,
#         'user_id': user.id,
#         # Assuming 'login' is the email used for signup
#         'email': email,
#         'phone': phone
#         # Add other fields as needed
#     }
#     student_model.create(student_data)
#     print("sssssssssssssssssssssss", student_data)
#     return user

# this is custom in standard delete it mosab
# user_id = request.env.user.id
# print("assssssssssssssssssssssss######",user_id)
# request.env['student.attendance'].sudo().create({
#     'user_id': user_id,
#     'slide': values['slide'].id,
#     'course_id': values['slide'].channel_id.id,
#     'is_attended': True,
# })

#  slide = request.env['student.attendance'].create({
#      'name': 'ddddddddddddddd',
#      'channel_id': values['channel'].id, })
#  print("assssssssssssssssssssssss######", slide)
