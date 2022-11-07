from fastapi import FastAPI, HTTPException
from fastapi.exceptions import RequestValidationError
from models import ZeroDimensionalEnergyBalanceModel
from pydantic import BaseModel
from typing import List
from models import Constants


DEBUG = True


class SimulationInput(BaseModel):
    model_name: str  # Arbitrary name for this simulation
    initial_temperature: float  # Starting temperature for this simulation
    insolation: float # Area-averaged solar radiation
    albedo: float # Proportion of light reflected from surface
    tau: float # Capacity of atmosphere to transmit radiation to space


class SimulationResponse(SimulationInput):
    # Inherits from the input model as it returns this as data to be stored
    temperatures: List[float]
    times: List[float]


class Validator:
    @staticmethod
    def validate(model_input: SimulationInput):
        # Validate all required input fields

        # Return dictionary where key success is a boolean and key message describes the failure
        if not Validator.check_temperature(model_input.initial_temperature):
            return {"success": False, "message": "Initial temperature must be in the range -100 and 100"}
        elif not Validator.check_insolation(model_input.insolation):
            return {"success": False, "message": "Insolation must be in the range 170.65 and 682.6"}
        elif not Validator.check_albedo(model_input.albedo):
            return {"success": False, "message": "Albedo must be in the range 0.01 and 0.99"}
        elif not Validator.check_tau(model_input.tau):
            return {"success": False, "message": "Tau must be in the range 0.01 and 0.99"}
        else:
            return {"success": True, "message": None}

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


print(Constants.ALPHA, Constants.TAU, Constants.INSOLATION_OBSERVED)

app = FastAPI()


@app.get("/")
async def root():
    # Debugging purposes
    return {"message": "Hello World"}


@app.post("/execute/", response_model=SimulationResponse)
async def execute(model_input: SimulationInput):
    # Runs climate model given the model name and the initial temperature in degrees C
    # Returns temperature and time as list of floats

    # Validate the data
    validation_result = Validator.validate(model_input)
    if not validation_result["success"]:
        raise HTTPException(status_code=400, detail=validation_result["message"])

    # Create model, run model, then get output data
    model = ZeroDimensionalEnergyBalanceModel(name=model_input.model_name,
                                              initial_temperature=model_input.initial_temperature,
                                              insolation=model_input.insolation,
                                              albedo=model_input.albedo,
                                              tau=model_input.tau)
    model.run()
    simulation_data = model.get_data()
    if DEBUG:
        print(simulation_data["temperatures"])
        print(simulation_data["times"])
        print(len(simulation_data["temperatures"]))

    # Combine input dictionary with simulation data dictionary to instantiate SimulationResponse object
    # which is returned
    response_dictionary = model_input.dict() | simulation_data
    model_output = SimulationResponse(**response_dictionary)
    return model_output
