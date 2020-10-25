---
layout: post
title: Database papers at CHI
date: '2011-05-26T22:05:10+00:00'
tags: []
tumblr_url: https://blog.marcua.net/post/5885111801
---
There is little I like more than a fine cheese and fresh-baked bread. Still, to fill the rest of my day without expanding my waistline, I go for a mix of databases and human-computer interaction. That’s why I was excited to see several database-oriented papers presented at [CHI](http://chi2011.org/). While many papers contained some amount of data, I’ll stick to the three that are unquestionably of interest to the databases community.

The first paper was for the social scientist in all of us. Amy Voida, Ellie Harmon, and Ban Al-Ani presented [Homebrew Databases: Complexities of Everyday Information Management in Nonprofit Organizations](http://www.ics.uci.edu/~amyvoida/Site/Whats_New/Entries/2011/2/7_Homebrew_Databases_Research_at_CHI_files/homebrewDatabases-chi11.pdf). Nonprofits are arguably some of the most difficult database users to design for. They have minimal resources, rarely employ fulltime technical staff, and solve non-core problems as they show up. This practice leads to homebrew, just-functional-enough solutions to many data management problems. The authors provide an interesting qualitative study of how nonprofits manage volunteer demographic and contact information. They provide descriptions of the homebrewed, often fractured collections of data stored in several locations. Reading this paper, I couldn’t help but think of how perfectly these homebrewed databases resembled Franklin, Halevy, and Maier’s [dataspaces](http://en.wikipedia.org/wiki/Dataspaces).

Sean Kandel presented [Wrangler](http://vis.stanford.edu/papers/wrangler), a project he’s been working on with Andreas Paepcke, Joe Hellerstein, and Jeff Heer. Wrangler lets users specify transformations on datasets by example. Each time a user shows Wrangler how to modify a record (or line of unstructured text), Wrangler updates its rank-ordered list of potential transformations that could have led to this modification. Wrangler borrows concepts such as interactive transformation languages from Vijayshankar Raman and Joe Hellerstein’s [Potter’s Wheel](http://control.cs.berkeley.edu/abc/). Its interface has a taste of David Huynh and Stefano Mazzocchi’s [Refine](http://code.google.com/p/google-refine/) as well as Huynh’s [Potluck](http://people.csail.mit.edu/dfhuynh/research/papers/iswc2007-potluck.pdf). Wrangler’s novelty comes in combining the interfaces and transformation languages with an inference and ranking engine. Since Wrangler is hosted, it is also capable of learning which transformations users prefer and improving its rankings over time!

The last slot goes to our own Eirik Bakke, who presented [Related Worksheets](http://www.mit.edu/~ebakke/research/related_worksheets_chi2011.pdf) along with David Karger and Rob Miller. Related worksheets make foreign key references a first-class citizen in the world of spreadsheets. Just as spreadsheets secretly made every office worker capable of maintaining a single-user, single-table relational database, Eirik has secretly enabled those workers to make references between spreadsheets without having to program. While adding foreign key references to a spreadsheet requires a simple user interface modification, its implications on how to display multi-valued cells in the spreadsheet are significant. Read the paper to see Eirik’s hierarchical solution to this problem!

Keep it up, data nerds! Soon we’ll be able to start a data community at CHI!
