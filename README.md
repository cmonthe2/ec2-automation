# ec2-automation

this project automate deployement of ec2-intsance with 2 users created via user-data and 2 volumes attached to the created instance using python3.
the instance configuration are provided in a YMAL file who is parsed during the automation and applied values to the resources that will be creation.
everything is automanted end to end .

# PREREQUISITE:
## Running Locally
  - user must have python3 installed 
  - AWS **access_key and secret_access_key** 
  - aws set of permission (create instances , create key_pair, create security group )
 you can make use of **aws configure** command to set a default aws credential in your local 
 
 ## Download Dependencies
 
 Download Dep.

pip3 install -r requirements.txt

#Running the Program with
Pretending to blow things up

change the permision to the file **ec2_script.py** to make it executable 

- **chmod +x ec2_script.py**
then run the program
- $ ./**ec2_script.py**

/Users/user/Desktop/ec2-automation/lookup.yaml

Successfully created Volume! vol-0d0a5be8a551191d0

Volume is available for use 

security-group ID: sg-0516174162e571a77

ec2_instance_Id: i-0c37087550c224fc0

instance in running state

instance is provisioning ..... 

##post-run step
after the program successfully run , it will generate a file **key-pair** file to your "presence working directory" call my-test-key.pem.  this file contain the
ssh-key needed to connect to your ec2 instance for all users.

###NOTE:
make sure to change the key permission to read only before using it : example : **chmod 400 my-test-key.pem**

now you can ssh to you ec2-insatnce 


