---
layout: post
title: 'Autodata: Automating common data operations'
---
# Introduction

Much of the work a data scientist or engineer performs today is rote and error-prone. Data practitioners have to perform tens of steps in order to believe their own analyses and models. The process for each step involves modifications to hundreds/thousands of lines of code copied from previous projects, making it easy to forget to tweak a parameter or default. Worse yet, because of the many dependent steps involved in a data workflow, errors compound. It's no surprise that even after checking off every item of a good data practices checklist, the data practitioner doesn't fully trust their own work.

Luckily, the data community has been making a lot of common operations less arcane and more repeatable. The community has been automating common procedures including data loading, exploratory data analysis, feature engineering, and model-building. This new world of *Autodata* removes some agency from data practitioners in exchange for repeatability and a reduction in repetitive error-prone work. Realized fully

To be clear, Autodata doesn't replace critical thinking: it just means that in fewer lines of code, a data practitioner can follow a best practice. Fully realized, an Autodata workflow will break a high-level goal like "I want to predict X" or "I want to know why Y is so high" into a set of declarative steps (e.g., "Summarize the data," "Build the model") that require little or no code to run, but still allow for introspection and iteration.

In this post, I'll first list projects in the space of Autodata, and then take a stab at what the future of Autodata could look like.

# The problems and projects
Here are a few trailblazing projects in the space, categorized by stage in the data analysis pipeline. I'm sure I've missed a number of projects in the space, as well as entire categories in the space. This area deserves a deeper survey: I'd love to collaborate with folks that agree!

## Data ingestion
You can't summarize or analyze your data in its raw form: you have to turn it into a dataframe or SQL-queriable table. When presented with a new CSV file or collection of JSON blobs, my first reaction is to load the data into some structured data store. Most datasets are small, and many analyses start locally, so I try loading the data into a [SQLite](https://www.sqlite.org/index.html) or [DuckDB](https://duckdb.org/) embedded database. This is almost always harder than it should be: the CSV file will have inconsistent string/numeric types and null values, and the JSON documents will pose additional problems around missing fields and nesting that prevents their loading into a relational database. The problem of loading a new dataset is the problem of describing and fitting it to a schema.

I've been intrigued by [sqlite-utils](https://sqlite-utils.readthedocs.io/en/stable/cli.html), which offers easy CSV and JSON importers into SQLite tables. DuckDB has similar support for [loading CSV files](https://duckdb.org/docs/data/csv). If your data is well-structured, these tools will allow you to load your data into a SQLite/DuckDB database. Unfortunately, if your data is nested, missing fields, or otherwise irregular, these automatic loaders tend to choke.

There's room for an open source project that takes reasonably structured data and generates a workable schema from it. In addition to detecting types, it should handle the occasional null value in a CSV and missing field in JSON, and should flatten nested data to better fit the relational model.  Projects like [genson](https://pypi.org/project/genson/) handle schema detection but not flattening/relational transformation. Projects like [visions](https://dylan-profiler.github.io/visions/visions/getting_started/introduction.html) lay a nice foundation for better detecting column types. In terms of papers, [Sato](https://arxiv.org/pdf/1911.06311.pdf) offers some thoughts on how to detect types and the [Section 4.3 of the Snowflake paper](https://dl.acm.org/doi/pdf/10.1145/2882903.2903741 speaks nicely to a gradual method for determining the structure of a blob. I'm excited for a future project that better ties together schema detection, flattening, and loading so that less manual processing is required.

## Exploratory data analysis

When presented with a new dataset, it's important to interrogate the data to get familiar with empty values, outliers, duplicates, variable interactions, and other limitations. Much of this work involves standard summary statistics and charts, and can thus be automatd at a first pass. While looking at the data you've loaded before trying to use it is important, wasting your time looping over variables and futzing with plotting libraries is not.

The [pandas-profiling](https://pandas-profiling.github.io/pandas-profiling/docs/master/rtd/pages/introduction.html) library will take a [pandas](https://pandas.pydata.org/) dataframe and automatically summarize it. Specifically, it generates an interactive set of per-column summary statistics and plots, raise warnings on missing/duplicate values, and identify useful interaction/correlation analyses (see an [example](https://pandas-profiling.github.io/pandas-profiling/examples/master/meteorites/meteorites_report.html) to understand what it can do). Whereas `pandas-profiling` is geared toward helping you get a high-level sense of your data, the [dabl](https://dabl.github.io/0.1.9/) project has more of a bias toward analysis that will help you build a model. It will automatically provide plots to identify the impact of various variables, show you how those variables interact, and give you a sense of how separable the data is. The [dataprep project](https://dataprep.ai/), from a group of folks that knows quite a bit about data cleaning, is building an API standardize the earlier parts of data pipelines, including cleaning and exploratory data analysis.

## Feature engineering
To build predictive models over your data, you have to engineer features for those models. For example, for your model to identify Saturdays as a predictor of poor sales, someone has to extract a `day_of_the_week` feature from the `purchase_datetime` column. In my N=1 experience, a ton of data engineering time goes into feature engineering, and most of that work could be aided by machines (and potentially automated away). Data engineers spend so much time one hot encoding their categorical variables, extracting features from datetime fields, vectorizing text blobs, and rolling up statistics on related entities. Feature engineering is further complicated by the fact that you can take it too far: because of the [curse of dimensionality](https://en.wikipedia.org/wiki/Curse_of_dimensionality), you should derive as many details as possible from the dataset, but not create so many features that they rival the size of your dataset. Often, engineers have to whittle their hard-earned features down once they realize they've created too many.

I'm heartened to see automatic feature engineering tools like [featuretools](https://featuretools.alteryx.com/en/stable/) for relational data and [tsfresh](https://tsfresh.readthedocs.io/en/latest/text/quick_start.html) for timeseries data. To the extent that engineers can use these libraries to automatically generate the traditional set of features from their base dataset, we'll save days to weeks of work. There's room for more open source development here, however, as much of the work has been about automatically creating new features (increasing dimensionality) and not enough has been on identifying how many features to create (preserving model simplicity).

## Model-building

A project like [scikit-learn](https://scikit-learn.org/stable/) offers so many models, parameters, and pipelines to tune when building a classification or regresion model. In practice, every use I've seen of `scikit-learn` has wrapped those primitives in a grid/random search of a large number of models and a large number of parameters. Data practitioners have their go-to copy-pastable templates for running cross validated grid search across the eye-numbing amount of variables for your favorite boosted or bagged collection of trees. Running the search is pretty mindless, and not always informed by some deep understanding of the models or which parts of the parameter space to explore. I've seen engineers spend weeks running model searches to eke out a not-so-meaningful improvement to an F-score, and would have gladly opted for a tool to help us arrive at a reasonable model faster.

Luckily, AutoML projects like [auto-sklearn](https://automl.github.io/auto-sklearn/master/) aim to abstract away model search: given a feature engineered dataset, a desired outcome variable, and a time budget, `auto-sklearn` will emit a reasonable ensemble in ~10 lines of code. The [dabl](https://dabl.github.io/0.1.9/) project also offers up the notion of a small amount of code for a reasonable baseline model. Whereas `auto-sklearn` asks the question "How much compute time are you willing to exchange for accuracy?" `dabl` asks "How quickly can you understand what a reasonable model can accomplish?"

## Repeatable pipelines

The sections present data problems as one-time problems. In practice, much of the work described above has to repeat as new data and new questions arise. If you transformed your data once to ingest or feature engineer it, how can you do that each time you get a new data dump? If you felt certain in the limitations of the data the first time you analyzed it, how can you remain certain as new records arrive? When you revisit a model to train it on new data or test a new hypothesis, how can you remember the process you used to arrive at the model last time?

There are solutions (not all of them open source just yet) for each of these problems of longevity. [dbt](https://docs.getdbt.com/docs/introduction) helps you create repeatable transformations so that the data loading workflow you created on your original dataset can be applied as new records and updates arrive. [great_expectations](https://greatexpectations.io/) helps you asserts facts about your data (e.g., unique columns, maximum values) that should be enforced across updates, and offers experimental functionality to automatically profile and propose such assertions.

Whereas the open source world has good answers to repeatable data transformation and data testing, I haven't been able to find open source tools to track and make repeatable all of the conditions that let to a trained model. [Weights & Biases](https://www.wandb.com/) and [CometML](https://www.comet.ml/) offer products in this space, and I hope that open source competitors arise.

# The future of Autodata

Autodata is in its infancy: most of the projects listed above aren't yet at 1.0 versions.  What could the future of Autodata look like?
* Autodata 0.0: Today, many of these projects exist, but aren't data practitioners' go-to tools. While dabblers will dabble, most practitioners will still rely on primitives like `pandas` or `scikit-learn` to make progress.
* Autodata 1.0: As the tools, documentation, and examples solidify over the coming years, practitioners will begin using packages like the ones in this post in production to ingest, understand, and model their data.
* Autodata 2.0: More connective tissue between these projects will remove the need for entire steps in the data pipeline. If `sqlite-utils` used a state-of-the-art schema detection library, "define the schema and load my data" might simply turn into "load my data." Similarly, if AutoML projects relied on best-of-class automatic feature engineering libraries, feature engineering as an explicit step might be eliminated in some cases.
* Autodata 3.0: So far, the automation I've described has been around removing rote work in the traditional data practitioner's workflow. It doesn't, however, actually answer questions you might have about the data. Future automation can help us answer higher-level questions that arise every day in an organization. For example, work like [Scorpion](http://www.vldb.org/pvldb/vol6/p553-wu.pdf) and [Sisu](https://sisudata.com/product/) answer the question "what might have caused this variable to change?" With Autodata 3.0, it would be great to see open source packages that help answer high-level questions like these with as little code as possible.


*Thank you to Peter Bailis, Lydia Gu, and Eugene Wu for their suggestions on improving a draft of this post. The first version they read was an unstructured mess of ideas, and they added structure, clarity, and a few missing reference. I'm particularly grateful for the level of detail of their feedback: I wasn't expecting so much care from such busy people!*



# Bits and pieces



. Finally, as you build models, you have to be careful to separate out testing and validation sets, ensure your model isn't more complex than the dataset allows, monitor a collection of scores to identify your most predictive model while also vetting your model hasn't gotten so large that it won't perform in production.

Following these procedures is critical if you want to trust your analyses and models. Unfortunately, each of the procedures above is arcane and error-prone.  They copy and paste the old code for plotting data across a number of axes to identify correlations. They dutifully edit their code for identifying the schema of the misshapen JSON blobs from their last project so that it works in their current project.

The success of companies like [Trifacta](https://www.trifacta.com/) and [Tamr](https://www.tamr.com/) shows that data cleaning and data integration are a huge problem in large companies. Perhaps because I've worked at smaller companies with data teams that know the importance of extracting, structuring, and cleaning data as early as possible, cleaning and integration have been smaller time sucks.
