# Calibration Samples - Kevin Conti Voice Skill

Generated following Prompt 3A of the personal voice extraction process.
These samples test the voice skill across 5 content types from the corpus.

---

## Sample 1: Blog Post Opening (Technical Project / Decision)

**Target content type:** Blog (personal/essay)
**Voice patterns tested:** Opening with concrete fact/event, short paragraphs, contractions, emotional directness, specific metrics, parenthetical asides, sentence fragments for emphasis, conjunction starters

---

Last week I killed a feature that took me three months to build.

Software Ideas had this "trend tracker" thing I'd been working on since January. The idea was pretty simple: scrape a bunch of data sources, score them, and surface ideas that were gaining traction before they hit the mainstream. I was so excited about it. I even told subscribers it was coming in one of the weekly newsletters.

Here's the problem. After three months of dev time and roughly $400 in API costs just for testing, the accuracy was terrible. Like, embarrassingly bad. I ran it against the last 50 ideas I'd manually researched, and it agreed with my analysis maybe 30% of the time. That's worse than a coin flip when you account for the ones that were obvious.

So I pulled the plug.

I know that sounds dramatic, but honestly it was one of the easiest decisions I've made this year. The sunk cost was real (three months!), but the alternative was shipping something that would make the newsletter worse. And the whole point of Software Ideas is that the research is thorough and trustworthy. Shipping a half-baked automation would've undermined the one thing people actually pay for.

The lesson here isn't "don't build features." It's that you need to be honest with yourself about when something isn't working. I spent the first two months convinced that the next tweak would fix it. It didn't. The data was just too noisy for the approach I was using.

What am I doing instead? Going back to the semi-manual process that actually works, but investing in better tooling to speed up the parts that are slow. Less sexy, way more useful.

---

## Sample 2: Professional Email (Project Update)

**Target content type:** Email
**Voice patterns tested:** "Hey!" opener, "Best," closer, short paragraphs, polite-casual register, practical details front-loaded, contractions, direct request framing

---

Hey!

Quick update on where things stand with the analytics migration. We finished moving the event tracking over to the new pipeline last Thursday, and so far everything looks good. The numbers are matching up with the old system within about 2% (which is expected given the different sampling methods).

There are two things I still need from your end. First, I need someone with admin access to the old dashboard to export the historical data before we shut it down. I'd do it myself but my account doesn't have the right permissions. Second, I want to schedule a 30-minute call sometime next week to walk through the new reporting setup so your team knows where to find everything.

I'm planning to keep the old system running through the end of March as a safety net. After that, we'll turn it off unless anyone flags issues.

Let me know what works for the call and who can handle the export. No rush on the call, but the export would be great to get done this week if possible.

Best,
Kevin Conti

---

## Sample 3: Reddit Comment (Technical Question Response)

**Target content type:** Reddit
**Voice patterns tested:** Context-setting opener, direct address to community, persuasive framing with evidence, casual register, specific examples, emotional directness, bold for emphasis, "you" address

---

I see this question come up a lot and I think most of the answers miss the point.

Everyone says "just pick a niche" like it's the easiest thing in the world. But the actual hard part isn't picking a niche. It's picking a niche where people are already spending money on bad solutions. Those are two very different things.

I run Software Ideas, where we research SaaS opportunities every week. The pattern I see over and over is this: founders pick a niche they're personally interested in, find a problem that exists, and then build a product without checking if anyone actually pays for solutions to that problem right now.

Here's a concrete example. "Project management for freelancers" sounds like a great niche. Freelancers definitely have project management problems. But look at what freelancers actually spend money on: invoicing, accounting, time tracking. The project management piece? Most of them use a free Trello board and they're fine with it. There's no money there.

Compare that to something like "compliance reporting for small healthcare practices." Boring as hell, right? But these practices are legally required to do this, they hate doing it, and they're already paying $200-500/month for outdated software that sucks. That's where the opportunity is.

So don't just pick a niche. Pick a niche where you can point to existing spend and existing frustration. If you can't find people already paying for a worse version of what you want to build, that's a red flag.

---

## Sample 4: Tweet Thread (Multi-Paragraph Tech Take)

**Target content type:** Tweet
**Voice patterns tested:** Dense declarative style, jumping straight into thesis, multi-paragraph format, higher abstraction level, no formatting/headers/bullets, contractions, visionary-but-grounded tone, specific references

---

The biggest lie in SaaS right now is that AI features are a moat. They aren't. They're table stakes.

I've been watching the same pattern play out across dozens of products over the past six months. Company adds an AI feature, gets a burst of attention, and then three competitors ship the same thing within weeks. The underlying models are the same. The API calls are the same. The "magic" is a thin wrapper around the same foundation model everyone else is using.

The actual moat is the same thing it's always been: distribution and data. If you have a unique dataset that your AI features train on, that's defensible. If you have 10,000 paying customers whose workflows generate proprietary data, that's defensible. But "we added GPT to our search bar" is not a moat. It's a feature that took your competitor's intern a weekend to copy.

I think we're going to see a lot of SaaS companies learn this the hard way over the next year. The ones that invested in genuine data advantages will pull ahead. The ones that treated AI as a marketing play will be right back where they started, competing on the same fundamentals as before.

---

## Sample 5: Blog Post (Strategy / How-To)

**Target content type:** Blog (strategy)
**Voice patterns tested:** Personal context hook, ## headers, numbered sections, consequence framing, rhetorical questions with immediate answers, binary contrast, quote blocks/credibility, bullet lists, "you" address, specific examples with real metrics, brief outro

---

# Why Most Founders Get Pricing Wrong (And How to Fix It)

I changed Software Ideas pricing three times in the first year. The first time, I was charging $9/month. I was terrified to charge more because I figured no one would pay for a newsletter about SaaS ideas. By the time I got to 200 subscribers at $9/month, I was doing the math and realizing I couldn't make this work as a full-time thing.

So I raised prices. And here's what happened: nothing bad. Churn didn't spike. New subscribers kept coming in at the same rate. I'd been leaving money on the table for months because I was scared of a reaction that never came.

This is something I see constantly with indie hackers and bootstrapped founders. They price too low, too early, and then they're stuck.

## The core problem: you're pricing based on your comfort, not the market

What drives most founders to pick their initial price? Honestly? It's usually a gut feeling based on what they'd personally pay. And that's almost always wrong.

Here's why. You are not your customer (unless you've specifically validated that you are). Your willingness to pay is shaped by your income, your priorities, and your relationship with money. Your customers might be companies with actual budgets who literally don't care about the difference between $29 and $49/month.

## The two pricing mistakes I see over and over

### Mistake 1: Pricing based on cost

Some founders look at their expenses (hosting, API costs, their time) and price just above that. This makes intuitive sense but it completely ignores what the customer gets out of it.

Think about it this way. If your product saves a company 10 hours of work per month, and that company pays its employees $50/hour, you're saving them $500/month in labor. Charging $19/month for that is insane. You're capturing less than 4% of the value you create.

### Mistake 2: Pricing based on competitors

The other trap is looking at what competitors charge and pricing slightly below them. This is dangerous for two reasons:

- You have no idea if your competitors have their pricing right (spoiler: they probably don't)
- You're anchoring yourself to someone else's strategy instead of understanding your own value

## What to do instead

Price based on the value your product creates for the customer. This sounds obvious, but it requires you to actually talk to your customers and understand what they'd pay.

Here's a dead simple framework that works:

- Ask 10 customers: "At what price would this be too expensive to consider?"
- Ask the same 10: "At what price would this be so cheap you'd question the quality?"
- Your sweet spot is somewhere between those two numbers

I used a version of this when I went from $9 to $19 to $29/month at Software Ideas. Every time, the "too expensive" number was way higher than I expected. Customers valued the research at $50-80/month. I was charging $9.

If you don't talk to your customers about pricing, you're guessing. And in my experience, founders consistently guess too low. The risk of being too cheap is way worse than the risk of being too expensive, because at least if you're too expensive, customers will tell you. If you're too cheap, they'll just quietly pay and you'll never know what you left on the table.
