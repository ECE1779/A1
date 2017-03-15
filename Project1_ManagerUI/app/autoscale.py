import boto3
import time
from datetime import datetime, timedelta
from operator import itemgetter


from app.config import *

def background_monitor():
    ec2 = boto3.resource('ec2')
    global high_threshold 
    global low_threshold
    global grow_ratio
    global shrink_ratio
    while True:
        """
        all_ec2_instances = ec2.instances.all()
        for instance in all_ec2_instances:
            if instance.tags is not None:
                for tag in instance.tags:
                    if tag['Key'] == 'Role' \
                            and tag['Value'] == 'worker' \
                            and instance.state.get('Name') == 'running':
                        cpu = worker.get_worker_utilization(instance.id)
                        max_cpu = 0
                        min_cpu = 100
                        for point in cpu['Datapoints']:
                            max_cpu = max(max_cpu, point['Maximum'])
                            min_cpu = min(min_cpu, point['Minimum'])
                            avg_cpu = point['Average']
                        print(
                            instance.id + ": max: " + str(max_cpu) + " min: " + str(min_cpu) + " avg: " + str(avg_cpu))
                        if max_cpu > high_cpu_threshold:
                            grow_pool()
                        elif max_cpu < low_cpu_threshold:
                            shrink_pool()


        """
        print(str(high_threshold) + " " + str(low_threshold) + " "  +str(grow_ratio) + " " + str(shrink_ratio))
        avg_cpu = 0
        total_cpu = 0
        active_worker_count = 0


        global elb_worker_pool
        client = boto3.client('elb')
        response = client.describe_instance_health(
            LoadBalancerName='PRJ1-LB',
        )
        for instances in response["InstanceStates"]:
            elb_worker_pool.update({instances["InstanceId"]:"true"})
            
        print(elb_worker_pool)
        for instance_id, status in elb_worker_pool.items():
            if status == "true":
                #get cpu

                cpu = get_worker_utilization(instance_id)
                current_instance_cpu = float(cpu['Datapoints'][0]['Average'])
                
                total_cpu += current_instance_cpu
                active_worker_count += 1
                
        avg_cpu = total_cpu / active_worker_count
        print(str(active_worker_count) + " workers  " + str(avg_cpu) + " avg cpu")
        if avg_cpu > high_threshold:
            grow_pool()
            
        if avg_cpu < low_threshold:
            shrink_pool()

        time.sleep(10)
    return


def grow_pool():
    print("grow")
    global high_threshold 
    global low_threshold
    global grow_ratio
    global shrink_ratio
    global elb_worker_pool
    
    active_worker_count = 0
    for instance_id, status in elb_worker_pool.items():
        if status == "true":
            active_worker_count += 1

    expected_worker_count = active_worker_count * grow_ratio
    if expected_worker_count > 4:
        expected_worker_count = 4


    active_worker_count = 0
    for instance_id, status in elb_worker_pool.items():
        if status == "true":
            active_worker_count += 1
        if status == "false" and active_worker_count < expected_worker_count:
            elb_worker_pool[instance_id] = "true"
            #add to pool 

            client = boto3.client('elb')
            
            response = client.register_instances_with_load_balancer(
            Instances=[{'InstanceId':instance_id,},], LoadBalancerName = 'PRJ1-LB',
            )
            
            active_worker_count += 1

    return


def shrink_pool():
    print("shrink")
    global high_threshold 
    global low_threshold
    global grow_ratio
    global shrink_ratio
    global elb_worker_pool
    active_worker_count = 0
    for instance_id, status in elb_worker_pool.items():
        if status == "true":
            active_worker_count += 1
    print(str(active_worker_count) + " workers")
    expected_worker_count = active_worker_count / grow_ratio
    if expected_worker_count < 1:
        expected_worker_count = 1



    for instance_id, status in elb_worker_pool.items():
        if status == "true" and active_worker_count > expected_worker_count:
            active_worker_count -= 1
            # Remove instane to Elastic Load Balancer
            elb_worker_pool[instance_id] = "false"
            client = boto3.client('elb')
            
            response = client.deregister_instances_from_load_balancer(
            Instances=[{'InstanceId':instance_id,},], LoadBalancerName = 'PRJ1-LB',
            )
            print("removing " + instance_id)



    return



def get_worker_utilization(id):
    ec2 = boto3.resource('ec2')

    client = boto3.client('cloudwatch')

    metric_name = 'CPUUtilization'

    #    CPUUtilization, NetworkIn, NetworkOut, NetworkPacketsIn,
    #    NetworkPacketsOut, DiskWriteBytes, DiskReadBytes, DiskWriteOps,
    #    DiskReadOps, CPUCreditBalance, CPUCreditUsage, StatusCheckFailed,
    #    StatusCheckFailed_Instance, StatusCheckFailed_System

    namespace = 'AWS/EC2'
    statistic = 'Average'  # could be Sum,Maximum,Minimum,SampleCount,Average

    cpu = client.get_metric_statistics(
        Period=1 * 60,
        StartTime=datetime.utcnow() - timedelta(seconds=2 * 60),  # go two minutes back
        EndTime=datetime.utcnow() - timedelta(seconds=0 * 60),
        MetricName=metric_name,
        Namespace=namespace,  # Unit='Percent',
        Statistics=['Average', 'Maximum', 'Minimum'],
        Dimensions=[{'Name': 'InstanceId', 'Value': id}]
    )

    cpu_stats = []

    for point in cpu['Datapoints']:
        hour = point['Timestamp'].hour
        minute = point['Timestamp'].minute
        time = hour + minute / 60
        cpu_stats.append([time, point['Average']])

    cpu_stats = sorted(cpu_stats, key=itemgetter(0))

    return cpu
