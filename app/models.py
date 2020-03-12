from app.extensions import db, login_manager
from datetime import datetime, date, timedelta
from flask import url_for
from flask_login import UserMixin
from werkzeug.security import check_password_hash, generate_password_hash
from enum import Enum
from hashlib import md5
import os
import base64

from app.permissions import Role

from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy import and_

@login_manager.user_loader
def load_user(id):
    return User.query.get(int(id))

class PaginatedAPIMixin(object):
    @staticmethod
    def to_collection_dict(query, page, per_page, endpoint, **kwargs):
        resources = query.paginate(page, per_page, False)
        data = {
            'items': [ item.to_dict() for item in resources.items ],
            '_meta': {
                'page': page,
                'per_page': per_page,
                'total_pages': resources.pages,
                'total_items': resources.total
            },
            '_links': {
                'self': url_for(endpoint, page=page, per_page=per_page,
                                **kwargs),
                'next': url_for(endpoint, page=page + 1, per_page=per_page,
                                **kwargs) if resources.has_next else None,
                'prev': url_for(endpoint, page=page - 1, per_page=per_page,
                                **kwargs) if resources.has_prev else None
            }
        }
        return data

#https://docs.sqlalchemy.org/en/13/orm/basic_relationships.html#association-object
class TravelArrangementTouristUser(db.Model):
    __tablename__ = 'travel_arrangement_tourist_users'

    travel_arrangement_id = db.Column(db.Integer,
                                      db.ForeignKey('travel_arrangements.id'),
                                      primary_key=True,
                                      nullable=False)
    tourist_user_id = db.Column(db.Integer,
                                db.ForeignKey('tourist_users.id'),
                                primary_key=True,
                                nullable=False)

    travel_arrangement = db.relationship(
        'TravelArrangement',
        back_populates='_tourists')
    tourist_user = db.relationship(
        'TouristUser',
        back_populates='_arrangements')

class UserRole(db.Model):
    __tablename__ = 'user_roles'

    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    #user_id = db.Column(db.Integer, db.ForeignKey('
    role = db.Column(
        db.Integer,
        default=Role.TOURIST,
        unique=True,
        nullable=False)

    users = db.relationship('User', back_populates='user_role', uselist=True)

class GuideUserResponse(db.Model):
    __tablename__ = 'guide_user_responses'

    class Type():
        PENDING : int = 0
        ACCEPTED : int = 1
        DENIED : int = 1

    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    guide_id = db.Column(db.Integer,
                         db.ForeignKey('guide_users.id'),
                         nullable=False)
    travel_arrangement_id = db.Column(db.Integer,
                         db.ForeignKey('travel_arrangements.id'),
                         nullable=False)
    status = db.Column(db.Integer,
                       default=Type.PENDING,
                       nullable=False)

    #travel_arrangement = db.relationship(
    #    'TravelArrangement',
    #    back_populates='_tourists')
    #tourist_user = db.relationship(
    #    'TouristUser',
    #    back_populates='_arrangements')


class User(db.Model, UserMixin, PaginatedAPIMixin):
    __tablename__ = 'users'

    id =  db.Column(db.Integer, autoincrement=True, primary_key=True) 
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(50), index=True, unique=True)
    first_name = db.Column(db.String(30), index=True)
    last_name = db.Column(db.String(30), index=True)
    password_hash = db.Column(db.String(128))
    role_id = db.Column(db.Integer, db.ForeignKey('user_roles.id'))

    token = db.Column(db.String(32), index=True, unique=True)
    token_expiration = db.Column(db.DateTime)

    user_role = db.relationship('UserRole', back_populates='users')
    
    def is_admin(self):
        return self.user_role.role == Role.ADMIN
    def is_guide(self):
        return self.user_role.role == Role.GUIDE
    def is_tourist(self):
        return self.user_role.role == Role.TOURIST

    def get_admin(self):
        return AdminUser.query.filter_by(user_id=self.id).first_or_404()
    def get_guide(self):
        return GuideUser.query.filter_by(user_id=self.id).first_or_404()
    def get_tourist(self):
        return TouristUser.query.filter_by(user_id=self.id).first_or_404()

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def avatar(self, size):
        digest = md5(self.email.lower().encode('utf-8')).hexdigest()
        return 'https://www.gravatar.com/avatar/{}?d=identicon&s={}'.format(
            digest, size)

    def set_role(self, role):
        self.role_id = UserRole.query.filter_by(role=role).first().id

    def to_dict(self, include_email=False):
        data = {
            'id': self.id,
            'username': self.username,
            'first_name': self.first_name,
            'last_name': self.last_name,
            '_links': {
                'self': url_for('api.get_user', id=self.id),
                'avatar': self.avatar(100)
            }
        }
        if include_email:
            data['email'] = self.email
        if self.user_role == Role.TOURIST:
            data['role'] = 'tourist'
        elif self.user_role == Role.GUIDE:
            data['role'] = 'guide'
        elif self.user_role == Role.ADMIN:
            data['role'] = 'admin'
        return data

    def from_dict(self, data, new_user=False):
        for field in ['username', 'email', 'first_name', 'last_name']:
            setattr(field, data[field])
        if new_user and 'password' in data:
            self.set_password(data['password'])
    
    def get_token(self, expires_in=3600):
        now = datetime.utcnow()
        if self.token and self.token_expiration > now + timedelta(seconds=60):
            return self.token
        self.token = base64.b64encode(os.urandom(24)).decode('utf-8')
        self.token_expiration = now + timedelta(seconds=expires_in)
        db.session.add(self)
        return self.token

    def revoke_token(self):
        self.token_expiration = datetime.utcnow() - timedelta(seconds=1)

    @staticmethod
    def check_token(token):
        user = User.query.filter(User.token==token).first()
        if user is None or user.token_expiration < datetime.utcnow():
            return None
        return user

class TouristUser(db.Model):
    __tablename__ = 'tourist_users'

    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))

    user = db.relationship('User')
    _arrangements = db.relationship('TravelArrangementTouristUser',
                               back_populates='tourist_user',
                               uselist=True)
    arrangements = association_proxy(
        '_arrangements',
        'travel_arrangement')

    # TODO: Handle error when not enough spaces
    def book(self, arrangement, spots):
        if arrangement.avl_spots >= spots and \
           not self.is_booked(arrangement):
            db.session.add(TravelArrangementTouristUser(
                travel_arrangement_id=arrangement.id,
                tourist_user_id=self.id))
            arrangement.avl_spots -= spots
            db.session.commit()
            return arrangement.calculate_price(spots)
        
    def unbook(self, arrangement):
        if self.is_booked(arrangement):
            pass
            #self.arrangements.remove(arrangement)

    def is_booked(self, arrangement):
        return TravelArrangementTouristUser.query.filter(
            and_(TravelArrangementTouristUser.travel_arrangement_id== \
                    arrangement.id,
                 TravelArrangementTouristUser.tourist_user_id==self.id)) \
                    .count() > 0

    # returns arrangements that I didn't book yet
    def get_arrangements_query(self):
        #SELECT *
        #FROM travel_arrangement TA
        #LEFT JOIN travel_arrangement_tourist_user TT ON (TT.travel_arrangement_id=TA.id AND TT.tourist_user_id=1)
        #--WHERE TA.start_date > _TODAY_
        return TravelArrangement.query.outerjoin(
            TravelArrangementTouristUser,
            and_(TravelArrangementTouristUser \
                    .travel_arrangement_id==TravelArrangement.id,
                 TravelArrangementTouristUser.tourist_user_id==self.id)).filter(
                    and_(TravelArrangement.start_date > date.today(),
                         TravelArrangementTouristUser.tourist_user_id==None,
                         TravelArrangement.avl_spots > 0)) \
                            .order_by(TravelArrangement.start_date.desc())
                        
    def get_arrangements(self):
        return self.get_arrangements_query().all()

class GuideUser(db.Model):
    __tablename__ = 'guide_users'

    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))

    user = db.relationship('User')

    arrangements = db.relationship('TravelArrangement', lazy='dynamic',
        back_populates='guide')

    # returns all the arrangements that I didn't request guide position for
    def get_arrangements_query(self):
        # TODO: Filter out travel arrangement guide requests only if they are not
        # declined by the administrator. ( ??? )
        ##SELECT * FROM travel_arrangement T
        ##LEFT JOIN guide_user_response G ON (G.travel_arrangement_id=T.id and G.guide_id=4)
        ##WHERE T.guide_id is NULL and G.id is NULL
        ##ORDER BY T.start_date DESC
        #.filter(uslov1, uslov2)
        return TravelArrangement.query.outerjoin(
            GuideUserResponse,
            and_(GuideUserResponse.travel_arrangement_id==TravelArrangement.id,
                 GuideUserResponse.guide_id==self.id)).filter(and_(
                    TravelArrangement.guide_id==None,
                    GuideUserResponse.id==None)).order_by(
                        TravelArrangement.start_date.desc()).distinct(
                            GuideUserResponse.travel_arrangement_id,
                            GuideUserResponse.guide_id)

    def get_arrangements(self):
        return self.get_arrangements_query().all()

    def request_guide_position(self, arrangement):
        if not arrangement and arrangement.guide is not None:
            return False
        db.session.add(GuideUserResponse(
                guide_id=self.id,
                travel_arrangement_id=arrangement.id))
        db.session.commit()
        

class AdminUser(db.Model):
    __tablename__ = 'admin_users'

    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))

    user = db.relationship('User')

    arrangements = db.relationship('TravelArrangement',
        order_by='desc(TravelArrangement.start_date)',
        back_populates='admin', uselist=True)
    
    # returns my arrangements for which guides requested the guide position
    def get_arrangements_query(self):
        #SELECT T.*, U.* FROM travel_arrangements T
        #JOIN guide_user_responses R ON R.travel_arrangement_id=T.id
        #JOIN guide_users G ON R.guide_id=G.id
        #JOIN users U ON G.user_id=U.id
        #WHERE T.admin_id=1 AND T.guide_id IS NULL
        #ORDER BY T.id ASC
        return TravelArrangement.query.join(GuideUserResponse, 
            GuideUserResponse.travel_arrangement_id==TravelArrangement.id) \
                .join(GuideUser, GuideUserResponse.guide_id==GuideUser.id) \
                    .join(User, GuideUser.user_id==User.id).filter(and_(
                        TravelArrangement.admin_id==self.id,
                        TravelArrangement.guide_id==None)).order_by(
                            TravelArrangement.id).add_entity(
                                User)

    def get_arrangements(self):
        return self.get_arrangements_query().all()


class TravelArrangement(db.Model, PaginatedAPIMixin):
    __tablename__ = 'travel_arrangements'

    def avl_spots_default(context):
        return context.get_current_parameters()['total_spots']

    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    start_date = db.Column(db.Date, default=datetime.utcnow)
    end_date = db.Column(db.Date, default=datetime.utcnow)
    description = db.Column(db.String(250))
    location = db.Column(db.String(50))
    price = db.Column(db.Integer) # price / spot
    total_spots = db.Column(db.Integer)
    avl_spots = db.Column(db.Integer, default=avl_spots_default)
    admin_id = db.Column(db.Integer,
                         db.ForeignKey('admin_users.id'),
                         nullable=False)
    guide_id = db.Column(db.Integer,
                         db.ForeignKey('guide_users.id'), 
                         nullable=True)
    
    guide = db.relationship('GuideUser',
        back_populates='arrangements')
    admin = db.relationship('AdminUser',
        back_populates='arrangements')

    _tourists = db.relationship('TravelArrangementTouristUser',
                               back_populates='travel_arrangement',
                               uselist=True)
    tourists = association_proxy('_tourists',
        'tourist_user')

    def calculate_price(self, spots):
        if spots > 3:
            return (3 + (spots - 3) * 0.8) * self.price
        return spots * self.price
            
    # TODO: Implement stuff. 
    def notify_users_deletion(self):
        return

    def to_dict(self, avl_spots=False):
        data = {
            'id': self.id,
            'location': self.location,
            'description': self.description,
            'price': self.price,
            'total_spots': self.total_spots,
            'avl_spots': self.avl_spots,
            'start_date': self.start_date.isoformat() + 'Z',
            'end_date': self.end_date.isoformat() + 'Z',
            '_links': {
                'self': url_for('api.get_arrangement', id=self.id),
            }
        }
        return data

    def from_dict(self, data):
        #for field in ['location', 'description', 'price', 'price',
        #              'total_spots', 'start_date', 'end_date']:
        for field in ['location', 'description', 'price', 'price',
                      'total_spots']:
            if field in data:
                setattr(self, field, data[field])
        if 'total_spots' in data:
            self.avl_spots = data['total_spots']
