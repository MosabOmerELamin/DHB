# -*- coding: utf-8 -*-

{
    'name': 'DHB',
    'version': '1.0',
    'license': 'LGPL-3',
    'author': 'mosab omer',
    'category': 'website',
    'summary': 'elearning',
    'description': """
        This module provide core education management system includes managing
            * Admission
    """,
    'depends': [
                'base',
                'web',
                'mail',
                'website',
                'website_slides',
                'website_sale_slides',
                'auth_signup'


    ],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'views/student_views.xml',
        'views/student_menu.xml',
        'views/course_attendance.xml',
        'views/video_access_temp.xml',
        'views/sign_inherit_temp.xml',
        'views/slide_view_extensions.xml',
        'views/batch_view.xml',
        'views/web_batch_design.xml',
        "views/otp_verification.xml",
        "views/login_view.xml",
        "views/otp_signup.xml",
        'views/subscription_request_view.xml',
        'views/mock_exam_view.xml',
        'views/mock_details_view.xml',
        'views/complaint_form_view.xml',
        'views/student_feedback_view.xml',
        'views/internal_student_registration_view.xml',
        'views/external_student_registration_view.xml',
        'views/student_payment_view.xml',
        'views/closing_interview_view.xml',
        'views/closing_interview_link_view.xml',
        'report/closing_interview_report_action.xml',
        'report/report_closing_interview_template.xml',
        'wizard/course_attendance_view.xml',
        'wizard/attendance_report_temp.xml',
        'data/data.xml',
        'data/cron.xml',
        'data/std_id.xml'


    ],
    'assets': {
        'web.assets_common': [
            '/dhb_custom/static/src/css_field_size.css'

        ]
    },



    # ],
    # 'qweb': ['static/src/checkbox_script.js',
    #          'static/src/video_access.js'],
    'installable': True,
    'application': True,
    'auto_install': True,


}
