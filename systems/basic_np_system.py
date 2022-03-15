from xmlrpc.client import Server
import util.arrivals as arrivals
import util.server as server
import sys
import util.queue as queue
import analysis.events as events
import analysis.statistic as statistic

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

		self.time_between_job1 = []
		self.time_between_job2 = []
		self.last_served_class = None
		self.last_served_class_time = None
		self.have_seen_class2 = False
		self.have_seen_class1 = False

	def get_next_job(self):
		if (self.queue1.num_jobs() != 0):
			return self.queue1.pop()
		if (self.queue2.num_jobs() != 0):
			return self.queue2.pop()
		return None

	def handle_service(self):
		# Get num jobs in system
		curr_time = self.server.time_next_depart()
		completed_job = self.server.complete()

		response_time = curr_time - completed_job.arrival_time

		# Pop job from queue according to class 1 having priority
		new_job_to_serve = self.get_next_job()

		# Push this job if it exists to the server
		if new_job_to_serve is not None:
			# Update time between jobs
			# If same kind of job as last served, add on size to time
			# End this run and start new one
			if new_job_to_serve.priority != self.last_served_class:
				if new_job_to_serve.priority == 1:
					if self.have_seen_class1:
						time_diff = curr_time - self.last_served_class_time
						self.time_between_job1.append(time_diff)
					self.have_seen_class1 = True
				else:
					if self.have_seen_class2:
						time_diff = curr_time - self.last_served_class_time
						self.time_between_job2.append(time_diff)
					self.have_seen_class2 = True
				
				self.last_served_class_time = curr_time + new_job_to_serve.size
				self.last_served_class = new_job_to_serve.priority

			new_job_to_serve.start_service_time = curr_time
			self.server.push(new_job_to_serve, curr_time)

		num1_jobs = self.queue1.num_jobs() + self.server.num_jobs_priority(1)
		num2_jobs = self.queue2.num_jobs() + self.server.num_jobs_priority(2)

		waiting_time = completed_job.start_service_time - completed_job.arrival_time
		assert(abs(waiting_time - (response_time - completed_job.size)) <= 0.001)
		return events.PriorityDepartEvent(curr_time, response_time, num1_jobs, num2_jobs, waiting_time, completed_job)

	def handle_arrival(self):
		curr_time = self.arrivals.time_next_arrive

		# Get new job and generate next arrival time
		job_arrive = self.arrivals.arrive()

		# Count number of jobs in the system for each class
		num1_jobs = self.queue1.num_jobs() + self.server.num_jobs_priority(1)
		num2_jobs = self.queue2.num_jobs() + self.server.num_jobs_priority(2)

		# Put this arrival in the correct queue; class 1 has strict priority
		if job_arrive.priority == 1:
			self.queue1.push(job_arrive)
		else:
			self.queue2.push(job_arrive)

		# If the server is idle, try to grab a new job
		if self.server.num_jobs() == 0:
			# Pops job according to strict class 1 priority
			next_job = self.get_next_job()

			if next_job is not None:
				next_job.start_service_time = curr_time
				self.server.push(next_job, curr_time)

				# Update time between jobs
				if next_job.priority != self.last_served_class:
					if self.last_served_class == 2:
						# Finished a run of class 2 jobs
						if self.have_seen_class1:
							time_diff = curr_time - self.last_served_class_time
							self.time_between_job1.append(time_diff)
						self.have_seen_class1 = True
					
					elif self.last_served_class == 1:
						# Finished a run of class 1 jobs
						if self.have_seen_class2:
							time_diff = curr_time - self.last_served_class_time
							self.time_between_job2.append(time_diff)
						self.have_seen_class2 = True

					# New run starts after this job finishes, as it was the last time we served a job like it
					self.last_served_class_time = curr_time + next_job.size
					self.last_served_class = next_job.priority

		return events.PriorityArrivalEvent(curr_time, num1_jobs, num2_jobs)

	def step(self):
		if self.arrivals.time_next_arrive <= self.server.time_next_depart():
			# Arrival comes first
			return self.handle_arrival()
		if self.server.time_next_depart() <= self.arrivals.time_next_arrive:
			# Complete the job in the server before arrival can come
			return self.handle_service()

	def simulate_run(self):
		self.server = server.Server()
		self.queue1 = queue.FCFSQueue()
		self.queue2 = queue.FCFSQueue()

		num_completions1 = 0
		num_completions2 = 0

		responses = []
		waiting_times = []

		num_jobs1_seen = []
		num_jobs2_seen = []

		job1_sizes = []
		job2_sizes = []

		# Start with first job and set up final priority
		self.time_between_job1 = []
		self.time_between_job2 = []

		while num_completions1 < self.num_jobs_per_run or num_completions2 < self.num_jobs_per_run or len(self.time_between_job1) < 300 or len(self.time_between_job2) < 300:
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

		timeBetweenJob1 = 0 if len(self.server.time_between_job1s) == 0 else sum(self.server.time_between_job1s)/len(self.server.time_between_job1s)
		timeBetweenJob2 = 0 if len(self.server.time_between_job2s) == 0 else sum(self.server.time_between_job2s)/len(self.server.time_between_job2s)

		return statistic.BasicNPStatistic(T1, T2, TQ1, TQ2, S1, S2, N1, N2, timeBetweenJob1, timeBetweenJob2)
	def simulate(self):
		t1_runs = []
		t2_runs = []
		tq1_runs = []
		tq2_runs = []
		n1_runs = []
		n2_runs = []
		s1_runs = []
		s2_runs = []
		mt1_runs = []
		mt2_runs = []
		for i in range(self.num_runs):
			res = self.simulate_run()
			t1_runs.append(res.T1)
			t2_runs.append(res.T2)
			tq1_runs.append(res.TQ1)
			tq2_runs.append(res.TQ2)
			n1_runs.append(res.N1)
			n2_runs.append(res.N2)
			s1_runs.append(res.S1)
			s2_runs.append(res.S2)
			mt1_runs.append(res.job1MixingTime)
			mt2_runs.append(res.job2MixingTime)
			progress(i, self.num_runs)
		
		return statistic.BasicNPResults(t1_runs, t2_runs, tq1_runs, tq2_runs, s1_runs, s2_runs, n1_runs, n2_runs, mixingTime1=mt1_runs, mixingTime2=mt2_runs)