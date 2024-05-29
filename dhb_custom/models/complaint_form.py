from odoo import models, fields, api, _
from datetime import datetime, timedelta
from odoo.exceptions import UserError, ValidationError


class ComplaintForm(models.Model):
    _name = 'complaint.form'
    _inherit = 'mail.thread'
    _description = 'Complaint Form'

    # Assuming learner_name, learner_id, mobile, and email are mandatory fields.
    student_id = fields.Many2one('tc.student',
                                 string='Learner Name')
    learner_id = fields.Char(string='Learner ID', required=False)
    mobile = fields.Char(string='Mobile')
    email = fields.Char(string='E-mail')
    date_formal_complaint_received = fields.Date(
        string='Date Formal Complaint Form Received')

    # For nature of complaint, you could use a selection field.
    nature_of_complaint = fields.Selection(
        [('academic', 'Academic'),
         ('non_academic', 'Non-Academic')],
        string='Nature of Complaint'
    )

    evidence_of_resolution = fields.Text(string='Evidence of Resolution Steps')
    complaint_summary = fields.Text(string='Complaint Summary')

    desired_outcome = fields.Text(string='Desired Outcome')
    details_of_correspondence = fields.Text(
        string='Details of Correspondence and Other Material')

    complaint_type = fields.Selection(
        [('suggestion', 'Suggestion'),
         ('complain', 'Complain')],
        string='Complaint Status',
        default='unsolved',
        required=True,
    )

    state = fields.Selection(
        [('solved', 'Solved'),
         ('unsolved', 'Unsolved'),
         ('stage_two', 'Stage Two'),
         ('canceled', 'Canceled')],
        string='Complaint Status',
        default='unsolved',
        required=True,
    )

    # stage_two form
    learner_number = fields.Char(string='Learner Number')
    first_name = fields.Char(string='First Name')
    surname = fields.Char(string='Surname')
    phone = fields.Char(string='Phone')
    mail = fields.Char(string='E-mail')
    review_grounds = fields.Selection([
        ('procedural_irregularity', 'Procedural Irregularity'),
        ('new_evidence', 'New Evidence'),
        ('not_reasonable', 'Not Reasonable')],
        string='Grounds for Review',
        help='Select the grounds on which you are seeking a review of your complaint'
    )
    review_request_reason = fields.Text(string="Review Request Reason")
    stage_two_date = fields.Date(string="Stage Two Date")

    @api.model
    def auto_advance_stage(self):
        """
        This method advances the stage of complaints to 'Stage Two'
        if they are not solved within a certain time frame.
        """
        today = datetime.now().date()

        unsolved_complaints = self.search([('state', '=', 'unsolved')])
        complaints_to_advance = unsolved_complaints.filtered(
            lambda r: r.date_formal_complaint_received and today == r.date_formal_complaint_received +
            timedelta(days=25)
        )

        complaints_to_advance.write({'state': 'stage_two'})

    # Methods to change states
    def action_solve(self):
        """Set the complaint's state to 'Solved'."""
        self.state = 'solved'

    # def action_unsolve(self):
    #     """Set the complaint's state to 'Unsolved'."""
    #     self.state = 'unsolved'

    def action_stage_two(self):
        """Set the complaint's state to 'Stage Two'."""
        self.state = 'stage_two'

    def action_cancel(self):
        """Set the complaint's state to 'Canceled'."""
        self.state = 'canceled'

    def complaint_email(self):
        email_from = self.student_id.user_id.company_id.email
        email_to = self.student_id.email
        name = self.student_id.name
        print("SSSSSSSSSSS", email_from)
        mail_body = """\
                        <html>
                            <body>
                                <p>
                                    Dear <b>%s</b>,
                                        <br>
                                        <p> 
                                            give us a time to solve the complain , 
                                            
                                        </p>
                                    Thanks & Regards.
                                </p>
                            </body>
                        </html>
                    """ % (name)
        mail = self.env['mail.mail'].sudo().create({
            'subject': _('Postponing the outcome of the complaint'),
            'email_from': email_from,
            'email_to': email_to,
            'body_html': mail_body,
        })
        mail.send()
        # Raise a confirmation message
        # message = "Email sent to %s" % email_to
        # self.message_post(body=message, message_type="notification")

        current_date = datetime.now()

        # Format the date as a string
        formatted_date = current_date.strftime('%Y-%m-%d %H:%M:%S')

        # Construct the message with the date
        message = "Email sent to %s on %s" % (email_to, formatted_date)

        # Post the message with the specified date
        self.message_post(body=message, message_type="notification", context={
            'mail_post_autofollow': True, 'default_model': self._name, 'default_res_id': self.id, 'mail_create_nolog': True, 'date': formatted_date})
