from fastapi import FastAPI, HTTPException
from models import ZeroDimensionalEnergyBalanceModel, RcpModel
from validation import EBMValidator, RcpFAIRValidator
from api_models import ZeroDimensionEBMInput, ZeroDimensionEBMResponse, FAIRPresetInput, FAIRPresetResponse

DEBUG = True

app = FastAPI()


@app.get("/")
async def root():
    # Debugging purposes
    return {"message": "Hello World"}


@app.post("/execute/EBM", response_model=ZeroDimensionEBMResponse)
async def execute_EBM(model_input: ZeroDimensionEBMInput):
    # Runs 0-dimensional energy balance model given the model name and the initial temperature in degrees C
    # Returns temperature and time as list of floats

    # Validate the data
    validator = EBMValidator(model_input)
    validation_result = validator.validate_all()
    if not validation_result["success"]:
        raise HTTPException(status_code=400, detail=validation_result["message"])

    # Create and run model
    model = ZeroDimensionalEnergyBalanceModel(name=model_input.model_name,
                                              initial_temperature=model_input.initial_temperature,
                                              insolation=model_input.insolation,
                                              albedo=model_input.albedo,
                                              tau=model_input.tau)
    model.run()

    # Get output data
    simulation_data = model.get_temperature_time_data()

    if DEBUG:
        print(simulation_data)

    # Combine input dictionary with simulation data dictionary to instantiate SimulationResponse object which is returned
    response_dictionary = model_input.dict() | simulation_data
    model_output = ZeroDimensionEBMResponse(**response_dictionary)
    return model_output


@app.post("/execute/FAIR/preset", response_model=FAIRPresetResponse)
async def execute_FAIR_preset(model_input: FAIRPresetInput):
    # Runs FAIR model with preset RCP scenario data supplied by library
    # Returns lists of temperature and time

    # Validation
    validator = RcpFAIRValidator(model_input)
    validation_result = validator.validate_all()
    if not validation_result["success"]:
        raise HTTPException(status_code=400, detail=validation_result["message"])

    # Create model and run
    model = RcpModel(name=model_input.model_name,
                     rcp_scenario=model_input.rcp_scenario)
    model.run()

    # Get temperature time data
    simulation_data = model.get_temperature_time_data()
    if DEBUG:
        print(simulation_data)

    # Combine input with simulation data (temperature-time data)
    response_dictionary = model_input.dict() | simulation_data
    model_output = FAIRPresetResponse(**response_dictionary)
    return model_output
