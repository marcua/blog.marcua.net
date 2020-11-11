---
layout: post
title: 'Autodata: Automating common data operations'
---

Alright.  I've directly made a bunch of suggestions and edits as stream of consciousness as I read through.  Main points:

* Beginning could be tighter,
* list of needs is good (could have a bit more categorization)
* Autodata of what? To what end?  I think you should make that clear and pick a class of tasks.  Scorpion/Sisu for instance don't have much to do with building models (though they could be extended towards that).  Dabl is specifically about models.  
* Gu's suggestion of replacing Autodata x.0 --> semantically meaningful signifier is good.

Misc Comments start:

* This image from Jeff's Visualization Is Not Enough talk may help set the stage
  * <img src="https://eagereyes.org/wp-content/uploads/2019/09/58C5C099-48C7-4E5B-B5FA-F9E0EAFDCCBE.jpeg"/>
* The paragraph is kind of long.  
* I think you're mainly trying to say that there's a lot of steps, it's hard to do each step properly since it depends on teh data and use case, and it's hard to even know if you did all the "appropriate" steps.  
* It could help to give examples of steps and how if they are even slightly off, how a conclusion could be wrong.  That's more descriptive than prescriptive.

If you speak with a data scientist or engineer, you'll hear about all of the important procedures they put in place to ensure their work is trustworthy and repeatable. For instance, they might say that when presented with a new dataset, it's important to interrogate the data to get familiar with empty values, outliers, duplicates, and other limitations; before performing analyses, it's important to clean and structure the data, often placing it in a database and strictly defining its schema; when feature engineering, you should derive as many details from the dataset, but not create so many features that they rival the size of your dataset; before you build a model, it's important to perform some exploratory data analysis to build hypotheses around how the variables in your dataset interact; and finally, as you build models, you have to be careful to separate out testing and validation sets, ensure your model isn't more complex than the dataset allows, monitor a collection of scores to identify your most predictive model while also vetting your model hasn't gotten so large that it won't perform in production.


* I think the phrase "these procedures" implies that the paragraph above is sufficient

Following these procedures is critical if you want to trust your analyses and models. Unfortunately, each of the procedures above is arcane and error-prone. Every data practitioner has their go-to copy-pastable templates for running cross validated grid search across the eye-numbing amount of variables for your favorite boosted or bagged collection of trees. They copy and paste the old code for plotting data across a number of axes to identify correlations. They dutifully edit their code for identifying the schema of the misshapen JSON blobs from their last project so that it works in their current project.

* The last sentence sounds like the actual lead!! 

On one hand, every data practitioner knows they have to perform tens of steps in order to believe their own analyses. On the other hand, the process for each step involves handed-down error-prone modifications to thousands of lines of code copied from previous projects. It's no surprise that even after checking off every item of a good data practices checklist, the data practitioner doesn't fully trust their own work.

* Make clear the ideal first: 
  * Ideally, we put data in a box and correct trustworthy answers come out.  
  * It's unlikely we can fully automate the entire process, but theres' great headway towards automating different pieces and helping orchestrate
* who constitutes the data community these days?

Luckily, the data community has been making a lot of these operations less arcane and more repeatable. The community has been automating common procedures including data loading, exploratory data analysis, feature engineering, and model-building. This new world of *Autodata* removes some agency from data practitioners in exchange for repeatability and a reduction in rote error-prone work.

* "Motivated by practical challenges we've faced at B12?"
* I get the sense that the list of projects is to show examples of how far we are from autodata 100.0?  Hint at that explicitly by using a more pointed word than "intriguing".  Please allow me to suggest a few:  "Disappointing", "Misguided", or "Good starts but not there yet".  
 
In this post, I'll highlight a few projects I've found intriguing, categorized by stage in the data analysis pipeline. The post isn't meant to be comprehensive: the projects here all relate to some problem I've faced at work that have caused me to look for solutions.

###  *Data ingestion*

* Lead with the goal: get shit into a database.
  * Do you load into a DB because you're a DB PHd?  Or beacuse it's a good idea?
  * What's the limitation of dumping shit into a data frame?
* Is it just that ETL hasn't been introduced to the Jupyter/data science world?
* Snowflake's auto-nested-schema detection is dope.  S4.3 of https://w6113.github.io/files/papers/snowflake.pdf

When presented with a new CSV file or collection of JSON blobs, my first reaction is to load the data into some structured data store. Most datasets are small, and many analyses start locally, so I try loading the data into a [SQLite](https://www.sqlite.org/index.html) or [DuckDB](https://duckdb.org/) embedded database. This is almost always harder than it should be: the CSV file will have inconsistent string/numeric types and null values, and the JSON documents will pose additional problems around missing fields and nesting that prevents their loading into a relational database. 

I've been intrigued by [sqlite-utils](https://sqlite-utils.readthedocs.io/en/stable/cli.html), which offers easy CSV and JSON importers into SQLite tables. DuckDB has similar support for [loading CSV files](https://duckdb.org/docs/data/csv). If your data is well-structured, these tools will allow you to load your data into a SQLite/DuckDB database. Unfortunately, if your data is nested, missing fields, or otherwise irregular, these automatic loaders tend to choke. 

* Megagon folks have doing some neat semantic type detection stuff https://arxiv.org/abs/1911.06311

There's room for an open source project that takes reasonably structured data and generates a workable schema from it. In addition to detecting types, it should handle the occasional null value in a CSV and missing field in JSON, and should flatten nested data to better fit the relational model.  Projects like [genson](https://pypi.org/project/genson/) handle schema detection but not flattening/relational transformation. Projects like [visions](https://dylan-profiler.github.io/visions/visions/getting_started/introduction.html) lay a nice foundation for better detecting column types. I'm excited for a future project that better ties together schema detection, flattening, and loading so that less manual processing is required.

### *Exploratory data analysis*

* Ambrose' quartet is a good reason why "exploration" is useful!  
* Jiannan's been building a "sci-kit for data prep" tool: https://dataprep.ai/

Looking at the data you've loaded before trying to build models with it is important. Wasting your time looping over variables and futzing with plotting libraries is not. The [pandas-profiling](https://pandas-profiling.github.io/pandas-profiling/docs/master/rtd/pages/introduction.html) library will take a [pandas](https://pandas.pydata.org/) dataframe and automatically generate an interactive set of per-column summary statistics and plots, raise warnings on missing/duplicate values, and identify useful interaction/correlation analyses (see an [example](https://pandas-profiling.github.io/pandas-profiling/examples/master/meteorites/meteorites_report.html) to understand what it can do). Whereas `pandas-profiling` is geared toward helping you get a high-level sense of your data, the [dabl](https://dabl.github.io/0.1.9/) project has more of a bias toward analysis that will help you build a model. It will automatically provide plots to identify the impact of various variables, show you how those variables interact, and give you a sense of how separable the data is.

###  *Feature engineering*


The success of companies like [Trifacta](https://www.trifacta.com/) and [Tamr](https://www.tamr.com/) shows that data cleaning and data integration are a huge problem in large companies. Perhaps because I've worked at smaller companies with data teams that know the importance of extracting, structuring, and cleaning data as early as possible, cleaning and integration have been smaller time sucks. In my N=1 experience, a ton of data engineering time goes into feature engineering, and most of that work could be aided by machines (and potentially automated away). Data engineers spend so much time one hot encoding their categorical variables, extracting features from datetime fields, vectorizing text blobs, rolling up statistics on related entities, and selecting features once they have taken things too far. I'm heartened to see automatic feature engineering tools like [featuretools](https://featuretools.alteryx.com/en/stable/) for relational data and [tsfresh](https://tsfresh.readthedocs.io/en/latest/text/quick_start.html) for timeseries data. To the extent that engineers can use these libraries to automatically generate the traditional set of features from their base dataset, we'll save days to weeks of work.

###  *Model-building*

* Ameet/Evan/Neil's company Determined.ai seems to be doing the hyperparam search management
* Bunch of papers suggest that model doesn't matter.  Re's Overton paper from CIDR 2020 explicitly says this.

A project like [scikit-learn](https://scikit-learn.org/stable/) offers so many models, parameters, and pipelines to tune when building a classification or regresion model. In practice, every use I've seen of `scikit-learn` has wrapped those primitives in a grid/random search of a large number of models and a large number of parameters. It's pretty mindless, and not always informed by some deep understanding of the models or which parts of the parameter space to explore. I've seen engineers spend weeks running model searches to eke out a not-so-meaningful improvement to an F-score, and would have gladly traded off a tool to help us arrive at a reasonable model faster. Luckily, AutoML projects like [auto-sklearn](https://automl.github.io/auto-sklearn/master/) aim to abstract away model search: given relatively feature engineered data and a time budget, `auto-sklearn` will emit a reasonable ensemble in ~10 lines of code. The [dabl](https://dabl.github.io/0.1.9/) project also offers up the notion of a small amount of code for a reasonable baseline model. Whereas `auto-sklearn` asks the question "How much compute time are you willing to exchange for accuracy?" `dabl` asks "How quickly can you understand what a reasonable model can accomplish?"



## Looking Forward

* You'll want to define up front what autodata is supposed to mean!
* Rephares "What could the future look like" as "What are the steps towards autodata"?

I'm sure I've missed a number of projects in the space, as well as entire categories in the space. If anyone wanted to collaborate on a deeper survey, I'd be game. Autodata is in its infancy: most of the projects listed above aren't yet at 1.0 versions.  What could the future of Autodata look like?


* Autodata 0.0: Today, many of these projects exist, but aren't data practitioners' go-to tools. While dabblers will dabble, most practitioners will still rely on primitives like `pandas` or `scikit-learn` to make progress.
* Autodata 1.0: As the tools, documentation, and examples solidify over the coming years, practitioners will begin using packages like the ones in this post in production to ingest, understand, and model their data.
* Autodata 2.0: More connective tissue between these projects will remove the need for entire steps in the data pipeline. If `sqlite-utils` used a state-of-the-art schema detection library, "define the schema and load my data" might simply turn into "load my data." Similarly, if AutoML projects relied on best-of-class automatic feature engineering libraries, feature engineering as an explicit step might be eliminated in some cases.
  * this is a good point.  there's so many places and formats just to store data: different DBs, data frames, csvs, etc
* Autodata 3.0: So far, the automation I've described has been around removing rote work in the traditional data practitioner's workflow. It doesn't, however, actually answer questions you might have about the data. Future automation can help us answer higher-level questions that arise every day in an organization. For example, work like [Scorpion](http://www.vldb.org/pvldb/vol6/p553-wu.pdf) and [Sisu](https://sisudata.com/product/) answer the question "what might have caused this variable to change?" With Autodata 3.0, it would be great to see open source packages that help answer high-level questions like these with as little code as possible.