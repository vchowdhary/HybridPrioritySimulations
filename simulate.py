import argparse
import fcfs_system
import basic_np_system
import switching_np_system

def run_fcfs_basic(num_runs, num_jobs_per_run, lambda_, mu):
	print("Running Basic FCFS Simulation...")
	basic_system = fcfs_system.FCFSSystem(num_runs, num_jobs_per_run, lambda_, mu)
	T_runs, N_runs = basic_system.simulate()

	ET = sum(T_runs)/len(T_runs)
	EN = sum(N_runs)/len(N_runs)
	rho = lambda_/mu

	print("Lambda: {}, mu: {}, rho: {}".format(lambda_, mu, rho))
	print("E[T]: {}, E[N]: {}".format(ET, EN))
	print("Expected E[T]: {}, Actual E[T]: {}".format(1/(mu - lambda_), ET))
	print("Expected E[N]: {}, Actual E[N]: {}".format(rho/(1-rho), EN))
	print("Little's Law holds? lambdaE[T]: {}, E[N]: {}".format(lambda_*ET, EN))


def run_np_basic(num_runs, num_jobs_per_run, lambda1, lambda2, mu1, mu2):
	print("Running Basic NonPreemptive Simulation...")
	basic_system = basic_np_system.NPPrioritySystem(num_runs, num_jobs_per_run, lambda1, lambda2, mu1, mu2)
	T1_runs, T2_runs, TQ1_runs, TQ2_runs, N1_runs, N2_runs, S1_runs, S2_runs = basic_system.simulate()

	ET1 = sum(T1_runs)/len(T1_runs)
	ET2 = sum(T2_runs)/len(T2_runs)

	ETQ1 = sum(TQ1_runs)/len(TQ1_runs)
	ETQ2 = sum(TQ2_runs)/len(TQ2_runs)

	EN1 = sum(N1_runs)/len(N1_runs)
	EN2 = sum(N2_runs)/len(N2_runs)

	ES1 = sum(S1_runs)/len(S1_runs)
	ES2 = sum(S2_runs)/len(S2_runs)

	rho1 = lambda1/mu1
	rho2 = lambda2/mu2
	rho = rho1 + rho2

	lambda_ = lambda1 + lambda2
	Se = lambda1/lambda_ * 1/(mu1) + lambda2/lambda_ * 1/(mu2)

	print("Se: {}".format(Se))

	ET = lambda1/lambda_*ET1 + lambda2/lambda_*ET2
	EN = EN1 + EN2

	expectedTQ1 = rho*Se/(1-rho1)
	expectedTQ2 = rho*Se/((1-rho1)*(1-rho))

	goalT1 = expectedTQ1 + 1/mu1
	goalT2 = expectedTQ2 + 1/mu2

	print("Lambda1: {}, lambda2: {}, mu1: {}, mu2: {}, rho1: {}, rho2: {}".format(lambda1, lambda2, mu1, mu2, rho1, rho2))
	print("Expected E[S1]: {}, Actual E[S1]: {}".format(1/mu1, ES1))
	print("Expected E[S2]: {}, Actual E[S2]: {}".format(1/mu2, ES2))
	print("E[T1]: {}, E[N1]: {}".format(ET1, EN1))
	print("E[T2]: {}, E[N2]: {}".format(ET2, EN2))
	print("Expected E[T1]: {}, Actual E[T1]: {}".format(goalT1, ET1))
	print("Expected E[T2]: {}, Actual E[T2]: {}".format(goalT2, ET2))
	print("Expected E[TQ1]: {}, Actual E[TQ1]: {}".format(expectedTQ1, ETQ1))
	print("Expected E[TQ2]: {}, Actual E[TQ2]: {}".format(expectedTQ2, ETQ2))
	print("Little's Law holds for class 1? lambda1E[T1]: {}, E[N1]: {}".format(lambda1*ET1, EN1))
	print("Little's Law holds for class 2? lambda2E[T2]: {}, E[N2]: {}".format(lambda2*ET2, EN2))
	print("Little's Law holds overall? lambdaE[T]: {}, E[N]: {}".format(lambda_*ET, EN))

def run_switching_np(num_runs, num_jobs_per_run, lambda1, lambda2, mu1, mu2, stay_prob):
	print("Running Switching NonPreemptive Simulation...")
	basic_system = switching_np_system.SwitchingNPSystem(num_runs, num_jobs_per_run, lambda1, lambda2, mu1, mu2, stay_prob)
	
	# System parameters
	lambda_ = lambda1 + lambda2

	rho1 = lambda1/mu1
	rho2 = lambda2/mu2
	rho = rho1 + rho2

	lambdaA = lambda1*stay_prob + lambda2*(1-stay_prob)
	lambdaB = lambda1*(1-stay_prob) + lambda2*stay_prob

	# Computing size distribution
	expected_SA = ((lambda1*stay_prob)/lambdaA)*1/mu1 + ((lambda2*(1-stay_prob))/lambdaA)*1/mu2
	expected_SB = ((lambda1*(1-stay_prob))/lambdaB)*1/mu1 + ((lambda2*stay_prob)/lambdaB)*1/mu2

	rhoA = stay_prob*rho1 + (1-stay_prob)*rho2
	rhoB = stay_prob*rho2 + (1-stay_prob)*rho1

	Se = lambda1/lambda_ * 1/(mu1) + lambda2/lambda_ * 1/(mu2)
	print("Se: {:.6f}".format(Se))

	print("Lambda1: {}, lambda2: {}, lambda: {}, mu1: {:.3f}, mu2: {:.3f}, rho1: {:.3f}, rho2: {:.3f}, stay prob: {}".format(lambda1, lambda2, lambda_, mu1, mu2, rho1, rho2, stay_prob))
	print("LambdaA: {:.3f}, LambdaB: {:.3f}, rhoA: {:.3f}, rhoB: {:.3f}".format(lambdaA, lambdaB, rhoA, rhoB))

	switching_res = basic_system.simulate()

	# Computing actual SA and SB
	ESA = sum(switching_res.SAs)/len(switching_res.SAs)
	ESB = sum(switching_res.SBs)/len(switching_res.SBs)

	print("Expected SA: {}, Actual SA: {}".format(expected_SA, ESA))
	print("Expected SB: {}, Actual SB: {}".format(expected_SB, ESB))

	# Computing expected class A and B time
	expected_TAQ = rho*Se/(1-rhoA)
	expected_TBQ = rho*Se/((1-rho)*(1-rhoA))

	expected_TA = expected_TAQ + expected_SA
	expected_TB = expected_TBQ + expected_SB

	ETA = sum(switching_res.TAs)/len(switching_res.TAs)
	ETB = sum(switching_res.TBs)/len(switching_res.TBs)

	print("Expected TA: {}, Actual TA: {}".format(expected_TA, ETA))
	print("Expected TB: {}, Actual TB: {}".format(expected_TB, ETB))

	# Computing expected class 1 and 2 time

	expected_T1 = stay_prob*expected_TAQ + (1-stay_prob)*expected_TBQ + 1/mu1
	expected_T2 = stay_prob*expected_TBQ + (1-stay_prob)*expected_TAQ + 1/mu2

	ET1 = sum(switching_res.T1s)/len(switching_res.T1s)
	ET2 = sum(switching_res.T2s)/len(switching_res.T2s)

	print("Expected T1: {}, Actual T1: {}".format(expected_T1, ET1))
	print("Expected T2: {}, Actual T2: {}".format(expected_T2, ET2))

	# Check Little's Law for class 1, 2, A, and B jobs and overall
	EN1 = sum(switching_res.N1s)/len(switching_res.N1s)
	print("Little's Law holds for class 1? lambda1*ET1: {} = EN1: {}?".format(lambda1*ET1, EN1))

	EN2 = sum(switching_res.N2s)/len(switching_res.N2s)
	print("Little's Law holds for class 2? lambda2*ET2: {} = EN2: {}?".format(lambda2*ET2, EN2))

	ENA = sum(switching_res.NAs)/len(switching_res.NAs)
	print("Little's Law holds for class A? lambdaA*ETA: {} = ENA: {}?".format(lambdaA*ETA, ENA))

	ENB = sum(switching_res.NBs)/len(switching_res.NBs)
	print("Little's Law holds for class B? lambdaB*ETB: {} = ENB: {}?".format(lambdaB*ETB, ENB))

	EN = EN1 + EN2
	print("Little's Law holds overall? lambdaE[T]: {}, E[N]: {}".format(lambda1*ET1 + lambda2*ET2, EN))

parser = argparse.ArgumentParser(description='What settings do you want to run with?')
parser.add_argument('system', metavar='S', type=int, help='What system do you want to run? \\ 0. Basic FCFS \\ 1. Basic Two Queue NP', 
					default=0)

parser.add_argument('--num_runs', metavar='R', type=int, help = 'Number of runs in simulation', default = 100)
parser.add_argument('--num_jobs_per_run', metavar='J', type=int, help = 'Number of jobs per run in simulation', default = 1000)
parser.add_argument('--lambda_', metavar='lam', type=float, help = 'Arrival rate', default = 8)
parser.add_argument('--mu', metavar='mu', type=float, help = 'Service rate', default = 10)

parser.add_argument('--lambda1', metavar='lam1', type=float, help='Arrival rate for class 1', default = .7)
parser.add_argument('--lambda2', metavar='lam2', type=float, help='Arrival rate for class 2', default = 2)

parser.add_argument('--mu1', metavar='mu1', type=float, help = 'Service rate for class 1', default = 1)
parser.add_argument('--mu2', metavar='mu2', type=float, help = 'Service rate for class 2', default = 10)

parser.add_argument('--stay-prob', metavar='p', type=float, help = 'Routing probability', default = 0.8)
args = parser.parse_args()

FCFS = 0
NPBasic = 1
SWITCHING = 2

if args.system == FCFS:
	run_fcfs_basic(args.num_runs, args.num_jobs_per_run, args.lambda_, args.mu)
elif args.system == NPBasic:
	run_np_basic(args.num_runs, args.num_jobs_per_run, args.lambda1,
	             args.lambda2, args.mu1, args.mu2)
elif args.system == SWITCHING:
	run_switching_np(args.num_runs, args.num_jobs_per_run, args.lambda1, args.lambda2,
	                 args.mu1, args.mu2, args.stay_prob)