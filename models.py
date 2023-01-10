import matplotlib.pyplot as plt
import climlab
import fair
from fair.RCPs import rcp26, rcp45, rcp60, rcp85

# Climate models

class Constants:
    # Define observed real-world constants
    INSOLATION_OBSERVED = 341.3  # area-averaged incoming solar radiation in W/m2
    OLR_OBSERVED = 238.5  # Outgoing longwave radiation in W/m2
    SIGMA = 5.67E-8  # Stefan-Boltzmann constant
    T_OBSERVED = 288.  # global average surface temperature
    TAU = OLR_OBSERVED / SIGMA / T_OBSERVED ** 4  # tuned value of transmissivity to model greenhouse model
    F_REFLECTED = 101.9  # reflected shortwave flux in W/m2
    ALPHA = F_REFLECTED / INSOLATION_OBSERVED  # global albedo
    ASR_OBSERVED = INSOLATION_OBSERVED - F_REFLECTED  # Absorbed shortwave radiation in W/m2


class History:
    # Stores all the information about the output data from running the climate simulation
    def __init__(self):
        self.temperature = []  # in degrees Celsius
        self.time = []  # in days

    def record(self, temperature, current_time):
        # Stores the data of one timestep
        # params state: current temperature in degrees C
        # params current_time: current time elapsed from start given in years
        self.temperature.append(temperature)
        self.time.append(current_time)

    def record_all(self, temperatures, times):
        # Stores the temperature and year data for all supplied timesteps
        self.temperature.extend(temperatures)
        self.time.extend(times)

    def visualise(self):
        # Plots temperature vs time graph (for debugging purposes)
        plt.plot(self.time, self.temperature)
        plt.xlabel("Time (years)")
        plt.ylabel("Temperature ($^\circ$C)")
        plt.show()


class Simulation:
    # Base class for the climate models to store basic information about the simulation
    def __init__(self, name, initial_temperature):
        self.name = name
        self.initial_temperature = initial_temperature
        self.history = History()

    def show_history(self):
        # Visualise temperature vs time so far
        self.history.visualise()

    def get_temperature_time_data(self):
        # Dictionary of temperature and time for ease of converting to response object
        return {"temperatures": self.history.temperature, "times": self.history.time}


class ZeroDimensionalEnergyBalanceModel(Simulation):
    # 0-dimensional energy balance model
    def __init__(self, name, initial_temperature, insolation, albedo, tau):
        # params name: name of simulation
        # params initial_temperature: temperature in degrees C
        super().__init__(name, initial_temperature)
        self.insolation = insolation
        self.albedo = albedo
        self.tau = tau

    def run(self):
        # Sets up climate model and runs it in accordance with time
        # Run time is currently fixed at 50 years / 600 months
        # Timestep is currently fixed at 1 month
        delta_t = 60. * 60. * 24. * 30.  # time step of 1 month
        time_steps = 600 # 600 iterations

        # Initialising components of environment and defining the interactions between
        # Create zero-dimensional domain
        state = climlab.surface_state(
            num_lat=1,  # a single point
            water_depth=100.,  # 100 meters slab of water (sets the heat capacity)
            T0=self.initial_temperature, # global mean initial temperature
            T2=0, # no gradient in initial temperature
        )

        # Longwave radiation process (outgoing)
        olr = climlab.radiation.Boltzmann(name='OutgoingLongwave',
                                          state=state,
                                          tau=self.tau,  # transmissivity of atmosphere
                                          eps=1.,   # emissivity of surface of planet
                                          timestep=delta_t)

        # Shortwave radiation process (incoming)
        asr = climlab.radiation.SimpleAbsorbedShortwave(name='AbsorbedShortwave',
                                                        state=state,
                                                        insolation=self.insolation,
                                                        albedo=self.albedo,
                                                        timestep=delta_t)

        # Couple time-dependent processes to form EBM
        ebm = climlab.couple([olr, asr])
        ebm.name = self.name

        # Running the simulation
        # step forward in time to run climate model
        self.history.record(self.initial_temperature, 0) # Record initial values
        for step_num in range(1, time_steps+1):
            ebm.step_forward()
            # Only record every year
            if step_num % 12 == 0:
                current_temperature = state.Ts[0][0]
                current_year = step_num * delta_t // (60.0 * 60.0 * 24 * 30 * 12) # Convert from seconds to years
                self.history.record(current_temperature, current_year)



class FAIRModel(Simulation):
    # Finite Amplitude Impulse-Response model
    # Carbon-cycle based model based on changes of CO2 Emissions

    def __init__(self, name):
        # Set initial temperature to 0.0 as investigating change from pre-industrial ages
        super().__init__(name=name, initial_temperature=0.0)


class RcpModel(FAIRModel):
    # Runs FAIR model using pre-set RCP projection data

    # Mapping of RCP scenario number to RCP scenario dataset
    rcp_scenario_dict = {1: rcp26,
                         2: rcp45,
                         3: rcp60,
                         4: rcp85}

    def __init__(self, name, rcp_scenario):
        super().__init__(name)
        self.rcp_scenario = self.rcp_scenario_dict[rcp_scenario]

    def run(self):
        # Run the model using set RCP dataset
        co2_concentrations, total_radioactive_forcing, temperatures = fair.forward.fair_scm(emissions=self.rcp_scenario.Emissions.emissions)
        # Record all temperature data
        self.history.record_all(temperatures, self.rcp_scenario.Emissions.year)
