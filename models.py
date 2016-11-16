from main import db


class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    userid = db.Column(db.String())
    # name = db.Column(db.String())
    xp = db.Column(db.Integer())
    # lastmsg = db.Column(db.String())
    # lastloc = db.Column(db.JSON())
    # language = db.Column(db.String())

    def __init__(self, userid):
        self.userid = userid
        self.xp = 0

    def __repr__(self):
        return '<userid {}>'.format(self.userid)
