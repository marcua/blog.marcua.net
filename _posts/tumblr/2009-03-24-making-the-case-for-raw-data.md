---
layout: post
title: Making the case for Raw Data
date: '2009-03-24T10:44:00+00:00'
tags: []
tumblr_url: https://blog.marcua.net/post/89373158
---
[Tim Berners-Lee](http://www.ted.com/index.php/talks/tim_berners_lee_on_the_next_web.html)’s recent TED talk on Linked Data has inspired quite a few people to ask what exactly linked data is, how it differs from data on the semantic web, and how realistic it is to assume universal and unique addressability of data items. A world with linked data would be a world with richer, more explorable data, and that notion on its own makes Tim’s talk worth viewing. The most inspiring part of his talk, in my opinion, was the one in which he got the entire crowd to loudly demand RAW DATA NOW. Given the push for more open datasets in government, and given that more websites are becoming API-providing data platforms, it is important to demand raw data where possible.

## The magic behind raw data

The best thing about raw data is that almost everyone knows how it works. This means that as far as the data (re)user is concerned, the datasets are text files (or perhaps a close variant) that they can download, open in some default application, and get some immediate use out of it.

If the US Federal budget dataset is released as a comma-separated file, a middle-schooler can download the file, open it in a spreadsheet application, and sum the columns to see how much we’re spending on the Department of Education this year. A more skilled high-schooler can upload the file to [Many Eyes](http://manyeyes.alphaworks.ibm.com/manyeyes/), make a pie chart out of it, and post it to their blog. A first-year college student can write a php script to allow people to comment on various parts of that pie chart, allowing you to drill in to various slices to get a finer granularity.

With raw data, you’ve opened more people to more visualization, exploration, and discussion than was available through the original web application that acted as a firewall to your database.

## Hugging the data to death

During his talk, Tim spoke about “Database Huggers,” or people who, for various reasons, hide their data away in databases. Once the data sits in a database, the publisher might provide a specific and constrained view of the data by way of a website, or they might hide it even more, simply calculating some aggregate statistic over the data and claiming, without verification, that the data has certain properties.

There are several legitimate reasons for database hugging. Some data was meant to be private–academic, medical, and financial information are all datapoints we’d prefer to keep private. We’d hope our service providers will keep it out of the hands of others. Similarly, a company might have competitive reasons for keeping information private, especially when it would be equally valuable to their competitors and not too valuable to the public–lists of customers and transaction histories come to mind. Keeping this information far from the publicly accessible web is responsible and wise.

There are other cases, however, where the data should legitimately stay open and publicly accessible. Open government initiatives will result in many datasets published by organizations that [will](http://www.recovery.gov/) or [should](http://www.nih.gov/) exist in the public domain. Many [Long Tail](http://en.wikipedia.org/wiki/The_Long_Tail) websites, maintained by small groups of [hobbyists](http://simile.mit.edu/exhibit/examples/cereals/cereal-characters.html), probably would not mind if the datasets they generate are published in their full glory. For these types of applications, raw data is ideal.

Even in the case of datasets that should be open to the public, database huggers will sometimes disable direct access to the data, instead opting to place it in a database that sits behind an html-generating web application. Thinking that you’ve hidden your data behind HTML, thus making it safe from reuse, is an unwise assumption. In about an hour, a decent programmer can write a perl script to crawl your site and tease the data apart from the obfuscated HTML that surrounds it, reverse-engineering your database without asking for permission. In fact, there are [tools](http://simile.mit.edu/wiki/Solvent) that make this process easier than writing a one-off perl script. And if you think you can block the person from accessing every page on your site in a short period of time, then they will just collaborate with _everyone else_ who wants the data, write a [Greasemonkey](http://www.greasespot.net/) script to collect parts of the site that they browse, and eventually collect your entire presented dataset.

Databases are not inherently evil. They provide an excellent way to store, index, and query data, but they also have a way of separating the average user from that data. Most websites, for example, do not publish a read-only username and password to their database, for fear of arbitrary queries that could easily take down their machines, or at least keep the machines busy for a long time. We should design tools to maintain the excellent services that databases have been built to provide over the last four decades, without limiting the access to the raw data when such access would be most valuable.

## Are APIs the future of raw data?

There is a middle ground between the highly private datasets and the obviously open ones. Most forward-thinking organizations have realized this. They have also realized that if they have something to sell, be it in meatspace or screenspace, it’s better to release the data about their offerings to anyone that wants to use it, so that people eventually end up at their site. They do this by providing a web [API](http://en.wikipedia.org/wiki/API) to make their dataset queriable, essentially telling other software developers which questions they can answer about the dataset (_query for books by author_, _query for restaurants by cuisine_). [Amazon](http://www.amazon.com/) has some APIs, as does [Yelp](http://www.yelp.com/), and you’d have to be a pretty self-loathing web 2.0 company to not provide an API over _some portion_ of your data. So are APIs the solution? Not always.

APIs are a step in the right direction–open data is better than obfuscated data. APIs help both third-party developers and dataset publishers get more out of a dataset. They have a few drawbacks as well:

- The API is an HTTP interface to _your_ database. This means that if _someone else_ makes a third-party application that is immensely popular, it’s your database that pays for the brunt of its popularity. You weren’t expecting a huge ramp-up in server load? Too bad.
- As kind as the dataset publisher is, they can’t predict _every_ use of the data–if they could, they already would have implemented the best use cases. If they can’t predict how the consumer/developer will use the data, they might not publish a good hook into the dataset. This would either prevent or make awkward the interaction between the third-party application and the publisher.
- Building an API for a dataset makes the people who are nice enough to share their data do _more work_ on top of designing their application. Following common [REST](http://en.wikipedia.org/wiki/Representational_State_Transfer) or [CRUD](http://en.wikipedia.org/wiki/Create,_read,_update_and_delete) conventions makes this easier, but still puts the onus on the developer. As a corollary, APIs don’t change with the data. APIs are frequently revised, meaning that a change in your data requires constant upkeep of your API.

One might argue that some of the criticisms of APIs are unfair:

- Saying that raw data will reduce the load on your database implies that the third party has some cache of the data, which is thus slightly out-of-date. You could imagine some sort of [Comet](http://en.wikipedia.org/wiki/Comet_(programming))-updated raw dataset system, but it’s unlikely for now that dataset publishers will be willing to stream live updates to third parties.
- Perhaps the limited API functionality is for good reason. Amazon might never want you to be able to download their entire dataset–they don’t want to waste the bandwidth and they don’t want competitors to know exactly how many items they have on hand.
- Publishing any sort of raw data will require extra work on behalf of the dataset publisher. Perhaps API-writing is the least invasive of their time?

An ideal data management tool would allow raw data publishing when possible, and make it easier to build APIs when some limited access is desirable. We should not pretend to know the point at which raw data is superior to APIs, but the point exists somewhere. It’s important to understand the benefits that raw data provides on top of web APIs, so that you can think about when it would be valuable to use.

## After all this time, the answer was text files?

You’ve probably become skeptical of these suggestions. Are we really supposed to throw away decades of database research in how to properly store, index, and query reasonably sized datasets so that a middle-schooler can look at the data in a different way? Of course not. The interesting research question becomes whether we can give the user the illusion of raw data while still benefiting from database technology where possible.

That’s one research direction we’re taking within the Haystack group. With the constraint that the raw data, in human-readable text files, should always be available, we’d like to blur the boundaries between databases and data-aware webservers.

Specifically, what we plan on designing is an apache web server module that recognizes when it is serving a dataset, perhaps by taking note that it is serving a .csv, .rdf, or .json file. In such cases, the server would cook the data into a database behind the scenes. Data-aware clients (in javascript for the time being, but in the browser one day) can then query the web server about the data directly. Updates become difficult, but we can make consistency guarantees about the original raw data text files to ensure that someone can download them and see up-to-date information.

If you prefer programmatic access to the files, the module turns into a REST(, SQL, SPARQL, you favorite path language)-capable endpoint. If you prefer to get down and dirty with the data, you’ve got the text files.

We certainly don’t want to stand in the way of a world with Linked Data, so if you’d like, the tool will eventually return data with URIs. We can’t guarantee the URIs will resolve to anything useful, but that just might require a human’s touch. We’re not sure how that fits into the picture for the average data publisher, since the marginal benefit to the individual of universally addressing your own data is small, whereas the benefit to everyone else of adding another linked dataset grows with the number of datasets it is linked to.

## And now, for some questions

We’re early in the development of our tools, so we’re open to your ideas and suggestions. Keeping text files up-to-date with the database that’s proxying them is nontrivial. Thinking of the ideal client/server mode of operation will also take time. We probably haven’t thought of the most important must-have feature yet, so any suggestions are welcome.

_Thanks to Ted Benson, Sam Madden, and David Karger for their thoughts on this post._

(Cross-posted on the [Haystack Blog](http://groups.csail.mit.edu/haystack/blog/2009/03/24/making-the-case-for-raw-data/))

