import util.jobs as jobs

# Basic server class
class Server():
	def __init__(self):
		self.job_serving = None
		self.time_depart = float('inf')
		self.last_time_served_job1 = None
		self.last_time_served_job2 = None
		self.time_between_job1s = []
		self.time_between_job2s = []

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
		if job is not None and self.num_jobs() == 0:
			self.time_depart = time_now + job.size
			self.job_serving = job
			if job.priority == 1:
				if self.last_time_served_job1 is not None:
					self.time_between_job1s.append(time_now - self.last_time_served_job1)
				self.last_time_served_job1 = time_now + job.size
			else:
				if self.last_time_served_job2 is not None:
					self.time_between_job2s.append(time_now - self.last_time_served_job2)
				self.last_time_served_job2 = time_now + job.size

	def work(self, time_now):
		# Work left in server is just the current job
		return self.time_depart - time_now

	def num_jobs(self):
		if self.job_serving is None:
			return 0
		else:
			return 1

	def num_jobs_priority(self, priority):
		if self.job_serving is None:
			return 0
		elif self.job_serving.priority == priority:
			return 1
		else:
			return 0
	
	def num_jobs_final_priority(self, priority):
		if self.job_serving is None:
			return 0
		elif self.job_serving.final_priority == priority:
			return 1
		else:
			return 0