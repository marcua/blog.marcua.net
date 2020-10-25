---
layout: post
title: Human-powered Sorts and Joins
date: '2011-12-08T11:53:55+00:00'
tags: []
tumblr_url: https://blog.marcua.net/post/13925039897
---
(Cross-posted on the [Crowd Research Blog](http://crowdresearch.org/blog/?p=2168))

There [has](http://db.csail.mit.edu/qurk/) [been](http://www.crowddb.org/) a [lot](http://www-cs-students.stanford.edu/~adityagp/scoop.html) of excitement in the database community about crowdsourced databases. &nbsp;At first blush, it sound like databases are yet another application area for crowdsourcing: if you have data in a database, a crowd can help you process it in ways that machines cannot. &nbsp;This view of crowd-powered databases misses the point. &nbsp;The real benefit of thinking of human computation as a databases problem is that it helps you manage complex crowdsourced workflows.

Many crowd-powered tasks require complicated workflows in order to be effective, as we see in algorithms like Soylent’s [Find-Fix-Verify](http://projects.csail.mit.edu/soylent/). &nbsp;These custom workflows require [thousands](http://code.google.com/p/soylent/source/browse/turkit/library/find-fix-verify.js) of lines of code to curry data between services like MTurk and business logic in several languages (1000-2000 in the case of Find-Fix-Verify!). &nbsp;If we provide workflow developers with a set of common operators, like filters and sorts, and a declarative interface to combine those operators, such as SQL or [PigLatin](https://pig.apache.org/docs/r0.7.0/piglatin_ref1.html), we can reduce the painful crowdsourced plumbing code while focusing on a set of operators to improve as a community.

This is not an academic argument: Find-Fix-Verify can be implemented with a FOREACH-FOREACH-SORT in PigLatin, or a SELECT-SELECT-ORDERBY in SQL, resulting in several tens of lines of code. &nbsp;All told, we can get a two order-of-magnitude reduction in workflow code. &nbsp;The task at hand is thus to make the best-of-breed reusable operators for crowd-powered workflows. &nbsp;In our [VLDB 2012 paper](http://db.csail.mit.edu/qurk/qurk-vldb2012.pdf), we look at two such operators: Sorts and Joins.

## Sorts

Human-powered sorts are everywhere. &nbsp;When you submit a product review with a 5-star rating, you’re implicitly contributing a datapoint to a large product ranking algorithm. &nbsp;In addition to rating-based sorts, there are also comparison-based ones, where a user is asked to compare two or more items along some axis. &nbsp;For a particularly cute example of comparison-based sorting, see [The Cutest](http://thecutest.info/), a site that identifies the cutest animals in the world by getting pairwise comparisons from heartwarmed visitors.

The two sort-input methods can be found in the image below. &nbsp;On the left, users compare five squares by size. &nbsp;On the right, users rate each square on a scale from one to seven by size after seeing 10 random examples.

[![Comparison- and Rating-based Sort](http://db.csail.mit.edu/qurk/comparison-rating.png)](http://db.csail.mit.edu/qurk/comparison-rating.png)

In our paper, we show that&nbsp;comparisons provide accurate rankings, but are expensive: they require a number of comparisons quadratic in the number of items being compared. &nbsp;Rating is quite accurate, and cheaper than sorts: it’s linear in the number of items rated. &nbsp;We also propose a hybrid of the two that balances cost and accuracy, where we first rate all items, and then compare items with similar ratings.

These techniques can reduce the cost of sorting a list of items by 2-10x. &nbsp;Human-powered sorts are valuable for a variety of tasks. &nbsp;Want to know which animals are most dangerous? &nbsp;From least to most dangerous, a crowd of Turkers said:

    flower, ant, grasshopper, rock, bee, turkey, dolphin, parrot, baboon, rat, tazmanian devil, lemur, camel, octopus, dog, eagle, elephant seal, skunk, hippo, hyena, great white shark, moose, komodo dragon, wolf, tiger, whale, panther

The different sort implementations highlight another benefit of declaratively defined workflows. &nbsp;A system like Qurk can take user constraints into account (linear costs? quadratic costs? something in between?) and identify a comparison-, rating-, or hybrid-based sort implementation to meet their needs.

## Joins

Human-powered Joins are equally pervasive. &nbsp;The area of [Entity Resolution](http://en.wikipedia.org/wiki/Identity_resolution) has captured the attention of researchers and practitioners for decades. &nbsp;In the space of finance, is IBM the same as International Business Machines? &nbsp;Intelligence analysis runs into a combinatorial explosion in the number of ways to say [Muammar Muhammad Abu Minyar al-Gaddafi](http://en.wikipedia.org/wiki/Muammar_Gaddafi)’s name. &nbsp;And most importantly, how can I tell if Justin Timberlake is the person in the image I’m looking at?

We explored three interfaces for solving the celebrity matching problem (and more broadly, the human-powered entity resolution problem). &nbsp;The first is a simple join interface, asking users if the same celebrity is displayed in two images. &nbsp;The second employs batching, asking Turkers to match several pairs of celebrity images. &nbsp;The third interface employs more complex batching by asking Turkers to match celebrities arrayed in two columns.

[![Simple Joins, Naive Batching, and Smart Batching](http://db.csail.mit.edu/qurk/simple-naive-smart.png)](http://db.csail.mit.edu/qurk/simple-naive-smart.png)

As we batch more pairs to match per task, cost goes down, but so does Turker accuracy. &nbsp;Still, we found that we can achieve around a 10x cost reduction without significantly losing in result quality. &nbsp;We can achieve even more savings by having workers identify features of the celebrities, so that we don’t, for example, try to match up males with females.

## We’re Not Done Yet

We now have insight into how to effectively design two important human-powered operators, sorts and joins. &nbsp;There are two directions to go from here: bring in learning models, and design more reusable operators.

Our paper shows how to achieve more than order-of-magnitude cost reductions in join and sort costs, but this is often not enough. &nbsp;To further reduce costs while maintaining accuracy, we’re looking at training machine learning classifiers to perform simple join and sort tasks, like determining that Cambridge Brewing Co. is likely the same as Cambridge Brewing Company. &nbsp;We’ll still need humans to handle the really tricky work, like figuring out which of the phone numbers for the brewing company is the right one.

Sorts and joins aren’t the only reusable operators we can implement. &nbsp;Next up: human-powered aggregates. &nbsp;In groups, humans are surprisingly accurate at estimating quantities ([jelly beans in a jar](http://thebernoullitrial.wordpress.com/2008/12/19/the-wisdom-of-gummy-bears/), anyone?). &nbsp;We’re building an operator that takes advantage of this ability to count with a crowd.

For more, see our full paper, [Human-powered Sorts and Joins](http://db.csail.mit.edu/qurk/qurk-vldb2012.pdf).  
_This is joint work with [Eugene Wu](http://www.mit.edu/~eugenewu/), [David Karger](http://people.csail.mit.edu/karger/), [Sam Madden](http://db.lcs.mit.edu/madden/), and [Rob Miller](http://people.csail.mit.edu/rcm/)._

