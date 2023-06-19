---
layout: post
title: 'ayb: A multi-tenant database that helps you own your data'
date: 2023-06-11 22:45 +0000
---
## Introduction

Today's databases are simultaneously ubiquitous and frustratingly inaccessible to most people. Your own data likely lives in thousands of databases at various companies and organizations. But if you wanted to create a database for yourself in which to store data and share it, you'd need the skills of both a system administrator and a software engineer. By virtue of the complexity of database management systems (and market forces), your data either lives in other people's databases or in hard-to-share unstructured files on your computer. If it was easier to create and share databases, more people and teams would use them to manage and own their data.

To make this concrete, imagine a journalist or student that's looking to create a database around a new dataset and build a visualization they host on a website. Using existing database tools, they have to secure a machine, install Postgres/MySQL, update various configuration settings to allow incoming connections, and create and host a web application to gatekeep the database credentials. Instead, what if our user could: 1) Register for an account on a service provided by their newsroom or school, 2) Issue a `create database` command and make their database publicly accessible in read only mode, and 3) Issue SQL from the command line or over HTTP?

Toward that vision, I've been building [ayb](https://github.com/marcua/ayb), which is a multi-tenant database management system with easy-to-host instances that quickly allow you to register an account, create databases, share them with collaborators, and query them from a web application or the command line. With `ayb`, [all your (data)base can finally belong to you](https://www.youtube.com/watch?v=qItugh-fFgg). `ayb` is open source (Apache 2.0-licensed) and requires a single command to start a server. What does `ayb` offer?
* **Popular storage formats as an ejection seat**. `ayb` databases are just [SQLite](https://www.sqlite.org/index.html) files, and `ayb` relies on SQLite for query processing. SQLite is the most widely used database on the planet, and if you one day decide `ayb` isn't for you, you can walk away with your data in a single file. (We'll support other formats like DuckDB's after its storage format stabilizes.)
* **Easy registration and database creation**. To borrow a tired analogy, an `ayb` instance is like GitHub for your databases: once you create an account on an `ayb` instance, you can create databases quickly and easily. Next on the roadmap are features like authentication and permissions so that you can easily share your databases with particular people or make them publicly accessible.
* **Multi-tenancy**. While `ayb` is easy to get up and running, you shouldn't have to be a system administrator to get started. Each `ayb` instance can serve multiple users' databases, so that on a team, in a classroom, or in a newsroom, one person can get it running and everyone else can utilize the same instance. Once `ayb` has authentication and permissions, I'll plan on running a public `ayb` instance so people can spin up databases without having to run their own instance. Clustering/distribution is on the roadmap so that eventually, if your instance ever needed to, it could run on multiple nodes.
* **An HTTP API**. To make it easy to integrate into web applications, `ayb` exposes databases over an HTTP API. Other wire protocols (e.g., the PostgreSQL wire protocol) are on the roadmap for broader compatibility with existing applications.

As of June 2023, `ayb` is neither feature complete nor production-ready. Functionality like authentication, permissions, collaboration, isolation, high availability, and transaction support are on the [Roadmap](https://github.com/marcua/ayb#roadmap) but not available today. If you want to collaborate, reach out!

In the rest of this article, you can:
* See `ayb` action in an [end-to-end example](#an-end-to-end-example)
* Better understand who `ayb` is for in [students, sharers, and sovereigns](#students-sharers-and-sovereigns).
* Learn [where to go from here](#where-to-go-from-here).

## An end-to-end example

### Installing
`ayb` is written in Rust, and is available as the `ayb` crate. Assuming you have [installed Rust on your machine](https://www.rust-lang.org/tools/install), installing `ayb` takes a single command:

```bash
cargo install ayb
```

### Running a server
An `ayb` server stores its metadata in SQLite or [PostgreSQL](https://www.postgresql.org/), and stores the databases it's hosting on a local disk. To configure the server, create an `ayb.toml` configuration file to tell the server what host/port to listen for connections on, how to connect to the database, and the data path for the hosted databases:

```bash
$ cat ayb.toml
host = "0.0.0.0"
port = 5433
database_url = "sqlite://ayb_data/ayb.sqlite"
# Or, for Postgres:
# database_url = "postgresql://postgres_user:test@localhost:5432/test_db"
data_path = "./ayb_data"
```

Running the server then requires one command
```bash
$ ayb server
```


### Running a client
Once the server is running, you can set its URL as an environment variable called `AYB_SERVER_URL`, register a user (in this case, `marcua`), create a database `marcua/test.sqlite`, and issue SQL as you like. Here's how to do that at the command line:

```bash
$ export AYB_SERVER_URL=http://127.0.0.1:5433

$ ayb client register marcua
Successfully registered marcua

$ ayb client create_database marcua/test.sqlite
Successfully created marcua/test.sqlite

$ ayb client query marcua/test.sqlite "CREATE TABLE favorite_databases(name varchar, score integer);"

Rows: 0

$ ayb client query marcua/test.sqlite "INSERT INTO favorite_databases (name, score) VALUES (\"PostgreSQL\", 10);"

Rows: 0

$ ayb client query marcua/test.sqlite "INSERT INTO favorite_databases (name, score) VALUES (\"SQLite\", 9);"

Rows: 0

$ ayb client query marcua/test.sqlite "INSERT INTO favorite_databases (name, score) VALUES (\"DuckDB\", 9);"

Rows: 0

$ ayb client query marcua/test.sqlite "SELECT * FROM favorite_databases;"
 name       | score 
------------+-------
 PostgreSQL | 10 
 SQLite     | 9 
 DuckDB     | 9 

Rows: 3
```

The command line invocations above are a thin wrapper around `ayb`'s HTTP API. Here are the same commands as above, but with `curl`:
```bash
$ curl -w "\n" -X POST http://127.0.0.1:5433/v1/marcua -H "entity-type: user"

{"entity":"marcua","entity_type":"user"}

$ curl -w "\n" -X POST http://127.0.0.1:5433/v1/marcua/test.sqlite -H "db-type: sqlite"

{"entity":"marcua","database":"test.sqlite","database_type":"sqlite"}

$ curl -w "\n" -X POST http://127.0.0.1:5433/v1/marcua/test.sqlite/query -d 'CREATE TABLE favorite_databases(name varchar, score integer);'

{"fields":[],"rows":[]}

$ curl -w "\n" -X POST http://127.0.0.1:5433/v1/marcua/test.sqlite/query -d "INSERT INTO favorite_databases (name, score) VALUES (\"PostgreSQL\", 10);"

{"fields":[],"rows":[]}

$ curl -w "\n" -X POST http://127.0.0.1:5433/v1/marcua/test.sqlite/query -d "INSERT INTO favorite_databases (name, score) VALUES (\"SQLite\", 9);"

{"fields":[],"rows":[]}

$ curl -w "\n" -X POST http://127.0.0.1:5433/v1/marcua/test.sqlite/query -d "INSERT INTO favorite_databases (name, score) VALUES (\"DuckDB\", 9);"

{"fields":[],"rows":[]}

$ curl -w "\n" -X POST http://127.0.0.1:5433/v1/marcua/test.sqlite/query -d "SELECT * FROM favorite_databases;"

{"fields":["name","score"],"rows":[["PostgreSQL","10"],["SQLite","9"],["DuckDB","9"]]}
```

## Students, sharers, and sovereigns 
If `ayb` is successful, it will become easier to create a database, interact with it, and share it with relevant people/organizations. There are three groups that would benefit most from such a tool, and by studying the problems they face, we can make `ayb` more useful for them.

**Students**. The barrier to learn how to work with data is too high, and much of it is in operational overhead (how to set up a database? how to connect to it? how to share what I've learned?). Ideally, aside from registering for an account and creating a database, there should be no operational overhead to writing your first SQL query. It should be easy to fork a data set and start asking questions, and it should be easy to start inserting rows into your own small data set. If you get stuck, it should be easy to give a mentor or teacher access to your database and get some help.

**Sharers**. Scientists, journalists, and other people who want to share a data set have largely ad hoc means to share that data, and their collaborators and readers' experience is limited by the ad hoc sharing decisions. You've encountered this if you've ever tried to do something with the CSV file someone shared over email or if you've wanted to visualize the data presented in an article in a slightly different way. Sharers should be able to create a database, add collaborators, and eventually open it up to the public to fork/query in a read-only way with as little overhead for themselves or the recipient as possible. While this design pushes computation onto the shared instances and away from capable laptops, it enables consistency in data and allows collaborators to benefit from future updates.

**Sovereigns**. When you use most hosted applications, you're not in control of your own data. Today's application stack places ownership of the database and data with the organization that wrote the application. While this model has several benefits, it also means that your data isn't yours, which has privacy, security, economic, and extensibility implications. The company that hosts the application has sovereignty over the database that hosts the data, and if you're lucky (or live in a place with reasonable regulations), they allow you to export portions of your data in sometimes unhelpful formats. The most speculative use case for `ayb` is that it grants end-users sovereignty over their data. Imagine a world where, before signing up for an application, you spin up an `ayb` database and authorize the application to your new database. As long as you're still getting value from an app, it can provide functionality on top of your data. If you ever change your mind about the app, the data is yours by default, and you can change who has access to your data.

## Where to go from here
Thank you for reading this far. From here, you can:
* Build your own database! It [takes minutes](https://github.com/marcua/ayb#getting-started)!
* Read more about what functionality is coming soon to `ayb` in the [Roadmap](https://github.com/marcua/ayb#roadmap).
* Make a contribution to the project, starting with the details on [how to contribute](https://github.com/marcua/ayb#contributing).
* Create an issue, email me, or reach out on social media to get started (my [contact information is here](https://marcua.net/) and I promise to be welcoming).

## Thank you
Thank you to Sofía Aritz, Meredith Blumenstock, Daniel Haas, Meelap Shah, and Eugene Wu and for reading and suggesting improvements to early drafts of this blog post.
