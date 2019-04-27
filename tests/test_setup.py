import unittest
from reservation import create_app
from reservation.config import TestConfig


class TestApp(unittest.TestCase):
    def setUp(self):
        tested_app = create_app(TestConfig)
        tested_app.app_context().push()
        self.app = tested_app.test_client()

    def test_404_on_invalid_url(self):
        # Send the request and check the response status code
        response = self.app.get("/invalidurl")
        self.assertEqual(response.status_code, 404)

        # Validate the body's format to be JSON
        self.assertTrue(response.is_json)
        body = response.json

        # Validate the body
        self.assertCountEqual(['code', 'msg', 'error'], body.keys())
        self.assertTrue(body['code'] == 404 and body['error'])

    def test_app_setup(self):
        # send the request and check the response status code
        response = self.app.get("/version")
        self.assertEqual(response.status_code, 200)

        # Validate the body's format to be JSON
        self.assertTrue(response.is_json)
        body = response.json

        # Validate we have the right fields, content is irrelevant in this case
        self.assertCountEqual(['service', 'version'], body.keys())


if __name__ == '__main__':
    unittest.main()
