from fastapi import FastAPI
from models import ZeroDimensionalEnergyBalanceModel
from pydantic import BaseModel


class ModelInput(BaseModel):
    model_name: str # Arbitrary name for this simulation
    initial_temperature: float # Starting temperature for this simulation


app = FastAPI()


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.post("/execute/")
async def execute(model_input: ModelInput):
    # Runs climate model given the model name and the initial temperature in degrees C
    # Returns temperature and time as list of floats
    model = ZeroDimensionalEnergyBalanceModel(model_input.model_name, model_input.initial_temperature)
    model.run()
    simulation_data = model.get_data()
    return simulation_data
