from fastapi import FastAPI, HTTPException
from fastapi.exceptions import RequestValidationError
from models import ZeroDimensionalEnergyBalanceModel
from pydantic import BaseModel
from typing import List

DEBUG = False

class ModelInput(BaseModel):
    model_name: str # Arbitrary name for this simulation
    initial_temperature: float # Starting temperature for this simulation

class ModelOutput(BaseModel):
    temperatures: List[float]
    times: List[float]

class Validator:
    @staticmethod
    def validate(model_input: ModelInput):
        # Validate all required input fields
        if not Validator.check_temperature(model_input.initial_temperature):
            return {"success": False, "message": "Initial temperature must be in the range -100 and 100"}
        return {"success": True, "message": None}

    @staticmethod
    def check_temperature(initial_temperature):
        # Returns true if initial temperature of model within -100 and 100 degrees celsius else false
        return -100 <= initial_temperature <= 100


app = FastAPI()


@app.get("/")
async def root():
    # Debugging purposes
    return {"message": "Hello World"}

@app.post("/execute/", response_model=ModelOutput)
async def execute(model_input: ModelInput):
    # Runs climate model given the model name and the initial temperature in degrees C
    # Returns temperature and time as list of floats

    # Validate the data
    validation_result = Validator.validate(model_input)
    if not validation_result["success"]:
        raise HTTPException(status_code=400, detail=validation_result["message"])

    model = ZeroDimensionalEnergyBalanceModel(model_input.model_name, model_input.initial_temperature)
    model.run()
    simulation_data = model.get_data()
    if DEBUG:
        print(simulation_data)
    return simulation_data
