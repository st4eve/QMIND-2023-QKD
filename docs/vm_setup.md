---

title: VM Setup
layout: default
nav_order: 3
permalink: /

---

# VM Setup
For this project we will use three different virtual machines to simulate Alice, Bob, and Eve. Alice and Bob will use the Ubuntu Linux OS while Eve will use Kali Linux OS. To start download virtual box using this [link](https://www.virtualbox.org/wiki/Downloads). 
### Alice and Bob
Once installed download a single Ubunutu iso file using this [link](https://ubuntu.com/download/desktop). The single iso file can be used for both VM's. In virtual box click the add button and create two vm's for alice and bob. **Note: please set a password (perferrably easy one) for both.** Use all default settings for creating the VM. 
Close all VM's and return the virtualbox menu screen click on one of the VM's and click the settings button. Enter the Network page (left side) and set the adapter 1 to 'bridged adapter'. Click the 'adapter 2' tab and enabled it setting it also to 'bridged adapter'. **Note: This must be done for both Alice and Bob**
Enter the VM again and check if python is install by using 'python3 --version' in terminal. If the command is not reconnized you have to do download it from online or add it to the environment path folder (Ask chatgpt or use youtube).
Once your able to execute python scripts you can use the server and client python scripts in the github to send communications between vm's. **Note: the scripts will require you to enter the vm's IP and password**

### Eve
You can download the Kali Linux iso [here](https://www.kali.org/get-kali/#kali-platforms). The setup is the same as above here, use default settings and set a password. Futhermore, the network settings will also have to be set using the same method as above. Click the serach button in the OS and make sure both Wireshark and Ettercap are installed, if not follow this [tutorial to install](https://www.youtube.com/watch?v=sXhuo_as7L8&ab_channel=fenterprises). Use eth1 as the adapter when using Wireshark and Ettercap to monitoring the traffic.