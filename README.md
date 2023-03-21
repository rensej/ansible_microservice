# ansible_microservice
Ansible container for execute mobility related playbooks

# To Build Image (from folder containig Dockerfile):

docker image build --tag ansible:latest .

# To create container

docker run --name ansible -dt --mount type=bind,src=[binded volume],dst=/binded ansible:latest
