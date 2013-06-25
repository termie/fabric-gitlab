# -*- mode: ruby -*-
# vi: set ft=ruby :

Vagrant::Config.run do |config|
  config.vm.box = "raring64"
  config.vm.box_url = "http://cloud-images.ubuntu.com/raring/current/raring-server-cloudimg-vagrant-amd64-disk1.box"
  config.vm.customize ["modifyvm", :id, "--memory", 1024]
  # config.vm.boot_mode = :gui
  config.vm.network :hostonly, "192.168.33.10"
  #config.vm.network :bridged
  #config.vm.forward_port 80, 8080
end
