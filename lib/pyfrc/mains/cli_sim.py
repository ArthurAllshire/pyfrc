
import inspect
import json
from os.path import abspath, dirname, exists, join

from ..test_support import pyfrc_fake_hooks

from .. import sim
#from ..sim.field import elements

import hal_impl.functions

class PyFrcSim:
    """
        Executes the robot code using the low fidelity simulator and shows
        a tk-based GUI to control the simulation 
    """

    def __init__(self, parser):
        pass

    def run(self, options, robot_class, **static_options):
        
        from .. import config
        config.mode = 'sim'
        
        # load the config json file
        robot_file = abspath(inspect.getfile(robot_class))
        robot_path = dirname(robot_file)
        sim_path = join(robot_path, 'sim')
        config_file = join(sim_path, 'config.json')
        
        if exists(config_file):
            with open(config_file, 'r') as fp:
                config_obj = json.load(fp)
        else:
            config_obj = {}
        
        # setup defaults
        config_obj.setdefault('pyfrc', {})
        
        config_obj['pyfrc'].setdefault('field', {})
        
        config_obj['pyfrc'].setdefault('analog', {})
        config_obj['pyfrc'].setdefault('CAN', {})
        config_obj['pyfrc'].setdefault('dio', {})
        config_obj['pyfrc'].setdefault('pwm', {})
        config_obj['pyfrc'].setdefault('relay', {})
        config_obj['pyfrc'].setdefault('solenoid', {})
        
        config_obj['pyfrc'].setdefault('joysticks', {})
        for i in range(6):
            config_obj['pyfrc']['joysticks'].setdefault(str(i), {})
            config_obj['pyfrc']['joysticks'][str(i)].setdefault('axes', {})
            config_obj['pyfrc']['joysticks'][str(i)].setdefault('buttons', {})
            
            config_obj['pyfrc']['joysticks'][str(i)]['buttons'].setdefault("1", "Trigger")
            config_obj['pyfrc']['joysticks'][str(i)]['buttons'].setdefault("2", "Top")
        
        fake_time = sim.FakeRealTime()
        hal_impl.functions.hooks = pyfrc_fake_hooks.PyFrcFakeHooks(fake_time)
        hal_impl.functions.reset_hal()
    
        sim_manager = sim.SimManager()
        
        controller = sim.RobotController(robot_class, fake_time)
        #if controller.has_physics():
        #    robot_element = sim.RobotElement(controller, px_per_ft)
        #else:
        #    center = (field_size[0]*px_per_ft/2, field_size[1]*px_per_ft/2)
        #    robot_element = elements.TextElement("Physics not setup", center, 0, '#000', 12)
        
        sim_manager.add_robot(controller)
        
        controller.run()
        controller.wait_for_robotinit()
        
        ui = sim.SimUI(sim_manager, fake_time, config_obj)
        #ui.field.add_moving_element(robot_element)
        ui.run()
    
        # once it has finished, try to shut the robot down
        # -> if it can't, then the user messed up
        if not controller.stop():
            print('Error: could not stop the robot code! Check your code')
    
        return 0
