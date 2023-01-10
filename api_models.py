from pydantic import BaseModel
from typing import List

# Models for API input/output

class SimulationInput(BaseModel):
    model_name: str  # Arbitrary name for this simulation


class SimulationResponse(BaseModel):
    # Inherits from the input model as it returns this as data to be stored
    temperatures: List[float]
    times: List[float]


class ZeroDimensionEBMInput(SimulationInput):
    initial_temperature: float  # Starting temperature for this simulation
    insolation: float # Area-averaged solar radiation
    albedo: float # Proportion of light reflected from surface
    tau: float # Capacity of atmosphere to transmit radiation to space


class ZeroDimensionEBMResponse(ZeroDimensionEBMInput, SimulationResponse):
    pass


# class FAIRInput(SimulationInput):
#     is_rcp: bool # Specify if using pre-determined IPCC data
#     rcp_scenario: int | None = None # scenario choice; only required if is_rcp set to true


# class FAIRResponse(FAIRInput, SimulationResponse):
#     pass

class FAIRPresetInput(SimulationInput):
    rcp_scenario: int # scenario choice


class FAIRPresetResponse(FAIRPresetInput, SimulationResponse):
    pass
