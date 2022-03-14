class BasicNPStatistic():
	def __init__(self, T1, T2, TQ1, TQ2, S1, S2, N1, N2, job1MixingTime, job2MixingTime):
		self.T1 = T1
		self.T2 = T2
		self.TQ1 = TQ1
		self.TQ2 = TQ2
		self.S1 = S1
		self.S2 = S2
		self.N1 = N1
		self.N2 = N2
		self.job1MixingTime = job1MixingTime
		self.job2MixingTime = job2MixingTime

class BasicNPResults():
	def __init__(self, T1s, T2s, TQ1s, TQ2s, S1s, S2s, N1s, N2s, mixingTime1, mixingTime2):
		self.T1s = T1s
		self.T2s = T2s
		self.TQ1s = TQ1s
		self.TQ2s = TQ2s
		self.S1s = S1s
		self.S2s = S2s
		self.N1s = N1s
		self.N2s = N2s
		self.mixingTime1 = mixingTime1
		self.mixingTime2 = mixingTime2

class SwitchingStatistic():
	def __init__(self, T1, T2, TA, TB, SA, SB, N1, N2, NA, NB, job1MixingTime, job2MixingTime, varJ1, varJ2):
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
		self.varJ1 = varJ1
		self.varJ2 = varJ2

class SwitchingResults():
	def __init__(self, T1s, T2s, TAs, TBs, SAs, SBs, N1s, N2s, NAs, NBs, mixingTime1, mixingTime2, varJ1, varJ2):
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
		self.varJ1 = varJ1
		self.varJ2 = varJ2