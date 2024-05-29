from odoo import http
from odoo.http import request
from odoo.addons.website_slides.controllers.main import WebsiteSlides
from odoo.exceptions import ValidationError


class CustomWebsiteSlides(WebsiteSlides):
    @http.route('''/slides/slide/<model("slide.slide"):slide>''', type='http', auth="public", website=True, sitemap=True)
    def slide_view(self, slide, **kwargs):

        if slide.is_intro:
            return super(CustomWebsiteSlides, self).slide_view(slide, **kwargs)

        response = super(CustomWebsiteSlides,
                         self).slide_view(slide, **kwargs)

        user_id = request.env.user.id
        student_id = request.env['tc.student'].sudo().search(
            [('user_id', "=", request.env.user.id)])
        print("student_id", student_id)
        # slide_id = slide.id
        channel_id = slide.channel_id.id if slide.channel_id else None
        # slide_seq_s = slide.slide_seq

        print("User ID: ", user_id, "Slide ID: ",
              slide.id, "Course ID: ", channel_id)
        # slide_seqeunce = request.env['slide.slide.partner'].browse(slide_id)
        rec_seqeunce = request.env['slide.slide.partner'].sudo().search([
            ('channel_id', "=", channel_id),
            ('partner_id', "=", request.env.user.partner_id.id),
            ('slide_id.slide_seq', '=', slide.slide_seq-1),
            # ('quiz_completed', '!=', True)
            # ('slide_id.slide_category', '=', 'quiz'),

        ], limit=1)
        # , order = 'slide.slide_seq desc',

        # print("###########", rec_seqeunce.slide_seq, "ssssssssss", rec_seqeunce)
        # rec_seq = request.env['slide.slide.partner'].sudo().search([
        #     ('partner_id', '=', request.env.user.partner_id.id),
        #     ('slide_id', '=', slide.id)
        # ], limit=1)
        # print("#############", rec_seqeunce,
        #       'sasassas', rec_seqeunce.quiz_completed, "wwwwwwww", slide.slide_seq)

        if (not rec_seqeunce) and slide.slide_seq != 1:

            raise ValidationError("first complete the quiz")
        if rec_seqeunce and rec_seqeunce.quiz_completed == False:

            raise ValidationError("first complete the quiz")

        else:

            if slide.slide_category != 'quiz':
                # update video quiz complated to true
                rec_search = request.env['slide.slide.partner'].sudo().search([
                    ('channel_id', "=", channel_id),
                    ('partner_id', "=", request.env.user.partner_id.id),
                    ('slide_id', '=', slide.id)


                ], limit=1)

                rec_search.sudo().write({'quiz_completed': True, })
                # Search for an existing attendance record for the same user, slide, and course
                attendance_record = request.env['student.attendance'].sudo().search([
                    ('student_id', '=', student_id.id),
                    ('slide_id', '=', slide.id),
                    ('course_id', '=', channel_id),
                ], limit=1)

                # Create the attendance record only if it does not exist
                if not attendance_record:
                    request.env['student.attendance'].sudo().create({
                        'student_id': student_id.id,
                        'slide_id': slide.id,
                        'course_id': channel_id,
                        'is_offline_attended': True,
                    })
                else:
                    print("Attendance record already exists for User ID: ", user_id,
                          "Slide ID: ", slide.id, "Course ID: ", channel_id)
            else:
                print("Slide is a quiz, not creating an attendance record for User ID: ",
                      user_id, "Slide ID: ", slide.id, "Course ID: ", channel_id)

        # Proceed with the original slide view handling

        return response

    @http.route('/slides/slide/quiz/submit', type="json", auth="public", website=True)
    def slide_quiz_submit(self, slide_id, answer_ids):
        rec_seq = request.env['slide.slide.partner'].sudo().search([
            ('partner_id', '=', request.env.user.partner_id.id),
            ('slide_id', '=', slide_id)
        ], limit=1)
        if rec_seq:

            rec_seq.sudo().write({'quiz_completed': True})

        response = super(CustomWebsiteSlides, self).slide_quiz_submit(
            slide_id, answer_ids)
        return response

    @http.route(['/batch'], type='http', auth='public', website=True, csrf=False)
    def batch_redirect(self):
        # Your logic here to display the batch page
        return request.render('dhb_custom.template_batch_calendar')

    @http.route('/slides/channel/enroll', type='http', auth='public', website=True)
    def slide_channel_join_http(self, channel_id=None):
        # response = super(CustomWebsiteSlides,
        #                  self).slide_channel_join_http(channel_id)
        return request.redirect('/batch')

    # @http.route(['/slides/channel/join'], type='http', auth='public', website=True)
    # def slide_channel_join(self):

    #     # return response
    #     rec = request.redirect('/batch')
    #     print("eeeeeeee", rec)
    #     return request.redirect('/batch')

        # cljsonass Course(http.Controller):

        #     @http.route('/get_courses', type='json', auth="user")
        #     def get_courses(self):
        #         course_rec = request.env['slide.channel'].search([])
        #         courses = []
        #         for rec in course_rec:
        #             vals = {
        #                 'id': rec.id,
        #                 'name': rec.name
        #             }
        #             courses.append(vals)
        #         data = {'status': 200, 'response': courses, 'message': 'Succses'}
        #         return data
