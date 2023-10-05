from equipment import Equity, Eload, PSU
from time import sleep

class PerformanceTest:

    def __init__(self) -> None:
        """
        Initializes the PerformanceTest class.
        """
        self._id = 1000
        self._name = 'Load Transient'
        self._description = 'None'
        self._state = 'START'
        self._sleep_time = 0.1
        self._temperature_step = 0

        # Importing all modules:
        self.equity = Equity()
        self.eload = Eload()
        self.psu = PSU()

        # Configuring functions:
        self._configure_eload()
        self._configure_equity()
        self._configure_psu()

        # Configuring temperature list:
        self._temperature = [-10.0, 25.0, 85.0]
        # [0.0, 25.0, -5.0]

    def _run_test(self):
        """
         Main function of the test code that executes a series of steps in this test simulation.
         """
        
        # State control code. 
        if self._state == 'START':
            # Initial test setup:
            self._current_temperature = self._temperature[self._temperature_step]

            if not 0 <= self._current_temperature <= 60:
                raise ValueError('Temperature range error!')

            # Setting stabilization temperature time
            self._stabilization_temperature_time = 40 * 60

            if not 0 <= self._stabilization_temperature_time <= 3600:
                raise ValueError('Stabilization temperature time range error')
            
            # Setting voltage C
            self._voltage_C = 120.0

            # Initial electric current
            self._initial_current = 3.0

            if not 0 <= self._initial_current <= 5:
                raise ValueError('Initial electric current range error')
            
            assert type(self._initial_current) is float

            # Final current
            self._final_current = 6.0
            if not 1 <= self._final_current <= 10:
                raise ValueError('Final electric current range error')
            
            assert type(self._final_current) is float
            
            # Setting voltage X
            self._voltage_X = 20.0

            self.eload.write(f'VOLT {self._voltage_X}')
            self._state = 'CONFIGURE_EQUITY'

        elif self._state == 'CONFIGURE_EQUITY':
            # Setting actual current
            self._actual_current = self._initial_current

            self.equity.set_temperature(self._current_temperature)

            while self._current_temperature != self.equity.get_temperature():
                sleep(1)
            
            #sleep(self._stabilization_temperature_time)
            self._state = 'CONFIGURE_PSU'

        elif self._state == 'CONFIGURE_PSU':
            self.psu.set_voltage(self._voltage_X)
            sleep(1)

            self._state = 'CONFIGURE_ELOAD'

        elif self._state == 'CONFIGURE_ELOAD':
            self.eload.write(f'CURR {self._actual_current}')
            sleep(1)
            self._state = 'SHOW_OUTPUT'
        
        elif self._state == 'SHOW_OUTPUT':
            self._output_power = float(self.eload.query("MEAS:POW?"))

            print(f'ELOAD | Current Electric Current:{self.eload.query("MEAS:CURR?")} A')
            print(f'ELOAD | Current Electric Voltage: {self.eload.query("MEAS:VOLT?")} V')

            print(f'PSU | Current Electric Current: {self.psu.get_current()} A')
            print(f'PSU | Current Electric Voltage: {self.psu.get_voltage()} V')

            print(f'ELOAD Actual output power: {self._output_power}')
 

            if self._output_power >= self._voltage_X:
                self._state = 'END'
                
            else:
                self._state = 'CONFIGURE_ELOAD'

            self._state = 'VERIFY_TEMPERATURE_STEP'

        elif self._state == 'VERIFY_TEMPERATURE_STEP':
            self._temperature_step += 1
            if self._temperature_step < len(self._temperature):
                self._current_temperature = self._temperature[self._temperature_step]
                self._state = 'START'
            else:
                self._state = 'END'

        elif self._state == 'END':
            self.psu.set_voltage(0)
            self.eload.write('CURR 0')
            self.eload.write('VOLT 0')
            self._stop_flag = True

        else:
            raise Exception('Invalid FM status')

    def _configure_eload(self):
        """
        Puts the initial Eload configuration.
        """
        self.eload.write('CURR 0')

    def _configure_equity(self):
        """
        Puts the initial Equity configuration. 
        """
        self.equity.set_temperature(25.0)

    def _configure_psu(self):
        """
         Puts the initial PSU configuration.
         """
        self.psu.set_voltage(0.0)

    def _generate_report(self):
        pass

    def run_test(self):
        """
        Main function to run the simulation.
        """

        self._stop_flag = False
        while not self._stop_flag:
            self._run_test()
            sleep(self._sleep_time)
        print('The tests were completed successfully!')

performance_test = PerformanceTest()
performance_test.run_test()