---
layout: post
title: John Glaser on Healthcare Information Technology
date: '2011-12-15T11:21:00+00:00'
tags: []
tumblr_url: https://blog.marcua.net/post/14265051674
---
I recently sat in on a lecture for Professor Peter Szolovits’s [Biomedical Computing](http://stellar.mit.edu/S/course/6/fa11/6.872/index.html) course. The lecture was open to a greater audience, given the prominence of the speaker. As a non-expert, I found it to be a useful look into the current state of healthcare IT and the coming legislative and technical challenges facing the industry. My notes are below.

John Glaser, Ph.D.  
Formerly CIO of Partners/Brigham And Women’s Hospital  
Currently CEO of Siemens Health Services

Free advice: get a healthcare proxy and power of attorney set up. Easier to do now than have someone else guess later how you want to live/die.

Why does Health IT suck?

- Not for lack of money put into the system
- Not for lack of smart people working on the problem

Current model

- Insurance companies/patients pay per volume (per birth, per surgery, etc.) almost regardless of quality
- Boards of directors are very conservative. Don’t want to be the board that made an IT decision that made a huge hospital fail.

U.S. Numbers to give context

- 60% of hospitals are \<= 100 beds
- Of 500K physicians, majority work in 2-3-doctor practice (not IT-savvy, or modestly interested in IT at best)
- 2/3 of medical decisions are heuristic/not scientific, and many have a difficult-to-verify outcome
- volatile knowledge domain: 700k academic articles have come out in the last (decade?)
- 20% of doctors are a decade away from retirement, so perhaps newer doctors will bring IT mentality with them?
- PricewaterhouseCoopers survey: 58% of (independent?) doctors considering quitting, selling practice, or joining a larger practice
- various societies are discussing requirements: to become board (re-)certified (oncology, etc.), you have to show facility in technology.

Health IT Services

- huge fragmentation: the 3rd largest health IT services company has 7% of market. if they win every open engagement from now until (?), they will have 11% of the market.
- lots of players: 300 electronic health record providers in US, 25% exit and 25% enter per year
- engagements are long: bringing up a new hospital IT system takes 2-4 years. from the moment you decide to change IT systems, you will continue to use your old one for the next 4-5 years as you transition.

Affordable Care Act (ACA)

- costs are projected to go up 26% in the next decade. ACA stipulates that govt. will compensate 12% more in the next decade: providers have to make up the difference.
- to incentivize quality care, govt. will hold on to 10% of payments until you prove treatment was effective (hard to define).
- currently, for a single procedure (e.g., total hip replacement) you might get 12 different bills (e.g., surgeon, materials, anesthesia). new system: govt. pays a single provider one bill, with a fixed amount. incentivizes a holistic view.
- risk: hospitals go out of business. potential future doctors don’t enter medicine. doctors “fire” bad patients to make their numbers look good.

Consolidation

- doctors in small practices joining larger networks to avoid managing the ACA requirements.
- single payment requirement will cause groups of doctors to more tightly collaborate (contractually).

Transition challenges

- ACA is rolling out over the course of a decade.
- need to be careful, since some patients will be handled by old rules, and some by new rules. so do you not apply decision support-based treatment to patients on old rules, or just do fee-for-service? lots of mental overhead for doctors.

Fixed fee challenges

- paying a fixed amount per treatment doesn’t work for everything. Diabetes is sort of predictable, but a trauma might range from a broken toe to severe burns on 90% of body.
- (Adam’s note) perhaps large pools of insured patients will smooth over the individual spikes in cost of care.

Information Technology needs

- systems must span inpatient, outpatient, emergency care, rehab
- need revenue cycle + contract management system that handles continuum of care. this is complex: medicare + blue cross might pay diff amounts for “good” diabetes treatment, and “good” might be defined differently.
- systems should manage individuals and populations: how did all 100 people w/ respiratory problems do last month? which patients strayed from predicted path? what should have happened? why/why not?
- sophisticated business intelligence + analysis: predict who will get worse, etc.
- interoperability w/ different providers
- rules+workflow engines to ensure followups/next steps/help primary care doctors coordinate care, manage exceptions, follow up properly. also allow this in collaborative care environment w/ lots of specialists checking in and out.
- high availability + low total cost of ownership
- engage patients

New challenges for primary care physicians (PCPs)

- At the moment, PCP moves from one patient to the next every 15 minutes, sees 100s of lab results per day
- Only 25% of data from specialists comes back to a PCP within a month
- In future, PCPs will be responsible for closing the loop on specialists, tests, etc., with more accountability, but still be given just as much or more information, with similar delays. Workflow management systems are key here!

Interesting technical challenges

- filtering patient care notes: 10s of pages of patient care history. No doctor can read them all before seeing patient. how to help doctors find relevant notes across different doctors, annotations, etc.
- supporting collaboration between multiple providers
- parsing notes to remind providers. e.g., “Ask about patient’s daughter next time.”
- cleaning up conflicting medical record data: was it type 1 or type 2 diabetes? was it a heart attack, or just a test for one?
