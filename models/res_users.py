from odoo import models, fields, api
from odoo.exceptions import ValidationError
import logging
from odoo import models, api

_logger = logging.getLogger(__name__)
class ResUsers(models.Model):
    _inherit = 'res.users'

    document_access_ids = fields.One2many(
        'documents.access',
        compute='_compute_document_access_ids',
        string='Document Access',
        readonly=True
    )

    def _compute_document_access_ids(self):
        Access = self.env['documents.access']
        for user in self:
            user.document_access_ids = Access.search([
                ('partner_id', '=', user.partner_id.id)
            ]) if user.partner_id else False

    @api.model
    def create(self, vals):
        _logger.warning("==== USER CREATE DEBUG START ====")
        _logger.warning("CREATE VALS: %s", vals)
        _logger.warning("GROUP COMMANDS: %s", vals.get('groups_id'))
        _logger.warning("==== USER CREATE DEBUG END ====")

        return super().create(vals)


    
