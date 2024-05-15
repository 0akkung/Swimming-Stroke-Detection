from flask_seeder import Seeder, Faker, generator
from project.models import User
from werkzeug.security import generate_password_hash


# All seeders inherit from Seeder
class UserSeeder(Seeder):

    # run() will be called by Flask-Seeder
    def run(self):
        # Create a new Faker and tell it how to create User objects
        faker = Faker(
            cls=User,
            init={
                "id": generator.Sequence(),
                "name": generator.Name(),
                "email": generator.Email(),
                "password": generate_password_hash("coach", method='pbkdf2:sha256'),
                "role": 'coach'
            }
        )

        # Create 5 users
        for user in faker.create(5):
            print("Adding user: %s" % user)
            self.db.session.add(user)
