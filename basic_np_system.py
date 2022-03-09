from multiprocessing.connection import wait
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
		self.queue1 = queue.FCFSQueue()
		self.queue2 = queue.FCFSQueue()
		self.arrivals = arrivals.PriorityArrivals(lambda1, lambda2, mu1, mu2)

	def handle_service(self):
		# Get num jobs in system
		num1_jobs = self.queue1.num_jobs()
		num2_jobs = self.queue2.num_jobs()

		curr_time = self.server.time_next_depart()
		completed_job = self.server.complete()
		# print("Completed job {} at time {:.3f}".format(completed_job, self.time))

		# Pop job from queue and push to server
		if (self.queue1.num_jobs() != 0):
			new_job_to_serve = self.queue1.pop()
		elif (self.queue2.num_jobs() != 0):
			new_job_to_serve = self.queue2.pop()
		else:
			new_job_to_serve = None

		if new_job_to_serve is not None:
			# print("Serving job {}".format(new_job_to_serve))
			new_job_to_serve.start_service_time = curr_time
			self.server.push(new_job_to_serve, curr_time)

		waiting_time = completed_job.start_service_time - completed_job.arrival_time
		assert(abs(waiting_time - (curr_time - completed_job.arrival_time - completed_job.size)) <= 0.001)
		return events.PriorityDepartEvent(curr_time, curr_time - completed_job.arrival_time, num1_jobs,
									num2_jobs, waiting_time, completed_job)

	def handle_arrival(self):
		curr_time = self.arrivals.time_next_arrive
		# Get new job and generate next arrival time
		job_arrive = self.arrivals.arrive()
		# print("Job {} just arrived".format(job_arrive))

		if job_arrive.priority == 1:
			self.queue1.push(job_arrive)
		else:
			self.queue2.push(job_arrive)

		if self.server.num_jobs() == 0:
			# Server is idle right now, so take a new job if possible
			if self.queue1.num_jobs() != 0:
				# print("job can go directly to server")
				next_job = self.queue1.pop()
				next_job.start_service_time = curr_time
				self.server.push(next_job, curr_time)
			elif self.queue2.num_jobs() != 0:
				next_job = self.queue2.pop()
				next_job.start_service_time = curr_time
				self.server.push(next_job, curr_time)
		
		num1_jobs = self.queue1.num_jobs()
		num2_jobs = self.queue2.num_jobs()

		return events.PriorityArrivalEvent(curr_time, num1_jobs, num2_jobs)

	def step(self):
		if self.arrivals.time_next_arrive <= self.server.time_next_depart():
			# Arrival comes first
			return self.handle_arrival()
		if self.server.time_next_depart() <= self.arrivals.time_next_arrive:
			# Complete the job in the server before arrival can come
			return self.handle_service()
		

	def simulate_run(self):
		num_completions1 = 0
		num_completions2 = 0
		responses = []
		waiting_times = []
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
				waiting_times.append(event)
				num_jobs1_seen.append(event.num1_jobs_seen)
				num_jobs2_seen.append(event.num2_jobs_seen)
			else:
				num_jobs1_seen.append(event.num1_jobs_seen)
				num_jobs2_seen.append(event.num2_jobs_seen)

		response1_times = [event.response_time for event in responses if event.job.priority == 1]
		response2_times = [event.response_time for event in responses if event.job.priority == 2]
		waiting1_times = [event.waiting_time for event in responses if event.job.priority == 1]
		waiting2_times = [event.waiting_time for event in responses if event.job.priority == 2]

		T1 = 0 if len(response1_times) == 0 else sum(response1_times)/len(response1_times)
		T2 = 0 if len(response2_times) == 0 else sum(response2_times)/len(response2_times)
		TQ1 = 0 if len(waiting1_times) == 0 else sum(waiting1_times)/len(waiting1_times)
		TQ2 = 0 if len(waiting2_times) == 0 else sum(waiting2_times)/len(waiting2_times)
		N1 = 0 if len(num_jobs1_seen) == 0 else sum(num_jobs1_seen)/len(num_jobs1_seen)
		N2 = 0 if len(num_jobs2_seen) == 0 else sum(num_jobs2_seen)/len(num_jobs2_seen)

		return (T1, T2, TQ1, TQ2, N1, N2)
	def simulate(self):
		t1_runs = []
		t2_runs = []
		tq1_runs = []
		tq2_runs = []
		n1_runs = []
		n2_runs = []
		for i in range(self.num_runs):
			avg_response1_time, avg_response2_time, avg_waiting1, avg_waiting2, avg_jobs1_seen, avg_jobs2_seen = self.simulate_run()
			t1_runs.append(avg_response1_time)
			t2_runs.append(avg_response2_time)
			tq1_runs.append(avg_waiting1)
			tq2_runs.append(avg_waiting2)
			n1_runs.append(avg_jobs1_seen)
			n2_runs.append(avg_jobs2_seen)
			progress(i, self.num_runs)
		return t1_runs, t2_runs, tq1_runs, tq2_runs, n1_runs, n2_runs








































































