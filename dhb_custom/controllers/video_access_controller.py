# from odoo import http
# from odoo.http import request


# class VideoAccessController(http.Controller):
#     @http.route('/video/access', type='json', auth='user')
#     def video_access(self, **kwargs):
#         # Extract slide_id and course_id from kwargs
#         slide_id = kwargs.get('slide_id')
#         course_id = kwargs.get('course_id')

#         # Proceed only if both IDs are provided
#         if slide_id and course_id:
#             user_id = request.env.user.id
#             request.env['student.attendance'].sudo().create({
#                 'user_id': user_id,
#                 'slide_id': slide_id,
#                 'course_id': course_id,
#                 'is_attended': True,
#             })
#         else:
#             return {'error': 'Missing slide_id or course_id'}
