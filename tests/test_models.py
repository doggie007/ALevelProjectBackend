import unittest
from models import Constants, ZeroDimensionalEnergyBalanceModel, RcpModel
from itertools import product


class TestOneDimensionalEnergyBalanceModel(unittest.TestCase):
    def test_run_output_matches_analytical_solution(self):
        # Compare analytical equilibrium temperature is nearly the same as the final temperature for the simulation
        # through using an absolute tolerance value of 0.1

        absolute_tolerance = 0.1
        equilibrium_temperature = (((1 - Constants.ALPHA) * Constants.INSOLATION_OBSERVED) / (Constants.TAU * Constants.SIGMA)) ** 0.25

        test_model = ZeroDimensionalEnergyBalanceModel("Arbitrary Name", 100, Constants.INSOLATION_OBSERVED, Constants.ALPHA, Constants.TAU)
        test_model.run()
        test_data = test_model.get_temperature_time_data()
        normalised_final_temperature = test_data["temperatures"][-1] + 273.15 # Converted from celsius to kelvin

        self.assertAlmostEqual(equilibrium_temperature, normalised_final_temperature, delta=absolute_tolerance)

    def test_boundary_initial_temperatures_do_not_crash_EBM(self):
        # Check whether boundary initial temperature doesn't cause EBM model to fail
        boundary_initial_temperature = [-50, 100]
        for initial_temperature in boundary_initial_temperature:
            try:
                test_model = ZeroDimensionalEnergyBalanceModel("Arbitrary Name", 30.0, Constants.INSOLATION_OBSERVED, Constants.ALPHA, Constants.TAU)
                test_model.run()
            except:
                self.assertTrue(False, msg=f"Fails at temperature={initial_temperature}")
                return
        self.assertTrue(True)


    def test_boundary_environmental_constants_do_not_crash_EBM(self):
        # Cycle through all the possible permutations of boundary environmental constants
        # ensuring they do not cause EBM model to fail
        # Create list of all permutations
        boundary_insolation = [Constants.INSOLATION_OBSERVED / 2, Constants.INSOLATION_OBSERVED * 2]
        boundary_albedo = [0.01, 0.99]
        boundary_tau = [0.01, 0.99]
        permutations = product(boundary_insolation, boundary_albedo, boundary_tau)

        for (curr_insolation, curr_albedo, curr_tau) in permutations:
            try:
                test_model = ZeroDimensionalEnergyBalanceModel("Arbitrary Name", 30.0, curr_insolation,
                                                               curr_albedo, curr_tau)
                test_model.run()
            except:
                self.assertTrue(False, msg=f"Fails at insolation={curr_insolation}, albedo={curr_albedo}, tau={curr_tau}")
                return
        self.assertTrue(True)

class TestFAIRModel(unittest.TestCase):
    def test_all_rcp_scenarios_run_successfully(self):
        try:
            for scenario in range(1, 5):
                model = RcpModel(name="Arbitrary", rcp_scenario=scenario)
                model.run()
        except:
            self.assertTrue(False)
        self.assertTrue(True)



if __name__ == '__main__':
    unittest.main()
