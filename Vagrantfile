# -*- mode: ruby -*-
# vi: set ft=ruby :

Vagrant.configure("2") do |config|
  #base box
  config.vm.box = "ubuntu/bionic64"
  
  #hostname
  config.vm.hostname = "testvm"
  
  #ports
  config.vm.network "forwarded_port", guest: 80, host: 8080
  config.vm.network "forwarded_port", guest: 443, host: 4443

  config.vm.provider "virtualbox" do |vb|
    # Customize the amount of memory on the VM:
    vb.memory = "4096"   
    # set vm name
    vb.name = "testvm"
  end

  
  #docker
  config.vm.provision "docker" do |d|    
    d.post_install_provision "shell", inline: <<-SHELL
      sudo echo "alias net-pf-10 off" >> /etc/modprobe.d/ipv6.conf
      sudo echo "options ipv6 disable_ipv6=1" >> /etc/modprobe.d/ipv6.conf
      sudo echo "blacklist ipv6" >> /etc/modprobe.d/ipv6.conf
      
      sudo echo "net.ipv6.conf.all.disable_ipv6 = 1" >> /etc/sysctl.conf
      sudo echo "net.ipv6.conf.default.disable_ipv6 = 1" >> /etc/sysctl.conf
      sudo echo "net.ipv6.conf.lo.disable_ipv6 = 1" >> /etc/sysctl.conf
      sudo sysctl -p
    SHELL
  end
  config.vm.provision "docker_compose"
  
  config.vm.provision "shell", inline: "sudo usermod -aG docker ${USER}"
  config.vm.provision "shell", inline: "sudo apt-get -y install python3-pip"

end
