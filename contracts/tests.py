from accounts.tests import ModelTestCase


class ContractTestCase(ModelTestCase):
    def test_contract_creation_successfull(self):
        self.assertEqual(self.contract.client, self.custom_client)
        self.assertEqual(self.contract.employee, self.employee)
        self.assertEqual(self.contract.total_costs, self.COSTS)

    def test_contract_total(self):
        self.assertEquals(self.contract.total, f"{self.COSTS} €")

    def test_contract_paid_amount(self):
        self.assertEquals(self.contract.paid_amount, f"{self.AMOUNT} €")

    def test_contract_rest_amount(self):
        result = self.COSTS - self.AMOUNT
        self.assertEquals(self.contract.rest_amount, f"{result} €")

    def test_contract_str(self):
        self.assertEquals(
            f"{self.custom_client.get_full_name} ({self.employee.user.email})",
            f"{self.CLIENT_FIRST_NAME} {self.CLIENT_LAST_NAME} ({self.USER_EMAIL})")

# Create your tests here.
