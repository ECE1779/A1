from flask import render_template, redirect, url_for, request
from app import webapp

import boto3
from app import config
from datetime import datetime, timedelta
from dateutil import tz

from operator import itemgetter


@webapp.route('/manager_UI',methods=['GET'])
# Display an HTML list of all ec2 instances
def ec2_list():

    # create connection to ec2
    ec2 = boto3.resource('ec2')

   # instances = ec2.instances.filter(
   # Filters=[{'Name': 'instance-state-name', 'Values': ['running']}])

    instances = ec2.instances.all()

    return render_template("manager_UI/list.html",title="Worker Pool Management",instances=instances)


@webapp.route('/manager_UI/<id>',methods=['GET'])
#Display details about a specific instance.
def ec2_view(id):
    ec2 = boto3.resource('ec2')

    instance = ec2.Instance(id)

    client = boto3.client('cloudwatch')

    metric_name = 'CPUUtilization'

    ##    CPUUtilization, NetworkIn, NetworkOut, NetworkPacketsIn,
    #    NetworkPacketsOut, DiskWriteBytes, DiskReadBytes, DiskWriteOps,
    #    DiskReadOps, CPUCreditBalance, CPUCreditUsage, StatusCheckFailed,
    #    StatusCheckFailed_Instance, StatusCheckFailed_System


    namespace = 'AWS/EC2'
    statistic = 'Average'                   # could be Sum,Maximum,Minimum,SampleCount,Average



    cpu = client.get_metric_statistics(
        Period=1 * 60,
        StartTime=datetime.utcnow().replace(tzinfo=tz.tzutc()).astimezone(tz.gettz('America/New_York'))- timedelta(seconds=60 * 60),
        EndTime=datetime.utcnow().replace(tzinfo=tz.tzutc()).astimezone(tz.gettz('America/New_York')) - timedelta(seconds=0 * 60),
        MetricName=metric_name,
        Namespace=namespace,  # Unit='Percent',
        Statistics=[statistic],
        Dimensions=[{'Name': 'InstanceId', 'Value': id}]
    )

    cpu_stats = []


    for point in cpu['Datapoints']:
        hour = point['Timestamp'].hour
        minute = point['Timestamp'].minute
        time = hour + minute/60
        cpu_stats.append([time,point['Average']])

    cpu_stats = sorted(cpu_stats, key=itemgetter(0))


    statistic = 'Sum'  # could be Sum,Maximum,Minimum,SampleCount,Average

    return render_template("manager_UI/view.html",title="Worker Instance Information",
                           instance=instance,
                           cpu_stats=cpu_stats,
                           )

@webapp.route('/manager_UI/create',methods=['POST'])
# Start a new EC2 instance
def ec2_create():

    ec2 = boto3.resource('ec2')

    ec2.create_instances(ImageId=config.ami_id, MinCount=1, MaxCount=1)
    InstanceType='t2.small',
    SubnetId='subnet-0c0f0f45'

    return redirect(url_for('ec2_list'))


@webapp.route('/manager_UI/<id>',methods=['POST'])
# Terminate a EC2 instance
def elb_register(id):
    # Add instane to Elastic Load Balancer
    
    client = boto3.client('elb')
    
    response = client.register_instances_with_load_balancer(
    Instances=[{'InstanceId':id,},], LoadBalancerName = 'PRJ1-LB',
    )
    
    return redirect(url_for('ec2_list'))


@webapp.route('/manager_UI/stop/<id>',methods=['POST'])
# Stop a EC2 instance
def elb_deregister(id):
    # Remove instane to Elastic Load Balancer

    client = boto3.client('elb')
    
    response = client.deregister_instances_from_load_balancer(
    Instances=[{'InstanceId':id,},], LoadBalancerName = 'PRJ1-LB',
    )
    
    return redirect(url_for('ec2_list'))

@webapp.route('/manager_UI/start/<id>',methods=['POST'])
# Terminate a EC2 instance
def ec2_start(id):
    # create connection to ec2
    ec2 = boto3.resource('ec2')

    ec2.instances.filter(InstanceIds=[id]).start()

    return redirect(url_for('ec2_list'))

@webapp.route('/manager_UI/autoscale',methods=['GET'])
# Display an empty HTML form that allows users to define new student.
def auto_scale():
    return render_template("manager_UI/autoscale.html",title="Auto Scale Policy")

@webapp.route('/manager_UI/autoscale',methods=['POST'])
def auto_scale_policy():
    maxCPU = request.form.get('Max CPU Usage (%) for Scale up',"")
    minCPU = request.form.get('Min CPU Usage (%) for Scale down',"") 
    scale_up_ratio = request.form.get('Scale Up Ratio',"")
    scale_down_ratio = request.form.get('Scale Down Ratio',"")     
    
    return redirect(url_for('ec2_list'))


