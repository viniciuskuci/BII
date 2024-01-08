import numpy as np
import os
import sys

class SIMULATE:
    #the output is the throughput time of the system

    def __init__(self):
        
        self.cycle_times = []
        self.machine_info = {}
        self.simulation_time = 1440
    
    def schedule(self, event_name, event_value, simulation_time, window, 
                    station_1, station_2, station_3, station_4):
        
        if event_name == 'INIT':
            self.simulation_time = simulation_time
            current_dir = os.getcwd()
            
            try:
                os.remove(os.path.join(current_dir,'simulation.py'))
                print("simulation.py file removed.")
            except:
                pass

            return [event_value, None, None, None]
        
        elif event_name == 'RUN':
            input = [station_1, station_2, station_3, station_4]
            
            for i in range(len(input)):
                if i >= len(self.cycle_times):
                    self.cycle_times.append([])
                if input[i] != None:
                    self.cycle_times[i].append(input[i])
           
            for i in range(len(self.cycle_times)):
                if  len(self.cycle_times[i]) == window:
                    mean = round(np.mean(self.cycle_times[i]), 2)
                    st_dev = round(np.std(self.cycle_times[i]), 2)
                    self.machine_info["M"+str(i+1)] = [mean, st_dev]
                    self.cycle_times[i].pop(0)
            
            #generate_simulation_file method needs the machines to be in order
            self.machine_info = dict(sorted(self.machine_info.items()))             
            
            if len(self.machine_info) >= 2:
                current_dir = os.getcwd()
                try:
                    file = open(os.path.join(current_dir,'simulation.py'), "r")
                    file.close()
                except:
                    self.generate_simulation_file(self.machine_info, current_dir)
            return [None, event_value, None, None]

        elif event_name == 'RUN_SIM':
            current_dir = os.getcwd()
            try:
                sys.path.append(current_dir)
                import simulation
                print(self.machine_info)
                print("Running simulation...")
                machine_cycle_times = [i[0] for i in self.machine_info.values()] #only considering the mean
                throughput_time = simulation.execute_simulation(machine_cycle_times, self.simulation_time)
                return [None, None, event_value, throughput_time]
            except:
                print("Unexpected error:", sys.exc_info())
                return [None, None, event_value, None]
               
        return [None, event_value, None]



    @staticmethod 
    def generate_simulation_file(machines_dict, dir):
        print("Generating simulation file...")
        machine_names = list(machines_dict.keys())
        machine_cycle_times = [i[0] for i in machines_dict.values()] #only considering the mean
        file = open(os.path.join(dir,'simulation.py'), "w")

        file.write("import argparse\n")
        file.write("import numpy as np\n")
        file.write("\n")
        file.write("cycle_times = [" + ', '.join(map(str, machine_cycle_times)) + "]\n") 
        file.write("\n")   
        file.write("parser = argparse.ArgumentParser()\n")
        file.write("parser.add_argument('-c', '--cycle_times', nargs='*', default=[], type=float, help='Machines cycle times')\n")
        file.write("parser.add_argument('-s', '--simulation_time', default=1440, type=float, help='Simulation time')\n")
        file.write("args = parser.parse_args()\n")
        file.write("parsed_simulation_time = args.simulation_time\n")
        file.write("parsed_cycle_times = args.cycle_times\n")
        file.write("\n")
        file.write("if len(parsed_cycle_times) == len(cycle_times):\n")
        file.write("    cycle_times = parsed_cycle_times\n")
        file.write("\n")
        file.write("def execute_simulation(cycle_times, parsed_simulation_time):\n")
        file.write("    from simantha import System, Machine, Source, Buffer, Sink\n")
        file.write("    S = Source()\n")
        file.write("    sink = Sink()\n")

        for i in range(len(machine_names)):
            file.write("    M"+str(i+1)+" = Machine(name='"+machine_names[i]+"', cycle_time=dict(constant=cycle_times["+str(i)+"]))\n")
        file.write("\n")
        for i in range(len(machine_names)-1):
            file.write("    Queue_"+machine_names[i]+"_"+machine_names[i+1]+" = Buffer(name='Queue_"+machine_names[i]+"_"+machine_names[i+1]+"', capacity=10)\n")
        file.write("\n")
        file.write("    S.define_routing(downstream=[M1])\n")
        file.write("\n")

        for i in range(len(machine_names)):
            if i == 0:
                file.write("    M"+str(i+1)+".define_routing(upstream=[S], downstream=[Queue_"+machine_names[i]+"_"+machine_names[i+1]+"])\n")
            elif i == len(machine_names)-1:
                file.write("    M"+str(i+1)+".define_routing(upstream=[Queue_"+machine_names[i-1]+"_"+machine_names[i]+"], downstream=[sink])\n")
            else:
                file.write("    M"+str(i+1)+".define_routing(upstream=[Queue_"+machine_names[i-1]+"_"+machine_names[i]+"], downstream=[Queue_"+machine_names[i]+"_"+machine_names[i+1]+"])\n")
        file.write("\n")

        for i in range(len(machine_names)-1):
            file.write("    Queue_"+machine_names[i]+"_"+machine_names[i+1]+".define_routing(upstream=[M"+str(i+1)+"], downstream=[M"+str(i+2)+"])\n")
        file.write("\n")
        file.write("    objects = [S, sink] + [")

        for i in range(len(machine_names)):
            if i == len(machine_names)-1:
                file.write("M"+str(i+1))
            else:
                file.write("M"+str(i+1)+", ")
        
        for i in range(len(machine_names)-1):  
            file.write(", Queue_"+machine_names[i]+"_"+machine_names[i+1])
        file.write("]\n")
        file.write("    system = System(objects=objects)\n")
        file.write("    system.simulate(simulation_time=parsed_simulation_time, verbose=False)\n")
        file.write("\n")
        file.write("    return parsed_simulation_time / sum(sink.level for sink in system.sinks)\n")
        file.write("\n")
        file.write("if __name__ == '__main__':\n")
        file.write("    print('Throughput time: ', execute_simulation(cycle_times, parsed_simulation_time))\n")
        file.close()

    
#test:
        
"""

a = SIMULATE()
b = a.schedule('INIT', 0, 1440, 4, 0.25, 0.6, 0.32, 0.25)
b = a.schedule('RUN', 0, 1440, 4, 0.25, 0.6, 0.32, 0.25)
b = a.schedule('RUN', 0, 1440, 4, 0.25, 0.6, 0.32, 0.25)
b = a.schedule('RUN', 0, 1440, 4, 0.25, 0.6, 0.32, 0.25)
b = a.schedule('RUN', 0, 1440, 4, 0.25, 0.6, 0.32, 0.25)
b = a.schedule('RUN_SIM', 0, 1440, 4, 0.25, 0.6, 0.32, 0.25)
print(b)

"""

	