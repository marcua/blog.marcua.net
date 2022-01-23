---
layout: post
title: "Explanation Algorithms: Why did this happen?"
date: 2022-01-23 00:00 +0000
---

## Why did this happen? What changed?

As more organizations get better at structuring their data and building reports on top of it, new questions arise. Teams used to ask "how many new customers do we get each week?" or "what is the cost of medical care for this group?" and the technology for answering those questions in a timely manner has gotten more and more accessible and understood. Once teams answer these questions and monitor them over time, the answers beget new questions like "why did we see less customers last week?" and "despite similar outcomes, why are the medical costs for this group so high?"

Luckily, the academic community has an answer to such "why" questions: explanation algorithms. An explanation algorithm looks at columns/properties of your dataset and identifies high-likelihood explanations (called "predicates" in database-speak). For example, the algorithms might find that you got less customers in the segment of people who saw a new marketing campaign, or that the medical costs for the group you're studying can largely be attributed to an increase in not-so-effective treatments.

Explanation algorithms are a big deal in both academia and industry. Some of my database community heroes have published some influential papers XXX(cite all the things) on the topic. The academic interest is founded in real pain: I can't imagine how many data analyst hours have gone into issuing ad hoc GROUP BY queries to try to slice and dice datasets to explain some change in a dataset over time. Companies like [Sisu](https://sisudata.com/) (founded by Peter Bailis, one of the authors off the DIFF paper discussed below) are built on the premise that data consumers are increasingly asking "why?"

In this post, I'll first cover two approaches to explanation algorithms, and then introduce an open source implementation of one of them that I've been implementing for a while.

## Two ways to ask for explanations

In XYZ, Eugene Wu and Sam Madden introduced Scorpion XXX(footnote), an XXX(algorithm? operator) that explains why an aggregate (e.g., the customer count last week) is higher or lower than other example data. Figure 1 in their paper explains the problem quite nicely. They imagine a user looking at a chart, in this case of aggregate temperatures from a collection of sensors, highlighting some outliers and asking "compared to the rest of the chart, why are these points so high?"

XYZ(Figure 1)

Scorpion has two nice properties. First, it operates on aggregates: in my experience, it's not until you look at some weekly or monthly statistics that you notice that something is off and search for an explanation. Second, it is performant on a pretty wide variety of aggregates, with optimizations for the most common ones (e.g., sums, averages, counts, standard deviations). I believe that of all the explanation algorithms, Scorpion has the most intuitive phrasing of the question ("why so high/low?") with the most intuitive experience (highlighting questionable results in a chart).

The challenge in implementing Scorpion is that, as presented, it does its processing outside of the database that stores the data. Specifically, the way Scorpion partitions and merges subsets of the data to identify an explanation requires decision trees and clustering algorithms that traditionally execute outside of the database XXX(hellerstein). It also is specific to aggregates, which while commonly the source of "why" questions, aren't the only form of that question.

This is where DIFF XXX(citation) comes in. In 2019, XXX introduced an explanation algorithm in the form of a database operator called DIFF that can easily be expressed in SQL. How it works can most easily be explained by an example within the paper:

XXX(bottom left screenshot from page 422)

In this example, the DIFF operator compares the crash logs of an application from this week to those of last week and considering factors like application version, device, and operating system. The most likely explanation happened 20x more this week than last week (`risk_ratio = 20.0`), and explains 75% of this week's crashes (`support = 75%`).

DIFF requires that we do some mental gymnastics to transform our original "why was X so high?" question into a "how are these two groups different?" question. It also requires the user to wrap their head around statistics like risk ratios and support. In exchange for that mental overhead, DIFF is exciting for its praticality. As evident in the example, it's quite literally expressed in SQL. While a contribution of the paper is a specialized and efficient implementation of DIFF that databases don't have today, it can also be implemented entirely in the database as a series of SQL GROUP BY/JOIN/WHERE operators.

If you have a relational database, love SQL, and want to run an explanation algorithim, DIFF is exciting because those three things are all you need. Luckily for both of us, dear reader, I had a relational database, loved SQL, and wanted to run an explanation algorithm.

## An open source implementation of DIFF


## Where to go from here?



## Thank you
Eugene Wu, Sam Madden, Peter Bailis
