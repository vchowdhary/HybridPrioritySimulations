class ArrivalEvent():
    def __init__(self, time):
        self.time = time
    def __repr__(self):
        return "Arrival {:.3f}".format(self.time)

class PriorityArrivalEvent():
    def __init__(self, time, num1_jobs, num2_jobs):
        self.time = time
        self.num1_jobs_seen = num1_jobs
        self.num2_jobs_seen = num2_jobs
    def __repr__(self):
        return "Arrival at {:.3f}, num 1 jobs = {}, num2 jobs = {}".format(self.time, self.num1_jobs_seen, self.num2_jobs_seen)


class DepartEvent():
    def __init__(self, curr_time, response_time, num_jobs_seen, job):
        self.curr_time = curr_time
        self.response_time = response_time
        self.num_jobs_seen = num_jobs_seen
        self.job = job
    def __repr__(self):
        return "Job {} departs at {:.3f}, response time {:.3f}".format(self.job.jid,
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
        return "Job {} departs at {:.3f}, response time {:.3f}, num 1 jobs {}, num 2 jobs {}".format(self.job.jid,
                                                               self.curr_time,
                                                               self.response_time,
                                                               self.num1_jobs_seen,
                                                               self.num2_jobs_seen)
















































































































































































































































