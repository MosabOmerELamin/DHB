from odoo import http, SUPERUSER_ID, _
from odoo.http import request, Response
from datetime import datetime, timedelta
import pytz  # Import pytz module for timezone handling
import json
import base64
import re
import logging
import binascii
from random import choice
import string
from odoo.exceptions import UserError

# Set up logger
_logger = logging.getLogger(__name__)


# def custom_json_dumps(data):
#     json_string = json.dumps(data, ensure_ascii=False)
#     # Replace escaped forward slashes if they are undesirably affecting your consumers
#     json_string = json_string.replace('\/', '/')
#     return json_string


class ApiMainController(http.Controller):
    @http.route('/api/register', auth='none', type='json', methods=['POST'], csrf=False)
    def register(self, **post):

        data = json.loads(request.httprequest.data.decode('utf-8'))
        _logger.info(f"Received data: {data}")

        default_company = request.env['res.company'].search([], limit=1)
        if not default_company:
            _logger.error("No company found in the system")
            return {'error': 'No company found in the system'}
        portal_group = request.env.ref(
            'base.group_portal', raise_if_not_found=False)
        if not portal_group:
            _logger.error("Portal group not found")
            return {'error': 'Portal group not found'}

        _logger.info(f"Default Company ID: {default_company.id}")
        default_company_id = default_company.id

        if 'login' in data and 'firstName' in data and 'password' in data:
            try:
                user = request.env['res.users'].with_user(SUPERUSER_ID).sudo().create({
                    'login': data['login'],
                    'name':  f"{data['firstName']} {data['secondName']} {data['thirdName']} {data['fourthName']}",
                    'email': data['email'],
                    'password': data['password'],
                    'company_id': default_company_id,
                    'company_ids': [(4, default_company_id)],
                    'groups_id': [(6, 0, [portal_group.id])]
                })

                partner_vals = {
                    'phone': data['mobile']
                }

                user.partner_id.write(partner_vals)
                serial_number = request.env['ir.sequence'].with_user(
                    SUPERUSER_ID).sudo().next_by_code('tc.student.serial')
                _logger.info(f"Student Serial: {serial_number}")

                # Create student record
                student_data = {
                    'name': user.name,
                    'user_id': user.id,
                    # Assuming 'email' and 'mobile' are keys in your JSON data
                    'email': data['email'],
                    'phone': data['mobile'],
                    # 'pre_center': data['pre_center']
                    # Add other fields as needed
                }

                student = request.env['tc.student'].sudo().create(student_data)

                ser = request.env['tc.student'].sudo().search(
                    [('id', '=', student.id)])
                ser.write({'serial_number': serial_number})

                _logger.info(f"Student created with ID: {student.id}")

                _logger.info(f"User created with ID: {user.id}")
                _logger.info(f"User created with ID: {student.id}")
                return {'success': True, 'id': student.id}
            except Exception as e:
                _logger.error(f"Error creating user: {str(e)}")
                return {'error': str(e)}
        else:
            _logger.warning("Missing required fields")
            return {'error': 'Missing required fields'}

    @http.route('/api/login', auth='none', type='json', methods=['POST'], csrf=False)
    def login(self, **kw):
        """
        Handle the login process by checking user credentials against res.users model.
        """
        # Retrieve login details from the request
        login = kw.get('login')  # or request.params.get('login') for JSON body
        # or request.params.get('password') for JSON body
        password = kw.get('password')

        uid = request.session.authenticate(request.session.db, login, password)

        if uid:
            user = request.env['res.users'].browse(uid)
            # Optionally, return some user information
            student = request.env['tc.student'].sudo().search(
                [('user_id', '=', user.id)])

            user_info = {
                'id': user.id,
                'name': user.name,
                'login': user.login,
                'email': user.email,
            }
            student_info = {
                'id': student.id,
                'student_name': student.name,
                'student_email': student.email,
                'student_phone': student.phone
                # Add more fields as needed
            }
            return {'success': True, 'student': student_info}
        else:
            return {'success': False, 'error': 'Invalid login or password'}

    @http.route('/api/check_intro_video', auth="none", methods=['GET'])
    def check_intro_video(self, **kw):

        slide_channel = request.env['slide.channel'].search(
            [('intro', '=', True)], limit=1)
        if slide_channel:

            slide_ids = slide_channel.slide_ids.filtered(
                lambda s: s.slide_category == 'video')
            if slide_ids:
                video_data = {
                    'id': slide_ids[0].id,
                    'name': slide_ids[0].name,
                    'video_url': slide_ids[0].video_url,
                }
                return_data = {
                    'success': True, 'intro_video_required': True, 'video_data': video_data}
            else:
                return_data = {'success': False,
                               'error': 'No introductory video found'}

        else:
            return_data = {'success': False,
                           'error': 'No introductory slide channel found'}
        # else:
        #     return_data = {'success': True, 'intro_video_required': False}

        return Response(
            json.dumps(return_data),
            content_type='application/json')

        # Your existing login method

    @http.route('/api/get_exam', type="http", auth="none", methods=['GET'])
    def get_exam(self, **kwargs):

        slide_channel = request.env['slide.channel'].sudo().search(
            [('intro', '=', True)], limit=1)
        if slide_channel:
            # Retrieve the quiz slide from the course
            quiz_slide = slide_channel.slide_ids.filtered(
                lambda s: s.slide_category == 'quiz')
            if quiz_slide:
                # Retrieve questions and answers from the quiz slide
                question_data = []
                for question in quiz_slide.question_ids:
                    answer_data = [{'id': answer.id, 'text': answer.text_value,
                                    'is_correct': answer.is_correct} for answer in question.answer_ids]
                    question_data.append(
                        {'id': question.id, 'text': question.question, 'answers': answer_data})
                return Response(json.dumps({'success': True, 'question_data': question_data}), content_type='application/json')
            else:
                return Response(json.dumps({'success': False, 'error': 'No quiz found'}), content_type='application/json')
        else:
            return Response(json.dumps({'success': False, 'error': 'No course found'}), content_type='application/json')

    @http.route('/api/get_intro_pdf', auth="none", methods=['GET'])
    def get_intro_pdf(self, **kwargs):
        response = {'success': False}
        headers = {'Content-Type': 'application/json'}

        slide_channel = request.env['slide.channel'].sudo().search(
            [('intro', '=', True)], limit=1)
        _logger.info(f"Slide channel: {slide_channel}")

        if slide_channel:
            # Retrieve the document slide from the course
            document_slide = slide_channel.slide_ids.filtered(
                lambda s: s.slide_category == 'document')
            _logger.info(f"Document: {document_slide}")

            if document_slide:
                if document_slide.source_type == 'local_file':
                    if document_slide.document_binary_content and isinstance(document_slide.document_binary_content, bytes):
                        document_base64 = base64.b64encode(
                            document_slide.document_binary_content).decode('utf-8')
                        response['document'] = document_base64
                    else:
                        response['document'] = None
                elif document_slide.source_type == 'external':
                    if document_slide.document_google_url:
                        response['document'] = document_slide.document_google_url
                    else:
                        response['document'] = None

                response['success'] = True
        else:
            response['message'] = "Slide channel not found."

        response = Response(json.dumps(response),
                            headers=headers)
        response.status_code = 200
        return response

    @http.route('/api/get_courses_list', auth='none', methods=['GET'], csrf=False)
    def get_courses_list(self, **kw):

        courses = http.request.env['slide.channel'].sudo().search([
            ('intro', '!=', True)])

        course_data = []
        for course in courses:
            _logger.info("Processing course: %s", course.id)
            print("Processing course:", course.id)  # Debugging
            if isinstance(course.image_1920, bytes):
                image_url = base64.b64encode(course.image_1920).decode('utf-8')
            elif isinstance(course.image_1920, str):
                image_url = course.image_1920
            else:
                image_url = None
                _logger.warning(
                    "Warning: Unexpected type for image_1920 %s", type(course.image_1920))
            course_element = {
                'id': course.id,
                'name': course.name,
                'price': course.co_price,
                'imageUrl': image_url,
            }
            course_data.append(course_element)
        _logger.info("Course data prepared: %s", course_element)
        # return json.dumps({'success': True, 'course_data': course_data})
        return http.Response(
            json.dumps({'success': True, 'course_data': course_data}),
            content_type='application/json')

    @http.route('/api/get_course_slides', auth='none', type="json", methods=['POST'], csrf=False)
    def get_course_slides(self, **kw):
        channel_id = kw.get('channel_id')
        if not channel_id:
            return {'error': 'Missing channel_id'}, 400

        try:
            channel_id = int(channel_id)
        except ValueError:
            return {'error': 'Invalid channel_id'}, 400

        Slide = request.env['slide.slide']
        slides = Slide.sudo().search([('channel_id', '=', channel_id),
                                      ('is_intro', '=', False)])

        slide_data = []
        for slide in slides:
            slide_info = {
                'id': slide.id,
                'name': slide.name,
                'type': slide.slide_category,
                'questions': "",
                'video_url': "",
                'document_name': "",
                'is_live': slide.is_live,
                'sequence': slide.slide_seq
            }

            if slide.slide_type == 'quiz':
                question_data = []
                for question in slide.question_ids:
                    answer_data = [
                        {'id': answer.id, 'text': answer.text_value,
                            'is_correct': answer.is_correct}
                        for answer in question.answer_ids
                    ]
                    question_data.append({
                        'id': question.id,
                        'text': question.question,
                        'answers': answer_data
                    })
                slide_info.update({'questions': question_data})

            elif slide.slide_category == 'video':
                slide_info.update({'video_url': slide.video_url})
            # elif slide.slide_category == 'document':

            #     if slide.document_binary_content and isinstance(slide.document_binary_content, bytes):
            #         document_base64 = base64.b64encode(
            #             slide.document_binary_content).decode('utf-8')
            #         slide_info.update({'document_name': document_base64})
            #     else:
            #         slide_info.update({'document_name': None})
            elif slide.slide_category == 'document':
                if slide.source_type == 'local_file':
                    if slide.document_binary_content and isinstance(slide.document_binary_content, bytes):
                        document_base64 = base64.b64encode(
                            slide.document_binary_content).decode('utf-8')
                        slide_info.update({'document_name': document_base64})
                    else:
                        slide_info.update({'document_name': None})
                elif slide.source_type == 'external':
                    if slide.document_google_url:  # Assuming this field contains the URL
                        slide_info.update(
                            {'document_name': slide.document_google_url})
                    else:
                        # Handle the case when the URL is not available, maybe log a warning or set to None
                        slide_info.update({'document_name': None})

            slide_data.append(slide_info)

        _logger.info(
            "Slide data prepared for channel %s with detailed contents", channel_id)
        return {'success': True, 'slides': slide_data}

    @http.route('/api/record_attendance', auth='none', type='json', methods=['POST'], csrf=False)
    def record_attendance(self, **kw):
        # Retrieve parameters from the request
        student_id = kw.get('student_id')
        slide_id = kw.get('slide_id')
        # channel_id = kw.get('channel_id')  # Assuming you also need the course ID

        # Validate the presence of all required parameters
        if not student_id or not slide_id:
            return {'error': 'Missing required parameters'}, 400

        # Ensure all ids are integers
        try:
            student_id = int(student_id)
            slide_id = int(slide_id)
            # channel_id = int(channel_id)
        except ValueError:
            return {'error': 'Invalid input data, IDs must be integers'}, 400

        slide = request.env['slide.slide'].sudo().browse(slide_id)

        # Search for an existing attendance record
        Attendance = request.env['student.attendance'].browse(slide_id)
        attendance_record = Attendance.sudo().search([
            ('student_id', '=', student_id),
            ('slide_id', '=', slide_id),
            # ('course_id', '=', channel_id),
        ], limit=1)

        # Create or update the attendance record
        if not attendance_record:
            Attendance.sudo().create({
                'student_id': student_id,
                'slide_id': slide_id,
                'course_id': slide.channel_id.id,
                'is_offline_attended': True,
            })
            _logger.info(
                f"Created new attendance record for Student ID: {student_id}, Slide ID: {slide_id}")
            return {'success': True, 'message': 'Attendance recorded'}
        else:
            _logger.info(
                f"Attendance record already exists for Student ID: {student_id}, Slide ID: {slide_id}")
            return {'success': False, 'message': 'Attendance already recorded'}

    @http.route('/api/get_student_courses', auth='none',
                type='json', methods=['POST'], csrf=False)
    def get_student_courses(self, **kw):

        student_id = kw.get('student_id')

        if student_id is None:
            return {'error': 'student_id is required'}, 400

        try:
            student_id = int(student_id)
        except ValueError:
            return {'error': 'student_id must be an integer'}, 400

        student = request.env['tc.student'].sudo().browse(student_id)
        if not student.exists():
            return {'error': 'No student found for the provided student_id'}, 404

        courses = []
        for batch in student.batch_ids:
            if batch.course_id:
                courses.append({
                    'course_id': batch.course_id.id,
                    'course_name': batch.course_id.name
                })

        _logger.info("Student %s is enrolled in %s courses",
                     student_id, len(courses))

        if not courses:
            return {'error': 'No courses associated with the student'}, 404

        return {'success': True, 'courses': courses}, 200

    @http.route('/api/get_batches', auth='none', methods=['POST'], type='json', csrf=False)
    def get_batches(self, **kw):
        # Extract course_id from the posted JSON data
        course_id = kw.get('course_id')

        # Validate presence and type of course_id
        if not course_id:
            return {'error': 'Missing course_id parameter'}
        try:
            course_id = int(course_id)
        except ValueError:
            return {'error': 'course_id must be an integer'}

        # Fetch batches associated with the course_id
        batches = request.env['tc.batch'].sudo().search([
            ('course_id', '=', course_id)
        ])

        # Prepare batch information to return
        batch_data = []
        for batch in batches:
            batch_info = {
                'id': batch.id,
                'name': batch.name,
                'begin_date': batch.begin_date.isoformat() if batch.begin_date else None,
                'end_date': batch.end_date.isoformat() if batch.end_date else None,
                'time_period': batch.time_period
            }
            batch_data.append(batch_info)

        # Return the batch data as JSON
        return {'success': True, 'batches': batch_data}

    @http.route('/api/get_course_details', auth='none', type="json", methods=['POST'], csrf=False)
    def get_course_details(self, **kw):
        channel_id = kw.get('channel_id')
        if not channel_id:
            return {'error': 'Missing channel_id'}, 400

        try:
            channel_id = int(channel_id)
        except ValueError:
            return {'error': 'Invalid channel_id'}, 400

        Slide = request.env['slide.slide']
        slides = Slide.sudo().search([('channel_id', '=', channel_id),
                                      ('is_intro', '=', True)])

        slide_data = []
        for slide in slides:
            slide_info = {
                'id': slide.id,
                'name': slide.name,
                'type': slide.slide_category,
                'questions': "",
                'video_url': "",
                'document_name': "",
                'sequence': slide.slide_seq
            }

            if slide.slide_type == 'quiz':
                question_data = []
                for question in slide.question_ids:
                    answer_data = [
                        {'id': answer.id, 'text': answer.text_value,
                            'is_correct': answer.is_correct}
                        for answer in question.answer_ids
                    ]
                    question_data.append({
                        'id': question.id,
                        'text': question.question,
                        'answers': answer_data
                    })
                slide_info.update({'questions': question_data})

            elif slide.slide_category == 'video':
                slide_info.update({'video_url': slide.video_url})
            # elif slide.slide_category == 'document':

            #     if slide.document_binary_content and isinstance(slide.document_binary_content, bytes):
            #         document_base64 = base64.b64encode(
            #             slide.document_binary_content).decode('utf-8')
            #         slide_info.update({'document_name': document_base64})
            #     else:
            #         slide_info.update({'document_name': None})
            elif slide.slide_category == 'document':
                if slide.source_type == 'local_file':
                    if slide.document_binary_content and isinstance(slide.document_binary_content, bytes):
                        document_base64 = base64.b64encode(
                            slide.document_binary_content).decode('utf-8')
                        slide_info.update({'document_name': document_base64})
                    else:
                        slide_info.update({'document_name': None})
                elif slide.source_type == 'external':
                    if slide.document_google_url:  # Assuming this field contains the URL
                        slide_info.update(
                            {'document_name': slide.document_google_url})
                    else:
                        # Handle the case when the URL is not available, maybe log a warning or set to None
                        slide_info.update({'document_name': None})

            slide_data.append(slide_info)

        _logger.info(
            "Slide data prepared for channel %s with detailed contents", channel_id)

        return {"success": True, "slides": slide_data}

    @http.route('/api/subscribe_course', auth='none', type="json", methods=['POST'], csrf=False)
    def subscribe_course(self, **kw):

        student_id = kw.get('student_id')
        batch_id = kw.get('batch_id')
        student_img = kw.get('student_img')
        student_identity_img = kw.get('student_identity_img')
        transaction_img = kw.get('transaction_img')

        if not student_id and batch_id:
            return json.dumps({'error': 'Missing student_id'}), 400

        try:
            student_id = int(student_id)
            batch_id = int(batch_id)

        except ValueError:
            return json.dumps({'error': 'Invalid student_id'}), 400
        existing_subscription = request.env['subscription.request'].sudo().search([
            ('student_id', '=', student_id),
            ('batch_id', '=', batch_id)
        ])

        if existing_subscription:
            return {'error': 'Subscription request already exists for this student and batch'}

        # payment_records = self.env['student.payment'].search([
        #     ('student_id', '=', self.student_id.id),
        #     ('state', '=', True)])
        subscript = request.env['subscription.request'].sudo().create({
            'student_id': student_id,
            'batch_id': batch_id,
            'student_img': student_img,
            'student_identity_img': student_identity_img,
            'transaction_img': transaction_img
        })
        return {'success': True, 'msg': 'Record created', 'record_id': subscript.id}

    @http.route('/api/get_attendance_table', auth='none', type="json", methods=['POST'], csrf=False)
    def get_attendance_table(self, **kw):
        channel_id = kw.get('channel_id')
        student_id = kw.get('student_id')
        if not channel_id and student_id:
            return {'error': 'Missing channel_id and student_id'}, 400

        try:
            channel_id = int(channel_id)
            student_id = int(student_id)
        except ValueError:
            return {'error': 'Invalid channel_id and student_id'}, 400

        Attendance = request.env['student.attendance']
        attendance_record = Attendance.sudo().search([
            ('course_id', '=', channel_id),
            ('student_id', '=', student_id)
        ])
        _logger.info(
            "rec: %s", attendance_record)
        if not attendance_record.exists():
            return {'error': 'Course not found'}, 404

        table = []
        for rec in attendance_record:
            att_details = {
                'student': rec.student_id.name,
                'lecture_name': rec.slide_id.name,
                'attended': rec.is_offline_attended,
                'att_date': rec.date
            }
            table.append(att_details)

        return {'success': True, 'table': table}, 200

    # mock exam

    @http.route('/api/get_mock_exam', auth='none',
                type='json', methods=['post'], csrf=False)
    def get_mock_exam(self, **kw):

        channel_id = kw.get('channel_id')

        if channel_id is None:
            return {'error': 'channel_id is required'}, 400

        try:
            channel_id = int(channel_id)
        except ValueError:
            return {'error': 'channel_id must be an integer'}, 400

        mock = request.env['mock.exam'].sudo().search(
            [('channel_id', '=', channel_id)])
        if not mock:
            return {'error': 'There is no mock exam for this course'}
        mock_data = {
            'course': mock.channel_id.name,
            'pdf': mock.mock_pdf_document,
            'word': mock.mock_word_document
        }
        return {'success': True, 'mock_info': mock_data}, 200

    @http.route('/api/student_mock_answer', auth='none',
                type='json', methods=['POST'], csrf=False)
    def student_mock_answer(self, **kw):

        student_id = kw.get('student_id')
        answer_file = kw.get('answer_file')
        # feedback = kw.get('feedback')

        if student_id is None:
            return {'error': 'student_id is required'}, 400

        try:
            student_id = int(student_id)
        except ValueError:
            return {'error': 'student_id must be an integer'}, 400
        student = request.env['tc.student'].sudo().browse(student_id)
        if not student:
            return {'error': 'Student not found'}, 404

        # Check if answer_file or feedback is missing
        if not answer_file:
            return {'error': 'answer_file is required'}, 400

        mock_details = request.env['mock.details'].sudo().sudo().create({
            'student_id': student_id,
            'answer_file': answer_file,

        })

        return {
            'success': True,
            'message': 'Record created successfully',
            'id': mock_details.id,
            'info': {
                'student_id': mock_details.student_id.name,
                'answer_file': mock_details.answer_file,
            }
        }

    @http.route('/api/student_mock_feedback', auth='none', methods=['POST'], type='json', csrf=False)
    def student_mock_feedback(self, **kw):
        # Retrieve student_id from the request parameters
        student_id = kw.get('student_id')

        # Validate the presence of student_id
        if student_id is None:
            return {'error': 'student_id is required'}, 400
        try:
            student_id = int(student_id)
        except ValueError:
            return {'error': 'student_id must be an integer'}, 400

        # Retrieve the student and their feedback
        student = request.env['tc.student'].sudo().browse(student_id)
        if not student:
            return {'error': 'Student not found'}, 400

        # Retrieve the associated mock details record
        mock_details_record = request.env['mock.details'].sudo().search(
            [('student_id', '=', student.id)], limit=1)
        if not mock_details_record:
            return {'error': 'No mock details found for the student'}, 400

            # Retrieving new task fields
        task1 = mock_details_record.task1
        task2 = mock_details_record.task2
        task3 = mock_details_record.task3
        task4 = mock_details_record.task4
        task5 = mock_details_record.task5

        # Returning the new task fields and status code as a tuple
        return {
            'success': True,
            'task1': task1,
            'task2': task2,
            'task3': task3,
            'task4': task4,
            'task5': task5
        }, 200

    # complain
    @http.route('/api/complaint_stage_one', auth='none', methods=['POST'], type='json', csrf=False)
    def complaint_stage_one(self, **kw):
        # first_stage field
        student_id = kw.get('student_id')
        # learner_id = kw.get('learner_id')
        mobile = kw.get('mobile')
        email = kw.get('email')
        date_formal_complaint_received = kw.get(
            'date_formal_complaint_received')
        nature_of_complaint = kw.get('nature_of_complaint')
        complaint_type = kw.get('complaint_type')
        evidence_of_resolution = kw.get('evidence_of_resolution')
        complaint_summary = kw.get('complaint_summary')
        desired_outcome = kw.get('desired_outcome')
        details_of_correspondence = kw.get('details_of_correspondence')
        # state = kw.get('state')  # Get the state from the request payload
        # complain id
        complaint_id = int(kw.get('complaint_id')) if kw.get(
            'complaint_id') else False
        # stage two field

        # Create or update Complaint Form recor
        if complaint_id:
            complaint_form = request.env['complaint.form'].sudo().browse(
                complaint_id)
            # _logger.info("Before write - learner_number: %s, stage_two_date: %s",
            #              complaint_form.learner_number, complaint_form.stage_two_date)
            # If the record already exists, update it with additional fields
            complaint_form.write({
                # 'learner_number': kw.get('learner_number'),
                'first_name': kw.get('first_name'),
                'surname': kw.get('surname'),
                'phone': kw.get('phone'),
                'mail': kw.get('mail'),
                'procedural_irregularity': kw.get('procedural_irregularity'),
                'new_evidence': kw.get('new_evidence'),
                'not_reasonable': kw.get('not_reasonable'),
                'review_request_reason': kw.get('review_request_reason'),
                'stage_two_date': kw.get('stage_two_date'),

            })
            # _logger.info("After write - learner_number: %s, stage_two_date: %s",
            #              complaint_form.learner_number, complaint_form.stage_two_date)
            complaint = complaint_form
        else:
            # Create a new Complaint Form record
            complaint = request.env['complaint.form'].sudo().create({
                'student_id': student_id,
                # 'learner_id': learner_id,
                'mobile': mobile,
                'email': email,
                'date_formal_complaint_received': date_formal_complaint_received,
                'nature_of_complaint': nature_of_complaint,
                'complaint_type': complaint_type,
                'evidence_of_resolution': evidence_of_resolution,
                'complaint_summary': complaint_summary,
                'desired_outcome': desired_outcome,
                'details_of_correspondence': details_of_correspondence,
                # 'state': state,
            })

        # Return response
        return {'status': 'success', 'id': complaint.id}

    @http.route('/api/complaint_list', auth='none', methods=['POST'], type='json', csrf=False)
    def complaint_list(self, **kw):
        # first_stage field
        student_id = kw.get('student_id')

        if student_id is None:
            return {'error': 'student_id is required'}, 400

        try:
            student_id = int(student_id)
        except ValueError:
            return {'error': 'student_id must be an integer'}, 400
        complain = request.env['complaint.form'].sudo().search([
            ('student_id', '=', student_id)
        ])

        complaint_list = []

        for rec in complain:
            complaint_data = {
                'id': rec.id,
                'student_id': rec.student_id.name,
                'learner_id': rec.learner_id,
                'mobile': rec.mobile,
                'email': rec.email,
                'date_formal_complaint_received': rec.date_formal_complaint_received,
                'complaint_type': rec.complaint_type,
                'nature_of_complaint': rec.nature_of_complaint,
                'state': rec.state
                # Add other fields as needed
            }
            complaint_list.append(complaint_data)

        return {'success': True, 'complaints': complaint_list}

    # student course feedback

    @http.route('/api/student_course_feedback', auth='none', methods=['POST'], type='json', csrf=False)
    def student_course_feedback(self, **kw):
        # Retrieve student_id from the request parameters
        student_id = kw.get('student_id')
        channel_id = kw.get('channel_id')
        feedback_file = kw.get('feedback_file')

        # Validate the presence of student_id
        if not student_id and channel_id:
            return {'error': 'student_id  and channel_id is required'}, 400
        try:
            student_id = int(student_id)
        except ValueError:
            return {'error': 'student_id and channel_id must be an integer '}, 400

        if not feedback_file:
            return {'error': 'feedback_file is required'}, 400

        feedback_details = request.env['student.feedback'].sudo().create({
            'student_id': student_id,
            'channel_id': channel_id,
            'feedback_file': feedback_file

        })

        return {
            'success': True,
            'message': 'Record created successfully',
            'id': feedback_details.id,
            # 'info': {
            #     'student_id': feedback_details.student_id.name,
            #     'channel_id': feedback_details.channel_id.name,
            #     'feedback_file': feedback_details.feedback_file
            # }
        }

    @http.route('/api/student_attendance_statement', auth='none', methods=['POST'], type='json', csrf=False)
    def student_attendance_statement(self, **kw):
        # Retrieve student_id from the request parameters
        student_id = kw.get('student_id')
        channel_id = kw.get('channel_id')

        if not student_id and channel_id:
            return {'error': 'student_id  and channel_id is required'}, 400
        try:
            student_id = int(student_id)
            channel_id = int(channel_id)
        except ValueError:
            return {'error': 'student_id and channel_id must be an integer '}, 400

            # Fetch the batches for the given channel_id
        batches = request.env['tc.batch'].sudo().search(
            [('course_id', '=', channel_id)])
        _logger.info("batches: %s",
                     batches)

        # Initialize a list to store the attendance statement
        attendance_statement = []

        # Loop through each batch
        for batch in batches:

            # Check if the student is enrolled in the current batch
            if student_id in batch.student_ids.ids:
                _logger.info("student: %s",
                             student_id)
                # Check if the batch end date has passed
                end_date = batch.end_date.date()
                today = datetime.now().date()
                batch_timezone = batch.end_date.tzinfo
                today_timezone = datetime.now().astimezone().tzinfo

                # Log date, timezone, and values
                _logger.info("Batch End Date: %s (Timezone: %s)",
                             end_date, batch_timezone)
                _logger.info("Today's Date: %s (Timezone: %s)",
                             today, today_timezone)

                _logger.info("date: %s",
                             end_date)
                _logger.info("today: %s",
                             today)
                if today > end_date:
                    _logger.info("End date has passed")
                # Check if the student has attended all videos in the batch
                    total_videos = request.env['slide.slide'].sudo().search_count(
                        [('channel_id', '=', channel_id), ('is_intro', '=', False), ('slide_category', '=', 'video'), ('is_live', '=', False)])
                    _logger.info("total videos: %s",
                                 total_videos)

                    attended_videos = request.env['slide.slide'].sudo().search_count([
                        ('channel_id', '=', channel_id),
                        ('is_intro', '=', False),
                        ('slide_category', '=', 'video'),
                        ('is_live', '=', False),
                        ('attendance_ids.student_id', '=', student_id),
                        ('attendance_ids.is_offline_attended', '=', True)
                    ])

                    attended_videos_count = attended_videos

                    _logger.info("attended_videos: %s",
                                 attended_videos)
                    # _logger.info("attended_videos: %s",
                    #              attended_videos_count)
                    if attended_videos == total_videos:
                        attendance_statement.append({
                            'student_id': student_id,
                            'channel_id': channel_id,
                            'number of attendance': attended_videos_count,
                            'status': 'Attended all videos'
                        })
                    else:
                        attendance_statement.append({
                            'student_id': student_id,
                            'channel_id': channel_id,
                            'number of attendance': attended_videos_count,
                            'status': 'Did not attend all videos'
                        })

        return {'attendance_statement': attendance_statement}

    @http.route('/api/student_registration_exam', auth='none', methods=['POST'], type='json', csrf=False)
    def student_registration_exam(self, **kw):
        student_id = kw.get('student_id')
        channel_id = kw.get('channel_id')

        if not student_id and channel_id:
            return {'error': 'student_id and channel_id is required'}, 400
        try:
            student_id = int(student_id)
            channel_id = int(channel_id)
        except ValueError:
            return {'error': 'student_id and channel_id must be an integer'}, 400

        total_videos = request.env['slide.slide'].sudo().search_count([
            ('channel_id', '=', channel_id),
            ('is_intro', '=', False),
            ('slide_category', '=', 'video'),
            ('is_live', '=', False)
        ])
        _logger.info("total videos: %s", total_videos)

        attended_videos = request.env['slide.slide'].sudo().search_count([
            ('channel_id', '=', channel_id),
            ('is_intro', '=', False),
            ('slide_category', '=', 'video'),
            ('is_live', '=', False),
            ('attendance_ids.student_id', '=', student_id),
            ('attendance_ids.is_offline_attended', '=', True)
        ])
        student = request.env['tc.student'].sudo().browse(student_id)
        country_name = kw.get('country_id')
        if country_name:
            country_name = country_name.capitalize()
            country = request.env['res.country'].sudo().search(
                [('name', '=', country_name)], limit=1)
            if country:
                country_id = country.id
            else:
                return {'error': 'Country not found'}, 400
        else:
            country_id = False

        if attended_videos == total_videos:
            _logger.info("total_videos %s = attended_videos %s ",
                         total_videos, attended_videos)
            if student.payment_id.state == 'paid':
                existing_registration = request.env['internal.student.registration'].sudo().search([
                    ('student_id', '=', student_id)
                ])
                if not existing_registration:
                    register = request.env['internal.student.registration'].sudo().create({
                        'student_id': kw.get('student_id'),
                        'student_no': student.old_serial if student.old_serial else '',
                        'title': kw.get('title'),
                        'forenames_given_name': kw.get('forenames_given_name'),
                        'surname_family_name': kw.get('surname_family_name'),
                        'gender': kw.get('gender'),
                        'dob': kw.get('dob'),
                        'mail_address': kw.get('mail_address'),
                        'address_line1': kw.get('address_line1'),
                        'address_line2': kw.get('address_line2'),
                        'address_line3': kw.get('address_line3'),
                        'address_line4': kw.get('address_line4'),
                        'town_city': kw.get('town_city'),
                        'county': kw.get('county'),
                        'postcode': kw.get('postcode'),
                        'country_id': country_id,
                        'work_phone': kw.get('work_phone'),
                        'home_phone': kw.get('home_phone'),
                        'mobile_phone': kw.get('mobile_phone'),
                        'email': kw.get('email'),
                        'nationality': kw.get('nationality'),
                        'Practical_exam': kw.get('Practical_exam'),
                        'Theoretical_exam': kw.get('Theoretical_exam'),
                        'both_exam': kw.get('both_exam')
                    })
                    existing_interview = request.env['closing.interview'].sudo().search([
                        ('student_id', '=', student_id)
                    ])
                    if not existing_interview:
                        if register.Theoretical_exam or register.both_exam:
                            _logger.info("Theoretical_exam %s or both %s",
                                         register.Theoretical_exam, register.both_exam)
                            interview = request.env['closing.interview'].sudo().create({
                                'student_id': student_id,
                                'channel_id': channel_id
                                # Other fields for the interview record
                            })
                            interview_id = interview.id  # Store the ID for the response
                        else:
                            interview_id = False  # No interview created
                    else:
                        return {'status': 'error', 'msg': 'An interview record already exists for this student'}

                    # Return response
                    return {'status': 'success', 'id': register.id, 'interview_id': interview_id}
                else:
                    return {'status': 'error', 'msg': 'A registration record already exists for this student'}
            else:
                return {'status': 'error', 'msg': 'The student has not paid for the exam'}
        else:
            return {'status': 'success', 'msg': 'The student did not attend all lectures'}

    @http.route('/api/student_payment', auth='none', methods=['POST'], type='json', csrf=False)
    def student_payment(self, **kw):
        student_id = kw.get('student_id')
        channel_id = kw.get('channel_id')
        payment_method = kw.get('payment_method')
        amount = kw.get('amount')
        payment_date = kw.get('payment_date')
        notification = kw.get('notification')

        if not student_id or not channel_id:
            return {'error': 'student_id and channel_id are required'}, 400
        try:
            student_id = int(student_id)
            channel_id = int(channel_id)
        except ValueError:
            return {'error': 'student_id and channel_id must be integers'}, 400

        if not all([amount, payment_date, notification]):
            return {'error': 'All fields are required'}, 400

        # Access the 'student.payment' model
        Payment = request.env['student.payment'].sudo()

        # Search for an existing payment record
        existing_payment = Payment.search(
            [('student_id', '=', student_id), ('channel_id', '=', channel_id)], limit=1)

        payment_values = {
            'amount': kw.get('amount'),
            'payment_method': kw.get('payment_method'),
            'payment_date': kw.get('payment_date'),
            'notification': kw.get('notification'),
        }

        if existing_payment:
            # If there is an existing payment, return a message indicating already paid
            return {'message': 'You have already made your payment'}
        else:
            course = request.env['slide.channel'].sudo().browse(
                channel_id)
            _logger.info("price: %s", course.co_price)
            if float(amount) == course.co_price:

                # Create a new payment record if no existing payment and amount is correct
                Payment.create({
                    'student_id': student_id,
                    'channel_id': channel_id,
                    'student_payment_line_ids': [(0, 0, payment_values)]})
                return {'message': 'Payment record created successfully, and payment is complete'}
            else:
                return {'error': 'The amount does not match the course price'}, 400

    @http.route('/api/complaint_response', auth='none', methods=['POST'], type='json', csrf=False)
    def complaint_response(self, **kw):
        student_id = kw.get('student_id')
        response = kw.get('response')

        if not student_id:
            return {'error': 'student_id is required'}, 400
        try:
            student_id = int(student_id)
        except ValueError:
            return {'error': 'student_id must be integers'}, 400

        # complaint = request.env['complaint.form'].search([
        #     ('student_id', '=', student_id)
        # ])
        complaint = request.env['complaint.form'].browse(student_id)
        if complaint:
            if response == "ok":
                complaint.write({'state': 'solved'})
                return {'succses': True, 'msg': 'complaint has been solved'}
            else:
                complaint.write({'state': 'stage_two'})
                return {'succses': True, 'msg': 'complaint has been move to stage two'}
        else:
            return {'succses': True, 'msg': 'there is complaint for this student in the system'}

    @http.route('/api/create_external_student', auth='none', methods=['POST'], type='json', csrf=False)
    def create_external_student(self, **kw):
        student_id = kw.get('student_id')
        learner_number = kw.get('learner_number')
        learner_first_name = kw.get('learner_first_name')
        learner_surname = kw.get('learner_surname')
        qualification = kw.get('qualification')
        mode_of_study = kw.get('mode_of_study')

        if not student_id:
            return {'error': 'student_id is required'}, 400
        try:
            student_id = int(student_id)
        except ValueError:
            return {'error': 'student_id must be integers'}, 400

        student = request.env['complaint.form'].browse(student_id)
        name_parts = student.name.split()

        # Extracting first name and surname
        first_name = name_parts[0]  # First element is the first name
        surname = name_parts[-1]  # Last element is the surname

        if student.pre_center:
            request.env['external.student.registration'].create({
                'student_id': student_id,
                'learner_number': student.old_serial if student.old_serial else '',
                'learner_first_name': first_name,
                'learner_surname': surname,
                'qualification': qualification,
                'mode_of_study': mode_of_study
            })
            return {'sucsess': True, 'msg': 'external student created'}
        else:
            return {'sucsess': False, 'msg': 'student is already internal'}

    @http.route('/api/closing_interviews_link', auth='none', methods=['POST'], type='json', csrf=False)
    def closing_interviews_link(self, **kw):
        student_id = kw.get('student_id')

        if not student_id:
            return {'error': 'student_id is required'}, 400
        try:
            student_id = int(student_id)
        except ValueError:
            return {'error': 'student_id must be integers'}, 400

        interview_records = request.env['closing.interview'].sudo().search(
            [('student_id', '=', student_id)])
        interview_links = request.env['closing.interview.link'].sudo().search([
            ('active', '=', True)
        ])
        if not interview_records:
            return {'success': False, 'message': 'No closing interview records found for the student'}, 404
        datas = []
        dates = interview_links.date.strftime('%Y-%m-%d')

        if interview_links:
            for link in interview_links:
                interviews_data = []
                for interview in link.interview_ids:
                    student_name = interview.student_id.name
                    interview_period = interview.interview_period  # Fetching existing value
                    interviews_data.append({
                        'student_id': interview.student_id.id,
                        'student_name': student_name,
                        'interview_period': interview_period
                    })

                datas.append({
                    'meet_link': link.meet_link,
                    # Convert date to string
                    'date': dates,
                    'interviews': interviews_data
                })

            # return json.dumps(data)

            return {'success': True, 'link data': datas}
        else:
            return {'success': True, 'msg': 'No interview meeting link'}

    @http.route('/api/update_student_data', auth='none', methods=['POST'], type='json', csrf=False)
    def update_student_data(self, **kw):

        student_id = kw.get('student_id')
        pre_center = kw.get('pre_center')
        reason_you_left = kw.get('reason_you_left')
        previous_center_name = kw.get('previous_center_name')
        pervious_courses = kw.get('pervious_courses')
        old_serial = kw.get('old_serial')
        cant_remember = kw.get('cant_remember')
        result_img = kw.get('result_img')
        if not student_id:
            return {'error': 'student_id is required'}, 400
        try:
            student_id = int(student_id)
        except ValueError:
            return {'error': 'student_id must be integers'}, 400

        student_record = request.env['tc.student'].sudo().browse(student_id)
        _logger.info("student id %s", student_record.id)

        if student_record:
            try:
                student_record.write({
                    'pre_center': pre_center,
                    'reason_you_left': reason_you_left,
                    'previous_center_name': previous_center_name,
                    'pervious_courses': pervious_courses,
                    'old_serial': old_serial,
                    'cant_remember': cant_remember,
                    'result_img': result_img
                })
                _logger.info("student udpdate %s,%s",
                             student_record.pre_center, student_record.old_serial)
                return {'success': True}
            except Exception as e:
                return {'success': False, 'error': str(e)}
        else:
            return {'success': False, 'error': 'Student record not found'}

    @http.route('/api/answer_student_pdf', auth='none', methods=['POST'], type='json', csrf=False)
    def answer_student_pdf(self, **kw):
        student_id = kw.get('student_id')
        slide_id = kw.get('slide_id')
        answer_file = kw.get('answer_file')

        if not student_id and slide_id:
            return {'error': 'student_id and slide_id is required'}, 400
        try:
            student_id = int(student_id)
            slide_id = int(slide_id)
        except ValueError:
            return {'error': 'student_id and slide_id must be an integer'}, 400

        student = request.env['tc.student'].sudo().browse(student_id)
        # name_parts = student.name.split()
        file_name = student.name.capitalize()

        slide = request.env['slide.slide'].sudo().browse(slide_id)
        slide_name = slide.name.capitalize()
        f_name = f'{file_name} - {slide_name}'

        attachment_exists = request.env['ir.attachment'].sudo().search([
            ('name', '=', f_name),
            ('res_id', '=', slide_id)
        ])
        if attachment_exists:
            return {'message': 'Attachment already exists for this slide'}

        attachment = request.env['ir.attachment'].sudo().create({
            'name': f_name,
            'datas': answer_file,
            'type': 'binary',
            'res_model': 'slide.slide',
            'res_id': slide_id
        })
        return {'success': True, 'message': 'Attachment created successfully', 'attch_id': attachment.id}

    @http.route('/api/reset_password_otp', type='json', auth='none', methods=['POST'], csrf=False)
    def reset_password_otp(self, **kw):

        email = kw.get('email')
        if not email:
            return {'success': False, 'message': 'Email, missing'}

        OTP = self.generate_otp(4)

        user_id = request.env["res.users"].sudo().search(
            [("email", "=", email)])
        if not user_id:
            return {'error': 'User with the provided email address not found. Please make sure you have entered the correct email address.'}
        name = user_id.name
        vals = {
            'otp': OTP,
            'email': email
        }
        user = request.env.user

        user_record = user.search([], limit=1)
        if user_record:
            company_id = user_record.company_id.id
            print("Company ID:", company_id)
        else:
            print("User record not found")

        email_from = user_record.company_id.email
        print("SSSSSSSSSSS", email_from)
        mail_body = """\
                        <html>
                            <body>
                                <p>
                                    Dear <b>%s</b>,
                                        <br>
                                        <p>
                                            To reset password the verification process for your Odoo account,
                                            <br>Please use the following One-Time Password (OTP): <b>%s</b>
                                        </p>
                                    Thanks & Regards.
                                </p>
                            </body>
                        </html>
                    """ % (name, OTP)
        mail = request.env['mail.mail'].sudo().create({
            'subject': _('Reset Your Password Account - OTP Required'),
            'email_from': email_from,
            'email_to': email,
            'body_html': mail_body,
        })
        mail.send()
        res = request.env['otp.verification'].sudo().create(vals)
        return {'success': True, 'message': 'Email sent successfully to', 'email': email}

    @http.route('/api/reset_otp_verify', type='json', auth='none', website=True, sitemap=False)
    def reset_otp_verify(self, *args, **kw):
        email = str(kw.get('email'))
        res_id = request.env['otp.verification'].sudo().search(
            [('email', '=', email)], order="create_date desc", limit=1)

        try:
            otp = str(kw.get('otp'))
            otp_no = res_id.otp
            if otp_no == otp:
                res_id.state = 'verified'
                # Return success message along with registration redirection
                return {
                    'message': 'OTP verified successfully. Registration process initiated.',
                    # 'redirect': self.register(*args, **kw)
                }
            else:
                res_id.state = 'rejected'
                # Return message for wrong OTP
                return {'error': 'Invalid OTP. Please enter the correct OTP.'}
        except UserError as e:
            # Handle any exceptions
            return {'error': e.name or e.value}

    def generate_otp(self, number_of_digits):
        otp = ''.join(choice(string.digits) for _ in range(number_of_digits))
        return otp

    @http.route('/api/reset_password', auth='none', type='json', methods=['POST'], csrf=False)
    def reset_password(self, **kw):
        data = json.loads(request.httprequest.data.decode('utf-8'))
        _logger.info(f"Received data for password reset: {data}")
        email = kw.get('email')
        new_password = kw.get('new_password')
        confirm_password = kw.get('confirm_password')

        if email and new_password and confirm_password:
            if new_password != confirm_password:
                _logger.warning(
                    "New password and confirm password do not match")
                return {'error': 'New password and confirm password do not match'}
            try:
                user = request.env['res.users'].sudo().search(
                    [('email', '=', email)])
                if user:
                    user.write({'password': new_password})
                    _logger.info(
                        f"Password reset successful for user: {user.id}")
                    return {'success': True}
                else:
                    _logger.error("User not found")
                    return {'error': 'User not found'}
            except Exception as e:
                _logger.error(f"Error resetting password: {str(e)}")
                return {'error': str(e)}
        else:
            _logger.warning("Missing required fields")
            return {'error': 'Missing required fields'}


