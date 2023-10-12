FROM ubuntu:20.04

#install ansible
RUN apt update && DEBIAN_FRONTEND=noninteractive apt install -y software-properties-common && add-apt-repository --yes --update ppa:ansible/ansible && apt install -y ansible vim git

#install docker module
RUN ansible-galaxy collection install community.docker
 
# ansible output defaults
RUN echo '[defaults]' >> /etc/ansible/ansible.cfg  && echo '# Human-readable output' >> /etc/ansible/ansible.cfg  && echo 'stdout_callback = yaml' >> /etc/ansible/ansible.cfg && echo 'host_key_checking = False' >> /etc/ansible/ansible.cfg
