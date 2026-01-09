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
    is_admin_user = fields.Boolean(string='Is Admin User')

    its_user_type = fields.Selection([
        ('its_portal_user', 'Portal User'),
        ('its_staff_user', 'Staff User')
    ], default='its_portal_user', string='User Type')

    def _compute_document_access_ids(self):
        Access = self.env['documents.access']
        for user in self:
            user.document_access_ids = Access.search([
                ('partner_id', '=', user.partner_id.id)
            ]) if user.partner_id else False

    @api.model
    def create(self, vals):
        # Detect user type
        its_user_type = vals.get('its_user_type', 'its_portal_user')
        is_admin_user = vals.get('is_admin_user', False)
        print("---33--"*11, its_user_type, is_admin_user)

        # 🔹 PORTAL USER FLOW
        if not is_admin_user and its_user_type == 'its_portal_user':
            portal_group = self.env.ref('base.group_portal')
            internal_group = self.env.ref('base.group_user')

            # Force portal flags
            vals.update({
                'share': True,
            })

            # Create user FIRST
            user = super(ResUsers, self.sudo()).create(vals)

            # Now fix groups explicitly
            user.sudo().write({
                'groups_id': [
                    (3, internal_group.id),   # remove internal user
                    (4, portal_group.id),     # add portal group
                ]
            })

            return user
        
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

        # ✅ If Admin checkbox is checked → add admin group
        if is_admin_user:
            user.sudo().write({
                'groups_id': [(4, admin_group.id)]
            })

        # ✅ Auto-assign Staff only if no role selected
        if staff_group and not (
            _group_in_cmds(staff_group) or
            (admin_group and _group_in_cmds(admin_group))
        ):
            user.sudo().write({
                'groups_id': [(4, staff_group.id)]
            })

        return user

    
