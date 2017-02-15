.. line-block::

	**University of Rome "La Sapienza"**
	*Master of Science in Engineering in Computer Science*
	*Data Mining, a.y. 2016-17*
	Data Mining Group Project by Andrea Bissoli, Tommaso D'Orsi and Fabrizio Farinacci

Tweemportance-analyzer
=======

The aim of this software is to suggest a more efficient use of hashtags on Twitter, given the previous history of the subject and his audience. That is, it provides a mean to maximize the probability of reaching a wider audience and/or reaching some desired person.

Tweemportance-analyzer uses **Independent Cascade Model (ICM)** to analyze interelation between replies and hashtag used focusing on one specific person (the SOURCE of information) and building a model to suggest the source which hashtag to use in order to achive its visibility goals.

Independent Cascade Model (ICM)
--------
ICM is a stochastic information diffusion model where the information flows over the network through Cascade. Nodes can have two states
	- (i) Active: It means the node already influenced by the information in diffusion.
	- (ii) Inactive: node unaware of the information or not influenced.
The process runs in discrete steps. At the beginning of ICM process, few nodes are given the information known as seed nodes. Upon receiving the information these nodes become active. In each discrete step, an active node tries to influence one of its inactive neighbors. In spite of its success, the same node will never get another chance to activate the same inactive neighbor. The success depends on the propagation probability of their tie. Propagation Probability of a tie is the probability by which one can influence the other node. In reality, Propagation Probability is relation dependent, i.e., each edge will have different value. However, for the experimental purpose, it is often considered to be same for all ties.
The process terminates when no further nodes became activated from inactive state.

Main functionalities
===================
The four main functionalities of the program are the following:
	- SIMULATION: Given a potential tweet of the source, the software simulates a possible outcome of the tweet, that is, given the hashtags of a tweet, the software executes a run of the independent cascade model and returns the outcome.
	- EXPECTED VALUE: Given a potential tweet of the source, the software estimates the expected outcome of the tweet. More specifically *Tweemportance-analyzer* computes the expected number of nodes in the graph reached  by the tweet, and for each node, returns the probability of that node being involved in the discussion.
	- MAXIMIZE EXPECTED VALUE: Given a potential tweet of the source, the software obtains through ranking aggregation the potentially most suitable hashtags the source could include in the tweet. For each  of those candidates, it estimates the outcome of the tweet if the candidate would be included. Finally the program returns the hashtags that provides, in expectation, a better outcome.
	- MAXIMIZE PROBABILITY TO REACH TARGET NODE: Given a potential tweet of the source, and a target node the source is trying to reach, the software finds both the hashtags the target is most interested into, and the hashtags that could be included in the tweet. Aggregating and ranking the results, it then computes, through diverse routing, which solutions provide the highest probability of reaching the target node.


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

Once the tweets-graph files are been written, we have to extract the informations related to the hashtags and create the union graph (from each tweet graph) as we have to make a model to perform the probability studies. For each collected hashtag we identify all the tweet-graphs mentioning that hashtag in order to create a set of bitmasks (one for each hashtags) used to compare the similarity (Jaccard) of the hashtags in an efficient way. This will be needed in the following steps in order to suggest the best hashtags to use in a specific situation (eg. suggest a second hashtag to use with one give in input).

To build the **final graph** we take the union of all the tweet-graphs, base on the history these graphs provide we can estimate for each hashtag and for each edge the probability (for each hashtag, probability is equal to number of edges occurencies **divided** hashtag tweet-graph cardinality) of the tweet traversing that link. 

In this step we also need to do some preprocessing of the hashtahs-graphs calculation. More specifically are required for the on-line steps the similiraties (Jaccard) between each pair of hashtags are computed and arranged into a sorted list (one for each hashtag) from the most similar to the least. This will be feed to the ranking aggregadion mechanism (meadian ranking aggregation techinque) used in the hashtag suggestion functionality.



How to create the graph
------
	- Choose a SOURCE
	- Run twitter_data_retrive.py and wait
	- Run build_tweet_graph.py
	- Run graph_builder.py

Basic usage
------
	- Run ui_basic.py and follow the UI

Screenshot
------
SIMULATION

.. image:: https://github.com/FabFari/tweemportance-analyzer/blob/master/screenshot/1.png
   :align: center
   
EXPECTED VALUE

.. image:: https://github.com/FabFari/tweemportance-analyzer/blob/master/screenshot/2.png
   :align: center
   
MAXIMIZE EXPECTED VALUE

.. image:: https://github.com/FabFari/tweemportance-analyzer/blob/master/screenshot/3.png
   :align: center
   
MAXIMIZE PROBABILITY TO REACH TARGET NODE(person)

.. image:: https://github.com/FabFari/tweemportance-analyzer/blob/master/screenshot/4_p.png
   :align: center
   
MAXIMIZE PROBABILITY TO REACH TARGET NODE(person, tweet)

.. image:: https://github.com/FabFari/tweemportance-analyzer/blob/master/screenshot/4_pt.png
   :align: center
   
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
