class FCFSQueue():
	def __init__(self):
		self.jobs_waiting = []
		self.work = 0.0

	def pop(self):
		# Pop job from queue and update current work in queue
		if len(self.jobs_waiting) == 0:
			return None
		job = self.jobs_waiting.pop(0)
		self.work -= job.size
		return job

	def push(self, job):
		if (job is not None):
			self.work += job.size
			self.jobs_waiting.append(job)

	def work(self):
		return self.work

	def num_jobs(self):
		return len(self.jobs_waiting)

	def num_jobs_priority(self, priority):
		count = 0
		for job in self.jobs_waiting:
			# We want the jobs with this actual class
			if job.priority == priority:
				count += 1
		return count