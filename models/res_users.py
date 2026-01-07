from odoo import models, fields, api
from odoo.exceptions import ValidationError, AccessError
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
        # 🔐 ALWAYS create user with sudo
        user = super(ResUsers, self.sudo()).create(vals)

        staff_group = self.env.ref(
            'document_access_list.group_my_staff',
            raise_if_not_found=False
        )
        admin_group = self.env.ref(
            'document_access_list.group_my_admin',
            raise_if_not_found=False
        )

        groups_cmds = vals.get('groups_id', [])

        def _group_in_cmds(group):
            for cmd in groups_cmds:
                if cmd[0] == 4 and cmd[1] == group.id:
                    return True
                if cmd[0] == 6 and group.id in cmd[2]:
                    return True
            return False

        # 🚫 Prevent staff from creating admin users
        if (
            admin_group
            and _group_in_cmds(admin_group)
            and not self.env.user.has_group('base.group_system')
        ):
            raise AccessError("You are not allowed to create Admin users.")

        # ✅ Auto-assign Staff only if no role selected
        if staff_group and not (
            _group_in_cmds(staff_group) or
            (admin_group and _group_in_cmds(admin_group))
        ):
            user.sudo().write({
                'groups_id': [(4, staff_group.id)]
            })

        return user

    
