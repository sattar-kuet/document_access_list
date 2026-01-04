from odoo import models, fields

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
