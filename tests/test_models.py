import unittest
from models import ZeroDimensionalEnergyBalanceModel, Constants


class TestOneDimensionalEnergyBalanceModel(unittest.TestCase):
    def test_run_output_matches_analytical_solution(self):
        # Compare analytical equilibrium temperature is nearly the same as the final temperature for the simulation
        # through using an absolute tolerance value of 0.1

        absolute_tolerance = 0.1
        equilibrium_temperature = (((1 - Constants.ALPHA) * Constants.INSOLATION_OBSERVED) / (Constants.TAU * Constants.SIGMA)) ** 0.25

        test_model = ZeroDimensionalEnergyBalanceModel("Arbitrary Name", 100)
        test_model.run()
        test_data = test_model.get_data()
        normalised_final_temperature = test_data["temperatures"][-1] + 273.15 # Converted from celsius to kelvin

        self.assertAlmostEqual(equilibrium_temperature, normalised_final_temperature, delta=absolute_tolerance)


if __name__ == '__main__':
    unittest.main()