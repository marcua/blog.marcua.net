---
layout: post
title: 'NYT_Transformer and Data.gov: Your chance for a weekend hacking project!'
date: '2009-06-15T14:14:00+00:00'
tags: []
tumblr_url: https://blog.marcua.net/post/124082570
---
The awesome developers at [The New York Times’ Open blog](http://open.blogs.nytimes.com/) have just [posted about](http://open.blogs.nytimes.com/2009/06/15/introducing-nyt_transformer/)[NYT\_Transformer](http://code.nytimes.com/projects/nyt_transformer/doc/index.html), a tool for converting between various data formats (XML, comma-separated files) and data storage mediums (flat files, databases).

This isn’t the first time such a conversion utility has been written–[Babel](http://simile.mit.edu/babel/) comes to mind. The NYT\_Transformer has a few perks in its favor, however, namely that it seems to be used in heavy production at The New York Times, and that it allows you to convert between databases and flat files (nice touch!).

Written in php, the tool is geared toward web applications. An immediate thought, aside from batch jobs for various internal projects, would be to use the tool for a greater purpose: a data converter for [data.gov](http://www.data.gov).

While data.gov is a nice start at centralizing the directory of the U.S. government’s raw data feeds, it lacks a utility for converting between various data formats. Given that the sunlight foundation is currently[running a competition](http://www.sunlightlabs.com/contests/appsforamerica2/)to build tools on top of data.gov, this is the perfect opportunity to go meta and build a data.gov browser with automatic format conversion. That would help standardize the site a bit, and would be a nice signal for the folks at data.gov as to the file formats that people actually want for various datasets. If you’re interested in working on this project, let me know!

