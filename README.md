# Queuing Simulation Library

This is a basic implementation of a couple different queuing systems. The systems currently implemented are:
1. M/G/1 FCFS Queue
2. Two class non-preemptive strict priority queue
3. Two class non-preemptive hybrid priority queue with switching algorithm

## M/G/1/FCFS Queue

## Strict NP Queue

## Hybrid NP Queue w/Switching Algorithm
To simulate this algorithm, enter the following
```
simulate.py 2 --num_runs= --num_jobs_per_run= --lambda1= --mu1= --lambda2= --mu2= --stay-prob=
```
The parameters are as follows:
* `num_runs`: number of runs in the simulation for the ensemble average
* `num_jobs_per_run`: measures the length of a particular run (number of completions of both classes)
* `lambda1`: arrival rate of class 1
* `mu1`: service rate of class 1 (assuming Exponential) (will add support for other distributions)
* `lambda2`: arrival rate of class 2
* `mu2`: service rate of class 2
* `stay-prob`: probability that a class 1 job is sent to class A (i.e. first priority) and class 2 job is sent to class B (i.e second priority)

# Acknowledgements
Much of the basic outline of the system is adapted from Ziv Scully's Quevent code. 
