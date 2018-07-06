
# follow the notes at these links to get going 

#installing gsissh 
https://github.com/vivek-bala/docs/blob/master/misc/gsissh_setup_stampede_ubuntu_xenial.sh/


#do the following 

https://askubuntu.com/questions/249881/how-do-i-install-globus-toolkit


sudo apt-get install globus-proxy-utils globus-simple-ca
sudo apt-get install gsi-openssh
sudo apt-get install gsi-openssh-clients
sudo apt-get install myproxy


sudo echo "deb http://repository.egi.eu/sw/production/cas/1/current egi-igtf core" >> egi-igtf-core.list
# note you can do instead of echo same thing using "sudo vi"
sudo apt-get update
sudo apt-get install ca-policy-egi-core


sudo apt-get upgrade 

