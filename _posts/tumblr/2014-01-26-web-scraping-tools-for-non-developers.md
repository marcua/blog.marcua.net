---
layout: post
title: Web Scraping Tools for Non-developers
date: '2014-01-26T17:41:11+00:00'
tags: []
tumblr_url: https://blog.marcua.net/post/74655674340
---
I recently spoke with a resource-limited organization that is investigating government corruption and wants to access various public datasets to monitor politicians and law firms. They don’t have developers in-house, but feel pretty comfortable analyzing datasets in [CSV](https://en.wikipedia.org/wiki/Comma-separated_values) form. While many public datasources are available in structured form, some sources are hidden in what us data folks call the [deep web](https://en.wikipedia.org/wiki/Deep_Web). Amazon is a nice example of a deep website, where you have to enter text into a search box, click on a few buttons to narrow down your results, and finally access relatively structured data (prices, model numbers, etc.) embedded in HTML. Amazon has a structured database of their products somewhere, but all you get to see is a bunch of webpages trapped behind some forms.

A developer usually isn’t hindered by the deep web. If we want the data on a webpage, we can automate form submissions and key presses, and we can parse some ugly HTML before emitting reasonably structured CSVs or JSON. But what can one accomplish without writing code?

This turns out to be a hard problem. Lots of companies have tried, to varying degrees of success, to build a programmer-free interface for structured web data extraction. I had the pleasure of working on one such project, called [Needlebase](http://readwrite.com/2010/10/05/needlebase_get_this_diy_web_analysis_tool_before_g#awesm=~otZsWqX577hOPt) at ITA before Google acquired it and closed things down. [David Huynh](http://davidhuynh.net/), my wonderful colleague from grad school, prototyped a tool called [Sifter](http://simile.mit.edu/wiki/Sifter) that did most of what one would need, but like all good research from 2006, the lasting impact is his paper rather than his software artifact.

Below, I’ve compiled a list of some available tools. The list comes from memory, the advice of some friends that have done this before, and, most productively, a [question on Twitter](https://twitter.com/marcua/status/426783236132732928) that [Hilary Mason](http://twitter.com/hmason) was nice enough to retweet.

The bad news is that none of the tools I tested would work out of the box for the specific use case I was testing. To understand why, I’ll break down the steps required for a working web scraper, and then use those steps to explain where various solutions broke down.

# The anatomy of a web scraper

There are three steps to a structured extraction pipeline:

1. _Authenticate yourself_. This might require logging in to a website or filling out a [CAPTCHA](https://en.wikipedia.org/wiki/CAPTCHA) to prove you’re not…a web scraper. Because the source I wanted to scrape required filling out a CAPTCHA, all of the automated tools I’ll review below failed step 1. It suggests that as a low bar, good scrapers should facilitate a human in the loop: automate the things machines are good at automating, and fall back to a human to perform authentication tasks the machines can’t do on their own.

2. _Navigate to the pages with the data_. This might require entering some text into a search box (e.g., searching for a product on Amazon), or it might require clicking “next” through all of the pages that results are split over (often called pagination). Some of the tools I looked at allowed entering text into search boxes, but none of them correctly handled pagination across multiple pages of results.

3. _Extract the data_. On any page you’d like to extract content from, the scraper has to help you identify the data you’d like to extract. The cleanest example of this that I’ve seen is captured in a [video for one of the tools below](http://www.kimonolabs.com/): the interface lets you click on some text you want to pluck out of a website, asks you to label it, and then allows you to correct mistakes it learns how to extract the other examples on the page.

As you’ll see in a moment, the steps at the top of this list are hardest to automate.

# What are the tools?

Here are some of the tools that came highly recommended, and my experience with them. None of those passed the CAPTCHA test, so I’ll focus on their handling of navigation and extraction.

- [Web Scraper](https://chrome.google.com/webstore/detail/web-scraper/jnhgnonknehpejjnehehllkliplmbmhn) is a Chrome plugin that allows you to build navigable site maps and extract elements from those site maps. It would have done everything necessary in this scenario, except the source I was trying to scrape captured click events on links (I KNOW!), which tripped things up. You should give it a shot if you’d like to scrape a simpler site, and the [youtube video](https://www.youtube.com/watch?v=PgIfLxfRYnc) that comes with it helps get around the slightly confusing user interface.

- [import.io](http://import.io/) looks like a clean webpage-to-api story. The service views any webpage as a potential data source to generate an API from. If the page you’re looking at has been scraped before, you can access an API or download some of its data. If the page hasn’t been processed before, import.io walks you through the process of building connectors (for navigation) or extractors (to pull out the data) for the site. Once at the page with the data you want, you can annotate a screenshot of the page with the fields you’d like to extract. After you submit your request, it appears to get queued for extraction. I’m still waiting for the data 24 hours after submitting a request, so I can’t vouch for the quality, but the delay suggests that import.io uses [crowd workers](https://en.wikipedia.org/wiki/Crowdsourcing) to turn your instructions into some sort of semi-automated extraction process, which likely helps improve extraction quality. The site I tried to scrape requires an arcane combination of javascript/POST requests that threw import.io’s connectors for a loop, and ultimately made it impossible to tell import.io how to navigate the site. Despite the complications, import.io seems like one of the more polished website-to-data efforts on this list.

- [Kimono](http://www.kimonolabs.com/welcome.html) was one of the most popular suggestions I got, and is quite polished. After installing the Kimono bookmarklet in your browser, you can select elements of the page you wish to extract, and provide some positive/negative examples to train the extractor. This means that unlike import.io, you don’t have to wait to get access to the extracted data. After labeling the data, you can quickly export it as CSV/JSON/a web endpoint. The tool worked seamlessly to extract a feed from the Hackernews front page, but I’d imagine that failures in the automated approach would make me wish I had access to import.io’s crowd workers. The tool would be high on my list except that navigation/pagination is coming soon, and will ultimately cost money.

- [Dapper](http://open.dapper.net/dapp-factory.jsp), which is now owned by Yahoo!, provides about the same level of scraping capabilities as Kimono. You can extract content, but like Kimono it’s unclear how to navigate/paginate.

- [Google Docs](http://eagereyes.org/data/scrape-tables-using-google-docs) was an unexpected contender. If the data you’re extracting is in an HTML table/RSS Feed/CSV file/XML document on a single webpage with no navigation/authentication, you can use one of the [Import\* functions](https://support.google.com/drive/table/25273?hl=en&rd=2) in Google Docs. The [IMPORTHTML](https://support.google.com/drive/answer/3093339) macro worked as advertised in a quick test.

- [iMacros](http://imacros.net/browser/cr/welcome) is a tool that I could imagine solves all of the tasks I wanted, but costs more than I was willing to pay to write this blog post. Interestingly, the free version handles the steps that the other tools on this list don’t do as well: navigation. Through your browser, iMacros lets you automate filling out forms, clicking on “next” links, etc. To perform extraction, you have to pay at least $495.

- A friend has used [Screen-scraper](http://community.screen-scraper.com/) in the past with good outcomes. It handles navigation as well as extraction, but costs money and requires a small amount of programming/tokenization skills.

- [Winautomation](http://www.winautomation.com/) seems cool, but it’s only available for Windows, which was a dead end for me.

# So that’s it? Nothing works?

Not quite. None of these tools solved the problem I had on a very challenging website: the site clearly didn’t want to be crawled given the CAPTCHA, and the javascript-submitted POST requests threw most of the tools that expected navigation through links for a loop. Still, most of the tools I reviewed have snazzy demos, and I was able to use some of them for extracting content from sites that were less challenging than the one I initially intended to scrape.

All hope is not lost, however. Where pure automation fails, a human can step in. Several proposals suggested paying people on [oDesk](https://www.odesk.com/), [Mechanical Turk](https://www.mturk.com), or [CrowdFlower](http://crowdflower.com/) to extract the content with a human touch. This would certainly get us past the CAPTCHA and hard-to-automate navigation. It might get pretty expensive to have humans copy/paste the data for extraction, however. Given that the tools above are good at extracting content from any single page, I suspect there’s room for a human-in-the-loop scraping tool to steal the show: humans can navigate and train the extraction step, and the machine can perform the extraction. I suspect that’s what [import.io](http://import.io/) is up to, and I’m hopeful they keep the tool available to folks like the ones I initially tried to help.

While we’re on the topic of human-powered solutions, it might make sense to hire a developer on oDesk to just implement the scraper for the site this organization was looking at. While a lot of the developer-free tools I mentioned above look promising, there are clearly cases where paying someone for a few hours of script-building just makes sense.

