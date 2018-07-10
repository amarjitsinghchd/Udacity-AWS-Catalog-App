# -*- mode: ruby -*-
# vi: set ft=ruby :

Vagrant.configure("2") do |config|
  Vagrant::DEFAULT_SERVER_URL.replace('https://vagrantcloud.com')
  config.vm.box = "bento/ubuntu-16.04-i386"
  config.vm.box_version = "= 2.3.5"
  config.vm.network "forwarded_port", guest: 8000, host: 8000, host_ip: "127.0.0.1"
  config.vm.network "forwarded_port", guest: 8080, host: 8080, host_ip: "127.0.0.1"
  config.vm.network "forwarded_port", guest: 5000, host: 5000, host_ip: "127.0.0.1"

  # Work around disconnected virtual network cable.
  config.vm.provider "virtualbox" do |vb|
    vb.customize ["modifyvm", :id, "--cableconnected1", "on"]
  end

  config.vm.provision "shell", inline: <<-SHELL
    apt-get -qqy update

    # Work around https://github.com/chef/bento/issues/661
    # apt-get -qqy upgrade
    DEBIAN_FRONTEND=noninteractive apt-get -y -o Dpkg::Options::="--force-confdef" -o Dpkg::Options::="--force-confold" upgrade

    apt-get -qqy install make zip unzip postgresql

    sudo apt-get -qqy install python3 python3-pip
    sudo pip3 install --upgrade pip
    sudo pip3 install flask packaging oauth2client redis passlib flask-httpauth flask-wtf
    sudo pip3 install sqlalchemy flask-sqlalchemy psycopg2 bleach requests

    # Added by Amarjit to Support Flask WTF forms 
    sudo pip install flask-bootstrap
    sudo pip install -U Flask-WTF
    # Added by Amarjit to support Goolge Oauth2
    sudo pip install --upgrade google-api-python-client
    sudo pip install --upgrade google-auth google-auth-oauthlib google-auth-httplib2
    sudo pip install --upgrade flask
    sudo pip install --upgrade requests
    sudo pipenv install requests
    
    sudo apt-get -qqy install python python-pip
    sudo pip2 install --upgrade pip
    sudo pip2 install flask packaging oauth2client redis passlib flask-httpauth flask-wtf
    sudo pip2 install sqlalchemy flask-sqlalchemy psycopg2 bleach requests

    su postgres -c 'createuser -dRS vagrant'
    su vagrant -c 'createdb'
    su vagrant -c 'createdb news'
    su vagrant -c 'createdb forum'
    su vagrant -c 'psql forum -f /vagrant/forum/forum.sql'

    vagrantTip="[35m[1mThe shared directory is located at /vagrant\\nTo access your shared files: cd /vagrant[m"
    echo -e $vagrantTip > /etc/motd

    wget http://download.redis.io/redis-stable.tar.gz
    tar xvzf redis-stable.tar.gz
    cd redis-stable
    make
    make install

    echo "Done installing your virtual machine!"
  SHELL
end
