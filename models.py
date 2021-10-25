"""
This file defines the database models
"""

from .common import db, Field, auth, T
from pydal.validators import *


def get_user_email():
    return auth.current_user.get('email') if auth.current_user else None


def get_user():
    return auth.current_user.get('id') if auth.current_user else None


def get_username():
    return auth.current_user.get('username') if auth.current_user else None

### Define your table below
#
# db.define_table('thing', Field('name'))
#
## always commit your models to avoid problems later

db.define_table(
    'landlord',
    # TODO_complete: define the fields that are in the json.
    #Field('landlord_auth_id', 'reference auth_user'),
    Field('id', readable=False),
    Field('first_name', requires=IS_NOT_EMPTY(error_message=T('Please enter a first name'))),
    Field('last_name', requires=IS_NOT_EMPTY(error_message=T('Please enter a last name'))),
)

#db.landlord.landlord_auth_id.writeable = False
#db.landlord.landlord_auth_id.readable = False

db.define_table(
    'address',
    # TODO_complete: define the fields that are in the json.
    Field('reviews_landlord_id', 'reference landlord'),
    Field('address_property_address', requires=IS_NOT_EMPTY(error_message=T('Property Address Required'))),
)

db.address.id.readable = db.address.id.writable = False
db.address.reviews_landlord_id.readable = db.address.reviews_landlord_id.writable = False


db.define_table(
    'reviews',
    # TODO_complete: define the fields that are in the json.
    Field('reviews_renters_id', 'reference auth_user'),
    Field('renter_email'),
    Field('renter_name'),
    Field('reviews_landlordID'),
    Field('reviews_address_id', 'reference address'),
    Field('reviews_contents', requires=IS_NOT_EMPTY(error_message=T('Review cannot be empty'))),
    Field('reviews_score_overall', default='0'),
    Field('reviews_score_responsiveness', default='0'),
    Field('reviews_score_friendliness', default='0'),
    Field('reviews_property_address', requires=IS_NOT_EMPTY(error_message=T('Property Address Required'))),
    Field('count'),
    Field('thumbs_up', default='0'),
    Field('thumbs_down', default='0'),
)

db.reviews.id.readable = db.reviews.id.writable = False
db.reviews.reviews_renters_id.readable = db.reviews.reviews_renters_id.writable = False
#db.reviews.reviews_landlord_id.readable = db.reviews.reviews_landlord_id.writable = False
db.reviews.reviews_address_id.readable = db.reviews.reviews_address_id.writable = False
db.reviews.thumbs_up.readable = db.reviews.thumbs_up.writable = False
db.reviews.thumbs_down.readable = db.reviews.thumbs_down.writable = False
#db.reivews.reviews_property_address.readable = False

# db.define_table(
#     'address',
#     # TODO_complete: define the fields that are in the json.
#     Field('reviews_landlord_id', 'reference auth_user'),
#     Field('address_property_address', requires=IS_NOT_EMPTY(error_message=T('Property Address Required'))),
# )
#
# db.address.id.readable = db.address.id.writable = False
# db.address.reviews_landlord_id.readable = db.address.reviews_landlord_id.writable = False

db.define_table(
    'review_replies',
    Field('reply', requires=IS_NOT_EMPTY(error_message=T('Reply cannot be empty'))),
    Field('username', 'reference auth_user', default=get_username),
    Field('review_id', 'reference reviews'),
)


db.define_table('votings',
                Field('review', 'reference reviews'),
                Field('voted', 'integer', default = 0),
                Field('voter', 'reference auth_user', default=get_user),
)


db.commit()
