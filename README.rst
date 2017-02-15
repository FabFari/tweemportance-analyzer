.. line-block::

	**University of Rome "La Sapienza"**
	*Master of Science in Engineering in Computer Science*
	*Data Mining, a.y. 2016-17*
	Data Mining Group Project by Andrea Bissoli and Tommaso D'Orsi and Fabrizio Farinacci

Tweemportance-analyzer
=======


Tweemportance-analyzer uses **Independent Cascade Model (ICM)** to analyze interelation between replies and hashtag used focusing on one specific person (the SOURCE of information) and building a model to suggest the source which hashtag to use in order to achive its visibility goals.

Independent Cascade Model (ICM)
--------
ICM is a stochastic information diffusion model where the information flows over the network through Cascade. Nodes can have two states, (i) Active: It means the node already influenced by the information in diffusion. (ii) Inactive: node unaware of the information or not influenced.
The process runs in discrete steps. At the beginning of ICM process, few nodes are given the information known as seed nodes. Upon receiving the information these nodes become active. In each discrete step, an active node tries to influence one of its inactive neighbors. In spite of its success, the same node will never get another chance to activate the same inactive neighbor. The success depends on the propagation probability of their tie. Propagation Probability of a tie is the probability by which one can influence the other node. In reality, Propagation Probability is relation dependent, i.e., each edge will have different value. However, for the experimental purpose, it is often considered to be same for all ties.
The process terminates when no further nodes became activated from inactive state.

- Helping patients to follow their therapies, simplifying the communication with the health care assistants
- Giving health care assistants a simple and useful tool to keep track of the therapies of their assisted

Main functionalities
====================

The main functionalities offered by the application are:

- Record vital signs and nursing prescriptions, keeping track of your progress within long term treatments
- Manage a shared Google Calendar with your caregiver (and all those you would like to monitor your health progresses), with all your current treatments and performed measurements
- Send mail notifications through Google calendar, to remind you about your therapeutic requirements
- The possibility to contact, directly from the application, your caregivers and family members

Architecture
============



The frontend is a mobile application (Android).
The backend is a Python application running on Google App Engine.
The frontend interacts with a Web Service API offered by the GAE backend through Google Cloud Endpoints
Through the GAE backend, the app access to:
Google + API, to register the user
Google Calendar API, to store the history of measurement and therapies and to notify the user about its therapeutical requirements.

Demo
----

Here you can find a demo of the application:
https://www.youtube.com/watch?v=LHL-k30ffdg


Info & Contacts
===============

**Team**:

- `Andrea Bissoli <https://www.linkedin.com/in/andrea-bissoli-537768116/>`_
- `Fabrizio Farinacci <https://it.linkedin.com/in/fabrizio-farinacci-496679116/>`_
- `Tommaso D'Orsi tommasodorsi@gmail.com`_

The project was developed and has been presented within the course of "Pervasive Systems", 
held by Prof. Ioannis Chatzigiannakis within the Master of Science in Computer Science (MSE-CS),
at University of Rome "La Sapienza". Informations about the course are available in the following page:
http://ichatz.me/index.php/Site/PervasiveSystems2016.

Additional informations about the project can be found in the following Slideshare presentations:

- http://www.slideshare.net/FabrizioFarinacci1/recipex-your-personal-caregiver-and-lifestyle-makeover
- http://www.slideshare.net/FabrizioFarinacci1/recipex-your-personal-caregiver-and-lifestyle-makeover-62091050

