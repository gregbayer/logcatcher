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
2. Download & build & install [Scribe](https://github.com/facebook/scribe). You may also need to build/install Scribe dependencies like [boost](http://www.boost.org/).
3. Download & install [Tornado](http://www.tornadoweb.org/)
4. git clone git@github.com:gregbayer/logcatcher.git; cd logcatcher
6. See the Config section to setup your scribe log directory.
7. example_scripts/start_scribe_and_tornado.sh


# Config

The default scribe log directory is set to /mnt/scribe_logs/ in the example scripts. This is where the logs that are collected by LogCatcher will be stored. Optionally, you can use a script like example_scripts/move_scribe_logs_to_s3 to move completed log files after they roll.

To setup the default scribe log directory on an Ubuntu EC2 instance with ELB storage, run these commands:

        sudo chown -R ubuntu /mnt
        mkdir /mnt/scribe_logs

Update the following line in this file if you want to use a different directory. See Other Examples for more places you'll have to update this directory if you want to use the other example scripts.

* scribe/scribe.conf

		file_path=/mnt/scribe_logs/

# Example scripts

Strings to update:

* \<logcatcher dir\>  		---	Ex. /home/ubuntu/logcatcher
* <scribe_log_directory>	---	Ex. /mnt/scribe_logs/
* <scribe_log_category> 	---	Ex. application1
* <your_s3_bucket>			---	Ex. my-amazon-s3-bucket
* <your_error_logs_dir>		---	Ex. /home/ubuntu/logcatcher/logs
* <your_aws_key>			--- Ex. zxcabnfiuafabfkabfjka
* <your_aws_secret>			--- Ex. dvzxc+abnfi+uafabfkasdbfjkavzd

Starting LogCatcher:

* start_scribe_and_tornado.sh  --- if you want to run this script from anywhere, consider making the paths absolute.

		nohup scribed -c scribe/scribe.conf >> logs/scribe.log 2>&1 &
		sudo nohup python tornado/catch_logs.py >> logs/tornado.log 2>&1 &

Regularly moving logs to S3:

You will need to install [boto](https://github.com/boto/boto).

* example_scripts/crontab.sh

		30 * * * * nohup /usr/bin/python <logcatcher dir>/example_scripts/move_scribe_logs_to_s3.py <scribe_log_directory> <scribe_log_category> <your_s3_bucket> true >> <your_error_logs_dir>/move_scribe_logs_to_s3.log 2>&1

* example_scripts/move_scribe_logs_to_s3.py

		AWS_ACCESS_KEY_ID = '<your_aws_key>'
		AWS_SECRET_ACCESS_KEY = '<your_aws_secret>'
