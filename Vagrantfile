# -*- mode: ruby -*-
# vi: set ft=ruby :

VAGRANTFILE_API_VERSION = "2"

Vagrant.configure(VAGRANTFILE_API_VERSION) do |config|

    config.vm.define "linux", primary: true do |v|
        v.vm.provision "shell", path: "vagrant.sh"        
        v.vm.box = "chef/debian-7.4"
    end

    config.vm.provider "virtualbox" do |v|
        v.memory = 1024
    end

end
