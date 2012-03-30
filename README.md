# About

LogCatcher is an efficient and scalable logging system based on [Scribe](https://github.com/facebook/scribe) and [Tornado](http://www.tornadoweb.org/).

Using Tornado to handle HTTP requests and Scribe to buffer and write files, LogCatcher is able to store logs at near-disk speeds (more than 50 MB/s per small [Amazon EC2](http://aws.amazon.com/ec2/) instance). 

Once the logs have been written to disk, they can be regularly moved to [Amazon S3](http://aws.amazon.com/s3/) or another reliable long-term storage solution via a simple shell script. 

By placing a load balancer such as Amazon's Elastic Load Balancer ([ELB](http://aws.amazon.com/elasticloadbalancing/)) in front of several EC2 instances each running an instance of the LogCatcher stack, we are able to easily divide the load over as many servers as necessary. 

Since ELBs support pinging the LogCatcher's built-in heartbeat handler, the load balancer can be easily configured to automatically direct load away from failing machines.Provisioning these machines in multiple AWS availability zones makes achieving fault tolerance just as easy.

[Pulse](http://www.pulse.me)’s implementation of LogCatcher easily handles millions of events per hour and has been running continuously for over a year without any downtime.


# Getting Started

Note: The example scripts are designed to be run on an ubuntu EC2 instance and may need to be modified to work in your environment.

1. Provisition a machine on EC2 or elsewhere.
2. Download and install [Scribe](https://github.com/facebook/scribe)
3. Download and install [Tornado](http://www.tornadoweb.org/)
4. git clone git@github.com:gregbayer/logcatcher.git
5. See the Config section to setup your scribe log directory.
5. cd logcatcher
6. example_scripts/start_scribe_and_tornado.sh


# Config

To setup the default scribe log directory (/mnt/scribe_logs/) on an Ubuntu EC2 instance with ELB storage, run this command.
    sudo chown -R ubuntu /mnt
    mkdir /mnt/scribe_logs

These lines in the following LogCatcher files should be modified for your own specific needs.

* scribe/scribe.conf
        file_path=**/mnt/scribe_logs/**

# Other Examples

* example_scripts/crontab.sh
       30 * * * * nohup /usr/bin/python <logcatcher dir>/example_scripts/move_scribe_logs_to_s3.py /mnt/scribe_logs/ <scribe_log_category> <s3_bucket> true >> <your_error_logs_dir>/move_scribe_logs_to_s3.log 2>&1


