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
ICM is a stochastic information diffusion model where the information flows over the network through Cascade. Nodes can have two states
	- (i) Active: It means the node already influenced by the information in diffusion.
	- (ii) Inactive: node unaware of the information or not influenced.
The process runs in discrete steps. At the beginning of ICM process, few nodes are given the information known as seed nodes. Upon receiving the information these nodes become active. In each discrete step, an active node tries to influence one of its inactive neighbors. In spite of its success, the same node will never get another chance to activate the same inactive neighbor. The success depends on the propagation probability of their tie. Propagation Probability of a tie is the probability by which one can influence the other node. In reality, Propagation Probability is relation dependent, i.e., each edge will have different value. However, for the experimental purpose, it is often considered to be same for all ties.
The process terminates when no further nodes became activated from inactive state.

Main functionalities
====================

The main functionalities offered by the program are:

- SIMULATION: 
- EXPECTED VALUE: 
- MAXIMIZE THE EXPECTED VALUE: 
- MAXIMIZE THE PROBABILITY TO REACH A NODE: 

Data retrive and manipulation phases
============
Collecting data from Twitter
----------
The model uses Twitter data. We use a Twitter API through tweepy(`<http://docs.tweepy.org/en/v3.5.0/>`_). 
In order for the model to work, we need to collect a set of tweets from the SOURCE. Once we have collected the tweets from the SOURCE we have to collect the set of replies that originated from each SOURCE's tweets. 

The are two main method for achiving this: get_people() and get_replies(). Since the Twitter API doesn't allow to retrive all the replies starting from the only tweet, we have to get all replies to the source, get all the replies related to the tweets that we want to analyze and save the people involved.

Those method are called for each person collected during the exploration phase, starting from the SOURCE in "recursive-like" way, performing get_replies() for each person and then get_people() to discover new nodes.

Graph building process
-----------
After the Data retrival step, we have to build a graph of replies for each tweet. We use graph_from_data() function to do that. 

Once the tweets-graph files are been written, we have to extract the informations related to the hashtags and create the union graph (from each tweet graph) because we have to make a model to perform the probability studies. For each collected hashtags we identify all the tweets graphs mentioning that hashtags in order to create a set of bitmasks (one for each hashtags) used to compare the similarity (Jaccard) of the hashtags in an efficient way. This will be needed in the following steps in order to suggest the best hashtag to use a specific situation (eg. suggest a second hashtag to use with one give in input).

To build a final graph we have to label the edges with the probability of that edges 




Here you can find a demo of the application:
https://www.youtube.com/watch?v=LHL-k30ffdg


Info & Contacts
===============

**Team**:

- `Andrea Bissoli <https://www.linkedin.com/in/andrea-bissoli-537768116/>`_
- `Fabrizio Farinacci <https://it.linkedin.com/in/fabrizio-farinacci-496679116/>`_
- Tommaso D'Orsi (tommasodorsi@gmail.com)

The project was developed and has been presented within the course of "Data Mining", 
held by Prof. Aris Anagnostopoulos, Sapienza University of Rome. Ioannis Chatzigiannakis, Sapienza University of Rome. Aristides Gionis, Aalto University within the Master of Science in Computer Science (MSE-CS),
at University of Rome "La Sapienza". Informations about the course are available in the following page:
http://www.aris.me/index.php/data-mining-2016.
