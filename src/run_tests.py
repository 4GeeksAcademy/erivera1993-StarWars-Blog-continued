from src import app
from src.models import db, User, Character, Planet, Favorite


def run_smoke_tests():
    with app.app_context():
        # ensure DB and sample data
        db.create_all()
        if not User.query.first():
            u = User(email='test@example.com', password='x', is_active=True)
            db.session.add(u)
            db.session.commit()

        if not Planet.query.first():
            p = Planet(name='Tatooine', climate='arid', terrain='desert', population='200000')
            db.session.add(p)
            db.session.commit()

        if not Character.query.first():
            planet = Planet.query.first()
            c = Character(name='Luke Skywalker', gender='male', birth_year='19BBY', eye_color='blue', planet_id=planet.id)
            db.session.add(c)
            db.session.commit()

        client = app.test_client()

        print('GET /people ->', client.get('/people').get_json())
        print(f"GET /people/1 -> {client.get('/people/1').get_json()}")
        print('GET /planets ->', client.get('/planets').get_json())
        print('GET /planets/1 ->', client.get('/planets/1').get_json())
        print('GET /users ->', client.get('/users').get_json())
        print('GET /users/favorites ->', client.get('/users/favorites').get_json())

        # add favorite planet
        print('POST /favorite/planet/1 ->', client.post('/favorite/planet/1').get_json())
        print('GET /users/favorites (after add) ->', client.get('/users/favorites').get_json())
        print('DELETE /favorite/planet/1 ->', client.delete('/favorite/planet/1').get_json())
        print('GET /users/favorites (after delete) ->', client.get('/users/favorites').get_json())


if __name__ == '__main__':
    run_smoke_tests()
