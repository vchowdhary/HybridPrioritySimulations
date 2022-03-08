# Plan:

import heapq
import numpy as np

print("Hello")
ARRIVAL = 1
DEPARTURE = 0


def simulate(goal_num_jobs, mu, lambda_):
    def generate_arrival():
        return np.random.exponential(1.0/lambda_)

    def generate_size():
        return np.random.exponential(1.0/mu)

    first_arrival = generate_arrival()
    time = 0
    response_times = []
    num_jobs_seen = []
    num_in_system = 0
    num_completions = 0

    events = [(first_arrival, first_arrival, ARRIVAL)]

    while num_completions < goal_num_jobs:
        event = heapq.heappop(events)
        if event[2] == ARRIVAL:
            num_in_system += 1
            next_arrival = generate_arrival()
            heapq.heappush(events, (event[0] + next_arrival, event[0] +
                                    next_arrival, ARRIVAL))
            size = generate_size()
            heapq.heappush(events, (event[0] + size, event[1], DEPARTURE))
        else:
            num_in_system -= 1
            num_completions += 1
            response_times.append(event[0] - event[1])
            num_jobs_seen.append(num_in_system)


    Tavg = sum(response_times)/len(response_times)
    Navg = sum(num_jobs_seen)/len(num_jobs_seen)
    return Tavg, Navg

mu = 1
lambda_ = 0.9
rho = lambda_/mu
print(rho)
num_runs = 1000
Tens = 0
Nens = 0
for i in range(num_runs):
    res = simulate(300, mu, lambda_)
    Tens += res[0]
    Nens += res[1]
print(Tens/num_runs, Nens/num_runs, Tens/num_runs*lambda_)
