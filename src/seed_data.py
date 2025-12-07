from src import app
from src.models import db, User, Character, Planet


def seed():
    with app.app_context():
        db.create_all()

        if not User.query.first():
            u = User(email='test@example.com', password='x', is_active=True)
            db.session.add(u)

        if not Planet.query.first():
            p = Planet(name='Tatooine', climate='arid', terrain='desert', population='200000')
            db.session.add(p)
            db.session.flush()

        if not Character.query.first():
            planet = Planet.query.first()
            c = Character(name='Luke Skywalker', gender='male', birth_year='19BBY', eye_color='blue', planet_id=planet.id)
            db.session.add(c)

        db.session.commit()


if __name__ == '__main__':
    seed()
