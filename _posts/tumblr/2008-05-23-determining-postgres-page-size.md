---
layout: post
title: Determining Postgres Page Size
date: '2008-05-23T00:00:00+00:00'
tags: []
tumblr_url: https://blog.marcua.net/post/65207426
---
Normally 8k by default.

In 8.3.0, you can change BLCKSZ in src/include/pg\_config\_manual.h, and recompile from source to change it.

How can you tell what the page size of your installation is? Create a table with a single item in it. Then print the size of the table - since it fits on one page, the size is the size of the page.

> _[marcua@sorrel postgres]$ psql -d imdb  
> Welcome to psql 8.3.0, the PostgreSQL interactive terminal.  
>   
> Type: \copyright for distribution terms  
> \h for help with SQL commands  
> \? for help with psql commands  
> \g or terminate with semicolon to execute query  
> \q to quit  
>   
> imdb=# select 1 into test;  
> SELECT_
> 
> _imdb=# select pg\_size\_pretty(pg\_total__\_relation\_size(‘test’));_  
> _pg\_size\_pretty_  
> _—————-_  
> _16 kB_  
> _(1 row)_  
>   
> _imdb=# \q_

