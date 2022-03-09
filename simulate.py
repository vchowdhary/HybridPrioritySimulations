import argparse
import fcfs_system
import basic_np_system

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
    T1_runs, T2_runs, TQ1_runs, TQ2_runs, N1_runs, N2_runs = basic_system.simulate()

    ET1 = sum(T1_runs)/len(T1_runs)
    ET2 = sum(T2_runs)/len(T2_runs)

    ETQ1 = sum(TQ1_runs)/len(TQ1_runs)
    ETQ2 = sum(TQ2_runs)/len(TQ2_runs)

    EN1 = sum(N1_runs)/len(N1_runs)
    EN2 = sum(N2_runs)/len(N2_runs)

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
    print("E[T1]: {}, E[N1]: {}".format(ET1, EN1))
    print("E[T2]: {}, E[N2]: {}".format(ET2, EN2))
    print("Expected E[T1]: {}, Actual E[T1]: {}".format(goalT1, ET1))
    print("Expected E[T2]: {}, Actual E[T2]: {}".format(goalT2, ET2))
    print("Expected E[TQ1]: {}, Actual E[TQ1]: {}".format(expectedTQ1, ETQ1))
    print("Expected E[TQ2]: {}, Actual E[TQ2]: {}".format(expectedTQ2, ETQ2))
    print("Little's Law holds for class 1? lambda1E[T1]: {}, E[N1]: {}".format(lambda1*ET1, EN1))
    print("Little's Law holds for class 2? lambda2E[T2]: {}, E[N2]: {}".format(lambda2*ET2, EN2))
    print("Little's Law holds overall? lambdaE[T]: {}, E[N]: {}".format(lambda_*ET, EN))

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

args = parser.parse_args()

FCFS = 0
NPBasic = 1

if args.system == FCFS:
    run_fcfs_basic(args.num_runs, args.num_jobs_per_run, args.lambda_, args.mu)
elif args.system == NPBasic:
    run_np_basic(args.num_runs, args.num_jobs_per_run, args.lambda1,
                 args.lambda2, args.mu1, args.mu2)
