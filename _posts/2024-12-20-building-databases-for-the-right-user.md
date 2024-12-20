---
layout: post
title: Building databases for the right user
date: 2024-12-20
---
Relational databases are in their sixth decade, and the database community is understandably celebrating and reflecting its accomplishments. In two wonderful pieces, Donald Chamberlin shared [his perspective on the past half-century](https://cacm.acm.org/research/50-years-of-queries/), and Eugene Wu shared thoughts on [where we can go from here](https://wp.sigmod.org/?p=3801). At a time of reflection on relational database management systems as a largely solved problem, I'm struck by a painful contrast: database technology is more powerful than it's ever been, but the average person's relationship with their data is in the worst state its ever been.

In the state of the art that database researchers and practitioners have created, your data isn't yours. In exchange for access to some useful applications, your data likely lives in huge silos controlled by self-interested corporations, to be restricted, lost, leaked, sold, resold, and exploited. The groups that control these databases accrue most of the benefits, and you accrue most of the costs.

How did we get here? I'd argue it's because the smartest database minds have spent the last six decades building excellent technology, but designing it for the wrong user. For 60 years, databases have been designed with database administrators and developers in mind when they should have been designing for the people whose data lives in the databases:
![A hand-drawn cartoon diagram depicting a user, an application, and a database, with the application and database receiving more focus than the user](/assets/images/dbs-right-user/db-focus.png)

The lack of focus on the user didn't come from evil intentions, and there are many technical and organizational reasons why we've centralized data storage and processing. But the end result is the same: while most everyone agrees that you should own your data, most everyone knows that our tools make that challenging or impossible.

Luckily, we can fix the future. I believe that a simple motivating question can rally the database community for many decades to come: **how might we increase people's agency and sovereignty over their own data**? Let's spend the next few decades applying what we've learned so far to the user we should have been designing for all along.

## How it works today, and why it sucks
Let's take the traditional architecture of a web application. A user sends their requests to the application. The application logic in turn queries a database that stores the user's data along with the data of other users:
![A hand-drawn cartoon diagram in which a user provides data to an application, which inserts it into a database. The database acknowledges the insertion to the application, which acknowledges the insertion to the user.](/assets/images/dbs-right-user/traditional-insert.png)

The user never interacts with the database directly, and can only interact with their own data in ways that the application allows. Because the user's data lives in a database owned by someone else, the user loses agency and sovereignty over their own data. Barring regulation or a thoughtful application developer, the user doesn't have unrestricted access to their own data. They can't delete it, visualize it in a different way, or use it in another application. If the user wants to get all of the data they previously shared with the application, there's no guarantee the application will allow that:
![A hand-drawn cartoon diagram in which a user requests their data for an application, which responds "Nope!"](/assets/images/dbs-right-user/traditional-query.png)

The owner of the database, on the other hand, retains most of the power. They can restrict the user's access to their own data. They can delete the data. They can sell the data to a third party. They might introduce a bug that allows other people to access the data. They might get compromised. Or they can avoid all of these mistakes just to be acquired, and have the new management change course.

Put simply: in today's model, your data doesn't live in your database, and so it's not really your data.

## How it should work
Let's modify the architecture of the application above. What if it was easy for a user to create a personal database and authorize the application to access it? The user could maintain control over the database, and the web application would gain credentials to the database for as long as the user wished. An application might have access to many users' databases, and would interact with each user's database with credentials that the user authorized it to have. Here's a user sharing the credentials to their database (a key) with an application: 
![A hand-drawn cartoon diagram in which both the user and the application hav a database. The user provides a key to their database to an application, which inserts it into its database. The application's database acknowledges the insertion to the application, which acknowledges the insertion to the user.](/assets/images/dbs-right-user/proposed-key.png)

With those stored credentials, the application can service future requests from this user by querying the user's database using the stored credentials (XYZ: swap steps 4 and 5 for clarity in diagram below):
![A hand-drawn cartoon diagram in which a user provides data to an application, which looks up that user's key in the application database. The application then, which inserts data into the user's database. The user's database acknowledges the insertion to the application, which acknowledges the insertion to the user.](/assets/images/dbs-right-user/proposed-insert.png)

As long as the application continues to provide utility and the application owner keeps up their end of the bargain, the user can continue to authorize the application to access their data in their database. Our sovereign user has agency over their data, and can authorize multiple applications to interact with their database. They can also decide it's time to revoke access to some of those applications. Unlike in the traditional model, the user doesn't have to ask in order to access any of their previously shared data:
![A hand-drawn cartoon diagram in which a user can request their data from their database, which responds "HERE!" without any interaction with the application.](/assets/images/dbs-right-user/proposed-query.png)

The user is newly empowered to control who accesses the data in their database. They can connect their database to other applications, or modify their own data or visualize it in ways any one application doesn't allow. This model doesn't solve all problems, and an application developer could still leak data inadvertently or by design. A bug could still wipe out or corrupt a user's database, and multiple applications might interact in unexpected or undesirable ways. But in a world where users control their own database, users have more choice, and application owners have more accountability.

Put simply: in the future, your data should live in your database, giving you more control over what happens to that data.

## Terms of data use
Technologies rarely offer guarantees, and having sovereignty over your database wouldn't either. But this change in architecture would offer benefits beyond the technical: if you own the database, you can set the terms for accessing that data.

When you sign up for a service that stores your data today, you agree to Terms of Service (TOS) that dictate how you must act in order to keep using the service and accessing your own data. If you controlled your own database, you'd be able to bring your own set of terms to the relationship: in order to access your data, an application owner would have to agree to your Terms of Data Use (TODU).

In a TODU, you could specify
* Whether an application can log your data,
* Whether an application can copy your data, how, and for how long,
* Whether an application can share your data with a third party, and how,
* Whether an application can analyze your data along with that of other users, or whether the application can use your data to train models, and
* What responsibility the application owner has to communicate a change in management or ownership.

Like Terms of Service, a Terms of Data Use doesn't offer a technical guarantee, but it clarifies some expectations you have of the relationship. When you violate an application's TOS, you risk losing access to the application, and when an application violates your terms of data use, the application owner risks losing access to your database.

Newly empowered database owners are unlikely to write their own terms of data use from scratch. With time, standard checklists, templates, and defaults will provide great starting points, much like GitHub makes it easy to pick an open source license for a new project.

## What would it take?
Any sane technologist at this point will explain to you that databases are HARD! They'd ask if you really expect *the average person* to spin up a database? To back it up? To ensure it's available? To pick Terms of Data Use? To monitor how their data is used and enforce their own policies?

Yes, I expect the average person to do all of these things, but not by technical mastery or sweating the details. The average person will be able to do these things because the smartest database minds will empower them with technology that is designed and purpose-built to responsibly grant them sovereignty over their data.

Here are a few of the hard problems the database community would have to solve:
* *Easy database creation and maintenance*. None of this works until it's as easy to create a database as it is to create a Google document or a GitHub repository. A side project of mine, [ayb](https://github.com/marcua/ayb?tab=readme-ov-file#running-a-client) is a step toward this goal, though much more work in this space is required to allow any user to spin up a database (with good availability and backups) to share with an application.
* *Authorization and usable security*. Once a user creates their database, they have to share it with an application. How might we help users do this easily and securely?
* *Audit logs, provenance, and policies*. By sharing your database with an application, you're opening yourself up to leaks and side-channel attacks. Still, what sort of logging, provenance, and monitoring can we offer users so that they can tell when and how their data is accessed, and by whom? Are there ways to specify policies that restrict how an application uses your data?
* *Multi-user and collaboration*. One beneficial side effect of the traditional web application/database architecture is that, because all users are in one database, multi-user applications have a clear home for shared data. If everyone has their own database, it's more challenging to build applications around shared data. How might we make it easier to federate collaborators' databases?
* *Migrations*. It's complicated enough to change the schema of a database or migrate the data in the database as your application changes. How can we ease the burden on application developers whose application now has to be able to speak with multiple databases, each of which are at different stages of being migrated?
* *Performance, maybe*. Databases are typically quite close to the servers hosting an application. If database servers and application servers are not as collocated, round trips between the two will incur additional latency. I say *maybe* because modern applications generally rely on lots of third-party APIs, and so how bad it it really for an application to have to interact with a somewhat remote third-party database?

## People, not rows
The many decades of success that databases have seen are in large part thanks to their power to provide an abstraction that addresses a wide variety of problems. That abstraction of tables and rows is technically powerful, but it also distracts us from what lies beneath: the rows of a database often contain people, activities, and secrets. Let's keep building on the technical beauty that six decades of database research has provided, but let's not forget who we're building for: when databases contain people, let's help those people own their data.