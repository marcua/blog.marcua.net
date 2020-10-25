---
layout: post
title: A data differ to help journalists
date: '2015-06-02T22:14:47+00:00'
tags: []
tumblr_url: https://blog.marcua.net/post/120576686432
---
I recently read an [article](http://mobile.nytimes.com/2015/06/02/business/medicare-payments-billing-hospitals-doctors.html?referrer=) that reminded me of a type of reporting I’ve seen a few times now. In this article, the reporters compare a medical expenses dataset from this year to the one from last year. They report how some aggregates (e.g., average price) grouped by various fields (e.g., treatment type) have changed over time.

It would be nice to have a utility that, given two datasets (e.g., two csv files) that are schema-aligned, returns a report of how they differ from one-another in various ways. The utility could take hints of interesting grouping or aggregate columns, or just randomly explore the pairwise combinations of (grouping, aggregate) and sort them by various measures like largest deviation from their own group/across groups.

There are a few challenges with the “just show me interesting combinations” version of this:

- The approach suffers from [multiple hypothesis testing](https://en.wikipedia.org/wiki/Multiple_comparisons_problem) and you’re likely to end up finding differences where they might not actually exist.
- The system is going to present a bunch of different combinations to the user, resulting in overload. We’d have to think up some interface to present the various findings for them to be useful.

_update with related work:_

- Manasi Vartak, Aditya Parameswaran and friends are working on [SeeDB](http://web.engr.illinois.edu/~adityagp/seedb-tr.pdf). SeeDB optimizes for findings that would visualize well, so its goal might be slightly different. It also has a notion of how a query (subset of the dataset) differs from the rest of the dataset, which we could use for comparing two schema-aligned datasets.
- Michael Bernstein suggested [a look at this paper](http://web.mit.edu/bentley/www/papers/mashupsPH.pdf), which says _We found that long-term correlation data provided users with new insights about systematic wellness trends that they could not make using only the time series graphs provided by the sensor manufacturers._
