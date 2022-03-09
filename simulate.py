import numpy as np
import sys
import argparse

# Basic job class
class Job():
    def __init__(self, size, arrival_time, jid, priority=1):
        self.size = size
        self.arrival_time = arrival_time
        self.priority = priority
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

class PriorityArrivals():
    def __init__(self, lambda1, lambda2, mu1, mu2):
        lambda_ = lambda1 + lambda2
        self.time_next_arrive = np.random.exponential(1.0/lambda_)
        self.is_class_1_prob = lambda1/lambda_
        self.arrival_rate = lambda_
        self.mu1 = mu1
        self.mu2 = mu2
        self.jid = 0

    def time_next_arrive(self):
        return self.time_next_arrive

    def arrive(self):
        # New job arrives
        curr_time = self.time_next_arrive

        # Generate next arrival time
        next_arrival = np.random.exponential(1.0/self.arrival_rate)

        # Generate this new job's information
        jid = self.jid
        is_class_1 = np.random.binomial(1, self.is_class_1_prob)

        # Update info for next arrival
        self.jid += 1
        self.time_next_arrive += next_arrival

        # Create and return new job
        new_job_class = 1
        if is_class_1 == 1:
            new_job_class = 1
            size = np.random.exponential(1.0/self.mu1)
        else:
            new_job_class = 2
            size = np.random.exponential(1.0/self.mu2)

        new_job = Job(size, curr_time, jid, new_job_class)
        return (curr_time, new_job)

class ArrivalEvent():
    def __init__(self, time):
        self.time = time
    def __repr__(self):
        return "Arrival {}".format(self.time)

class PriorityArrivalEvent():
    def __init__(self, time, num1_jobs, num2_jobs):
        self.time = time
        self.num1_jobs_seen = num1_jobs
        self.num2_jobs_seen = num2_jobs
    def __repr__(self):
        return "Arrival at {}, num 1 jobs = {}, num2 jobs = {}".format(self.time, self.num1_jobs_seen, self.num2_jobs_seen)


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

class PriorityDepartEvent():
    def __init__(self, curr_time, response_time, num1_jobs_seen, num2_jobs_seen, job):
        self.curr_time = curr_time
        self.response_time = response_time
        self.num1_jobs_seen = num1_jobs_seen
        self.num2_jobs_seen = num2_jobs_seen
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

class NPPrioritySystem():
    def __init__(self, num_runs, num_jobs_per_run, lambda1, lambda2, mu1, mu2):
        self.time = 0
        self.num_runs = num_runs
        self.num_jobs_per_run = num_jobs_per_run
        self.server = Server()
        self.queueA = FCFSQueue()
        self.queueB = FCFSQueue()
        self.arrivals = PriorityArrivals(lambda1, lambda2, mu1, mu2)

    def step(self):
        #print("Next depart: {}, Next arrive: {}".format(self.server.time_depart, self.arrivals.time_next_arrive))
        if self.server.time_next_depart() <= self.arrivals.time_next_arrive:
            # Complete the job in the server

            # Get num jobs in system
#            if self.server.job_serving is not None and self.server.job_serving.priority == 1:
#                num1_jobs_in_server = 1
#            else:
#                num1_jobs_in_server = 0

#            if self.server.job_serving is not None and self.server.job_serving.priority == 2:
#                num2_jobs_in_server = 1
#            else:
#                num2_jobs_in_server = 0

            num1_jobs = self.queueA.num_jobs()
            num2_jobs = self.queueB.num_jobs()

            self.time = self.server.time_next_depart()
            completed_job = self.server.complete()

            # Pop job from queue and push to server
            if (self.queueA.num_jobs() != 0):
                new_job_to_serve = self.queueA.pop()
            elif (self.queueB.num_jobs() != 0):
                new_job_to_serve = self.queueB.pop()
            else:
                new_job_to_serve = None

            if new_job_to_serve is not None:
                self.server.push(new_job_to_serve, self.time)

            return PriorityDepartEvent(self.time, self.time -
                                       completed_job.arrival_time, num1_jobs,
                                       num2_jobs, completed_job)
        # Otherwise is arrival
        self.time = self.arrivals.time_next_arrive
        _, job_arrive = self.arrivals.arrive()

        #print(job_arrive)
        #print("Server busy?", self.server.num_jobs(), self.queueA.num_jobs(), self.queueB.num_jobs())
        if self.server.num_jobs() == 0:
            if job_arrive.priority == 1 and self.queueA.num_jobs() == 0:
                self.server.push(job_arrive, self.time)
            if job_arrive.priority == 2 and self.queueA.num_jobs() == 0 and self.queueB.num_jobs() == 0:
                self.server.push(job_arrive, self.time)
        else:
            if job_arrive.priority == 1:
                self.queueA.push(job_arrive)
            else:
                self.queueB.push(job_arrive)

        num1_jobs = self.queueA.num_jobs()
        num2_jobs = self.queueB.num_jobs()

        return PriorityArrivalEvent(self.time, num1_jobs, num2_jobs)

    def simulate_run(self):
        num_completions = 0
        responses = []
        arrivals = []
        while num_completions < self.num_jobs_per_run:
            event = self.step()
            if isinstance(event, PriorityDepartEvent):
                #print("Departure:", event.job)
                num_completions += 1
                responses.append(event)
            else:
                arrivals.append(event)

        response1_times = [event.response_time for event in responses if
                           event.job.priority == 1]
        response2_times = [event.response_time for event in responses if
                           event.job.priority == 2]
        num_jobs1_seen = [event.num1_jobs_seen for event in arrivals]
        num_jobs2_seen = [event.num2_jobs_seen for event in arrivals]

        T1 = 0 if len(response1_times) == 0 else sum(response1_times)/len(response1_times)
        T2 = 0 if len(response2_times) == 0 else sum(response2_times)/len(response2_times)
        N1 = 0 if len(num_jobs1_seen) == 0 else sum(num_jobs1_seen)/len(num_jobs1_seen)
        N2 = 0 if len(num_jobs2_seen) == 0 else sum(num_jobs2_seen)/len(num_jobs2_seen)

        return (T1, T2, N1, N2)
    def simulate(self):
        t1_runs = []
        t2_runs = []
        n1_runs = []
        n2_runs = []
        for i in range(self.num_runs):
            avg_response1_time, avg_response2_time, avg_jobs1_seen, avg_jobs2_seen = self.simulate_run()
            t1_runs.append(avg_response1_time)
            t2_runs.append(avg_response2_time)
            n1_runs.append(avg_jobs1_seen)
            n2_runs.append(avg_jobs2_seen)
        return t1_runs, t2_runs, n1_runs, n2_runs


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


def run_np_basic(num_runs, num_jobs_per_run, lambda1, lambda2, mu1, mu2):
    print("Running Basic NonPreemptive Simulation...")
    basic_system = NPPrioritySystem(num_runs, num_jobs_per_run, lambda1, lambda2, mu1, mu2)
    T1_runs, T2_runs, N1_runs, N2_runs = basic_system.simulate()

    ET1 = sum(T1_runs)/len(T1_runs)
    ET2 = sum(T2_runs)/len(T2_runs)

    EN1 = sum(N1_runs)/len(N1_runs)
    EN2 = sum(N2_runs)/len(N2_runs)

    rho1 = lambda1/mu1
    rho2 = lambda2/mu2
    rho = rho1 + rho2

    lambda_ = lambda1 + lambda2
    Se = lambda1/lambda_ * 1/mu1 + lambda2/lambda_ * 1/mu2

    print("Se: {}".format(Se))

    ET = lambda1/lambda_*ET1 + lambda2/lambda_*ET2
    EN = EN1 + EN2

    print("Lambda1: {}, lambda2: {}, mu1: {}, mu2: {}, rho1: {}, rho2: {}".format(lambda1, lambda2, mu1, mu2, rho1, rho2))
    print("E[T1]: {}, E[N1]: {}".format(ET1, EN1))
    print("E[T2]: {}, E[N2]: {}".format(ET2, EN2))
    print("Expected E[T1]: {}, Actual E[T1]: {}".format(rho*Se/(1-rho1) + 1/mu1, ET1))
    print("Expected E[T2]: {}, Actual E[T2]: {}".format(rho*Se/((1-rho)*(1-rho1)) + 1/mu2, ET2))
    print("Little's Law holds for class 1? lambda1E[T1]: {}, E[N1]: {}".format(lambda1*ET1, EN1))
    print("Little's Law holds for class 2? lambda2E[T2]: {}, E[N2]: {}".format(lambda2*ET2, EN2))
    print("Little's Law holds overall? lambdaE[T]: {}, E[N]: {}".format(lambda_*ET, EN))

parser = argparse.ArgumentParser(description='What settings do you want to run with?')
parser.add_argument('system', metavar='S', type=int, help='What system do you want to run? \\ 0. Basic FCFS',
                    default=0)
parser.add_argument('--num_runs', metavar='R', type=int, help = 'Number of runs in simulation', default = 100)
parser.add_argument('--num_jobs_per_run', metavar='J', type=int, help = 'Number of jobs per run in simulation', default = 1000)
parser.add_argument('--lambda_', metavar='lam', type=float, help =
                    'Arrival rate', default = 8)
parser.add_argument('--mu', metavar='mu', type=float, help = 'Service rate', default = 10)

parser.add_argument('--lambda1', metavar='lam1', type=float, help='Arrival rate for class 1', default = .7)
parser.add_argument('--lambda2', metavar='lam2', type=float, help='Arrival rate for class 2', default = 2)

parser.add_argument('--mu1', metavar='mu1', type=float, help = 'Service rate for class 1', default = 1)
parser.add_argument('--mu2', metavar='mu2', type=float, help = 'Service rate for class 2', default = 10)

args = parser.parse_args()

FCFS = 0
NPBasic = 1

if args.system == FCFS:
    run_fcfs_basic(args.num_runs, args.num_jobs_per_run, args.lambda_, args.mu)
elif args.system == NPBasic:
    run_np_basic(args.num_runs, args.num_jobs_per_run, args.lambda1,
                 args.lambda2, args.mu1, args.mu2)
