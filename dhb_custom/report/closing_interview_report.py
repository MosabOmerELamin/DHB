from odoo import api, fields, models


class ReportAttendance(models.AbstractModel):
    _name = 'report.dhb_custom.report_closing_interview_template'
    _description = 'Get attendance result as PDF.'

    @api.model
    def _get_report_values(self, docids, data=None):
        docs = self.env['closing.interview'].browse(
            self.env.context.get('active_id'))

        return {
            'doc_ids': docids,
            'doc_model': 'closing.interview',
            'docs': docs,
        }
