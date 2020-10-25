---
layout: post
title: Notes from NoSQL Live Boston 2010
date: '2010-03-11T23:08:00+00:00'
tags: []
tumblr_url: https://blog.marcua.net/post/442594842
---
I was excited to sit in on [NoSQL Live Boston](http://blog.mongodb.org/post/354381883/announcing-nosql-live-from-boston-march-11-2010) today. Thanks to [10gen](http://www.10gen.com/) for hosting and all of the speakers for putting the time in!

The NoSQL community is an interesting one. I was pleased to see Dwight Merriman suggest that the community look past its awkward and misleading name when figuring out how to define itself, and instead find other commonalities: removing the emphasis on joins, focusing on horizontal scalability, and building out non-relational data models. There was no consistent theme to the community, which is the point–if the era of one-size-fits-all solutions is over, you will be hard-pressed to easily define the movement.

**There are some special treats in here** : numbers from deployments at LinkedIn, StumbleUpon, and Twitter. Take a look at the “Scaling w/ NoSQL” panel for that.

Without further ado, here are my notes. I’ve found that these are often filled with typographical errors, so anything you offer up as a fix would be greatly appreciated.

## Dwight Merriman (CEO at 10gen)

- What is NoSQL? Look beyond the name, we’re stuck with it
  - No joins in-app + light transactional semantics =\> horizontal scalability
- Questions to ask of different offerings
  - What is your data model?
  - What is your consistency model?
  - What are the functional differences in operations, querying, etc.?

## Tim Anglade (CTO GemKitty)

General idea: what’s the future of NoSQL, how to get more adoption

European nosql conference–[nosqleu.com](http://nosqleu.com/)

We’re currently at the stage where makers took prototypes from academia, turned into hobby projects. Startups adopted as side-projects. Now VC-backed developers do work on nosql dbs full-time.

How to see adoption+support going forward?

- more development
- marketing
- education–currently it’s easy to only learn about relational model, sql. Need that model for nosql ecosystem.
- certification–because RDBMSs are more standardized, certifications are easier, so it’s easier to hire junior developers and engage lots of vendors.
- branding–“SQL” currently gets more searches than “mysql,” “oracle,” or “sql server.” For “NoSQL” its the opposite–less searches than for the nosql products (mongo, redis, couchdb, etc.)
- references–need a nosql book of reference. What is a document-oriented store, or Key/value (K/V) store?
- industry group that interfaces w/ industry, academia, and education. Runs conferences.

## Panel: Scaling w/ NoSQL

Speakers

- Mark Atwood–Gear6 (memcached support)
- Alex Feinberg–Voldemort developer at LinkedIn–simple get/put/delete K/V store.
- Doug Judd–Hypertable (bigtable implementation in c++, on top of HDFS)
- Ryan King–Twitter, which is replacing MySQL w/ Cassandra
- Ryan Rawson–HBase developer at Stumbleupon

How does each system scale?

- memcached–completely shared-nothing. Facebook has several TBs of memory pooled in memcached.
- Voldemort–based on dynamo’s consistency model, so completely symmetric. Largest LinkedIn cluster does 7k req/sec on the client, which results in 14k req/sec on each server in the pool (read quorum = 2).
- Cassandra–also symmetric based on dynamo’s consistency model (eventual consistency) but uses bigtable data model. Twitter currently stores all data in mysql, but cassandra is repeating all writes and they are currently testing reads live but not displaying the read results to users. Biggest benefit of scale–memcache helps scale reads, but cassandra, due to eventual consistency, scales writes nicely.
- Hypertable is based on HDFS, which is replicated, highly scalable.
- HBase is also based on HDFS. ZooKeeper helps master nodes run elections and lets new nodes take over tablets easily.

What’s life like for operations folks?

- Voldemort–easy to deploy, no single point of failure, and backups are built in through replication. Workload is expectable–no long-running queries, unlike SQL. Thus, little babysitting.
- Cassandra–currently, the engineering team are the operations folks. Numerous failure cases don’t require waking someone up at night. Cluster managed membership/rounting. Upgrade==rolling restart. mysql/memcache is harder to add capacity (data consistency issues)/change configs.
- Hypertable is easy to deploy, but hadoop’s HDFS is harder to get right.
- Rawson points out that HBase is easy, and handles drastically varying row sizes. Config changes require rsyncing configs to all machines, which doesn’t scale well. King points out that some combination of capistrano and ‘murder,’ a twitter open source project, help deploy config changes.
- Feinberg points out that configuration is always more of a dark art once data on disk \> data in memory.

Use cases/deployment in the wild

- memcache–lots of use cases, but most popular are sessions and prebaked HTML
- voldemort–scalable writes, UI settings, e-mail system, rate-limiting, shopping cart (original dynamo paper use case).
- cassandra–King points out Twitter’s use is simple. Some stats: 45 nodes, 9-10B rows. Avg tweets/sec: 600-700 (50M daily) with highly skewed spikes. When deployed, reads will need to be 100k/sec against the cluster.
- Hypertable–only listed analytics workloads: virus sitings (500M events/day), spam classification, site access statistics. No online/live query access stories.
- HBase–at stumbleupon, they have several uses. Numbers: 12K requests/sec in production cluster of 15 nodes. Reqs/sec are uneven–some nodes have 100’s reqs/sec, others have up to 2.4K reqs/sec. Separate cluster to handle analytics: 20 machines handle 7M rows/sec in mapreduce. If they double to 40 machines, they see ~15M rows/sec in mapreduce, so linear scaleup in mapreduce. Bulkloads on this cluster result in ~1M rows/sec insert speeds, and add up to 700GB compressed on disk.

Random discussion

- HDFS not designed for lots of random reads (Yahoo! experiment). But HBase does aggressive caching to avoid hitting disk, so in practice the HBase/Hypertable folks don’t think it’s a big issue.
- Hypertable vs. HBase: Judd says c++ makes for more efficient memory and cpu footprint. Rawson points out that as an apache software foundation project, HBase benefits from lots of contrib projects, such as HIVE/Pig query languages.
- Voldemort is persistent key-value store, whereas memcache is not persistent.
- CAP theorem mini-argument (yay!). For the uninitiated: ©onsistency, (A)vailability, (P)artition tolerance. Brewer’s theorem (proved later by Lynch et al.) is that you can only have two of these in your system. In any real networked system w/ packet loss, Partitions are a given, so tradeoff is between Consistency (will you be able to read the value you just wrote) and Availability (will parts of the system become unavailable/see latency spikes if a node dies). Voldemort/Cassandra==eventual consistency in exchange for high availability. Bigtable copies (HBase/Hypertable) give give up on availability guarantee in exchange for straightforward consistency. King points out that in real system with caching layers and dropped messages, you have to handle read repairs and inconsistency anyway, so embrace it in favor of high availability! Feinberg points out that Voldemort (+ Cassandra) let you demand strong consistency by forcing reads to come from consensus group anyway, so you get what you want.
- BigTable folks point out that range scans suck in all other systems. Automatic partitioning (at least in Cassandra) needs some love as well. memcache has no good notion of dynamic scalability–add more nodes and you might get some inconsistency.

## Panel: NoSQL in the Cloud

Participants

- Benjamin Day–consultant speaking on behalf of MSFT Azure platform
- Jonathan Ellis–works for rackspace, is lead of Cassandra development for apache project.
- Adam Kocoloski–cloudant, works on CouchDB cloud hosting offering.
- Daniel Rinehart–Allurent–startup which is using AWS for a lot, specifically SimpleDB.

Offerings

- Azure–offers SQL in the cloud (hosted sqlserver). Also offers blog/queue/KV cloud store.
- Rackspace offers cloud sites (like appengine for php)–handles multitenancy in mysql (host multiple users on a mysql install). Also offers cloud files (like Amazon S3) and cloud servers (like amazon AWS but with dedicated physical hard drives per cloud server).
- Cloudant–CouchDB cloud hosting. Have developed their own sharding layer on top of CouchDB.
- SimpleDB–nice since amazon handles scale for you. recently added consistent reads, conditional puts (had previously relied on eventual consistency).

Why do cloud + nosql relate?

- Ellis was contrarian here–cloud is nice, obviously. But for databases, cloud is good if you are storing something really small (and want to provision fraction of a machine), or to handle spiky traffic. But for data, you usually don’t see spikes like you see web traffic–if you have 20TB today, you will only have more than that tomorrow. So provisioning data storage in the cloud is silly. For things you’re sure you will have to store, provision real hardware that’s optimal for your setup, and keep adding hardware as you grow. Use cloud for more stateless, spiky things.

Blah blah blah–argument about whether there should be a standard “nosql storage” API to protect developers storing their stuff in proprietary services in the cloud. Probably unrealistic. To protect yourself, use an open software offering, and self-host or go with hosting solution that uses open offering.

Interesting discussion on disaster recovery. Since you’ve outsourced operations to the cloud, should you just trust the provider w/ diaster recovery. People kept talking about busses driving through datacenters or fires happening. What about the simpler problem: a developer drops your entire DB. Need to protect w/ backups no matter where you host.

## Lightning Talks

Alan Hoffman–CEO of Cloudant: Queries + Views in CouchDB

- Each JSON doc in CouchDB has a pkey. View engine lets you build indices.
- Indices are defined by map/reduce functions that emit the key/value pairs for indexing.
- Common pitfalls: don’t use tempviews–those are just for prototypes. Don’t do filtering or reordering in reduce tasks–just aggregate here.

Les Hill–Hashrocket: MongoDoc

- Built Object-Document Mapper for MongoDB in Ruby. Like ORM (object relational mapper), but for document stores like MongoDB.
- Not activerecord, but similar
- Current MongoDB driver for Ruby looks like JSON, whereas MongoDoc (his ODM) looks like more traditional ORMs.

Flinn Mueller–Tokyo Cabinet

- Cares about speed more than scale. TC mmaps disk for speed.
- TC has several backing stores
  - Hash store for simple Key/Value
  - B+Tree for range scans/duplicate keys
  - Fixed-length DB for fast access
  - Table store–stores tuples/documents. Supports queries w/ conditions, orders, limits, union/intersect/diff.
- Says he uses TC like memcache++, and as a queue, atomic counter, and tag cloud. Still uses relational DBs to store data–nosql is more of a utility.

Jim Wilson–Vistaprint: Full-Stack Javascript

- Impedance mismatch between business logic (usually object-oriented)/data model (usually relational), and business logic (usually php)/client-side (javascript).
- Wants to live in a world where Javascript runs on DB (JSON document stores), server (V8, node.js, etc), and client (the way it is now)

James Williams–BT/Ribbit: MongoDB on Groovy

- NoSQL is pot-relational, schemaless. Groovy is post-java, allows metaprogramming.
- Makes Mongo + Groovy be a good match in philosophy.

## Panel: Schema design and document-oriented DBs

(I missed most of this)

Panelists

- Paul Davis–would store patient history in a document store, but would still trust RDBMSs for mission-critical medical applications where strong consistency is required. Represented CouchDB.
- Eliot Horowitz–10gen (MongoDB)–advocates doing joins in-app, since Mongo doesn’t have foreign key constraints anyway
- Bryan Fink–Basho (Riak)–similar lack of foreign key constraints, also no indices.

Indexing

- Riak has no indexes. Use SOLR/Lucene to do full-test index of documents (wtf?)
- MongoDB–indices similar to mysql indices. Even have geospatial indexing.
- CouchDB does indices by way of mapreduce, as described above.

Foreign Keys for relations

- Riak supports links (references) but doesn’t enforce them and doesn’t clean up links to deleted items.
- MongoDB–DB references exists to refer to other documents. No constant validation, and deleted objects result in broken links (avoids multisite transactions).

How to lock down schemas/do migrations

- Riak–keep version number in the document. Modify schema on read. i.e. handle it in the application.
- MongoDB–similar process, but indices break when schema changes. Will add rename functionality soon.
- CouchDB–like everything in couchdb, use mapreduce.

Horizontal partitioning

- Riak–add machines. consistent hashing + read repair on failure. mapreduces run locally, so adding machines adds cpu power for mapreduce tasks.
- MongoDB–shard on range. currently has master-slace replication, but soon replica sets.
- CouchDB—no support–build your own partitioning/hashing scheme in front of couchdb installs.

Consistency

- Riak–eventual consistency using vector clocks. In some modes, can get back multiple versions which had conflicts to be solved by application. Like in dynamo paper, claims this is actually easy to solve in most cases.
- MongoDB–single master for any shard, so 100% consistent.

## Panel: Evolution of a Graph Data structure from research to production

Panelists

- Boris Iordonov–HypergraphDB (stores hypergraphs)
- Peter Neubauer–Neo4J (stores graphs w/ directed edges and typed nodes that have properties).
- Sandro Hawke–Represented W3C RDF model. Some think of it as a directed graph w/ URIs for source nodes and edges, and URIs or literal values for destination nodes.

How do you do schemas

- HypergraphDB has schema support at low level and package-level
- Neo4J doesn’t–leaves it to higher-level packages
- RDF–datatypes borrowed from XML, and RDFs or OWL for schemas

Implementation details

- HyperGraphDB offers ACID guarantees and may soon offer MVCC.
- Neo4J gives ACID guarantees. Constant-time traversals result in 1000-2000 traversals/msec (I think this is dubious on a DFS of a graph–each traversal would be a disk seek–what benchmark gave this?) **Update:** this was for in-memory or cached graphs.
- RDF is a standard, but in general query languages such as SPARQL are less about node traversal and more about graph pattern matching.

Query Model

- HypergraphDB—supports BFS/DFS or “more complicated” traversals. Query language for graph pattern finding as well. Supports SPARQL via a Sail, but no XPath since it’s not expressive enough for hypergraphs.
- Neo4J–traversals by way of objects that are represented as Java objects. Also supports SPARQL, XPath.
- RDF–lots of libraries in each language for raw graph access. Also, if you prefer, use SPARQL for declarative queries.

Who uses it

- HypergraphDB–released 2 months ago. Used for search in miami dade county. Knowledgebase for NLP/information extraction project.
- Neo4J–opensourced in 2007, lots of interest in social networking, recommendation engines, GIS/spatial indexing, activity streams, intelligence community.
- RDF–defense/intelligence, then health/life sciences picked it up, and now govt. data (data.gov.uk is represented by a bunch of sparql endpoints). govt data demands standards!

Sharding–graphs are hard to slice.

