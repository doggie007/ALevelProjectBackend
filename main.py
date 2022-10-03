from fastapi import FastAPI
from models import ZeroDimensionalEnergyBalanceModel
from pydantic import BaseModel
from typing import List


class ModelInput(BaseModel):
    model_name: str # Arbitrary name for this simulation
    initial_temperature: float # Starting temperature for this simulation

class ModelOutput(BaseModel):
    temperatures: List[float]
    times: List[float]

app = FastAPI()


@app.get("/")
async def root():
    # Debugging purposes
    return {"message": "Hello World"}

@app.post("/execute/", response_model=ModelOutput)
async def execute(model_input: ModelInput):
    # Runs climate model given the model name and the initial temperature in degrees C
    # Returns temperature and time as list of floats
    model = ZeroDimensionalEnergyBalanceModel(model_input.model_name, model_input.initial_temperature)
    model.run()
    simulation_data = model.get_data()
    print(simulation_data)
    return simulation_data
