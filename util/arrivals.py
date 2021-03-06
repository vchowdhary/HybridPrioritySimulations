import numpy as np
import util.jobs as jobs

# Basic Poisson Arrivals
class Arrivals():
	def __init__(self, lambda_, mu):
		self.time_next_arrive = 0.0
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

		return (curr_time, jobs.Job(size, curr_time, jid))

class PriorityArrivals():
	def __init__(self, lambda1, lambda2, mu1, mu2):
		lambda_ = lambda1 + lambda2
		self.time_next_arrive = 0.0
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

		if is_class_1 == 1:
			new_job_class = 1
			size = np.random.exponential(1.0/self.mu1)
		else:
			new_job_class = 2
			size = np.random.exponential(1.0/self.mu2)

		# Update info for next arrival
		self.jid += 1
		self.time_next_arrive += next_arrival

		# Create and return new job
		new_job = jobs.Job(size, curr_time, jid, new_job_class)
		return new_job

class SwitchingPriorityArrivals():
	def __init__(self, lambda1, lambda2, mu1, mu2, stay_prob):
		lambda_ = lambda1 + lambda2
		self.time_next_arrive = 0.0
		self.is_class_1_prob = lambda1/lambda_
		self.stay_prob = stay_prob
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
		# print("Next arrival will be at {:.3f}, is class 1? {}".format(self.time_next_arrive, bool(is_class_1)))

		# Create and return new job
		if is_class_1 == 1:
			new_job_class = 1
			size = np.random.exponential(1.0/self.mu1)
		else:
			new_job_class = 2
			size = np.random.exponential(1.0/self.mu2)

		final_class = new_job_class
		# Might switch the assigned class
		do_stay = np.random.binomial(1, self.stay_prob)
		if do_stay == 0:
			if final_class == 1:
				final_class = 2
			else:
				final_class = 1
		
		new_job = jobs.Job(size=size, arrival_time=curr_time, jid=jid, priority=new_job_class, final_priority=final_class)
		return new_job