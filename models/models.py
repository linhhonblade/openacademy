# -*- coding: utf-8 -*-

from datetime import timedelta
from odoo import models, fields, api, exceptions, _

# ===============================================
# Course model declaration
# ===============================================


class Course(models.Model):
    _name = 'openacademy.course'
    _description = 'OpenAcademy Course'

    name = fields.Char(string="Title", required=True)
    description = fields.Text()

    responsible_id = fields.Many2one(
        'res.users', ondelete='set null', string="Responsible", index=True)
    session_ids = fields.One2many(
        'openacademy.session', 'course_id', string="Sessions")

    # Since we add constraint UNIQUE to Course title
    # Re-implement "copy" method which allows to duplicate the Course object
    def copy(self, default=None):

        # make a copy of default parameter
        default = dict(default or {})

        # find how many record has "Copy of {course title} in databse"
        copied_count = self.search_count(
            [('name', '=like', _(u"Copy of {}%").format(self.name))]
        )
        if not copied_count:
            new_name = _(u"Copy of {}").format(self.name)
        else:
            new_name = _(u"Copy of {} ({})").format(self.name, copied_count)
        default['name'] = new_name
        return super(Course, self).copy(default)

    # add sql constraints
    # name and description should be different
    # course title should be unique
    _sql_constraints = [
        ('name_description_check', 'CHECK(name != description)',
         "The title of the course should not be the description"),

        ('name_unique', 'UNIQUE(name)', "The course title must be unique"),
    ]

# =================================================
# Session model declaration
# =================================================


class Session(models.Model):
    _name = 'openacademy.session'
    _description = 'OpenAcademy Session'
    name = fields.Char(required=True)

    # default start date is today
    start_date = fields.Date(default=fields.Date.today)
    duration = fields.Float(digits=(6, 2), help="Duration in days")
    seats = fields.Integer(string='Number of seats')
    active = fields.Boolean(default=True)

    # instructor has to be in Teacher category
    instructor_id = fields.Many2one('res.partner', string="Instructor", domain=[
                                    '|', ('instructor', '=', True), ('category_id.name', 'ilike', 'Teacher')])
    course_id = fields.Many2one(
        'openacademy.course', ondelete='cascade', string="Course", required=True)
    attendee_ids = fields.Many2many('res.partner', string="Attendees")

    # taken seats in percentage
    # a computed field
    taken_seats = fields.Float(string="Taken seats", compute='_taken_seats')

    # a computed field calculate end date
    # the inverse function makes the field writable
    # and allows moving the sessions (via drag and drop)
    # in the calendar view
    end_date = fields.Date(string="End Date", store=True,
                           compute='_get_end_date', inverse='_set_end_date')
    attendees_count = fields.Integer(
        string="Attendees count", compute='_get_attendees_count', store=True)
    color = fields.Integer()

    @api.depends('attendee_ids')
    def _get_attendees_count(self):
        for r in self:
            r.attendees_count = len(r.attendee_ids)

    @api.depends('start_date', 'duration')
    def _get_end_date(self):
        for r in self:
            if not (r.start_date and r.duration):
                r.end_date = r.start_date
                continue

            # Add duration to start_date, but Monday + 5days = Saturday
            # so subtract one second to get Friday instead
            duration = timedelta(days=r.duration, seconds=-1)
            r.end_date = r.start_date + duration

    def _set_end_date(self):
        for r in self:
            if not (r.start_date and r.end_date):
                continue

            # Compute the differeces btw start and end date
            # but Frid-Mon=4days so add one day to get 5 instead
            r.duration = (r.end_date - r.start_date).days + 1

    # computed field which depends on other fields
    # should declare dependencies
    # function to calculate taken seats

    @api.depends('seats', 'attendee_ids')
    def _taken_seats(self):
        for r in self:
            if not r.seats:
                r.taken_seats = 0.0
            else:
                r.taken_seats = 100.0 * len(r.attendee_ids) / r.seats

    # a python constraints ensure that seats must not be negatvie
    # and number of attendees must not exceed
    @api.onchange('seats', 'attendee_ids')
    def _verify_valid_seats(self):
        if self.seats < 0:
            return {
                'warning': {
                    'title': _("Incorrect 'seats' value"),
                    'message': _("The number of available seats may not be negative"),
                }
            }
        if self.seats < len(self.attendee_ids):
            return {
                'warning': {
                    'title': _("Too many attendees"),
                    'message': _("Increase seats or remove excess attendees"),
                }
            }

    # a python constraint ensures the instructor cannot be attendee of his courser
    @api.constrains('instructor_id', 'attendee_ids')
    def _check_instructor_not_in_attendees(self):
        for r in self:
            if r.instructor_id and r.instructor_id in r.attendee_ids:
                raise exceptions.ValidationError(
                    _("A session's instructor can't be an attendee"))
