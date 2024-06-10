from flask_seeder import Seeder, Faker, generator
from project.models import User, Profile, Location
from werkzeug.security import generate_password_hash


# All seeders inherit from Seeder
class UserSeeder(Seeder):

    # run() will be called by Flask-Seeder
    def run(self):
        user = User(name="Admin",
                    email="admin@example.com",
                    password=generate_password_hash("admin", method='pbkdf2:sha256'),
                    role="admin"
                    )

        # Create admin
        print("Adding user: %s" % user)
        self.db.session.add(user)

        # Create a new Faker and tell it how to create User objects
        faker = Faker(
            cls=User,
            init={
                "name": generator.Name(),
                "email": generator.Email(),
                "password": generate_password_hash("coach", method='pbkdf2:sha256'),
                "role": 'coach'
            }
        )

        # Create 5 coaches
        for user in faker.create(5):
            print("Adding user: %s" % user)
            self.db.session.add(user)

        # Create a new Faker and tell it how to create Location objects
        # faker = Faker(
        #     cls=Location,
        #     init={
        #         "name": generator.Name()
        #     }
        # )

