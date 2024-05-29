from odoo import models, fields, api, _
from datetime import datetime, timedelta
import json
from odoo.exceptions import UserError, ValidationError


class ClosingInterview(models.Model):
    _name = 'closing.interview'
    _description = 'Closing Interview'

    # api field
    student_id = fields.Many2one('tc.student',
                                 string='Student')
    channel_id = fields.Many2one('slide.channel',
                                 string='Course')
    link_id = fields.Many2one(
        'closing.interview.link', string='Interview Link')
    interview_period = fields.Char(
        string='Interview Period')
    active = fields.Boolean('Active',
                            default=True
                            )
    # part 1
    learner_name = fields.Char("Learner Name")
    nebosh_learner_number = fields.Char("NEBOSH Learner Number")
    learning_partner_name = fields.Char("Learning Partner Name")
    learning_partner_number = fields.Char("Learning Partner Number")
    name_of_interviewer = fields.Char("Name of Interviewer")
    date_of_birth = fields.Date("Date of Birth")
    date_of_closing_interview = fields.Date("Date of Closing Interview")
    time_of_closing_interview = fields.Float(
        "Time of Closing Interview", help="Time in hours")
    date_of_obe = fields.Date("Date of OBE")

    # part 2
    interviewer_introduced = fields.Boolean(
        "Interviewer Introduced Themselves to the Learner")
    interview_structure_explained = fields.Boolean(
        "Interviewer Explained the Structure of the Interview")
    identification_type = fields.Selection([
        ('passport', 'Passport'),
        ('drivers_license', 'Driver’s License'),
        ('national_id', 'National ID')
    ], "Type of Identification Provided by Learner")
    identification_satisfactory = fields.Boolean(
        "Identification Was Satisfactory")
    room_satisfactory = fields.Boolean("Interviewer Satisfied with the Room")
    no_unauthorised_resources = fields.Boolean(
        "No Unauthorised Resources Present")
    no_unauthorised_people = fields.Boolean("No Other People in the Room")
    notes = fields.Text("Notes")

    # part three
    # This field will store all questions and answers

    # Relation to Interview Questions
    interview_questions_ids = fields.One2many(
        'interview.question', 'interview_id', string="Interview Questions")
    question_notes = fields.Text("Any other notes")

    # part four
    notification_info = fields.Text(string="Notifying NEBOSH of repeated failures by a learner to attend a closing interview",
                                    default=lambda self: self._default_notification_info())

    # part five...
    nature_of_concern = fields.Text('Nature of concern')
    satisfaction_identification = fields.Text(
        "What is your concern? Were you satisfied with the identification provided by the learner? If not, please explain why.")
    satisfaction_answers = fields.Text(
        "Were you satisfied by the answers the learner provided to the questions? If not, please provide the questions you asked and the reasons for your concern.")
    concern_unauthorized_assistance = fields.Text(
        "Do you think the learner may have had unauthorised assistance during their preparation of their OBE or during the closing interview? If you do, please explain why you think this is.")
    other_concerns = fields.Text(
        "Please provide details of any other concerns that you have.")

    @api.model
    def _default_notification_info(self):
        return """A closing interview must be completed for each learner. If the learner fails to attend a closing interview on more than 3 occasions, without providing a valid explanation, the Learning Partner may wish to refer this to NEBOSH. Please email the learner details and the dates and times of the interviews missed to closinginterviews@nebosh.org.uk"""


class InterviewQuestion(models.Model):
    _name = 'interview.question'
    _description = 'Interview Question'

    interview_id = fields.Many2one(
        'closing.interview', string="Interview", ondelete="cascade")
    question = fields.Char("Task number for specific question")
    response = fields.Text("Notes on the learner's response")


class ClosingInterviewLink(models.Model):
    _name = 'closing.interview.link'
    _inherit = 'mail.thread'
    _description = 'Closing Interview Link'

    meet_link = fields.Char("Link")
    date = fields.Date(string='Date', required=True)
    start_time = fields.Datetime(string='Start Time')
    end_time = fields.Datetime(string='End Time')
    interview_ids = fields.One2many(
        'closing.interview', 'link_id', string='Interviews',
    )

    active = fields.Boolean(
        string='active',
        default=True
    )

    @api.model
    def default_get(self, fields):
        res = super(ClosingInterviewLink, self).default_get(fields)
        active_interviews = self.env['closing.interview'].search(
            [('active', '=', True)])
        if active_interviews:
            res['interview_ids'] = [
                (4,  interview.id) for interview in active_interviews]
        return res

    def send_interview_emails(self):
        for link in self:
            for interview in link.interview_ids:
                # Prepare email content
                email_from = interview.student_id.user_id.company_id.email
                email_to = interview.student_id.email
                print("SSSSSSSSSSS", email_from)
                mail_body = """\
                                <html>
                                    <body>
                                        <p>
                                            Dear <b>%s</b>,
                                                <br>
                                                <p> 
                                                    Dear <b>%s</b>,\n\nYour interview is scheduled at <b>%s</b> .\n\nPlease use the following link to join the interview: <b>%s</b>\n\n You can also find your interview time in the app.\n\nBest regards,\n[DHB]
                                                    
                                                </p>
                                            Thanks & Regards.
                                        </p>
                                    </body>
                                </html>
                            """ % (interview.student_id.name, interview.student_id.name, link.date, link.meet_link)
                mail = self.env['mail.mail'].sudo().create({
                    'subject': _('Interview Details'),
                    'email_from': email_from,
                    'email_to': email_to,
                    'body_html': mail_body,
                })
                mail.send()
                current_date = datetime.now()

        # Format the date as a string
        formatted_date = current_date.strftime('%Y-%m-%d %H:%M:%S')

        # Construct the message with the date
        message = "Email sent to %s on %s" % (email_to, formatted_date)

        # Post the message with the specified date
        self.message_post(body=message, message_type="notification", context={
            'mail_post_autofollow': True, 'default_model': self._name, 'mail_create_nolog': True, 'date': formatted_date})

    def action_send_interview_emails(self):
        self.send_interview_emails()
        return True

    def generate_interview_schedule(self):
        for link in self:
            duration = (link.end_time - link.start_time).total_seconds()

            num_students = len(link.interview_ids)
            num_interviews = int(duration / (15 * 60))
            if num_interviews < num_students:
                raise ValidationError(
                    "Not enough time slots for all students.")

            interval = timedelta(minutes=15)

            print("Start Time:", link.start_time)
            print("End Time:", link.end_time)
            print("Duration (seconds):", duration)
            print("Number of Interviews:", num_interviews)

            current_time = link.start_time
            for interview in link.interview_ids:
                interview_start_time = current_time
                interview_end_time = current_time + interval

                # Debugging
                print("Interview Start Time:", interview_start_time)
                print("Interview End Time:", interview_end_time)

                interview.interview_period = "%s - %s" % (
                    interview_start_time.strftime('%H:%M'),
                    interview_end_time.strftime('%H:%M'))
                current_time += interval
        return True
