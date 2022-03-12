import util.arrivals as arrivals
import util.server as server
import sys
import util.queue as queue
import analysis.events as events
import numpy as np

def progress(count, total, status=''):
	bar_len = 60
	filled_len = int(round(bar_len * count / float(total)))

	percents = round(100.0 * count / float(total), 1)
	bar = '=' * filled_len + '-' * (bar_len - filled_len)

	sys.stdout.write('[%s] %s%s ...%s\r' % (bar, percents, '%', status))
	sys.stdout.flush()  # As suggested by Rom Ruben (see: http://stackoverflow.com/questions/3173320/text-progress-bar-in-the-console/27871113#comment50529068_27871113)


class ServerSwitchNPSystem():
	def __init__(self, num_runs, num_jobs_per_run, lambda1, lambda2, mu1, mu2, class1_prio_prob):
		self.num_runs = num_runs
		self.num_jobs_per_run = num_jobs_per_run
		self.server = server.Server()
		self.queue1 = queue.FCFSQueue()
		self.queue2 = queue.FCFSQueue()
		self.arrivals = arrivals.PriorityArrivals(lambda1, lambda2, mu1, mu2)
		self.class1_prio_prob = class1_prio_prob

		new_job = self.arrivals.arrive()
		new_job.start_service_time = new_job.arrival_time
		self.server.push(new_job, new_job.arrival_time)

	def handle_service(self):
		# Get num jobs in system
		num1_jobs = self.queue1.num_jobs()
		num2_jobs = self.queue2.num_jobs()

		curr_time = self.server.time_next_depart()
		completed_job = self.server.complete()

		# Pop job from queue and push to server; picks class 1 with probability p
		class1_first = bool(np.random.binomial(1, self.class1_prio_prob))
		first_queue = self.queue1 if class1_first else self.queue2
		second_queue = self.queue2 if class1_first else self.queue1

		if (first_queue.num_jobs() != 0):
			new_job_to_serve = first_queue.pop()
		elif (second_queue.num_jobs() != 0):
			new_job_to_serve = second_queue.pop()
		else:
			new_job_to_serve = None

		if new_job_to_serve is not None:
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

		num1_jobs = self.queue1.num_jobs() + self.server.num_jobs_priority(1)
		num2_jobs = self.queue2.num_jobs() + self.server.num_jobs_priority(2)

		if job_arrive.priority == 1:
			self.queue1.push(job_arrive)
		else:
			self.queue2.push(job_arrive)

		if self.server.num_jobs() == 0:
			# Server is idle right now, so take a new job if possible
			class1_first = bool(np.random.binomial(1, self.class1_prio_prob))
			first_queue = self.queue1 if class1_first else self.queue2
			second_queue = self.queue2 if class1_first else self.queue1

			if first_queue.num_jobs() != 0:
				next_job = first_queue.pop()
				next_job.start_service_time = curr_time
				self.server.push(next_job, curr_time)
			elif second_queue.num_jobs() != 0:
				next_job = second_queue.pop()
				next_job.start_service_time = curr_time
				self.server.push(next_job, curr_time)

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

		job1_sizes = []
		job2_sizes = []

		while num_completions1 < self.num_jobs_per_run or num_completions2 < self.num_jobs_per_run:
			event = self.step()
			if isinstance(event, events.PriorityDepartEvent):
				if event.job.priority == 1:
					num_completions1 += 1
				else:
					num_completions2 += 1
				responses.append(event)
				waiting_times.append(event)
			else:
				num_jobs1_seen.append(event.num1_jobs_seen)
				num_jobs2_seen.append(event.num2_jobs_seen)

		job1_sizes = [event.job.size for event in responses if event.job.priority == 1]
		job2_sizes = [event.job.size for event in responses if event.job.priority == 2]

		response1_times = [event.response_time for event in responses if event.job.priority == 1]
		response2_times = [event.response_time for event in responses if event.job.priority == 2]
		waiting1_times = [event.waiting_time for event in responses if event.job.priority == 1]
		waiting2_times = [event.waiting_time for event in responses if event.job.priority == 2]

		S1 = 0 if len(job1_sizes) == 0 else sum(job1_sizes)/len(job1_sizes)
		S2 = 0 if len(job2_sizes) == 0 else sum(job2_sizes)/len(job2_sizes)

		T1 = 0 if len(response1_times) == 0 else sum(response1_times)/len(response1_times)
		T2 = 0 if len(response2_times) == 0 else sum(response2_times)/len(response2_times)
		TQ1 = 0 if len(waiting1_times) == 0 else sum(waiting1_times)/len(waiting1_times)
		TQ2 = 0 if len(waiting2_times) == 0 else sum(waiting2_times)/len(waiting2_times)
		N1 = 0 if len(num_jobs1_seen) == 0 else sum(num_jobs1_seen)/len(num_jobs1_seen)
		N2 = 0 if len(num_jobs2_seen) == 0 else sum(num_jobs2_seen)/len(num_jobs2_seen)

		return (T1, T2, TQ1, TQ2, N1, N2, S1, S2)
	def simulate(self):
		t1_runs = []
		t2_runs = []
		tq1_runs = []
		tq2_runs = []
		n1_runs = []
		n2_runs = []
		s1_runs = []
		s2_runs = []
		for i in range(self.num_runs):
			avg_response1_time, avg_response2_time, avg_waiting1, avg_waiting2, avg_jobs1_seen, avg_jobs2_seen, avg_s1, avg_s2 = self.simulate_run()
			t1_runs.append(avg_response1_time)
			t2_runs.append(avg_response2_time)
			tq1_runs.append(avg_waiting1)
			tq2_runs.append(avg_waiting2)
			n1_runs.append(avg_jobs1_seen)
			n2_runs.append(avg_jobs2_seen)
			s1_runs.append(avg_s1)
			s2_runs.append(avg_s2)
			progress(i, self.num_runs)
		return t1_runs, t2_runs, tq1_runs, tq2_runs, n1_runs, n2_runs, s1_runs, s2_runs