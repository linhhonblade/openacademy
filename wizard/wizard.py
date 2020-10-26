# -*- coding: utf-8 -*-

from odoo import models, fields

# a wizard that allow users to create attendees for a
# particular session, or for a list of sessions at once.


class Wizard(models.TransientModel):
    _name = 'openacademy.wizard'
    _description = 'Wizard: Quick Registration of Attendees to Sessions'

    def _default_sessions(self):
        return self.env['openacademy.session'].browse(self._context.get('active_ids'))

    session_ids = fields.Many2many(
        'openacademy.session', string="Sessions", required=True, default=_default_sessions)
    attendee_ids = fields.Many2many('res.partner', string="Attendees")

    # add attendees for current session or a list of sessions
    def subscribe(self):
        for session in self.session_ids:
            # |= is bitwise operation, can use for set union
            session.attendee_ids |= self.attendee_ids
        return {}
