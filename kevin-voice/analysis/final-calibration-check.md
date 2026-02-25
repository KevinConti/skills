# Final Calibration Check

Re-generated samples with all SKILL.md rules applied. These replace Samples 1 and 2
from calibration-samples.md.

---

## Sample 1: Blog Post Opening (Technical Project / Decision)

**Target content type:** Blog (personal/essay)
**Rules validated:** No "Here's the problem", no "The lesson here isn't X. It's Y", correct "So, what am I doing instead? Well, I'm going back to..." pattern, no "sexy", comma before "but"

---

Last week I killed a feature that took me three months to build.

Software Ideas had this "trend tracker" thing I'd been working on since January. The idea was pretty simple: scrape a bunch of data sources, score them, and surface ideas that were gaining traction before they hit the mainstream. I was so excited about it. I even told subscribers it was coming in one of the weekly newsletters.

But after three months of dev time and roughly $400 in API costs just for testing, the accuracy was terrible. Like, embarrassingly bad. I ran it against the last 50 ideas I'd manually researched, and it agreed with my analysis maybe 30% of the time. That's worse than a coin flip when you account for the ones that were obvious.

So I pulled the plug.

I know that sounds dramatic, but honestly it was one of the easiest decisions I've made this year. The sunk cost was real (three months!), but the alternative was shipping something that would make the newsletter worse. And the whole point of Software Ideas is that the research is thorough and trustworthy. Shipping a half-baked automation would've undermined the one thing people actually pay for.

And look, I'm not saying don't build features. You should build features. But you also need to be honest with yourself about when something isn't working. I spent the first two months convinced that the next tweak would fix it. It didn't. The data was just too noisy for the approach I was using.

So, what am I doing instead? Well, I'm going back to the semi-manual process that actually works, but investing in better tooling to speed up the parts that are slow. Less glamorous, way more useful.

---

## Sample 2: Professional Email (Project Update)

**Target content type:** Email
**Rules validated:** "Hey!" opener, "Best," closer, numbered list for action items, comma before "but"

---

Hey!

Quick update on where things stand with the analytics migration. We finished moving the event tracking over to the new pipeline last Thursday, and so far everything looks good. The numbers are matching up with the old system within about 2% (which is expected given the different sampling methods).

There are two things I still need from your end:

1. Someone with admin access to the old dashboard to export the historical data before we shut it down. I'd do it myself, but my account doesn't have the right permissions.
2. A 30-minute call sometime next week to walk through the new reporting setup so your team knows where to find everything.

I'm planning to keep the old system running through the end of March as a safety net. After that, we'll turn it off unless anyone flags issues.

Let me know what works for the call and who can handle the export. No rush on the call, but the export would be great to get done this week if possible.

Best,
Kevin Conti
