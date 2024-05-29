from odoo.addons.auth_signup.controllers.main import AuthSignupHome
from odoo.http import request
from odoo.exceptions import UserError
from odoo import http, tools, _


class AuthSignupExtra(AuthSignupHome):
    def _signup_with_values(self, token, values):
        context = self.get_auth_signup_qcontext()
        values.update({'is_studied': context.get('is_studied')})
        values.update({'reason': context.get('reason')})
        values.update({'phone': context.get('partner_id.phone')})
        values.update({'email': context.get('partner_id.email')})
        super(AuthSignupExtra, self)._signup_with_values(token, values)

    def do_signup(self, qcontext):
        """ Shared helper that creates a res.partner out of a token """
        values = {key: qcontext.get(key) for key in (
            'login', 'name', 'password', 'phone', 'email', 'is_studied', 'reason')}
        if not values:
            raise UserError(_("The form was not properly filled in."))
        if values.get('password') != qcontext.get('confirm_password'):
            raise UserError(_("Passwords do not match; please retype them."))
        supported_lang_codes = [code for code,
                                _ in request.env['res.lang'].get_installed()]
        lang = request.context.get('lang', '').split('_')[0]
        if lang in supported_lang_codes:
            values['lang'] = lang
        self._signup_with_values(qcontext.get('token'), values)
        request.env.cr.commit()
