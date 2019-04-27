import unittest
import datetime

from reservation import create_app
from reservation.config import TestConfig
from reservation.models import db, Reservation, Person


class TestReservation(unittest.TestCase):
    def setUp(self):
        tested_app = create_app(TestConfig)
        tested_app.app_context().push()

        db.create_all()

        # Add known rows
        self.date = datetime.datetime.now() + datetime.timedelta(days=7)
        batman = Person(name='Batman', email='batman@wayneindustries.com')
        reservation1 = Reservation(
            client=batman,
            start_datetime=self.date,
            party_size=4,
            note="Take care of alfred!"
        )
        reservation2 = Reservation(
            client=batman,
            start_datetime=self.date,
            party_size=4,
            note="Take care of alfred!"
        )

        # Add them to the db
        db.session.add(reservation1)
        db.session.add(reservation2)
        db.session.commit()

        self.db = db
        self.app = tested_app.test_client()

    def tearDown(self):
        # clean up the DB after every test
        self.db.session.remove()
        self.db.drop_all()

    def test_get_all_reservations(self):
        # Send the request and check the response status code
        response = self.app.get("/reservations")
        self.assertEqual(response.status_code, 200)

        # Validate the body's format to be JSON
        self.assertTrue(response.is_json)
        body = response.json

        # Validate the body
        self.assertEqual(len(body), 2)
        self.assertDictEqual(body[0], {'id': 1, 'name': 'Batman', 'size': 4, 'time': self.date.isoformat()})


if __name__ == '__main__':
    unittest.main()
