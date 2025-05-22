---
layout: post
title: "Rich: Enrich your CSVs with new columns"
date: 2025-05-02
---
This week a fellow B12er was performing an ad-hoc data analysis. They had a spreadsheet with some data, and wanted to classify the rows in the spreadsheet by a few different criteria along which they would look for trends. For an engineer, this would have been a quick Python script wrapping some classifier (in our case, the OpenAI API), but there wasn't an engineer available for the project. We looked at some third-party plugins for Google Sheets, but it wasn't clear what sorts of guarantees they made around data privacy, and we didn't feel comfortable installing them. So, with some help from OpenAI's `o3`, I created [Rich, an OpenAI-powered CSV data enricher](https://marcua.net/minitools/rich/) that's a fully client-side single-page application.

To start, you give Rich an OpenAI key (that's then stored in `localStorage` for convenience), point it at a CSV file, and prompt it to add any number of columns to the CSV. It then calls the OpenAI API row by row and asks it to fill in those extra columns. You get a new CSV with those enriched columns. Here's Rich in action:
![An animated GIF of a user uploading a CSV with three countries in it and adding population and capital columns that are automatically added to the newly downloaded CSV.](/assets/images/rich/rich.gif)

Most of the code (a self-contained HTML file with no external dependencies other than OpenAI) was emitted by `o3` in an hourlong iterative session. At some point the model stopped streaming a portion of the file and I had to manually take over. There was one bug with the initial/simplistic logic for CSV import, but `o3` took that feedback and provided a more robust implementation. There's a lingering optimization opportunity to use something like Structured Outputs/JSON formatting of the responses to require only one call per row rather than one call per CSV cell, but that's for another day.

The amount of boilerplate and nitty-gritty to get started makes this one of these projects I never would have undertaken without an AI assistant. I like that I was able to quickly create a standalone HTML file that respects users' privacy by executing all of its business logic in the browser. I can point someone at Rich knowing I'll never see any of the things they do with the data (OpenAI will, of course:)). Rich is Apache 2-licensed and [the code is available here](https://github.com/marcua/minitools/tree/main/rich). If you use Rich or have suggestions, reach out!
