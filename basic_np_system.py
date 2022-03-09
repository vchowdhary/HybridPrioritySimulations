import arrivals
import server
import sys
import queue
import events

def progress(count, total, status=''):
    bar_len = 60
    filled_len = int(round(bar_len * count / float(total)))

    percents = round(100.0 * count / float(total), 1)
    bar = '=' * filled_len + '-' * (bar_len - filled_len)

    sys.stdout.write('[%s] %s%s ...%s\r' % (bar, percents, '%', status))
    sys.stdout.flush()  # As suggested by Rom Ruben (see: http://stackoverflow.com/questions/3173320/text-progress-bar-in-the-console/27871113#comment50529068_27871113)


class NPPrioritySystem():
	def __init__(self, num_runs, num_jobs_per_run, lambda1, lambda2, mu1, mu2):
		self.num_runs = num_runs
		self.num_jobs_per_run = num_jobs_per_run
		self.server = server.Server()
		self.queueA = queue.FCFSQueue()
		self.queueB = queue.FCFSQueue()
		self.arrivals = arrivals.PriorityArrivals(lambda1, lambda2, mu1, mu2)

	def handle_service(self):
		if self.server.job_serving is not None and self.server.job_serving.priority == 1:
				num1_jobs_in_server = 1
		else:
			num1_jobs_in_server = 0
		
		if self.server.job_serving is not None and self.server.job_serving.priority == 2:
			num2_jobs_in_server = 1
		else:
			num2_jobs_in_server = 0

		# Get num jobs in system
		num1_jobs = self.queueA.num_jobs() + num1_jobs_in_server
		num2_jobs = self.queueB.num_jobs() + num2_jobs_in_server

		curr_time = self.server.time_next_depart()
		completed_job = self.server.complete()
		# print("Completed job {} at time {:.3f}".format(completed_job, self.time))

		# Pop job from queue and push to server
		if (self.queueA.num_jobs() != 0):
			new_job_to_serve = self.queueA.pop()
		elif (self.queueB.num_jobs() != 0):
			new_job_to_serve = self.queueB.pop()
		else:
			new_job_to_serve = None

		if new_job_to_serve is not None:
			# print("Serving job {}".format(new_job_to_serve))
			self.server.push(new_job_to_serve, curr_time)

		return events.PriorityDepartEvent(curr_time, curr_time -
									completed_job.arrival_time, num1_jobs,
									num2_jobs, completed_job)

	def handle_arrival(self):
		curr_time = self.arrivals.time_next_arrive
		job_arrive = self.arrivals.arrive()
		# print("Job {} just arrived".format(job_arrive))

		if self.server.num_jobs() == 0:
			if job_arrive.priority == 1 and self.queueA.num_jobs() == 0:
				# print("job can go directly to server")
				self.server.push(job_arrive, curr_time)
			if job_arrive.priority == 2 and self.queueA.num_jobs() == 0 and self.queueB.num_jobs() == 0:
				# print("job can go directly to server")
				self.server.push(job_arrive, curr_time)
		else:
			# print("Job has to go in queue {}".format(job_arrive.priority))
			if job_arrive.priority == 1:
				self.queueA.push(job_arrive)
			else:
				self.queueB.push(job_arrive)

		if self.server.job_serving is not None and self.server.job_serving.priority == 1:
			num1_jobs_in_server = 1
		else:
			num1_jobs_in_server = 0
		
		if self.server.job_serving is not None and self.server.job_serving.priority == 2:
			num2_jobs_in_server = 1
		else:
			num2_jobs_in_server = 0

		num1_jobs = self.queueA.num_jobs()
		num2_jobs = self.queueB.num_jobs()

		return events.PriorityArrivalEvent(curr_time, num1_jobs, num2_jobs)

	def step(self):
		if self.server.time_next_depart() <= self.arrivals.time_next_arrive:
			# Complete the job in the server before arrival can come
			return self.handle_service()
		else:
			return self.handle_arrival()

	def simulate_run(self):
		num_completions = 0
		num_completions1 = 0
		num_completions2 = 0
		responses = []
		num_jobs1_seen = []
		num_jobs2_seen = []
		while num_completions1 < self.num_jobs_per_run or num_completions2 < self.num_jobs_per_run:
			# print("=================")
			event = self.step()
			# print("Queue 1: {}".format([job.jid for job in self.queueA.jobs_waiting]))
			# print("Queue 2: {}".format([job.jid for job in self.queueB.jobs_waiting]))
			# print("Server: {}".format("" if self.server.job_serving is None else self.server.job_serving.jid))
			# print(event)
			if isinstance(event, events.PriorityDepartEvent):
				if event.job.priority == 1:
					num_completions1 += 1
				else:
					num_completions2 += 1
				responses.append(event)
				# num_jobs1_seen.append(event.num1_jobs_seen)
				# num_jobs2_seen.append(event.num2_jobs_seen)
			else:
				num_jobs1_seen.append(event.num1_jobs_seen)
				num_jobs2_seen.append(event.num2_jobs_seen)

		response1_times = [event.response_time for event in responses if event.job.priority == 1]
		response2_times = [event.response_time for event in responses if event.job.priority == 2]

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
			progress(i, self.num_runs)
		return t1_runs, t2_runs, n1_runs, n2_runs








































































