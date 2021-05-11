# Code for  Pooled Ordered Rectangular Testing
Based on paper PORT: Pooled Ordered Rectangular Testing for Improved Public Health Screening  by Terrance E. Boult, Yanyan Zhuang  which  will appear in the 2021 IEEE 9th International Conference on Healthcare Informatics (ICHI). Thanks to supporting project members K. Paulson  C. M. Vander Zanden, A. Nashikkar, N. Windesheim, and S. Zhou   for their contributions/discussions. Espeically K. Paulson and N. Windesheim who both worked on the code development and testing. 

# Usage instructions

```git clone https://github.com/Vastlab/PORT.git```

From the root of the cloned directory:

```
docker build -t $name .
docker run -dp $host_port:80 $name
```

The flask container should now be running on the host's port that you chose to map with $host_port.
