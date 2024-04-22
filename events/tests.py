from accounts.tests import ModelTestCase


class EventTestCase(ModelTestCase):
    def test_event_creation_successfull(self):
        self.assertEqual(self.event.contract.client, self.custom_client)
        self.assertEqual(self.event.employee, self.employee)
        self.assertEqual(self.event.location, self.LOCATION)
        
    def test_event_str(self):
        self.assertEquals(
            f"{self.event.name} ({self.employee.user.email})",
            f"{self.NAME} ({self.USER_EMAIL})")

# Create your tests here.
