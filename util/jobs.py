# Basic job class
class Job():
	def __init__(self, size, arrival_time, jid, priority=1, final_priority=None):
		self.size = size
		self.arrival_time = arrival_time
		self.start_service_time = None
		self.priority = priority
		if final_priority is None:
			self.final_priority = priority
		else:
			self.final_priority = final_priority
		self.jid = jid

	def __repr__(self):
		return "Job {}, priority {}, final priority {}, arrived at {:.3f}, size {:.3f}".format(self.jid,
		        self.priority,
		        self.final_priority,
		        self.arrival_time,
		        self.size)