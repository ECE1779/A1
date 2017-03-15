'''import boto3
elb = boto3.client('elb')
print(elb.describe_load_balancers())
'''
from app.config import aws_config, auto_scaling_config
from load_balancer_actions import LoadBalancerActions

import boto3, time, os, threading


class AutoScaling(object):
    def __init__(self, interval=1):
        self.interval = interval
        thread = threading.Thread(target=self.run, args=())
        thread.daemon = True
        thread.start()

    def run(self):
        print 'Start auto-scaling'
        while True:
            elb = boto3.client('elb')
            instances = \
            elb.describe_load_balancers(LoadBalancerNames=[aws_config['ELB_NAME']]).get('LoadBalancerDescriptions')[
                0].get('Instances')
            currNumOfWorkers = len(instances)

            lbActions = LoadBalancerActions()
            cpu_stat = lbActions.total_cpu_usage()
            if cpu_stat < auto_scaling_config['CPU_THRESHOLD_GROW']:
                factor = auto_scaling_config['WORKER_POOL_RATIO_EXPAND']
                numOfWorkersToSpawn = (currNumOfWorkers * factor) - currNumOfWorkers
                print 'Auto-scaling: spawning %s new workers...' % (numOfWorkersToSpawn)
                lbActions.spawn_workers(numOfWorkersToSpawn)
            elif cpu_stat > auto_scaling_config['CPU_THRESHOLD_SHRINK']:
                if currNumOfWorkers != 1:
                    factor = auto_scaling_config['WORKER_POOL_RATIO_SHRINK']
                    numOfWorkersToKill = currNumOfWorkers - int(round(currNumOfWorkers / (factor * 1.0)))
                    print 'Auto-scaling: killing %s workers...' % (numOfWorkersToKill)
                    lbActions.kill_workers(numOfWorkersToKill)
                else:
                    print 'Auto-scaling: load balancer only has 1 existing instance. We will not shrink beyond this number'
            time.sleep(self.interval)


autoScaling = AutoScaling(5000)

