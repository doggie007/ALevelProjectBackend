import unittest
from fastapi.testclient import TestClient
from main import app
from models import ZeroDimensionalEnergyBalanceModel

class TestAPIEndpoints(unittest.TestCase):
    def test_read_root(self):
        # Test API is functioning
        # GET request for root returns "Hello World"
        client = TestClient(app)
        response = client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {'message': "Hello World"})

    def test_execute_returns_correct_data(self):
        # POST request with valid data to /execute/ endpoint returns data
        # The data returned from API is exactly the same as simulation data
        client = TestClient(app)
        model_name = "Arbitrary Name"
        initial_temperature = 30

        response = client.post("/execute/", json={"model_name": model_name, "initial_temperature": initial_temperature})

        # Run model
        model = ZeroDimensionalEnergyBalanceModel(model_name, initial_temperature)
        model.run()
        simulation_data = model.get_data()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"temperatures": simulation_data["temperatures"], "times": simulation_data["times"]})

    def test_execute_invalid_http_request(self):
        pass


if __name__ == '__main__':
    unittest.main()
