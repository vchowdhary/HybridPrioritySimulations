class SwitchingStatistic():
	def __init__(self, T1, T2, TA, TB, SA, SB, N1, N2, NA, NB, job1MixingTime, job2MixingTime):
		self.T1 = T1
		self.T2 = T2
		self.TA = TA
		self.TB = TB
		self.SA = SA
		self.SB = SB
		self.N1 = N1
		self.N2 = N2
		self.NA = NA
		self.NB = NB
		self.job1MixingTime = job1MixingTime
		self.job2MixingTime = job2MixingTime

class SwitchingResults():
	def __init__(self, T1s, T2s, TAs, TBs, SAs, SBs, N1s, N2s, NAs, NBs, mixingTime1, mixingTime2):
		self.T1s = T1s
		self.T2s = T2s
		self.TAs = TAs
		self.TBs = TBs
		self.SAs = SAs
		self.SBs = SBs
		self.N1s = N1s
		self.N2s = N2s
		self.NAs = NAs
		self.NBs = NBs
		self.mixingTime1 = mixingTime1
		self.mixingTime2 = mixingTime2