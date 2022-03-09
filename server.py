import jobs

# Basic server class
class Server():
	def __init__(self):
		self.job_serving = None
		self.time_depart = float('inf')

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

	def work(self, time_now):
		# Work left in server is just the current job
		return self.time_depart - time_now

	def num_jobs(self):
		if self.job_serving is None:
			return 0
		else:
			return 1