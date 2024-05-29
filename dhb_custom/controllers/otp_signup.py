from random import choice
import string

from odoo.addons.web.controllers.home import Home, ensure_db
from odoo import http, _
from odoo.http import request
import json
from odoo.exceptions import UserError


class OtpSignupHome(Home):

    # @http.route(website=True)
    # def web_auth_signup(self, *args, **kw):
    #     qcontext = self.get_auth_signup_qcontext()
    #     return super(OtpSignupHome, self).web_auth_signup(*args, **kw)

    @http.route('/api/signup_otp', type='json', auth='none', methods=['POST'], csrf=False)
    def web_signup_otp(self, **kw):

        qcontext = request.params.copy()
        if "email" not in qcontext or "password" not in qcontext or "confirm_password" not in qcontext:
            return {'success': False, 'message': 'Email, password, or confirm_password missing'}

        OTP = self.generate_otp(4)
        if qcontext["password"] != qcontext["confirm_password"]:
            return {'success': False, 'message': 'Passwords do not match'}

        user_id = request.env["res.users"].sudo().search(
            [("email", "=", qcontext.get("email"))])
        if user_id:
            return {'success': False, 'message': 'Another user is already registered using this email address'}

        email = str(qcontext.get('email'))
        name = str(qcontext.get('name'))
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
                                            To complete the verification process for your Odoo account, 
                                            <br>Please use the following One-Time Password (OTP): <b>%s</b>
                                        </p>
                                    Thanks & Regards.
                                </p>
                            </body>
                        </html>
                    """ % (name, OTP)
        mail = request.env['mail.mail'].sudo().create({
            'subject': _('Verify Your Odoo Account - OTP Required'),
            'email_from': email_from,
            'email_to': email,
            'body_html': mail_body,
        })
        mail.send()
        res = request.env['otp.verification'].sudo().create(vals)
        return {'success': True, 'message': 'Email sent successfully to', 'email': email}

    @http.route('/web/signup/otp/verify', type='json', auth='none', website=True, sitemap=False)
    def web_otp_signup_verify(self, *args, **kw):
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
