---
layout: post
title: "Review: a bookmarklet to generate coding agent-ready code reviews"
date: 2025-12-07
---
I'm excited to share [Review](http://marcua.net/minitools/review), a bookmarket that makes it easier for you to code review AI coding agents. The bookmarklet turns all unresolved comments on a GitHub pull request into a Markdown-formatted text blob that you can paste into your coding agent of choice. Since a video is worth a thousand words, here's the tool in action with Claude Code:
<video width="640" height="360" controls>  
  <source src="/assets/video/review-bookmarklet-code-review-ai-agents/review.mp4" type="video/mp4">   
</video>

I've been using Claude Code to start all code explorations, bug fixes, and new features I've worked on in the past few months. As I used it on larger multi-hundred (and increasingly multi-thousand) line projects, I've found the need for a traditional code review interface. Since I do all of my other code reviews through GitHub, I wanted to replicate that experience for reviewing agents as well.

So I made Review! (Well, I asked Claude Code to make Review.) It's a bookmarklet, so it has access to any pull request you can load in a browser. You leave comments (including multi-line comments and code edit suggestions) on a that pull request. When you click the bookmarklet, you see all comments on the pull request formatted as Markdown references to the line(s) that the comments covered. Code edit suggestions are converted into code blocks that show each line prefixed with `-` or `+` for removal or addition appropriately. If there are comments you don't want to send the agent, you can delete them before copying the rest.

I've read about approaches that involved giving Claude access to GitHub comments via `gh` or another interface, but wanted a few things I couldn't get through that approach. First, we do development at B12 on remote machines, and I felt uncomfortable putting GitHub credentials on a remote machine (the `gh` command doesn't work via ssh key forwarding, for whatever reason). Second, it's rare that every comment on a pull request is one I want an AI coding agent to tackle: I might leave a question or explanation for a co-worker, or a peer reviews my code and leaves comments that I then want to turn into more bite-sized coding instructions for the agent. Finally, on larger code reviews, I worry that sending tens of comments won't result in good outcomes for the agent, and so I like to copy/paste subsets of the comments at a time and review those smaller diffs piece by piece. By being able to review and edit all Markdown comments before I copy/paste, it's easier to control what gets sent to the LLM.

If you use Review or have suggestions, reach out! I'd be happy to add features if there's anything that can help your review experience. Review is Apache 2-licensed and [the code is available here](https://github.com/marcua/minitools/tree/main/review).
