---
layout: post
title: 'What Should be Included in a Data Science Curriculum? '
date: '2012-04-11T15:02:00+00:00'
tags: []
tumblr_url: https://blog.marcua.net/post/20914495752
---
_(I recently wrote an answer to [What Should be Included in a Data Science Curriculum?](http://www.quora.com/Data-Science/What-should-be-included-in-a-data-science-curriculum)&nbsp;on Quora. &nbsp;Here’s a subset of that answer)_

[Eugene Wu](http://www.sirrice.com)&nbsp;and I recently taught a 6-day (3 hours per day) [course on data literacy basics](http://dataiap.github.com/dataiap/) targeted at computer science undergraduates. &nbsp;Our initial motivation was selfish: as databases researchers, we didn’t have a lot of experience with an end-to-end raw data-\>data product pipeline. &nbsp;After a few trial runs of our own, we realized certain data processing patterns kept showing up, and saw that we had a small course worth of content on our hands. &nbsp;The important thing here is that even with undergraduate- and graduate-level machine learning, statistics, and database courses under our belts, we still had a lot to learn about working with honest-to-goodness dirty data.  
  
Each&nbsp;module of our course could have had an entire semester dedicated to it, and so we favored basic skills with lots of hands-on experience over intellectual depth and rigor. &nbsp;We kept lectures to 20-30 minutes, giving students the remaining 2.5 hours to go through the labs we set up while we walked around answering questions. &nbsp;Lectures allowed students to know what they were in for at a high level, and the lab portion allowed them to cement those concepts with real datasets, code, and diagrams. &nbsp;All of the course content is available on github, and as an example, here is a direct link to [day 1’s lab](http://dataiap.github.com/dataiap/day1/).  
  
The&nbsp;syllabus we covered was:

- Day 1: an end-to-end experience in downloading campaign contribution data from the federal election commission, cleaning it up, and programmatically displaying it using basic charts.

- Day 2: visualization/charting skills using election and county health data.
- Day 3: statistics to take the hunches they got on day 2 and quantify them, learning about T-Tests and linear regression along the way.
- Day 4: text processing/summarization using the Enron email corpus.
- Day 5: MapReduce to scale up Day 4’s analysis using Elastic MapReduce on Amazon Web Services. &nbsp;This felt a bit forced, but the students were clamoring for distributed data processing experience.
- Day 6: the students teach us something they learned on their own datasets using techniques we’ve taught them.

While&nbsp;we set out to give computer science students with familiarity in python programming a dive into data, we ended up with folks from the physical sciences, doctors, and a few social scientists who had their own datasets to answer questions about. &nbsp;The last day allowed them to experiment with their new skills on their own data. &nbsp;Attendance on this day was lower than the previous days: the majority of the folks in attendance on day 6 were on the more experienced end, and I suspect that the undergrads, who were not yet exposed to data problems of their own, didn’t find it as engaging. &nbsp;It would be interesting to see how to develop course content that allows self-directed data science for students who still need a bit more inspiration.  
  
I&nbsp;should also say that our attempt is not the first one to bring data to the classroom.[Jeff Hammerbacher&nbsp;](https://twitter.com/#!/hackingdata)and [Mike Franklin](http://www.cs.berkeley.edu/~franklin/) at Berkeley have a wonderful semester-length [course on data science](http://datascienc.es/). &nbsp;The high-level outline of the course seems similar, but they get farther into data product design, and jump into each topic in more depth. &nbsp;Their [resources page](http://datascienc.es/resources)&nbsp;has a nice set of links to other educational efforts worth checking out.

