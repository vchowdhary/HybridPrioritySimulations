# Plan:

import heapq
import numpy as np

print("Hello")
ARRIVAL = 1
DEPARTURE = 0

class Job():
    def __init__(self, jid, arrival_time, job_class):
        self.jid = jid
        self.arrival_time = arrival_time
        self.num_jobs_seen = None
        self.num_jobs1_seen = None
        self.num_jobs2_seen = None
        self.departure_time = None
        self.job_class = job_class

    def get_response_time(self):
        if self.departure_time is None:
            return None
        else:
            return self.departure_time - self.arrival_time

    def __str__(self):
        return (str(self.jid))

    def __repr__(self):
        return str(self)
        #return "Job {} arrives at {}, depart at {}, class {}".format(self.jid, self.arrival_time, self.departure_time, self.job_class)

def simulate_mm1(goal_num_jobs, mu, lambda_):
    def generate_arrival():
        return np.random.exponential(1.0/lambda_)

    def generate_size():
        return np.random.exponential(1.0/mu)

    next_arrival  = generate_arrival()
    next_service = generate_size() + next_arrival
    t = next_arrival
    num_in_system = 0
    num_completions = 0
    queue = []
    completed_jobs = []
    jid = 1

    while num_completions < goal_num_jobs:
        if t == next_arrival:
            job = Job(jid, t)
            jid += 1
            queue.append(job)

            next_arrival = t + generate_arrival()
        if t == next_service:
            job = queue.pop(0)
            job.departure_time = t
            job.num_jobs_seen = len(queue)
            completed_jobs.append(job)
            num_completions += 1
            if len(queue) == 0:
                next_service = next_arrival +generate_size()
            else:
                next_service = t + generate_size()
        t = min(next_arrival, next_service)

    Tavg = sum([job.get_response_time() for job in
                          completed_jobs])/num_completions
    Navg = sum([job.num_jobs_seen for job in
                completed_jobs])/num_completions
    return Tavg, Navg


def simulate_bp(goal_num_jobs, mu1, mu2, lambda1, lambda2):
    def generate_arrival():
        return np.random.exponential(1.0/(lambda1 + lambda2))
    def generate_size(job_class):
        if job_class == 1:
            return np.random.exponential(1.0/mu1)
        else:
            return np.random.exponential(1.0/mu2)

    next_arrival  = generate_arrival()
    is_class1 = np.random.binomial(1, lambda1/(lambda1 + lambda2))

    if is_class1 == 1:
        next_service = next_arrival + generate_size(1)
        next_class = 1
    else:
        next_service = next_arrival + generate_size(2)
        next_class = 2

    t = next_arrival
    num_completions = 0
    num1_completions = 0
    num2_completions = 0
    queues = [[], []]
    completed_jobs = []
    jid = 1

    while num_completions < goal_num_jobs:
        #print("Class 1 Queue:", str(queues[0]))
        #print("Class 2 Queue:", str(queues[1]))
        #print("next arrival {}, is class 1? {}, next service {}, next class service {}".format(next_arrival, is_class1 == 1, next_service, next_class))
        if t == next_arrival:
            # Figure out which class next arrival goes to
            if is_class1 == 1:
                job = Job(jid, t, 1)
                queues[0].append(job)
            else:
                job = Job(jid, t, 2)
                queues[1].append(job)

            jid += 1
            next_arrival = t + generate_arrival()
            is_class1 = np.random.binomial(1, lambda1/(lambda1+lambda2))
            #print("Customer {} arrived at {}, class 2".format(jid - 1, t))
        if t == next_service:
            #print(t, next_class)
            # Job in service is completed
            job = queues[next_class - 1].pop(0)
            job.departure_time = t
            job.num_jobs1_seen = len(queues[0])
            job.num_jobs2_seen = len(queues[1])
            completed_jobs.append(job)
            if next_class == 1:
                num1_completions += 1
            else:
                num2_completions += 1
            num_completions += 1

            if len(queues[0]) == 0 and len(queues[1]) == 0:
                if is_class1 == 1:
                    next_service = next_arrival + generate_size(1)
                    next_class = 1
                else:
                    next_service = next_arrival + generate_size(2)
                    next_class = 2
            elif len(queues[0]) == 0 and len(queues[1]) != 0:
                next_service = t + generate_size(2)
                next_class = 2
            else:
                next_service = t + generate_size(1)
                next_class = 1

        #print("Class 1 Queue:", str(queues[0]))
        #print("Class 2 Queue:", str(queues[1]))
        t = min(next_arrival, next_service)

    T1avg = 0 if num1_completions == 0 else sum([job.get_response_time() for job in completed_jobs if
                 job.job_class == 1])/num1_completions
    T2avg = 0 if num2_completions == 0 else sum([job.get_response_time() for job in completed_jobs if
                 job.job_class == 2])/num2_completions
    N1avg = sum([job.num_jobs1_seen for job in completed_jobs])/num_completions
    N2avg = sum([job.num_jobs2_seen for job in completed_jobs])/num_completions
    return T1avg, T2avg, N1avg, N2avg


mu1 = 1000
lambda1 = 100
mu2 = 1000
lambda2 = 800

rho1 = lambda1/mu1
rho2 = lambda2/mu2
print(rho1, rho2)
num_runs = 1000
T1ens = 0
T2ens = 0
N1ens = 0
N2ens = 0
for i in range(num_runs):
    res = simulate_bp(100000, mu1, mu2, lambda1, lambda2)
    T1ens += res[0]
    T2ens += res[1]
    N1ens += res[2]
    N2ens += res[3]
    print(i, res)

T1avg = T1ens/num_runs
T2avg = T2ens/num_runs
N1avg = N1ens/num_runs
N2avg = N2ens/num_runs

print("T1: {}, T2: {}, N1: {}, N2: {}".format(T1avg, T2avg, N1avg, N2avg))
print("Little's Law for Class 1 Jobs: {}".format(lambda1*T1avg))
print("Little's Law for Class 2 Jobs: {}".format(lambda2*T2avg))
print("Little's Law overall; expected: {}, actual: {}".format(lambda1*T1avg + lambda2*T2avg, N1avg + N2avg))
