---

title: Home
layout: home
nav_order: 1
permalink: /

---

Welcome to the QSSH (Quantum Secure Shell Protocol) project. For an overview of the goals please start with the [Statement of Work]({{ site.url }}/sow/). 

**Goal:** To demonstrate the power of quantum communication through the generation of identity confirming and data encrypting keys.

Alice and Bob want to communicate secretly. To do so they need a secure key to encode their message and verify each other's identities in the future. However, Eve, who has nefarious intent, wants to eavesdrop. Through the use of QKD Alice and Bob can generate a key that Eve will never be able to crack ensuring their communication is 100% secure. The goal of QSSH is to guarantee secure communication between a user and a server. 

__Not sure what to be working on__: check the [projects page](https://github.com/users/st4eve/projects/1/views/3?layout=table)

## Meeting Notes
**Meeting Time:** Thursday at 20:00

- [November 11th, 2023]({{ site.url }}/meeting_notes/nov_11_2023.html)
- [November 16th, 2023]({{ site.url }}/meeting_notes/nov_16_2023.html)
- [November 23rd, 2023]({{ site.url }}/meeting_notes/nov_23_2023.html)
- [November 30th, 2023]({{ site.url }}/meeting_notes/nov_30_2023.html)
- [January 21st, 2024]({{ site.url }}/meeting_notes/jan_21_2024.html)
- [January 28th, 2024]({{ site.url }}/meeting_notes/jan_28_2024.html)
- [February 4th, 2024]({{ site.url }}/meeting_notes/feb_4_2024.html)
- [February 18th, 2024]({{ site.url }}/meeting_notes/feb_18_2024.html)

## Resources
Compiled below are some resources to learn about topics in the project. 

In [QKD]({{ site.url }}/#qkd) there are several resources for learning about quantum key distribution and quantum computing. For an up to date universal explanation of all things quantum I recommend _Musty Thoughts_. In [Python Networking](#python-networking) there are resources for basic communication in python. In [SSH](#ssh) there is an explanation of the SSH algorithm.

### QKD

- [BB84 algorithm explanation video](https://www.youtube.com/watch?v=2kdRuqvIaww)
- [Qiskit textbook](https://learning.quantum-computing.ibm.com/catalog)
- [Qiskit QKD tutorial](https://learn.qiskit.org/course/ch-algorithms/quantum-key-distribution)
- [Quantum computing with pennylane](https://pennylane.ai/qml/quantum-computing/)
- [Pennylane coding challenges](https://pennylane.ai/challenges/)
- [Musty Thoughs blog](https://www.mustythoughts.com)

### Python Networking

- [LAN socket connection using pyhton](https://www.siglenteu.com/application-note/open-socket-lan-connection-using-python/)
- [Socket programming in python](https://realpython.com/python-sockets/)

### SSH
- [Intro to ssh communication](https://www.youtube.com/watch?v=5JvLV2-ngCI)

### Setting up VMs
- [Setting up a VM]({{site.url}}/vm_setup.html)
