---
layout: post
title: Building a Social Data Commons
date: '2009-11-23T22:30:21+00:00'
tags: []
tumblr_url: https://blog.marcua.net/post/255139186
---
([cross-posted](http://groups.csail.mit.edu/haystack/blog/2009/11/23/building-a-social-data-commons/) on the Haystack blog)

Inspired by [Ted’s vision](http://groups.csail.mit.edu/haystack/blog/2009/11/18/plotting-a-course-for-data-gov/) of what he’d like to see happen to [data.gov](http://www.data.gov/), I decided to have a try at my hopes for it. Ted’s desires for data.gov are all ones that I agree would make the data more accessible. I would now like to discuss what else I might want in a world where such steps were taken: a world in which government data was centralized, versioned, searchable, and accessible.

Now what? Given the large and growing pile of data we will optimistically uncover, we will run into new frustrations. People will claim that the published data formats are not the ones that their analysis tool requires. People will be overwhelmed by dataset size, not knowing where to start. People will unknowingly recreate someone else’s data-munging workflows on the way to repeating analyses of the same data. People will become the next bottleneck if data ever ceases to be.

There’s no one answer to the concerns listed above because everyone has a different goal for the data. To handle these issues, we will need more than a place to find up-to-date datasets—we will also need a place where it is easy for people to share ideas and strategies for tackling data. We will need a _social data commons_.

Whereas blogs and wikis help report findings, steps, and missteps, a social data commons can be the place to go to “talk shop” about the available data. Even if people post their solutions using decentralized means, there will be benefit to pooling all of these resources in one place on the web. Here are some tools that will help the data-tinkerers get things done:

- **Data-munging war stories**. The first stage in data analysis is often long and frustrating. One must digest the dataset in the form they received it, and transform, clean, and filter out the subset that they wish to analyze, visualize, or otherwise present. The workflow differs for each dataset and application, but to the extent that people can share tools and instructions for processing each dataset, these should be written up in the form of recipes for baking the data.

- **Crowdsourced analysis**. Datasets can be overwhelming. While many exploration tasks are easily automated, it is often easiest to leave certain tasks (e.g., “Find the interesting pictures”) to humans. [Mechanical Turk](https://www.mturk.com/mturk/) gives us a hint at what this might look like, and the Guardian provides a wonderful [example](http://mps-expenses.guardian.co.uk/) of crowdsourced public data analysis in action.

- **Current uses showcases**. To spark competition, avoid duplicating work, and inspire follow-on projects, visitors should see a showcase of the current uses of each dataset. Aside from links to sites built around a dataset, the list can include [embedded visualizations](http://manyeyes.alphaworks.ibm.com/manyeyes/) of finished work.

- **Analysis wishlists**. Given that data released by a government reaches more than just programmers, there will be more people with ideas than people who can implement the ideas. People with ideas should be given an outlet, and passers-by should be asked to vote on these ideas to help data geeks with some free cycles discover the most insteresting unimplemented project.

- **Data wishlists**. If an agency were to dedicate resources to releasing another dataset, which one is in highest demand? As Ted [mentioned](http://groups.csail.mit.edu/haystack/blog/2009/11/18/plotting-a-course-for-data-gov/), governments should let demand drive delivery.

- **Forums**. No set of tools will encompass all use cases for social data analysis. A discussion forum can lead to the formation of interest groups while serving as a catch-all for needs not served by the list above.

The US government might hit a few bumps trying to implement some of these social features. For example, a conflict of interest might arise if the showcase of uses of a dataset includes a site critical of the current administration. Having the executive branch ban spam or abusive comments on a forum draws concern over limitations of [free speech](http://www.wired.com/techbiz/people/magazine/17-04/st_thompson). These details are not roadblocks, but they do signal that we can’t expect a social overlay to spring out of data.gov _per se_—if we want these features, we may have to build and manage them on a third party.

I’m sure there’s more to the social data commons than I listed here. What did I miss, and where can we seek further inspiration?

_Thanks to Ted for reading the first version of this entry._

