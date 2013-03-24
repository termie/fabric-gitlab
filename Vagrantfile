# -*- mode: ruby -*-
# vi: set ft=ruby :

Vagrant::Config.run do |config|
  config.vm.box = "precise"
  config.vm.box_url = "http://files.vagrantup.com/precise64.box"
  # config.vm.boot_mode = :gui
  config.vm.network :hostonly, "192.168.33.10"
  config.vm.network :bridged
  config.vm.forward_port 80, 8080
end
