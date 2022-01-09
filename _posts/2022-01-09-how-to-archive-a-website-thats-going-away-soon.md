---
layout: post
title: How to archive a website that's going away soon
date: 2022-01-09
---

## Preserving a piece of digital history

When we moved to NYC a few years ago, I wanted to keep up with what was going on in the neighborhood, but also wanted to avoid relying on Facebook or other closed silos to stay connected. Friends recommended an open forum administered and moderated by volunteers called [Jackson Heights Life](https://archive.jacksonheightslife.com) (and its sibling forum, [Astorians](https://archive.astorians.com). Each forum offered an RSS feed with its latest posts, which allowed me to track updates on neighborhood happenings from the comfort of my feed reader. This all worked well until the volunteers on the two forums announced that for various reasons, they were shutting the forums down with the new year.

Responses to the announcements varied, but some commenters wondered whether the forums' contents would be preserved, as they were nearing two decades of history. My immediate thought was to check [The Internet Archive](http://web.archive.org/web/*/http://www.jacksonheightslife.com//*), but the results weren't promising: there were very few crawls of the website in 2021, and the ones that existed were largely of images, not forum posts. I reached out to forum moderators, and they said that they been advised about digital preservation services, but that the costs were prohibitive (>= $1,000 per forum). Nostalgia struck, and I reasoned that my trying to capture the websites in the final few days of 2021 was better than nothing.

What follows is a hopefully reproducible set of steps involving a relatively lightweight Linux box, command line tools like `wget`, `git`, `grep`, and `sed`, and GitHub pages to host the archived website for free. After explaining my process, I'll also talk about a few trade-offs and things I wish had worked out better.


## Trade-offs / caveats / considerations

Before we begin, here are a few things to consider:
* I am not an archivist. If you have the benefit of time, money, or connections, consider consulting a professional. I spend a lot of time thinking about websites in my day job, but I'm no expert on digital preservation. If an archivist looked at my process, I bet they'd have a lot of suggestions/improvements/rewrites.
* I am not a lawyer. I had permission to crawl the forums from the owners/administrators/moderators, and confirmed this multiple times. Someone wiser than me would have to advise you on licensing/ownership/copyright, and you might want to get advice on this before you start.
* Time. It took me a few days to do all this, and I estimate about 1.5 full-time days of work (on new year's eve, hooray!). Hopefully you can save some time by reading this document, but expect to spend at least an afternoon on your new hobby. 
* Broken URLs. The previous owners have grand plans for www.astorians.com and www.jacksonheightslife.com, which is great for the neighborhood! This does mean, however, that old links to the website will break. Before you go setting up 301 redirects to preserve SEO, keep in mind that the (necessary)`--adjust-extension` and `--restrict-file-names=ascii,windows` and flags to `wget` that I share below will also change filenames on you. This is a guide to creating an archive of the content, not a facsimile of the old website and its behavior.
* Server-side rendering. I got very lucky with the PHP forums I was crawling. They largely rendered content server-side, and clicking a link would take you to a new URL, which would be server-side rendered again. If the website I was crawling was some modern single-page application that was rendered client-side, I'm pretty sure the `wget` tricks would not work.

This last point is worth considering more broadly: today's website architectures are perhaps optimized for latency or responsiveness, but not for preservation. For every walled garden or web application we encounter, how might we help its contents outlast the decades?

## Let's get started
Here's what you need to do to archive a website, with examples.

### Find a machine
I do all of my development on a remote server, and have a $5/month virtual server for all of my side projects. That helps with things like leaving long-running commands to run while you sleep, but it's not a requirement: you can run all of these commands from most laptops with access to a shell.

### Crawl the website
The first step is to crawl the website using a tool like `wget` in `recursive` mode. The following command (with a slightly more aggressive `wait` as the deadline approached) is the one I used:
```
wget -P . --recursive --page-requisites --adjust-extension --convert-links --wait=0.0625 --random-wait --restrict-file-names=ascii,windows https://www.website-you-are-crawling.com
```
The `wget` documentation is rich with examples and flags. I didn't explore a bunch that might have simplified things for me like `--mirror` or `--backup-converted`. The forums I crawled had hundreds of thousands of pages, and all in all it took approximately a full night's sleep to crawl each site. If you're running this on a laptop, you'll want to turn off automatic sleep mode (leaving yourself a reminder to bring it back when you're done). On a remote server, don't forget to use `tmux` or `screen` so your shell persists. Here are a few notes on the flags I used:
* `--recursive`: Keep requesting linked pages.
* `--page-requisites`: ...and their static assets (e.g., .js, .css)
* `--adjust-extension`: Add extensions like `.html` to file names that are missing it
* `--convert-links`: Rewrite references to files so that they work locally
* `--wait=1`: How many seconds to wait between requests to be nice to the server. If, like me, you end up with not a lot of time left on your deadline, you might reduce this to meet your deadline :).
* `--random-wait`: Introduce randomness tot he wait time on the previous line, in case something on the server might prevent crawling. Try to avoid this unless you have permission.
* `--restrict-file-names=ascii,windows`: (Probably necessary, but will changefile names, breaking URLs.) I used this to convert the query string into something that wouldn't confused browsers/servers. For example, if you're crawling `index.php?some=args` and hoping to convert that to something a web server can serve without running PHP, this flag will rewrite the path.


### Move the content into Git/GitHub
Before mucking with the downloaded source and potentially making a mistake, put the content into source control. I used [GitHub](https://docs.github.com/en/get-started/quickstart/create-a-repo) because it offers free web hosting through GitHub pages. Each of the forums' hundreds of thousands of pages worked out to about ~5 gigabytes of space. Intuition and previous things people told me made me worry about storing that much stuff in Git, but I've seen way larger repositories in professional contexts, so I wasn't going to worry about it if it worked. Things largely worked, with the warning that each `git` operation took tens of minutes and I had to set `ServerAliveInterval 60` and `ServerAliveCountMax 30` in [`~/.ssh/config` to avoid timing out](https://stackoverflow.com/questions/60833006/connection-to-github-com-closed-by-remote-host-when-pushing).

Given how slow some of the `git` operations end up, you might want to make sure the crawl worked at all before your initial `git add`/`git commit`. To do that, jump ahead to [test the website locally](#test-the-website-locally) to make sure things look reasonable (but not perfect, yet).

### Set up GitHub Pages
Let's host this archive for free! There are many options for doing this, from putting it up on S3/CloudFront to using Netlify or Vercel to host the static assets. I used [GitHub Pages](https://docs.github.com/en/pages) because it's free, but I'm not here to sell you anything. Many solutions would have sufficed. Here are some notes on what I learned:
* You can skip the `Jekyll` stuff. GitHub Pages has really nice integration with Jekyll so you can set up templates, etc., but you've just crawled a bunch of HTML and hope to never edit again. You can just disregard this part of their documentation.
* You can set up a [custom domain](https://docs.github.com/en/pages/configuring-a-custom-domain-for-your-github-pages-site). Early on in the documentation, they describe using `https://yourname.github.io/projectname` as the URL, but you can also set up a custom CNAME. The owners the original domains were kind enough to point [https://archive.astorians.com](https://archive.astorians.com) and [https://archive.jacksonheightslife.com](https://archive.jacksonheightslife.com) my way, which I think is a bit more fitting for an archive. They had other plans for the `www` CNAME, so to the residents of Queens I say: get excited!
* You can watch your website deploy after pushing changes in GitHub Actions. For example, [here is the list of deploys for archive.jacksonheightslife.com](https://github.com/marcua/jhlife-archive/actions). This is helpful because it took ~10 minutes per deploy, and this helped me know when the deploys were done.


### Test the website locally
After the crawl completes (and not while it's running, since `wget`'s `--convert-links` runs after the crawl is done), you can run a local web server with:
```
timeout 2h \
        python3 -m http.server \
               --bind 0.0.0.0 8001
```
With `0.0.0.0`, you will be able to access the server remotely, and you should pick a port (`8001` in the example) that's open on the server. The `timeout 2h` kills the server after 2 hours: I don't like forgetting to leave services running on my remote server. In my case, I visited `http://my-address.tld:8001` and clicked around and immediately ran into issues, which I addressed in the next step.

### Manually download missing assets and rewrite the source
This is the most labor-intensive part of the process.

* As you click around the local server, visual discrepancies will likely immediately pop up. `wget` can't anticipate, download, or rewrite every path (in my case, some URLs were constructed in JavaScript, and static references in CSS `background`s weren't rewritten). To spot less obvious issues, open the [network tab in your favorite browser](https://developer.mozilla.org/en-US/docs/Tools/Network_Monitor) and look for any requests to the original website. When the original website goes down, these assets will be missing and break the archived website.
* Manually download (you can use non-recursive `wget`) the missing assets and place them in the appropriate directory.
* Unfortunately, missing assets isn't the worst of your problems. In my case, even after `wget`'s `--convert-links`, I had ~150,000 pages for each forum with absolute URLs (or JavaScript that constructed those URLs) that I had to rewrite. Here are some handy command line tricks to help you on your journey in rewriting hundreds of thousands of files:
  * If you identify a pattern of static assets that `wget` didn't collect, and you can describe that pattern with a regular expression, use something like `grep -rho '"http://www.astorians.com/community/Theme[^\"]*"' . | sort | uniq | xargs wget -x -` to download all of the missing files. Replace the `...astorians...` path string with your regular expression.
  * If you encounter an incorrect string/reference in many files that you want to rewrite, use something like `git grep -lz 'OLD_STRING_TO_REPLACE' | xargs -0 sed -i '' -e 's/OLD_STRING_TO_REPLACE/NEW_STRING_TO_USE/g'`, replacing `OLD_STRING_TO_REPLACE` and `NEW_STRING_TO_USE` with regular expressions for the old and new string.

### Test the website on GitHub pages
Having tested the websites locally and manually fixing issues, you'd think life is good. When you look at the GitHub Pages-hosted website for the first time, expect more things to break. For me, GitHub Pages used HTTPS/TLS (yay!), which prevented the browser from loading insecure `http://...` static assets. Play some music and go back to the [manually...](#manually-download-missing-assets-and-rewrite-the-source) step. With 10 minutes between each deploy, you'll be here a while. 

### Feel good
At some point, you'll have iteratively refined your way to success. The first website refresh that looks half-decent will give you quite a thrill. You've preserved a bit of internet history. Go you.

## Thank you
Thank you to the owners, administrators, moderators, and commenters of Astorians and Jackson Heights Life. Your role was a lot more involved than mine.