import boto
from boto import s3
from boto.s3.key import Key
import os, glob
import subprocess
import sys
import logging
from datetime import datetime
import traceback
import socket

logging.basicConfig(level=logging.INFO)

# Fill these in - you get them when you sign up for S3
AWS_ACCESS_KEY_ID = '<your_aws_key>'
AWS_SECRET_ACCESS_KEY = '<your_aws_secret>'

SERVER_HOSTNAME = socket.gethostbyname(socket.gethostname())

conn = boto.connect_s3(AWS_ACCESS_KEY_ID,
            AWS_SECRET_ACCESS_KEY)


def get_files(dir, scribe_category):
    file_mask = scribe_category + '-*'
    print("Getting files for dir: " + dir + ", file_mask: " + file_mask)
    files = glob.glob( os.path.join(dir, file_mask) )
    clean_files = []
    for file in files:
        clean_file = os.path.abspath(file)
        print("Found file: " + clean_file)
        clean_files.append(clean_file)
    latest_file = os.path.realpath(os.path.join(dir, scribe_category + "_current"))
    print("Skipping latest file: " + latest_file)
    clean_files.remove(latest_file)
    return clean_files
            
      
def percent_cb(complete, total):
    sys.stdout.write('.')
    sys.stdout.flush()
    
def str2bool(v):
  return v.lower() in ["yes", "true", "t", "1"]

def move_files_to_s3(s3_bucket_name, scribe_category, files, delete_after_copy):

    today_datetime = datetime.utcnow()
    now = today_datetime.strftime("%Y-%m-%d_%H-%M")
    day_folder = today_datetime.strftime("dt=%Y-%m-%d")
    
    sub_folder = "category=" + scribe_category + '/' + day_folder + '/'
    
    if files and len(files) > 0:
        print "Moving files to S3 into sub_folder: " + str(sub_folder)
    else:
        print "No files to move to S3 at this time."
        return
    
    s3_backup_bucket_name = s3_bucket_name + "-backup"
    s3_backup_bucket = conn.get_bucket(s3_backup_bucket_name)
    if not s3_backup_bucket:
        s3_backup_bucket = conn.create_bucket(s3_backup_bucket_name,
            location=s3.connection.Location.DEFAULT)
    
    s3_bucket = conn.get_bucket(s3_bucket_name)
    if not s3_bucket:
        s3_bucket = conn.create_bucket(s3_bucket_name,
            location=s3.connection.Location.DEFAULT)
    
    for file in files:
        print "Processing file: " + str(file)
        try:
            filename = file
            if file.count('/') >= 1:
                filename = file[file.rfind('/')+1:]

            k = Key(s3_backup_bucket)
            k.key = sub_folder + filename + '_' + SERVER_HOSTNAME + '_' + now
            print 'Uploading %s to Amazon S3 bucket %s, from %s' % \
                   (k.key, s3_backup_bucket_name, file)
            k.set_contents_from_filename(file,
                    cb=percent_cb, num_cb=10)

            k = Key(s3_bucket)
            k.key = sub_folder + filename + '_' + SERVER_HOSTNAME + '_' + now
            print 'Uploading %s to Amazon S3 bucket %s, from %s' % \
                   (k.key, s3_bucket_name, file)
            k.set_contents_from_filename(file, cb=percent_cb, num_cb=10)

            if delete_after_copy:
                print 'Deleting %s' % (filename)
                os.remove(file)
        except:
            print "Error uploading file: " + file
            typ, info, trace = sys.exc_info()
            msg = "typ: %s, info: %s\n %s" %(str(typ), str(info), str(traceback.extract_tb(trace)))
            print msg


if len(sys.argv) < 5:
    print("Usage: <script> base_logging_dir scribe_category s3_bucket delete_after_copy")
else:
    try:
        print "\n-------------------------------\n"
        base_logging_dir = sys.argv[1]
        scribe_category = sys.argv[2]
        s3_bucket = sys.argv[3]
        dir = base_logging_dir + "/" + scribe_category
        files = get_files(dir, scribe_category)        
        move_files_to_s3(s3_bucket, scribe_category, files, str2bool(sys.argv[4]))
    except:
        print "Error moving scribe logs to S3"
        typ, info, trace = sys.exc_info()
        print "typ: " + str(typ) + ", info: " + str(info)
        print str(traceback.extract_tb(trace))
    
    
