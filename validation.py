from typing import Callable
from api_models import ZeroDimensionEBMInput, FAIRPresetInput
from models import Constants

# Validation models

class ValidationRule:
    def __init__(self, validation_func: Callable, test_value, error_message):
        # Validation function (returns boolean value) is called on the test value
        self.validation_func = validation_func
        self.test_value = test_value
        self.error_message = error_message

    def is_valid(self):
        return self.validation_func(self.test_value)


class Validator:
    def __init__(self, rules):
        self.rules = rules  # Array of validation rules

    def validate_all(self):
        # Validate all required input fields by checking all rules are followed
        # Returns a dictionary where key success is a boolean and key message describes the failure
        for rule in self.rules:
            if not rule.is_valid():
                return {"success": False, "message": rule.error_message}
        return {"success": True, "message": None}


class EBMValidator(Validator):
    def __init__(self, model_input: ZeroDimensionEBMInput):
        rules = [
        ValidationRule(EBMValidator.check_temperature, model_input.initial_temperature,
                       "Initial temperature must be in the range -100 and 100"),
        ValidationRule(EBMValidator.check_insolation, model_input.insolation,
                       "Insolation must be in the range 170.65 and 682.6"),
        ValidationRule(EBMValidator.check_albedo, model_input.albedo, "Albedo must be in the range 0.01 and 0.99"),
        ValidationRule(EBMValidator.check_tau, model_input.tau, "Tau must be in the range 0.01 and 0.99")
        ]
        super().__init__(rules)

    @staticmethod
    def check_temperature(initial_temperature):
        # Returns true if initial temperature of model within -100 and 100 degrees celsius else false
        return -100 <= initial_temperature <= 100

    @staticmethod
    def check_insolation(insolation):
        # Returns true if solar insolation is within -50% and +100% of observed value
        return Constants.INSOLATION_OBSERVED / 2 <= insolation <= Constants.INSOLATION_OBSERVED * 2

    @staticmethod
    def check_albedo(albedo):
        # Returns true if albedo between 0.01 and 0.99
        return 0.01 <= albedo <= 0.99

    @staticmethod
    def check_tau(tau):
        # Returns true if tau is between 0.01 and 0.99
        return 0.01 <= tau <= 0.99

class RcpFAIRValidator(Validator):
    def __init__(self, model_input: FAIRPresetInput):
        rules = [
            ValidationRule(RcpFAIRValidator.check_rcp_scenario_number, model_input.rcp_scenario, "Invalid RCP scenario number chosen")
        ]
        super().__init__(rules)

    @staticmethod
    def check_rcp_scenario_number(scenario_num):
        # Must be 1 - 4 inclusive
        return True if scenario_num in range(1, 5) else False
