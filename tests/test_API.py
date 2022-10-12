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

        # Run model for getting the correct data
        model = ZeroDimensionalEnergyBalanceModel(model_name, initial_temperature)
        model.run()
        simulation_data = model.get_data()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"temperatures": simulation_data["temperatures"], "times": simulation_data["times"], "model_name": model_name, "initial_temperature": initial_temperature})

    def test_execute_missing_required_parameters(self):
        # Raises 422 error if required parameter is missing
        # Test when parameter for initial temperature is missing
        client = TestClient(app)
        model_name = "Arbitrary Name"
        response = client.post("/execute/", json={"model_name": model_name})
        self.assertEqual(response.status_code, 422)

    def test_execute_invalid_parameter_type(self):
        # Raises 422 error if parameter input is of wrong type
        client = TestClient(app)
        model_name = "Arbitrary Name"
        initial_temperature = "one-hundred"
        response = client.post("/execute/", json={"model_name": model_name, "initial_temperature": initial_temperature})
        self.assertEqual(response.status_code, 422)

    def test_execute_invalid_parameter_value(self):
        # Raises 400 error if initial temperature value is not within realistic range
        client = TestClient(app)
        model_name = "Arbitrary Name"
        initial_temperature = 1000
        response = client.post("/execute/", json={"model_name": model_name, "initial_temperature": initial_temperature})
        self.assertEqual(response.status_code, 400)



if __name__ == '__main__':
    unittest.main()
