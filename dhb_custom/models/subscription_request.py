from odoo import models, fields, api
from odoo.exceptions import ValidationError
from odoo.exceptions import UserError


class SubscriptionRequest(models.Model):
    _name = 'subscription.request'
    _description = 'Subscription Request'

    student_id = fields.Many2one('tc.student', string='Student')
    batch_id = fields.Many2one('tc.batch', string='Batches')
    paid = fields.Boolean('Paid', compute='_compute_paid_status')
    student_img = fields.Binary(
        string='Student Image')
    student_identity_img = fields.Binary(
        string='Student Identity Image')
    transaction_img = fields.Binary(
        string='Transaction Image')

    state = fields.Selection([
        ('draft', 'Unconfirmed'), ('cancel', 'Cancelled'),
        ('confirm', 'Confirmed')],
        string='Subscription Status', readonly=True, default='draft')

    def action_confirm(self):
        if self.state != 'draft':
            raise UserError("Only draft records can be confirmed.")

        # Update the state to 'confirm'
        self.write({'state': 'confirm'})

        # Add the student ID to the student_ids field of tc.batch model
        batch_model = self.env['tc.batch']
        # You might need to adjust this search based on your requirements
        batch_records = batch_model.search(
            [('id', '=', self.batch_id.id)])

        batch_records.write({'student_ids': [(4, self.student_id.id)]})

    def action_cancel(self):
        self.write({'state': 'cancel'})

    def set_to_draft(self):
        self.write({'state': 'draft'})

    def unlink(self):
        for rec in self:
            if rec.state not in ['draft', 'cancel']:
                raise ValidationError(
                    "You can't delet record not in state draft or cancel")
        return super(SubscriptionRequest, self).unlink()

    @api.depends('student_id')
    def _compute_paid_status(self):
        for record in self:
            # Search for payment records related to the student
            payment_records = self.env['student.payment'].search([
                ('student_id', '=', record.student_id.id),
                ('state', '=', 'paid')
            ])
            # If any such records exist, set paid to True
            record.paid = bool(payment_records)
