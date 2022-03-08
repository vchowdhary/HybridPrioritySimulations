import numpy as np
import sys
import argparse

# Basic job class
class Job():
    def __init__(self, size, arrival_time, jid, priority=1):
        self.size = size
        self.arrival_time = arrival_time
        self.priority = 1
        self.jid = jid

    def __repr__(self):
        return "Job {}, priority {}, arrived at {}, size {}".format(self.jid,
                                                                    self.priority,
                                                                    self.arrival_time,
                                                                    self.size)
# Basic server class
class Server():
    def __init__(self):
        self.job_serving = None
        self.time_depart = float('inf')

    def time_next_depart(self):
        # Time for job to depart
        return self.time_depart

    def complete(self):
        # Complete the job currently being served
        job = self.job_serving
        # Reset server to default state
        self.job_serving = None
        self.time_depart = float('inf')
        return job

    def push(self, job, time_now):
        # Push job to server and update departure time
        if job is not None and self.job_serving is None:
            self.time_depart = time_now + job.size
            self.job_serving = job

    def work(self, time_now):
        # Work left in server is just the current job
        return self.time_depart - time_now

    def num_jobs(self):
        if self.job_serving is None:
            return 0
        else:
            return 1

class FCFSQueue():
    def __init__(self):
        self.jobs_waiting = []
        self.work = 0.0

    def pop(self):
        # Pop job from queue and update current work in queue
        if len(self.jobs_waiting) == 0:
            return None
        job = self.jobs_waiting.pop(0)
        self.work -= job.size
        return job

    def push(self, job):
        self.work += job.size
        self.jobs_waiting.append(job)

    def work(self):
        return self.work

    def num_jobs(self):
        return len(self.jobs_waiting)

# Basic Poisson Arrivals
class Arrivals():
    def __init__(self, lambda_, mu):
        self.time_next_arrive = np.random.exponential(1.0/lambda_)
        self.arrival_rate = lambda_
        self.mu = mu
        self.jid = 0

    def time_next_arrive(self):
        return self.time_next_arrive

    def arrive(self):
        # New job arrives
        curr_time = self.time_next_arrive
        jid = self.jid
        next_arrival = np.random.exponential(1.0/self.arrival_rate)
        size = np.random.exponential(1.0/self.mu)

        self.jid += 1
        self.time_next_arrive += next_arrival

        return (curr_time, Job(size, curr_time, jid))


class ArrivalEvent():
    def __init__(self, time):
        self.time = time
    def __repr__(self):
        return "Arrival {}".format(self.time)


class DepartEvent():
    def __init__(self, curr_time, response_time, num_jobs_seen, job):
        self.curr_time = curr_time
        self.response_time = response_time
        self.num_jobs_seen = num_jobs_seen
        self.job = job
    def __repr__(self):
        return "Job {} departs at {}, response time {}".format(self.job.jid,
                                                               self.curr_time,
                                                               self.response_time)

class FCFSSystem():
    def __init__(self, num_runs, num_jobs_per_run, lambda_, mu):
        self.time = 0
        self.num_runs = num_runs
        self.num_jobs_per_run = num_jobs_per_run
        self.server = Server()
        self.queue = FCFSQueue()
        self.arrivals = Arrivals(lambda_, mu)

    def step(self):
        if self.server.time_next_depart() <= self.arrivals.time_next_arrive:
            # Complete the job in the server
            self.time = self.server.time_next_depart()
            completed_job = self.server.complete()

            # Pop job from queue and push to server
            new_job_to_serve = self.queue.pop()

            if new_job_to_serve is not None:
                self.server.push(new_job_to_serve, self.time)

            # Get num jobs in system
            num_jobs = self.queue.num_jobs() + self.server.num_jobs()

            return DepartEvent(self.time, self.time - completed_job.arrival_time, num_jobs, completed_job)
        # Otherwise is arrival
        self.time = self.arrivals.time_next_arrive
        _, job_arrive = self.arrivals.arrive()

        if self.server.num_jobs() == 0:
            self.server.push(job_arrive, self.time)
        else:
            self.queue.push(job_arrive)

        return ArrivalEvent(self.time)

    def simulate_run(self):
        num_completions = 0
        responses = []
        while num_completions < self.num_jobs_per_run:
            event = self.step()
            if isinstance(event, DepartEvent):
                num_completions += 1
                responses.append(event)

        response_times = [event.response_time for event in responses]
        num_jobs_seen = [event.num_jobs_seen for event in responses]

        return (sum(response_times)/len(response_times),
         sum(num_jobs_seen)/len(num_jobs_seen))

    def simulate(self):
        T_runs = []
        N_runs = []
        for i in range(self.num_runs):
            avg_response_time, avg_jobs_seen = self.simulate_run()
            T_runs.append(avg_response_time)
            N_runs.append(avg_jobs_seen)
        return T_runs, N_runs


def run_fcfs_basic(num_runs, num_jobs_per_run, lambda_, mu):
    print("Running Basic FCFS Simulation...")
    basic_system = FCFSSystem(num_runs, num_jobs_per_run, lambda_, mu)
    T_runs, N_runs = basic_system.simulate()

    ET = sum(T_runs)/len(T_runs)
    EN = sum(N_runs)/len(N_runs)
    rho = lambda_/mu

    print("Lambda: {}, mu: {}, rho: {}".format(lambda_, mu, rho))
    print("E[T]: {}, E[N]: {}".format(ET, EN))
    print("Expected E[T]: {}, Actual E[T]: {}".format(1/(mu - lambda_), ET))
    print("Expected E[N]: {}, Actual E[N]: {}".format(rho/(1-rho), EN))
    print("Little's Law holds? lambdaE[T]: {}, E[N]: {}".format(lambda_*ET, EN))


parser = argparse.ArgumentParser(description='What settings do you want to run with?')
parser.add_argument('system', metavar='S', type=int, help='What system do you want to run? \\ 0. Basic FCFS',
                    default=0)
parser.add_argument('--num_runs', metavar='R', type=int, help = 'Number of runs in simulation', default = 100)
parser.add_argument('--num_jobs_per_run', metavar='J', type=int, help = 'Number of jobs per run in simulation', default = 1000)
parser.add_argument('--lambda_', metavar='lam', type=float, help =
                    'Arrival rate', default = 8)
parser.add_argument('--mu', metavar='mu', type=float, help = 'Service rate', default = 10)


args = parser.parse_args()

FCFS = 0

if args.system == FCFS:
    run_fcfs_basic(args.num_runs, args.num_jobs_per_run, args.lambda_, args.mu)
