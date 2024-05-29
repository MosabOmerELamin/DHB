from odoo import models, fields, api
# from datetime import datetime, timedelta
from odoo.exceptions import ValidationError, UserError


class StudentPayment(models.Model):
    _name = 'student.payment'
    _description = 'Student Payment'

    student_id = fields.Many2one('tc.student',
                                 string='Student')

    channel_id = fields.Many2one('slide.channel',
                                 string='Course')
    course_price = fields.Float(
        string="Price", related='channel_id.co_price')
    # remaining_amount = fields.Float(
    #     string="Remaining Amount",   compute='_compute_remaining_amount')

    # notification = fields.Binary(string='notification')
    student_payment_line_ids = fields.One2many('student.payment.line',
                                               'student_payment_id',
                                               string='Student Payment Line',
                                               )
    move_id = fields.Many2one(
        'account.move',
        string='Invoice id',
    )
    state = fields.Selection(
        [('draft', 'Draft'),
         ('paid', 'Paid'), ],
        string='State',
        default='draft',
    )

    @api.constrains('student_payment_line_ids')
    def _check_single_line(self):
        for record in self:
            if len(record.student_payment_line_ids) > 1:
                raise ValidationError(
                    "Only one student payment line is allowed per payment.")

    @api.constrains('student_id', 'channel_id')
    def _check_unique_student_channel(self):
        for payment in self:
            if payment.search_count([
                ('student_id', '=', payment.student_id.id),
                ('channel_id', '=', payment.channel_id.id),
                ('id', '!=', payment.id)
            ]) > 0:
                raise ValidationError(
                    "A student cannot have duplicate payments for the same course.")

    # @api.depends('course_price', 'student_payment_line_ids')
    # def _compute_remaining_amount(self):
    #     for record in self:
    #         total_paid_amount = sum(
    #             record.student_payment_line_ids.mapped('amount'))
    #         record.remaining_amount = record.course_price - total_paid_amount

    # @api.onchange('remaining_amount')
    # def _onchange_remaining_amount(self):
    #     if self.remaining_amount == self.course_price:
    #         self.state = 'draft'
    #     elif self.remaining_amount == 0:
    #         self.state = 'paid'


class StudentPaymentLine(models.Model):
    _name = 'student.payment.line'
    _description = 'Student Payment Line'

    amount = fields.Float(string="Amount")
    payment_date = fields.Date('Payment Date')
    payment_method = fields.Selection([
        ('cash', 'Cash'),
        ('bankak', 'Bankak'),
        ('card', 'Card'),
    ], string='Payment Method')
    student_payment_id = fields.Many2one(
        'student.payment',
        string='student_payment_id',
    )
    payment_id = fields.Many2one(
        'account.payment',
        string='Payment id',
    )
    notification = fields.Binary(string='notification')

    def action_invoice(self):
        Invoice = self.env['account.move']

        if self.student_payment_id.move_id:
            invoice = self.student_payment_id.move_id
        else:
            invoice = Invoice.create({
                'partner_id': self.student_payment_id.student_id.user_id.partner_id.id,
                'invoice_date': self.payment_date,
                'move_type': 'out_invoice',
                'invoice_line_ids': [
                    (0, 0, {
                        'product_id': self.student_payment_id.channel_id.product_id.id,
                        'account_id': self.student_payment_id.channel_id.product_id.categ_id.property_account_income_categ_id.id,
                        'tax_ids': [],
                    })
                ],
            })

            invoice.action_post()
            self.student_payment_id.move_id = invoice.id

        PaymentRegister = self.env['account.payment.register']
        payment_register = PaymentRegister.with_context({
            'active_ids': [invoice.id],
            'active_model': 'account.move',
        }).create({'amount': self.amount,
                   'payment_date': self.payment_date,
                   'communication': invoice.name, })

        #

        # payment_register.action_create_payments()
        pay_id = payment_register.action_create_payments()
        print('www', pay_id['res_id'])
        self.payment_id = pay_id['res_id']
        print('ads', str(self.notification))
        self.student_payment_id.state = 'paid'

        return True

    # def action_payment(self):
    #     if self.student_payment_id.payment_method == 'cash':
    #         journal = self.env['account.journal'].search(
    #             [('name', '=', 'Cash')])
    #         state = 'draft'
    #     elif self.student_payment_id.payment_method == 'bankak':
    #         journal = self.env['account.journal'].search(
    #             [('name', '=', 'Bank')])
    #         state = 'draft'

    #     else:
    #         journal = self.env['account.journal'].search(
    #             [('name', '=', 'Bank')])
    #         # state = 'posted'

    #     if journal:
    #         journal_id = journal.id
    #     partner = self.student_payment_id.student_id.user_id.partner_id.id
    #     print('account', self.student_payment_id.channel_id.product_id.categ_id.property_account_income_categ_id.id)

    #     payment_vals = {
    #         'amount': self.amount,
    #         'partner_id': partner,
    #         'date': self.payment_date,
    #         'journal_id': journal_id,
    #         'payment_type': 'inbound',
    #         'outstanding_account_id': self.student_payment_id.channel_id.product_id.categ_id.property_account_income_categ_id.id,
    #         'state': 'draft'
    #     }

    #     payment = self.env['account.payment'].create(payment_vals)

    #     if self.student_payment_id.payment_method == 'card':
    #         payment.action_post()
