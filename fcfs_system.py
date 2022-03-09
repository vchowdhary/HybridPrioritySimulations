import arrivals
import server
import jobs
import queue
import events

class FCFSSystem():
    def __init__(self, num_runs, num_jobs_per_run, lambda_, mu):
        self.time = 0
        self.num_runs = num_runs
        self.num_jobs_per_run = num_jobs_per_run
        self.server = server.Server()
        self.queue = queue.FCFSQueue()
        self.arrivals = arrivals.Arrivals(lambda_, mu)

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

            return events.DepartEvent(self.time, self.time - completed_job.arrival_time, num_jobs, completed_job)
        # Otherwise is arrival
        self.time = self.arrivals.time_next_arrive
        _, job_arrive = self.arrivals.arrive()

        if self.server.num_jobs() == 0:
            self.server.push(job_arrive, self.time)
        else:
            self.queue.push(job_arrive)

        return events.ArrivalEvent(self.time)

    def simulate_run(self):
        num_completions = 0
        responses = []
        while num_completions < self.num_jobs_per_run:
            event = self.step()
            if isinstance(event, events.DepartEvent):
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