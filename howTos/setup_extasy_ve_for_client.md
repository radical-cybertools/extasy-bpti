
# these are the command to run to set up the virtualenv on the client for running ExTASY

sudo apt install python-pip
apt-get install pip-install
pip install virtualenv

virtualenv extasy-tools
source extasy-tools/bin/activate
pip install -Iv radical.pilot==0.45.3 saga-python==0.45.1 radical.utils==0.45
radical-stack 
pip install radical.ensemblemd
ensemblemd-version


