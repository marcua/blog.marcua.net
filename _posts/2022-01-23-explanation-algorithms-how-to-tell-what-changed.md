---
layout: post
title: "Explanation Algorithms: What changed?"
date: 2022-01-23 00:00 +0000
---

## Why did this happen? What changed?

As organizations get better at structuring their data and building reports on top of it, new questions arise. Teams used to ask "how many new customers do we get each week?" or "what is the cost of medical care for this group?" and the technology for answering those questions in a timely manner has gotten more and more accessible and understood. Once teams answer these questions and monitor them over time, the answers beget new questions like "why did we see less customers last week?" and "despite similar outcomes, why are the medical costs for this group so high?"

Luckily, the academic community has an answer to such "why" questions: explanation algorithms. An explanation algorithm looks at columns/properties of your dataset and identifies high-likelihood explanations (called "predicates" in database-speak). For example, the algorithms might find that you got less customers in the segment of people who saw a new marketing campaign, or that the medical costs for the group you're studying can largely be attributed to an increase in not-so-effective treatments.

Explanation algorithms are a big deal in both academia and industry. Some of my database community heroes have published some influential papers on the topic. The academic interest is founded in real pain: I can't imagine how many data analyst hours have gone into issuing ad hoc GROUP BY queries to try to slice and dice datasets to explain some change in a dataset over time. Companies like [Sisu](https://sisudata.com/) (founded by Peter Bailis, one of the authors off the DIFF paper discussed below) are built on the premise that data consumers are increasingly asking "why?"

What's fascinating about explanation algorithms is that you can rephrase lots of different questions in the form of an explanation question. This is an area I've been interested in for a while, especially as it might help people like journalists and social scientists better identify interesting threads. In [A data differ to help journalists](https://blog.marcua.net/2015/06/02/a-data-differ-to-help-journalists.html) (2015), I said:

> It would be nice to have a utility that, given two datasets (e.g., two csv files) that are schema-aligned, returns a report of how they differ from one-another in various ways. The utility could take hints of interesting grouping or aggregate columns, or just randomly explore the pairwise combinations of (grouping, aggregate) and sort them by various measures like largest deviation from their own group/across groups.

At the time of that post, I hadn't yet connected the dots between the desire for such a system and the active work on this in the research world. Thanks several database researchers, that connection now exists! In this post, I'll first cover two approaches to explanation algorithms, and then introduce an open source implementation of one of them that I've been implementing for a while. 

## Two ways to ask for explanations

In 2013, Eugene Wu and Sam Madden introduced [Scorpion](http://sirrice.github.io/files/papers/scorpion-vldb13.pdf), a system that explains why an aggregate (e.g., the customer count last week) is higher or lower than other example data. Figure 1 in their paper explains the problem quite nicely. They imagine a user looking at a chart, in this case of aggregate temperatures from a collection of sensors, and highlighting some outliers to ask "compared to the other points on this chart, why are these points so high?"

| ![A figure from the Scorpion paper that shows how a user might highlight outliers on a chart](/assets/images/diff/scorpion-figure1.png) |
|:--:|
| A figure that shows how a user might highlight outliers on a chart (source: Scorpion paper) |

Scorpion has two nice properties. First, it operates on aggregates: in my experience, it's not until you look at some weekly or monthly statistics that you notice that something is off and search for an explanation. Second, it's performant on a pretty wide variety of aggregates, with optimizations for the most common ones (e.g., sums, averages, counts, standard deviations). I believe that of all the explanation algorithms, Scorpion has the most intuitive phrasing of the question ("why so high/low?") with the most intuitive experience (highlighting questionable results in a chart).

The challenge in implementing Scorpion is that, as presented, it does its processing outside of the database that stores the data. Specifically, the way Scorpion partitions and merges subsets of the data to identify an explanation requires decision trees and clustering algorithms that traditionally execute outside of the database[^madlib]. It also is specific to aggregates, which while commonly the source of "why" questions, aren't the only form of that question.

This is where [DIFF](http://www.bailis.org/papers/diff-vldb2019.pdf) comes in. In 2019, Firas Abuzaid, Peter Kraft, Sahaana Suri, Edward Gan, Eric Xu, Atul Shenoy, Asvin Ananthanarayan, John Sheu, Erik Meijer, Xi Wu, Jeff Naughton, Peter Bailis, and Matei Zaharia introduced an explanation algorithm in the form of a database operator called DIFF that can easily be expressed in SQL. If you're so inclined, here's the syntax for the DIFF operator:

| ![The syntax for the DIFF operator ](/assets/images/diff/diff-figure1.png) |
|:--:|
| The syntax for the DIFF operator (source: DIFF paper) |

If you're like me, an example might help:

| ![A simple example of the DIFF operator in action (source: DIFF paper)](/assets/images/diff/diff-example.png) |
|:--:|
| A simple example of the DIFF operator in action (source: DIFF paper) |

In this example, the DIFF operator compares the crash logs of an application from this week to those of last week and considering factors like application version, device, and operating system. The most likely explanation happened 20x more this week than last week (`risk_ratio = 20.0`), and explains 75% of this week's crashes (`support = 75%`).

DIFF requires that we do some mental gymnastics to transform our original "why was X so high?" question into a "how are these two groups different?" question. It also requires the user to wrap their head around statistics like risk ratios and support. In exchange for that mental overhead, DIFF is exciting for its praticality. As evident in the example, it's quite literally expressed in SQL. While a contribution of the paper is a specialized and efficient implementation of DIFF that databases don't have today, it can also be implemented entirely in the database as a series of SQL GROUP BY/JOIN/WHERE operators.

If you have a relational database, love SQL, and want to run an explanation algorithim, DIFF is exciting because those three things are all you need. Luckily for both of us, dear reader, I had a relational database, loved SQL, and wanted to run an explanation algorithm.

## An open source implementation of DIFF
Over the past few months, I've been implementing DIFF as a thin Python wrapper that generates the SQL necessary to compute the difference between two schema-aligned queries. To see a full example, you can check out this [Jupyter Notebook](https://github.com/marcua/datools/blob/main/examples/diff/intel-sensor.ipynb), but I'll show snippets below to give you a sense of how it works.

First, we need a dataset. For that, I took inspiration from the Scorpion paper's experiments, one of which relied on [sensor data from Intel](http://db.csail.mit.edu/labdata/labdata.html) collected by my grad school advisor Sam Madden (and a few collaborators). Using Simon Willison's excellent [sqlite-utils](https://sqlite-utils.datasette.io/en/stable/) library, I load the data into SQLite and inspect it:

```bash
# Retrieve and slightly transform the data
wget http://db.csail.mit.edu/labdata/data.txt.gz
gunzip data.txt.gz
sed -i '1s/^/day time_of_day epoch moteid temperature humidity light voltage\n/' data.txt
head data.txt

# Get it in SQLite
pip install sqlite-utils
sqlite-utils insert intel-sensor.sqlite readings data.txt --csv --sniff --detect-types
sqlite-utils schema intel-sensor.sqlite
```

That last `sqlite-utils schema` shows us what the newly generated `readings` table looks like:
```sql
CREATE TABLE "readings" (
   [day] TEXT,
   [time_of_day] TEXT,
   [epoch] INTEGER,
   [moteid] INTEGER,
   [temperature] FLOAT,
   [humidity] FLOAT,
   [light] FLOAT,
   [voltage] FLOAT
);
```

OK! So we have a row for each sensor reading, with the `day` and `time_of_day` it happened, an `epoch` to time-align readings from different sensors, a `moteid` (the ID of the sensor, otherwise known as a mote), and then the types of things sensors tend to sense: `temperature`, `humidity`, `light`, and `voltage`.

In the Scorpion paper (Sections 8.1 and 8.4), a user notices that various sensors placed throughout a lab detect too-high temperature values (reading [the experiment code](https://github.com/sirrice/scorpion/blob/ba1af715ebc33bc4c4a63612d63debd8650ee1cf/scorpion/tests/gentestdata.py#L80), this happens between 2004-03-01 and 2004-03-10). A natural question is why this happened. The Scorpion algorithm does its thing, and discovers that `modeid = 15` (a sensor with ID 15) was having a bad few days.

Can we replicate this result with DIFF? Let's see! The DIFF implementation is part of a library I've been building is called `datools`, which is a collection of tools I use for various data analyses. Let's install datools:

```bash
pip install datools
```

Now let's use it!

```python
from sqlalchemy import create_engine
from datools.explanations import diff
from datools.models import Column
from datools.sqlalchemy_utils import query_results_pretty_print

engine = create_engine('sqlite:///intel-sensor.sqlite')

candidates = diff(
        engine=engine,
        test_relation='SELECT moteid, temperature, humidity, light, voltage FROM readings WHERE temperature > 100 AND day > "2004-03-01" and day < "2004-03-10"',
        control_relation='SELECT moteid, temperature, humidity, light, voltage FROM readings WHERE temperature <= 100 AND day > "2004-03-01" and day < "2004-03-10"',
        on_column_values={Column('moteid'),},
        on_column_ranges={},
        min_support=0.05,
        min_risk_ratio=2.0,
        max_order=1)
for candidate in candidates:
    print(candidate)
```

What's `diff` have to say?

```python
Explanation(predicates=(Predicate(moteid = 15),), risk_ratio=404.8320855614973)
Explanation(predicates=(Predicate(moteid = 18),), risk_ratio=200.5765335449176)
```

Wow! `moteid = 15` is the top predicate that `datools.diff` identified as being the difference between the `test_relation` and `control_relation`! With a `risk_ratio = 404.83`, we learn that sensor 15 is about 400 times more likely to appear in the set of records with high temperature readings than in the set of records with low temperature readings. Hooray for replicating the Scorpion result! Poor sensor 15!

Let's break that call to `diff` down a bit so we understand what's going on:
* `engine` is a [SQLAlchemy](https://www.sqlalchemy.org/) engine that's connected to some database, in this case the SQLite database.
* `test_relation` is the "test set:" a query with records that show a particular condition. In our case, it's the high-temperature records during the period of interest. This could alternatively be a SQL query for "patients with high medical costs" or "customers who churned".
* `control_relation` is the "control set:" a query with records that don't show that particular condition. In our case, it's the lower-temperature records during the period of interest. This could alternatively be a SQL query for "patients who don't have high medical costs" or "customers who haven't churned".
* `on_column_values`: these are set-valued columns you want to consider as explanations. In our case, we're considering the `moteid` column, so we can identify a specific sensor thats misbehaving.
* `on_column_ranges`: these are range-valued columns you want to consider as explanations. `diff` will bucket these columns into ranges (15 equi-sized buckets), which works well for continuous variables like `{Column('humidity'), Column('light'), Column('voltage'),}`. In this example, we don't provide any (more on why later), but in the Jupyter Notebook, you can see this in action.
* `min_support`: The smallest fraction ([0, 1]) of the test set that the explanation should cover. For example, `min_support=0.05` says that if an explanation doesn't include at least 5% of the test set, we don't want to know about it.
* `min_risk_ratio`: The smallest risk ratio that the explanation should cover. For example, `min_risk_ratio=2.0` says that if an explanation isn't at least 2 times as likely to appear in the test set than in the control set, we don't want to know about it.
* `max_order`: How many columns to consider for a joint explanation. For example, in the Scorpion paper, the authors find that not just sensor 15 (one-column explanation), but sensor 15 under certain light and voltage conditions (three column-explanation), is the best explanation for outlier readings. To analyze three-column explanations, you'd set `max_order=3`. Sadly and hopefully temporarily, while `max_order` is the most fun, interesting, and challenging-to-implement parameter of the DIFF paper, `datools.diff` only supports `max_order=1` for now.

An astute reader will note that I coaxed the results in my example a bit by asking DIFF to consider only `moteid` (`on_column_values={Column('moteid'),}`). The Scorpion paper considers the other columns as well and still gets the strongest signal from `moteid`. In the [Jupyter Notebook](https://github.com/marcua/datools/blob/main/examples/diff/intel-sensor.ipynb), we dive into this more deeply and get distracted by other columns. I offer some hypotheses as to the reasons for this in the notebook, but to have a more informed opinion on why we can't replicate the Scorpion result in DIFF, we'll have to wait until `datools.diff` supports `max_order > 1`.

## Where to go from here?
Before we go off and celebrate the replication of the Scorpion paper's findings with the DIFF paper's algorithm, you should know that it's not all roses. Luckily, I'm just as excited about improving `datools.diff` as I was when I first wrote it, so consider the list below to be both limitations of the current version and a roadmap for the library. If you're curious, [this project board](https://github.com/marcua/datools/projects/1) tracks the things I'm working on most actively.

* **Make `diff` work on more than just SQLite**. `diff` generates SQL, and I'd love for that SQL to run on any database. This is largely a matter of improving the test harness to provision these databases and fixing whatever breaks, but it might also involve removing the dependence on SQLAlchemy. The next few databases I'm targeting are DuckDB, Postgres, and Redshift, but if you're interested in collaborating on something else, I'd love to help.
* **Support `max_order > 1`**. The DIFF paper's contributions are in how to support the combinatorial explosion of looking for multi-column explanations. I'd love to support at least 2- or 3-column explanations.
* **Use `diff` on more datasets**. If you've got a dataset (especially a public one) you're jonesing to try this on, let me know!
* **Replicate `diff` on Scorpion's analysis after implementing higher-order explanations**. The full Jupyter Notebook shows that `diff` can't yet replicate Scorpion's results when we ask it to consider more columns than `moteid`. It suggests explanations ranging from "DIFF an Scorpion are different algorithms and have different tradeoffs" to "Why are we considering an output measure as an explanation?" I think it's worth revisiting this after implementing `max_order > 1`, so that we can see how `datools.diff` handles more complex explanations.
* **Share more about `datools`**. `diff` is part of the `datools` package, but I haven't told you much about `datools`. Countless words have been spilled about how SQL, despite being the future of data analysis, also has its rough edges. `datools` smooths some of these edges out[^datools-example]


## Thank you
Eugene Wu, Sam Madden, Peter Bailis

## Footnotes

[^madlib]: Strictly speaking, it doesn't have to be the case that more complex analytics or machine learning algorithms have to be run outside the database. [MADlib](http://vldb.org/pvldb/vol5/p1700_joehellerstein_vldb2012.pdf) speaks to this nicely, although in practice the approach hasn't taken off as widely as I wish it did.

[^datools-example]: As an example, not every database (I'm looking at you, SQLite and Redshift) supports things like grouping sets and data cubes, but these operators are critical for making stuff like DIFF-in-SQL work effectively. `datools` has functionality that, if a database supports grouping sets, will use the native functionality, but if the database doesn't, [will do the next best thing](https://github.com/marcua/datools/blob/dc6e6f3b9cad04197872b0e6c6a6288f87e149ca/datools/sqlalchemy_utils.py#L46).