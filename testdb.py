from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base, User, Stamp


# When running script
engine = create_engine("sqlite:///apptest.db")
# Session maker object, to instantiate sessions from
Session = sessionmaker(bind=engine)


# Ensure all tables are created.
print("Creating tables")
Base.metadata.create_all(engine)    # This is on initiation of script
print(Base.metadata.tables.keys())  # Print a dict of all tables


if __name__ == "__main__":
    msg = """
Normally, it’s important to write change scripts in a way that’s independent of your application - the same SQL should be generated every time, despite any changes to your app’s source code. You don’t want your change scripts’ behavior changing when your source code does.
    """
    xp = 1 + len(msg) // 80
    session = Session()     # Need to create new session every time (?)
    # user1 = User(userid="12345", xp=2)     # Create a new user object
    # user2 = User(userid="23456", xp=20)     # Create a new user object
    # user3 = User(userid="34567", xp=50)     # Create a new user object
    # session.add_all([user1, user2, user3])
    rank = session.query(User).order_by(User.xp.desc()).all()
    for r in rank[:5]:
        print(r.userid, r.xp)

    if not session.query(User).filter_by(userid="1234").first():
        user1 = User(userid="1234", xp=xp)     # Create a new user object
        session.add(user1)  # Add user object to session
        session.commit()    # Write changes to database
    else:
        print("User exist!")
    q = session.query(User).all()   # Query by filter
    for u in q:
        print(u, u.id, u.xp)
    # q = session.query(User).filter_by(userid="2345").delete()    # Delete by filter
    session.commit()    # Write changes to database

    session = Session()
    if not session.query(Stamp).filter_by(descriptor="commit").first():
        cstamp = Stamp(descriptor="commit", stamp="12345678")
        session.add(cstamp)
        session.commit()
    for s in session.query(Stamp).all():
        # s.stamp += "9"
        print(s, s.id, s.descriptor, s.stamp)
    session.commit()
