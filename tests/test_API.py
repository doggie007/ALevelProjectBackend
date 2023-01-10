import unittest
from fastapi.testclient import TestClient
from main import app
from models import Constants, ZeroDimensionalEnergyBalanceModel, RcpModel


class TestEBMEndpoint(unittest.TestCase):
    def test_read_root(self):
        # Test API is functioning
        # GET request for root returns "Hello World"
        client = TestClient(app)
        response = client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {'message': "Hello World"})

    def test_execute_EBM_returns_correct_data(self):
        # POST request with valid data to /execute/ endpoint returns data
        # The data returned from API is exactly the same as simulation data
        client = TestClient(app)
        model_name = "Arbitrary Name"
        initial_temperature = 30

        response = client.post("/execute/EBM", json={ "model_name": model_name,
                                                      "initial_temperature": initial_temperature,
                                                      "insolation": Constants.INSOLATION_OBSERVED,
                                                      "albedo": Constants.ALPHA,
                                                      "tau": Constants.TAU
                                                      })

        # Run model for getting the correct data
        model = ZeroDimensionalEnergyBalanceModel(model_name,
                                                  initial_temperature,
                                                  Constants.INSOLATION_OBSERVED,
                                                  Constants.ALPHA,
                                                  Constants.TAU)
        model.run()
        simulation_data = model.get_temperature_time_data()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(),
                         {"temperatures": simulation_data["temperatures"], "times": simulation_data["times"],
                          "model_name": model_name, "initial_temperature": initial_temperature,
                          "insolation": Constants.INSOLATION_OBSERVED, "albedo": Constants.ALPHA, "tau": Constants.TAU})

    def test_execute_EBM_missing_required_parameters(self):
        # Raises 422 error if required parameters are missing
        client = TestClient(app)
        model_name = "Arbitrary Name"
        response = client.post("/execute/EBM", json={"model_name": model_name})
        self.assertEqual(response.status_code, 422)

    def test_execute_EBM_invalid_parameter_type(self):
        # Raises 422 error if parameter input is of wrong type
        client = TestClient(app)
        model_name = "Arbitrary Name"
        initial_temperature = "one-hundred"
        response = client.post("/execute/EBM", json={"model_name": model_name, "initial_temperature": initial_temperature,
                                                  "insolation": Constants.INSOLATION_OBSERVED, "albedo": Constants.ALPHA, "tau": Constants.TAU})
        self.assertEqual(response.status_code, 422)

    def test_execute_EBM_invalid_temperature_value(self):
        # Raises 400 error if initial temperature value is not within realistic range
        client = TestClient(app)
        model_name = "Arbitrary Name"
        initial_temperature = 1000
        response = client.post("/execute/EBM", json={"model_name": model_name, "initial_temperature": initial_temperature,
                                                  "insolation": Constants.INSOLATION_OBSERVED, "albedo": Constants.ALPHA, "tau": Constants.TAU})
        self.assertEqual(response.status_code, 400)

class TestFAIREndpoint(unittest.TestCase):
    def test_execute_Rcp_model_returns_correct_data(self):
        # Check API output for running RCP scenario returns expected data
        client = TestClient(app)
        model_name = "Arbitrary Name"
        response = client.post("/execute/FAIR/preset", json={"model_name": model_name, "rcp_scenario": 1})
        model = RcpModel(model_name, 1)
        model.run()
        simulation_data = model.get_temperature_time_data()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"model_name": model_name, "rcp_scenario": 1,
                                           "temperatures": simulation_data["temperatures"], "times": simulation_data["times"]})

    def test_execute_Rcp_model_missing_required_input(self):
        # Check API returns error if required is_rcp parameter not supplied
        client = TestClient(app)
        model_name = "Arbitrary Name"
        response = client.post("/execute/FAIR/preset", json={"model_name": model_name})
        self.assertEqual(response.status_code, 422)

    def test_execute_Rcp_model_invalid_number(self):
        # Check API output for running RCP scenario returns expected data
        client = TestClient(app)
        model_name = "Arbitrary Name"
        response = client.post("/execute/FAIR/preset", json={"model_name": model_name, "rcp_scenario": 5})
        self.assertEqual(response.status_code, 400)





if __name__ == '__main__':
    unittest.main()
