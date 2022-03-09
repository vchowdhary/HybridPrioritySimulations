from os import stat
import util.arrivals as arrivals
import util.server as server
import sys
import util.queue as queue
import analysis.events as events
import numpy as np
import analysis.statistic as statistic

def progress(count, total, status=''):
	bar_len = 60
	filled_len = int(round(bar_len * count / float(total)))

	percents = round(100.0 * count / float(total), 1)
	bar = '=' * filled_len + '-' * (bar_len - filled_len)

	sys.stdout.write('[%s] %s%s ...%s\r' % (bar, percents, '%', status))
	sys.stdout.flush()  # As suggested by Rom Ruben (see: http://stackoverflow.com/questions/3173320/text-progress-bar-in-the-console/27871113#comment50529068_27871113)


class SwitchingNPSystem():
	def __init__(self, num_runs, num_jobs_per_run, lambda1, lambda2, mu1, mu2, stay_prob):
		self.num_runs = num_runs
		self.num_jobs_per_run = num_jobs_per_run
		self.server = server.Server()
		self.queueA = queue.FCFSQueue()
		self.queueB = queue.FCFSQueue()
		self.arrivals = arrivals.SwitchingPriorityArrivals(lambda1, lambda2, mu1, mu2, stay_prob)
		self.stay_prob = stay_prob

		# Start with first job and set up final priority
		new_job = self.arrivals.arrive()
		new_job.start_service_time = new_job.arrival_time
		self.server.push(new_job, new_job.arrival_time)

	def handle_service(self):
		# Get num jobs in system by adding up across the queues
		num1_jobs = self.queueA.num_jobs_priority(1) + self.queueB.num_jobs_priority(1)
		num2_jobs = self.queueA.num_jobs_priority(2) + self.queueB.num_jobs_priority(2)

		numA_jobs = self.queueA.num_jobs()
		numB_jobs = self.queueB.num_jobs()

		# Finish job
		curr_time = self.server.time_next_depart()
		completed_job = self.server.complete()

		# Pop job from queue and push to server; class A has strict priority so try popping from there first
		if (self.queueA.num_jobs() != 0):
			new_job_to_serve = self.queueA.pop()
		elif (self.queueB.num_jobs() != 0):
			new_job_to_serve = self.queueB.pop()
		else:
			new_job_to_serve = None

		# If there was some job left to serve, start serving it
		if new_job_to_serve is not None:
			new_job_to_serve.start_service_time = curr_time
			self.server.push(new_job_to_serve, curr_time)

		waiting_time = completed_job.start_service_time - completed_job.arrival_time
		assert(abs(waiting_time - (curr_time - completed_job.arrival_time - completed_job.size)) <= 0.001)

		return events.SwitchingPriorityDepartEvent(curr_time, curr_time - completed_job.arrival_time, num1_jobs,
			   num2_jobs, numA_jobs, numB_jobs, waiting_time, completed_job)

	def handle_arrival(self):
		curr_time = self.arrivals.time_next_arrive
		# Get new job and generate next arrival time
		job_arrive = self.arrivals.arrive()

		if job_arrive.final_priority == 1:
			self.queueA.push(job_arrive)
		else:
			self.queueB.push(job_arrive)

		if self.server.num_jobs() == 0:
			# Server is idle right now, so take a new job if possible
			# class A has strict priority
			if self.queueA.num_jobs() != 0:
				next_job = self.queueA.pop()
				next_job.start_service_time = curr_time
				self.server.push(next_job, curr_time)
			elif self.queueB.num_jobs() != 0:
				next_job = self.queueB.pop()
				next_job.start_service_time = curr_time
				self.server.push(next_job, curr_time)
		
		# Get class 1 jobs and class 2 jobs across both queues
		num1_jobs = self.queueA.num_jobs_priority(1) + self.queueB.num_jobs_priority(1)
		num2_jobs = self.queueA.num_jobs_priority(2) + self.queueB.num_jobs_priority(2)

		# Get class A jobs and class B jobs
		numA_jobs = self.queueA.num_jobs()
		numB_jobs = self.queueB.num_jobs()

		return events.SwitchingPriorityArrivalEvent(curr_time, num1_jobs, num2_jobs, numA_jobs, numB_jobs)

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

		num_jobsA_seen = []
		num_jobsB_seen = []

		jobA_sizes = []
		jobB_sizes = []

		while num_completions1 < self.num_jobs_per_run and num_completions2 < self.num_jobs_per_run:
			event = self.step()
			if isinstance(event, events.SwitchingPriorityDepartEvent):
				if event.job.priority == 1:
					num_completions1 += 1
				else:
					num_completions2 += 1
				responses.append(event)
				waiting_times.append(event)
			else:
				num_jobs1_seen.append(event.num1_jobs_seen)
				num_jobs2_seen.append(event.num2_jobs_seen)
				num_jobsA_seen.append(event.numA_jobs_seen)
				num_jobsB_seen.append(event.numB_jobs_seen)

		# Computing SA and SB
		jobA_sizes = [event.job.size for event in responses if event.job.final_priority == 1]
		jobB_sizes = [event.job.size for event in responses if event.job.final_priority == 2]

		SA = 0 if len(jobA_sizes) == 0 else sum(jobA_sizes)/len(jobA_sizes)
		SB = 0 if len(jobB_sizes) == 0 else sum(jobB_sizes)/len(jobB_sizes)

		# Computing T1 and T2
		response1_times = [event.response_time for event in responses if event.job.priority == 1]
		response2_times = [event.response_time for event in responses if event.job.priority == 2]

		T1 = 0 if len(response1_times) == 0 else sum(response1_times)/len(response1_times)
		T2 = 0 if len(response2_times) == 0 else sum(response2_times)/len(response2_times)

		# Computing TA and TB
		responseA_times = [event.response_time for event in responses if event.job.final_priority == 1]
		responseB_times = [event.response_time for event in responses if event.job.final_priority == 2]

		TA = 0 if len(responseA_times) == 0 else sum(responseA_times)/len(responseA_times)
		TB = 0 if len(responseB_times) == 0 else sum(responseB_times)/len(responseB_times)

		# Computing N1 and N2
		N1 = 0 if len(num_jobs1_seen) == 0 else sum(num_jobs1_seen)/len(num_jobs1_seen)
		N2 = 0 if len(num_jobs2_seen) == 0 else sum(num_jobs2_seen)/len(num_jobs2_seen)

		# Computing NA and NB
		NA = 0 if len(num_jobsA_seen) == 0 else sum(num_jobsA_seen)/len(num_jobsA_seen)
		NB = 0 if len(num_jobsB_seen) == 0 else sum(num_jobsB_seen)/len(num_jobsB_seen)

		return statistic.SwitchingStatistic(T1, T2, TA, TB, SA, SB, N1, N2, NA, NB)
	def simulate(self):
		t1_runs = []
		t2_runs = []
		tA_runs = []
		tB_runs = []
		sA_runs = []
		sB_runs = []
		n1_runs = []
		n2_runs = []
		nA_runs = []
		nB_runs = []
		for i in range(self.num_runs):
			run_result = self.simulate_run()
			t1_runs.append(run_result.T1)
			t2_runs.append(run_result.T2)
			n1_runs.append(run_result.N1)
			n2_runs.append(run_result.N2)
			tA_runs.append(run_result.TA)
			tB_runs.append(run_result.TB)
			sA_runs.append(run_result.SA)
			sB_runs.append(run_result.SB)
			nA_runs.append(run_result.NA)
			nB_runs.append(run_result.NB)
			progress(i, self.num_runs)
		return statistic.SwitchingResults(t1_runs, t2_runs, tA_runs, tB_runs, sA_runs, sB_runs, n1_runs, n2_runs, nA_runs, nB_runs)