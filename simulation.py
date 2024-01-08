import argparse
import numpy as np

cycle_times = [0.25, 0.6, 0.32, 0.25]

parser = argparse.ArgumentParser()
parser.add_argument('-c', '--cycle_times', nargs='*', default=[], type=float, help='Machines cycle times')
parser.add_argument('-s', '--simulation_time', default=1440, type=float, help='Simulation time')
args = parser.parse_args()
parsed_simulation_time = args.simulation_time
parsed_cycle_times = args.cycle_times

if len(parsed_cycle_times) == len(cycle_times):
    cycle_times = parsed_cycle_times

def execute_simulation(cycle_times, parsed_simulation_time):
    from simantha import System, Machine, Source, Buffer, Sink
    S = Source()
    sink = Sink()
    M1 = Machine(name='M1', cycle_time=dict(constant=cycle_times[0]))
    M2 = Machine(name='M2', cycle_time=dict(constant=cycle_times[1]))
    M3 = Machine(name='M3', cycle_time=dict(constant=cycle_times[2]))
    M4 = Machine(name='M4', cycle_time=dict(constant=cycle_times[3]))

    Queue_M1_M2 = Buffer(name='Queue_M1_M2', capacity=10)
    Queue_M2_M3 = Buffer(name='Queue_M2_M3', capacity=10)
    Queue_M3_M4 = Buffer(name='Queue_M3_M4', capacity=10)

    S.define_routing(downstream=[M1])

    M1.define_routing(upstream=[S], downstream=[Queue_M1_M2])
    M2.define_routing(upstream=[Queue_M1_M2], downstream=[Queue_M2_M3])
    M3.define_routing(upstream=[Queue_M2_M3], downstream=[Queue_M3_M4])
    M4.define_routing(upstream=[Queue_M3_M4], downstream=[sink])

    Queue_M1_M2.define_routing(upstream=[M1], downstream=[M2])
    Queue_M2_M3.define_routing(upstream=[M2], downstream=[M3])
    Queue_M3_M4.define_routing(upstream=[M3], downstream=[M4])

    objects = [S, sink] + [M1, M2, M3, M4, Queue_M1_M2, Queue_M2_M3, Queue_M3_M4]
    system = System(objects=objects)
    system.simulate(simulation_time=parsed_simulation_time, verbose=False)

    return parsed_simulation_time / sum(sink.level for sink in system.sinks)

if __name__ == '__main__':
    print('Throughput time: ', execute_simulation(cycle_times, parsed_simulation_time))
