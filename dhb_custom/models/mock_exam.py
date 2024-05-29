from odoo import fields, models, api
from odoo.exceptions import ValidationError
from odoo.exceptions import UserError
from werkzeug.urls import url_decode
from werkzeug.utils import secure_filename
from werkzeug.urls import iri_to_uri
import os


class MockExam(models.Model):
    _name = "mock.exam"
    _description = 'Mock Exam'

    channel_id = fields.Many2one('slide.channel',
                                 string='Course', domain=[('intro', '=', False)])
    mock_pdf_document = fields.Binary(string="Mock PDF Document")
    mock_word_document = fields.Binary(string="Mock Word Document")
