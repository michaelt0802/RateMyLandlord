"""
This file defines actions, i.e. functions the URLs are mapped into
The @action(path) decorator exposed the function at URL:

    http://127.0.0.1:8000/{app_name}/{path}

If app_name == '_default' then simply

    http://127.0.0.1:8000/{path}

If path == 'index' it can be omitted:

    http://127.0.0.1:8000/

The path follows the bottlepy syntax.

@action.uses('generic.html')  indicates that the action uses the generic.html template
@action.uses(session)         indicates that the action uses the session
@action.uses(db)              indicates that the action uses the db
@action.uses(T)               indicates that the action uses the i18n & pluralization
@action.uses(auth.user)       indicates that the action requires a logged in user
@action.uses(auth)            indicates that the action requires the auth object

session, db, T, auth, and tempates are examples of Fixtures.
Warning: Fixtures MUST be declared with @action.uses({fixtures}) else your app will result in undefined behavior
"""
from pydal.validators import IS_IN_SET

from py4web import action, request, abort, redirect, URL, Field
from yatl.helpers import A

from py4web.utils.auth import Auth
from .common import db, session, T, cache, auth, logger, authenticated, unauthenticated, flash
from py4web.utils.form import Form, FormStyleBulma
from py4web.utils.url_signer import URLSigner
from .models import get_user_email, get_user, get_username
import random
url_signer = URLSigner(session)
lord_id = 0


@action('index', method=["GET", "POST"])
@action.uses(db, auth, 'index.html')
def index():
    auth = Auth(session, db, extra_fields=[
        Field('user_type', requires=IS_IN_SET("Renter", "Landlord"))
    ])
    user = auth.get_user()
    message = T("Hello {first_name}".format(**user) if user else "Hello")
    
    landlord_list = db(db.landlord.id).select().as_list()
    id_list = []
    for r in landlord_list:
        # check to see if the landlord has no reviews
        # if so don't include them in the display
        if db((db.reviews.reviews_landlordID == r['id'])).select().first() is not None:
            id_list.append(r['id'])

    if len(id_list) > 1:
        random_landlords = random.sample(id_list, 2)
    else:  # if there is only one landlord populate page with the only landlord twice
        random_landlords = [1, 1]

    example_landlord1 = db.landlord[random_landlords[0]]
    print(example_landlord1)
    example_landlord1_name = example_landlord1.first_name + " " + example_landlord1.last_name
    rows1 = db(
        (db.reviews.reviews_landlordID == random_landlords[0])
    ).select().sort(lambda row: random.random()).first()

    example_landlord2 = db.landlord[random_landlords[1]]
    print(example_landlord2)
    example_landlord2_name = example_landlord2.first_name + " " + example_landlord2.last_name
    rows2 = db(
        (db.reviews.reviews_landlordID == random_landlords[1])
    ).select().sort(lambda row: random.random()).first()

    return dict(
        message=message,
        load_reviews_url=URL('load_reviews', signer=url_signer),
        add_reviews_url=URL('add_reviews', signer=url_signer),
        delete_reviews_url=URL('delete_reviews', signer=url_signer),
        search_url=URL('search', signer=url_signer),
        example_landlord1_name=example_landlord1_name,
        example_landlord1_id=random_landlords[0],
        example_landlord2_name=example_landlord2_name,
        example_landlord2_id=random_landlords[1],
        rows1=rows1,
        rows2=rows2,
        get_votes_url=URL('get_votes', signer=url_signer),
        set_votes_url=URL('set_votes', signer=url_signer),
        get_voters_url=URL('get_voters', signer=url_signer),
        get_search_url_url=URL('get_search_url', signer=url_signer),
        add_landlord_url=URL('add_landlord', signer=url_signer),
        # get_thumbs_up_url=URL('get_thumbs_up', signer=url_signer),
        # get_thumbs_down_url=URL('get_thumbs_down', signer=url_signer),
        # set_thumbs_up_url=URL('set_thumbs_up', signer=url_signer),
        # set_thumbs_down_url=URL('set_thumbs_down', signer=url_signer),
        # get_thumbs_up_list_url=URL('get_thumbs_up_list', signer=url_signer),
        # get_thumbs_down_list_url=URL('get_thumbs_down_list', signer=url_signer),
    )


@action('load_reviews')
@action.uses(url_signer.verify(), db)
def load_reviews():
    rows = db(db.reviews).select().as_list()
    email = auth.get_user()['email']
    for r in rows:
        # add URL of the corresponding landlord review page
        r['url'] = URL('reviews', r['reviews_landlordID'])
        landlord = db(r['reviews_landlordID'] == db.landlord.id).select().first()
        r['landlord_name'] = landlord.first_name + ' ' + landlord.last_name
    return dict(rows=rows, email=email)


@action('dashboard_landlord')
@action.uses(url_signer.verify(), db)
def dashboard_landlord():
    return dict()


@action('dashboard_user')
@action.uses(db, session, auth.user, 'dashboard_user.html')
def dashboard_user():
    user = db(db.auth_user.email == get_user_email()).select().first()
    username = user.first_name + " " + user.last_name
    email = user.email
    return dict(
        username=username,
        email=email,
        load_reviews_url=URL('load_reviews', signer=url_signer),
        add_reviews_url=URL('add_reviews', signer=url_signer),
        delete_reviews_url=URL('delete_reviews', signer=url_signer),
    )


""" previous version
@action('reviews', method=["GET", "POST"])
@action.uses(db, session, auth.user, 'reviews.html')
def reviews():
    
    return dict(
        load_reviews_url = URL('load_reviews', signer=url_signer),
        add_reviews_url = URL('add_reviews', signer=url_signer),
        delete_reviews_url = URL('delete_reviews', signer=url_signer),
    )
"""


@action('reviews/<landlord_id:int>', method=["GET", "POST"])
@action.uses(db, session, auth.user, 'reviews.html')
def reviews(landlord_id=None):
    assert landlord_id is not None
    landlord = db.landlord[landlord_id]
    landlord_name = landlord.first_name + " " + landlord.last_name

    landlordID = landlord_id
    session['landlordID'] = landlord_id
    
    rows = db(
        (db.reviews.reviews_landlordID == landlord_id)
    ).select()  # as list
    
    num_rows = db(
        (db.reviews.reviews_landlordID == landlord_id)
    ).count()
    
    avg_overall = 0
    avg_friend = 0
    avg_resp = 0

    for r in rows:
        avg_overall += float(r.reviews_score_overall)
        avg_friend += float(r.reviews_score_friendliness)
        avg_resp += float(r.reviews_score_responsiveness)
    
    if num_rows > 0:
        avg_overall = round(avg_overall/num_rows)
        avg_friend = round(avg_friend/num_rows)
        avg_resp = round(avg_resp/num_rows)
    return dict(
        avg_overall=avg_overall,
        avg_friend=avg_friend,
        avg_resp=avg_resp,
        landlordID=landlordID,
        landlord_name=landlord_name,
        load_reviews_url=URL('load_reviews', signer=url_signer),
        add_reviews_url=URL('add_reviews', signer=url_signer),
        delete_reviews_url=URL('delete_reviews', signer=url_signer),
        get_votes_url=URL('get_votes', signer=url_signer),
        set_votes_url=URL('set_votes', signer=url_signer),
        get_voters_url=URL('get_voters', signer=url_signer),
    )

    
@action('add_landlord', method=["GET", "POST"])
@action.uses(db, session, auth.user)
def add_landlord():
    form = Form(db.landlord, csrf_session=session, formstyle=FormStyleBulma)
    if form.accepted:
        id = form.vars['id']
        redirect(URL('reviews', id))
    return dict(form=form)


@action('add_reviews', method=["GET", "POST"])
@action.uses(url_signer.verify(), db, auth, auth.user)
def add_reviews():
    renter = db(db.auth_user.email == get_user_email()).select().first()
    renter_name = renter.first_name + " " + renter.last_name
    print(renter_name)
    renter_id = renter.id if renter is not None else "Unknown"
    renter_email = renter.email
    reviews_landlordID = int(session.get('landlordID', None))
    #reviews_landlordID = request.json.get('reviews_landlordID')
    reviews_score_friendliness = int(request.json.get('reviews_score_friendliness'))
    reviews_score_responsiveness = int(request.json.get('reviews_score_responsiveness'))
    reviews_property_address = request.json.get('reviews_property_address')
    reviews_score_overall = (reviews_score_friendliness+reviews_score_responsiveness)/2
    reviews_contents = request.json.get('reviews_contents')

    id = db.reviews.insert(
        renter_name=renter_name,
        reviews_renters_id=renter_id,
        renter_email=renter_email,
        reviews_landlordID=reviews_landlordID,
        reviews_address_id=request.json.get('reviews_address_id'),
        reviews_contents=request.json.get('reviews_contents'),
        reviews_score_responsiveness=request.json.get('reviews_score_responsiveness'),
        reviews_score_friendliness=request.json.get('reviews_score_friendliness'),
        reviews_property_address=request.json.get('reviews_property_address'),
        reviews_score_overall=(reviews_score_friendliness+reviews_score_responsiveness)/2,
    )
    return dict(
        renter_name=renter_name,
        id=id,
        reviews_landlordID=reviews_landlordID,
        renter_id=renter_id, 
        renter_email=renter_email,
        reviews_score_responsiveness=reviews_score_responsiveness,
        reviews_score_friendliness=reviews_score_friendliness,
        reviews_property_address=reviews_property_address,
        reviews_score_overall=reviews_score_overall,
        reviews_contents=reviews_contents,
    )


@action('delete_reviews')
@action.uses(url_signer.verify(), db)
def delete_reviews():
    id = request.params.get('id')
    assert id is not None
    db(db.reviews.id == id).delete()
    return "--REVIEW DELETED--"


@action('get_votes')
@action.uses(db, auth.user, url_signer.verify())
def get_votes():
    review_id = request.params.get('review_id')
    r = db((db.votings.review == review_id) & (db.votings.voter == get_user())).select().first()
    voted = r.voted if r is not None else 0
    return dict(voted=voted)


@action('set_votes', method="POST")
@action.uses(db, auth.user, url_signer.verify())
def set_votes():
    review_id = request.json.get('review_id')
    checkVoted = request.json.get('voted')
    unVote = db((db.votings.review == review_id) & (db.votings.voter == get_user())).select().first()
    if unVote is None:
        voted = checkVoted
    elif checkVoted == unVote['voted']:
        voted = 0
    else:
        voted = checkVoted
    db.votings.update_or_insert(((db.votings.review == review_id) & (db.votings.voter == get_user())),
        voter=get_user(),
        voted=voted,
        review=review_id,
    )
    return "-Vote Updated-"
    

@action('get_voters')
@action.uses(db, auth.user, url_signer.verify())
def get_voters():
    review_id = request.params.get('review_id')
    count = 0

    allvTers = db((db.votings.review == review_id) & (db.votings.voted == 1)).select().as_list()
    for vTer in allvTers:
        count = count + 1

    alldvTers = db((db.votings.review == review_id) & (db.votings.voted == 2)).select().as_list()
    for dvTer in alldvTers:
        count = count - 1
    return dict(count=count)



@action('search')
@action.uses()
def search():
    q = request.params.get("q")
    q_name = q.split()
    print('q is:', type(q), q)
    print('q_name is:', type(q_name), len(q_name), q_name)
    q_first_name = q_name[0].title()
    not_found = False
    if len(q_name) < 2:
        rows = db(db.landlord.first_name.ilike(q_first_name+'%')).select().as_list()
        print('rows is:', rows)
        if len(rows) == 0:
            not_found = True
    else:
        q_last_name = q_name[1].title()
        rows = db((db.landlord.first_name.ilike(q_first_name + '%')) &
                  (db.landlord.last_name.ilike(q_last_name + '%'))).select().as_list()
        if len(rows) == 0:
            not_found = True
    print('is not found:', not_found)
    """
    print('stripped name is:', q_first_name, q_last_name)
    results_found = False
    results = 0
    for row in db(db.landlord.first_name == q_first_name).select():
        print('found', type(row), row)
        print('row.id', row.id)

        results = [{row.first_name + " " + row.last_name}, {row.id}]

        print(results)
        results_found = True
    if results_found is False:
        results = 'Not Found'
    """
    # rows = db(db.landlord.first_name.ilike(q_first_name+'%')).select().as_list()
    return dict(rows=rows, not_found=not_found)


@action('get_search_url')
@action.uses(db, url_signer)
def get_search_url():
    lord_id = int(request.params.get('lord_id'))
    return dict(url=URL('reviews', lord_id))

# @action("signup", method=["GET", "POST"])
# @action.uses(db, session, auth, 'signup.html')
# def signup():
#     form = Form(auth, csrf_session=session, formstyle=FormStyleBulma)
#     if form.accepted:
#         # We simply redirect; the insertion already happened.
#         # username = form.vars['reviews_username']
#         # db(db.reviews.reviews_username == username).update(username=username)
#         redirect(URL('index'))
#     # Either this is a GET request, or this is a POST but not accepted = with errors.
#     return dict(form=form)


# @action('add_review', method=["GET", "POST"])
# @action.uses(db, session, auth.user, 'add_review.html')
# def add_review():
#     form = Form(db.reviews, csrf_session=session, formstyle=FormStyleBulma)
#     if form.accepted:
#         # We simply redirect; the insertion already happened.
#         # username = form.vars['reviews_username']
#         # db(db.reviews.reviews_username == username).update(username=username)
#         redirect(URL('index'))
#     # Either this is a GET request, or this is a POST but not accepted = with errors.
#     return dict(form=form)


# @action('add_address', method=["GET", "POST"])
# @action.uses(db, session, auth.user, 'add_review.html')
# def add_address():
#     form = Form(db.reviews, csrf_session=session, formstyle=FormStyleBulma)
#     if form.accepted:
#         # We simply redirect; the insertion already happened.
#         # username = form.vars['reviews_username']
#         # db(db.reviews.reviews_username == username).update(username=username)
#         redirect(URL('index'))
#     # Either this is a GET request, or this is a POST but not accepted = with errors.
#     return dict(form=form)


# ----------------------------------------thumbs up/down code, uncomment when ready
# @action("get_thumbs_up")
# @action.uses(url_signer.verify(), db)
# def get_thumbs_up():
#     rows = db((db.thumbs_up.each_review == request.params.get('id')) &
#               (db.thumbs_up.rater == get_user())).select().as_list()
#     if len(rows) == 0:
#         up = 0
#     else:
#         up = int(rows[0]['up'])
#     return dict(up=up)
#
#
# @action("get_thumbs_down")
# @action.uses(url_signer.verify(), db)
# def get_thumbs_down():
#     rows = db((db.thumbs_down.each_review == request.params.get('id')) &
#               (db.thumbs_down.rater == get_user())).select().as_list()
#     if len(rows) == 0:
#         down = 0
#     else:
#         down = int(rows[0]['down'])
#     return dict(down=down)
#
#
# @action("set_thumbs_up", method="POST")
# @action.uses(url_signer.verify(), db)
# def set_thumbs_up():
#     id = request.json.get('id')
#     up = int(request.json.get('up'))
#
#     if up == 1:
#         db.thumbs_up.update_or_insert(
#             ((db.thumbs_up.each_review == id) & (db.thumbs_up.rater == get_user())),
#             each_post=id,
#             rater=get_user(),
#             up=up
#         )
#         db((db.thumbs_down.each_review == id) & (db.thumbs_down.rater == get_user())).delete()
#     else:
#         db((db.thumbs_up.each_review == id) & (db.thumbs_up.rater == get_user())).delete()
#     return "ok"
#
#
# @action("set_thumbs_down", method="POST")
# @action.uses(url_signer.verify(), db)
# def set_thumbs_down():
#     id = request.json.get('id')
#     down = int(request.json.get('down'))
#
#     if down == 1:
#         db.thumbs_down.update_or_insert(
#             ((db.thumbs_down.each_review == id) & (db.thumbs_down.rater == get_user())),
#             each_post=id,
#             rater=get_user(),
#             down=int(request.json.get('down'))
#         )
#         db((db.thumbs_up.each_review == id) & (db.thumbs_up.rater == get_user())).delete()
#     else:
#         db((db.thumbs_down.each_review == id) & (db.thumbs_down.rater == get_user())).delete()
#     return "ok"
#
#
# @action("get_thumbs_up_list")
# @action.uses(url_signer.verify(), db)
# def get_thumbs_up_list():
#     row_index = int(request.params.row_idx)
#     rows = db(db.thumbs_up.each_review == row_index).select().as_list()
#     list_up = []
#     for r in rows:
#         userId = r['rater']
#         row2 = db(db.auth_user.id == userId).select().as_list()
#         list_up.append(row2[0]['first_name'] + " " + row2[0]['last_name'])
#
#     final_name = ", ".join(k for k in list_up)
#     if final_name != "":
#         final_name = "Liked by " + final_name
#
#     return dict(final_name=final_name)
#
#
# @action("get_thumbs_down_list")
# @action.uses(url_signer.verify(), db)
# def get_thumbs_down_list():
#     row_index = int(request.params.row_idx)
#     rows = db(db.thumbs_down.each_review == row_index).select().as_list()
#     list_up = []
#     for r in rows:
#         userId = r['rater']
#         row2 = db(db.auth_user.id == userId).select().as_list()
#         list_up.append(row2[0]['first_name'] + " " + row2[0]['last_name'])
#
#     final_name = ", ".join(k for k in list_up)
#     if final_name != "":
#         final_name = "Disliked by " + final_name
#     return dict(final_name=final_name)
