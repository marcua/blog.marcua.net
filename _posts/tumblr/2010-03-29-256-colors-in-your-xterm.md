---
layout: post
title: 256 colors in your xterm!
date: '2010-03-29T12:25:00+00:00'
tags: []
tumblr_url: https://blog.marcua.net/post/481943878
---
Have you ever used emacs or vim from the command line in GNU/Linux and been offended by the horrible color scheme you saw? I’m embarrassed to admit that I’ve been through tons of vim color schemes and have never been able to understand why the colors did not show up as desired.

Yang’s [blog post](http://yz.mit.edu/wp/2010/03/26/256-color-xterm/) has changed my life. See [here](http://www.frexx.de/xterm-256-notes/) for more notes on which color schemes work well for vim. I’ve been enjoying [wombat256](http://www.vim.org/scripts/script.php?script_id=2465).

On Ubuntu on my laptop, I added “export TERM=xterm-256color” to the end of my “~/.bashrc”–You will have to re-open another terminal to see the results after saving your bashrc, or type “source ~/.bashrc” in your current terminal if you’re too antsy.

