This document highlights [Company]’s design review process, including best practices that we have learned from years of experience across doc reviews both large and small.

Here are the minimum expectations: if you write a design doc, it should follow the Design Doc Template , so all of our designs have a consistent structure; and you should review the goals before you work on the design itself. If you have questions about how rigorously you need to follow this document / how many people need to review a particular design, reach out to your manager, or any senior engineer. They can help you decide how big to make the reviews.

This document assumes that your design includes both data plane and control plane updates; designs that only include one plane may not need an org-wide review, as one example. Consult a senior engineer if you have questions.

# **0. Goals for this document**

The situation is familiar: an engineer has spent weeks or even months writing a whole design doc, only to have a huge hole poked in it by a senior engineer at the org-wide review. The hole is usually a missing or misunderstood goal, requiring a complete rewrite of the entire document. You just wasted two weeks, and feel terrible! This document is the hindsight that will enable you to avoid repeating our mistakes. If you follow the steps in this doc, you will:

1. Demonstrate incremental progress on design tasks, clearly showing your peers that you are working and making progress

2. Get feedback early in the process, starting within one or two days, to ensure that you have identified the right goals, requirements, and constraints *before* you even start on the design itself.

3. Earn trust by including key reviewers early and often in the design process

4. Create a design that clearly describes (or delegates to other documents) what we will build, why we need to build it, and how it will be done.

**You may experiment with incremental improvements to this process.** If you see a potential improvement and want to try it out, feel free to! Please tell @[Author Name] or @[PM Name]  how it went, and whether we should update this guidance to include it. If this is your first time writing a design doc for [Company], we recommend that you follow this process without experimenting first.

# **1. Goals of this review process**

In one sentence, the goal of design review process is to produce a high-quality design document that concisely, clearly, and convincingly communicates what we want to build, and how we propose to build it. The process is also designed to help teams look around corners and ensure one-way doors are taken deliberately,  while ensuring that the proposal meets the customer and operator experience requirements. The design review process is (and should be) a minimal set of mechanisms to ensure the design meets those goals.

1. Provide an easy-to-follow process that any engineer, from junior to senior levels, can use to create high quality design documents that facilitate well-run, easy-to-deliver features.

2. Deliver design docs quickly, in days-to-weeks instead of weeks-to-months.

3. Earn trust with key allies, so you don't have to defend the whole design yourself at wide-audience reviews like org-wide or partner-team reviews.

4. Ensure that engineering and the PM team are aligned on the customer experience.

5. Provide a collaborative environment to share ideas that drive innovation.

6. Provide relevant, useful, timely, low-stress feedback to the author.

7. Convince the team that we have identified the one-way door decisions, and align the team on how we want to handle those doors

8. Convince the team that the project lead understands the problem and is capable of tweaking the plan as we gain more knowledge.

9. Leave a written record of *why* we made the design decisions in the doc.

10. Ensure ownership of the feature lives with the author / document writer, not some independent reviewer, manager, or other party.

# **2. Design Review Process**

In general, we want to review goals before designs, and review with small expert audiences before wider audiences. Each phase brings a design closer to implementation. The 30,000-foot view looks like this:

1. **Phase 0 Deliverable: PR-FAQ Doc (Customer facing feature only)**

    1. Most customer facing features, and some internal features, benefit from a working backwards doc (PR-FAQ) that highlights the vision, customer benefits and customer experience of a new feature or product. When in doubt, ask your local senior engineer and the PM team if a PR-FAQ is appropriate.

    2. Identify the PM leading the PR-FAQ (can reach out to @[PM Name] ) and work with them to define the problem statement and customer experience. While the PM is responsible for writing the PR-FAQ doc, the design author collaborates with the PM to ensure that the proposal in the PR-FAQ can actually be built.

    3. Design authors should lean on the PM on any customer feedback needed to help drive the customer experience.

2. **Phase 1 Deliverable: Goals Doc**

    1. Understand the broad contours of the problem. Can take 1 hour or 1 week, depending on the problem space and your familiarity with it.

    2. Write the first draft of the problem statement, goals, non-goals, and constraints, following the Design Doc Template. This usually takes 1-2 days.

    3. Review the goals with key allies and partners, and incorporate feedback. This usually takes an afternoon.

    4. If the project team is known, review the goals with the people that will actually be doing the work. If the number of key allies is small, include the project team in the key allies review above. Try to keep these early meetings to 8 people or less; better to hold two small review meetings than one large one, this early in the process.

    5. Review the goals with the design review team, and incorporate feedback. This is usually a 30-minute optional meeting. Incorporating the feedback usually takes an afternoon.

        1. The purpose here is twofold- 1/ to expose the whole team to the design early, so they are aware of the project, and 2/ to ensure there are no big misses in the goals that would require a total rewrite of the design.

        2. It’s also a good way to identify additional key allies; the most vocal critics in the goals review often make good key allies that you can involve in targeted design discussions later in the process.

    6. Review the goals with partner teams, if there are any, and incorporate feedback. This usually takes a day.

3. **Phase 2 Deliverable: Design Doc**

    1. Write a first draft of the design, following the standard template: Design Doc Template . This usually takes a couple days.

    2. Run the first draft by your key allies, and incorporate their feedback. This usually takes a day or two depending on the type of feedback but can take longer.

    3. Run the revised draft by your key allies, get their buy-in, and convince yourselves that the doc is ready for a wider audience.

    4. Review with key partners, if any, and incorporate their feedback.

4. **Phase 3 Deliverable: Implementation**

    1. **You can start implementation here, if you want and have identified various milestones and work items needed for implementation phase.**

    2. Hold a final org-wide / interested-parties review, whose goals are primarily information-sharing and enthusiasm-building, not decision-making. Incorporate any feedback.

    3. Estimate the feature using the Story Sizing guide: (We’re working to expand this to be usable by all teams, with the goals of consistency and automatic project reporting.)

    4. Review the Milestones/stories/work-items with the team working on the implementation.

    5. Start implementing the feature!

5. **Phase 4: Figure out that there's something you need an implementation design for; repeat this process for the specific problem you are facing.**

## **2.1 Phase 1: The Goals Doc**

### **Understand the broad contours of the problem**

The goal here is to get familiar with the problem space, customer ask, etc. For features that have a PRFAQ, you should work with the PM to define the problem statement and customer experience, and ensure that the PR/FAQ gets closure before working on the design. There's nothing worse than spending weeks on a design doc, only for the whole design to be abandoned because the customer requirements changed.

How a PR/FAQ typically gets closed: the PM responsible for writing the PRFAQ will conduct an early review of the doc with the engineering lead, before reviewing the doc with the org’s leadership which generally includes GM, managers, PE and senior engineers.

### **Write initial problem statement; plus goals, non-goals, and constraints**

The goal of this step is to ensure that you understand both *what* we need to build, as well as *why* we need to build it. What do customers want to do with the feature? How much will they use it (capacity)? How sensitive is it to API or data plane latency? How will we know if it is working? The goal for this first review is to define the *solution space*, not the solution: the set of statements that a viable solution would meet.

The Problem Statement gives readers a quick summary of what the rest of the doc is all about by describing the problem you want to solve. It should include both *What* and *Why,* like this:

**Problem**

Today, the Platform does not support IPv6 global IPs or endpoints. This means that IPv6-only customers and clients, especially mobile clients, cannot use the Platform at all. Our customers would like to gain the load-balancing, acceleration, and failover benefits of the Platform for IPv6 clients and endpoints.

It is often useful to include a Customer Experience section here as well, describing how a customer will set up, use, and monitor the feature. I don't have a great example here yet.

Goals are best phrased as statements of fact that solutions can eventually be evaluated against.

**Goals**

1. Allow customers to send traffic from the internet to the Platform using IPv6 global IPs and source addresses.

2. Provide customers with visibility into how much traffic they are sending and where it is being sent, on par with our IPv4 visibility or better.

3. Allow customers to use IPv6 global IPs and endpoint addresses for all Platform endpoint types that support IPv6.

4. The routing behavior should be simple enough that PMs, TAMs, support, and other non-engineers can easily and accurately describe it to customers. (

    1. Specifically, <30s for a customer to understand how the routing behavior works.)

    2. Put another way, the goal is to overall drive to reduce customer confusion on how IPv6 traffic is routing to endpoints as much as possible.

5. Do not regress performance (availability, latency, or throughput) compared to IPv4.

6. Have operator monitoring that is as good or better than what we have today for IPv4, including the ability to measure availability and latency from ASNs across the globe.

7. Have operator tooling and capability that s as good or better than what we have today for IPv4, including the ability to withdraw specific prefixes from a stack and set BGP communities.

Good goals describe *what* is being built, not *how (*that's the Solutions section's job.) There should be many possible ways to meet each goal.

Similarly, a non-goals section can help you avoid unnecessary discussion of aspects that are out of scope of the design. The goal of a non-goals section is to limit the scope of the document (or feature), to avoid wasting discussion (and implementation) time on topics that are not relevant. I like to have a one-sentence rationale, and a note about whether it is a one- or two-way door.

**Non-Goals**

1. **IPv6 support for [Feature B] resources**.

    1. One-sentence rationale: There is not enough customer demand for IPv6 for [Feature B], and the solution space is pretty different for IPv6 compared to IPv4. It merits its own, separate design.

    2. A simple solution is discussed at Appendix 1; more complicated options are discussed at the PR/FAQ addendum in Link 2.

2. **IPv6-to-IPv4 NAT.** We will only support IPv6-to-IPv6 and IPv4-to-IPv4.

    1. One-sentence rationale: IPv6-to-IPv4 NAT does not support source IP preservation, which all the customers we have talked to need to meet their security and compliance needs; we also like the simplicity of "IPv4-to-IPv4 and IPv6-to-IPv6."

    2. We can always add it later as an option at the Resource, Resource Group, or Target level.

3. **IPv4-to-IPv6 NAT.** We will only support IPv6-to-IPv6 and IPv4-to-IPv4.

    1. One-sentence rationale: Per the PR/FAQ [2], most dual-stack and IPv6-only customers have dual-stack endpoints as well (ie, they do not need IPv4-only endpoints behind an IPv6 global IP).

    2. Note that unlike IPv6-to-IPv4 NAT, IPv4-to-IPv6 NAT could support source IP preservation by encoding the IPv4 address in an IPv6 address ( https://tools.ietf.org/html/rfc4291#section-2.5.5. )

    3. We can always add it later as an option at the Resource, Resource Group, or Target level.

4. **IPv6-only resources.** We will only add support for dual-stack resources for now.

    1. One-sentence rationale: There are no IPv6-only endpoints yet in our cloud environment, so adding IPv6-only resources is premature.

    2. We are discussing with the compute team to understand the timeline for IPv6-only subnets, and will scope this back in if the timeline lines up.

If you have numeric requirements, I prefer to list those in a separate Constraints (or Requirements) section. Here are some example constraints: "There is a hard limit of 500 endpoints per resource group"; "a storage service wants to bring 10 trillion concurrent connections"; etc.

I also sometimes use a Challenges section to describe key problems that the design will have to solve. IPv6 was a good example of where we needed this; each challenge got its own solutions section in the eventual design. You won't always know the challenges at this point, so feel free to omit it from the first review.

The list you generate will be incomplete, but it will spark good discussion with you Key Allies.

### **Identify Key Allies**

In general, you want to identify four to six key allies: an experienced engineer that you can bounce lots of ideas off of and get earnest early feedback from; a PM who can ask customers questions on your behalf, and clarify what our customers are looking for; subject matter experts in key code areas the project will need to modify; a key engineer for each partner team that you will need work from to deliver the project; and somebody on the team who is good at writing and can give you syntactic (structure / spelling / grammar / style) feedback. You should also

Here’s that info in a handy table that you can use in your design docs:

Key Allies and early reviewers:

| Role | Person | Why they are here |

| --- | --- | --- |

| Senior Engineer |  | First point of contact for bouncing ideas off of / helping you identify other folks to talk to |

| PM |  | Helps you understand the customer experience |

| Subject Matter Expert (SME) |  | Ensures that the solution is feasible & helps you understand the system |

| Partner Team POC: <team> |  | Ensures the team is aware of the work |

| Syntactic / Writing Feedback |  | Here to ensure the writing in the doc is readable |

| New Team Member |  | Here for visibility and growth / learning |

| Meeting Host |  | Helps run effective review meetings & helps you decide what feedback to incorporate / ignore. |

You will involve these allies early in the design review process, earning their trust and commitment to the design. When it comes time to have org-wide reviews, they'll help ensure you have productive meetings by facilitating discussion and answering questions from our (very zealous / involved / interested) team.

You should also identify a Meeting Host, who will host larger review meetings and take notes. We recommend choosing somebody who is not involved in the particular project under discussion, to ensure that ownership of the design remains with the author and owning team. The Meeting Host can also help you identify which pieces of feedback are important enough to be discussed in the high-level design itself, and which can be addressed in an FAQ or implementation design.

For projects (e.g. [Feature A], [Feature C], Routing) that have impact on our network (e.g. BGP advertisement), a Network Partner will be assigned for consultation and getting better understanding of the networking requirements. A Network Partner is a resource that the engineer can lean on to dive into network architecture, capabilities, and get their guidance on design choices. Your manager and key engineering ally can help you decide whether the design can benefit from a Network Partner’s guidance.

### **Review the problem statement, customer experience, and goals with key allies**

Having a clearly defined problem statement, customer experience and goals, before diving into the actual design, ensures the project and the engineer leading is steered in the right direction. Without early closure on the above there is a chance that the design heads in a direction that won’t meet the quality bar, leading to wasted effort and delays in the project. **You should hold a goals review before beginning design work on possible solutions.**

Keep the doc focused on just the problem statement, customer experience and goals and not solutions as those will change with any updates to the goals. Hold a meeting with your key allies (senior engineer, PM, partner team contacts) where they review just these early sections, and incorporate their feedback. I like to include one or two of my team members as well in each small-audience review, to build context and give them experience in these meetings.

After the meeting, reply to the invite thanking the reviewers for their time and great feedback, and sending a summary of the notes you took during the meeting. This helps ensure that everybody has the same understanding about what the suggestions were.

Depending on how much feedback there is, you can get consensus that the goals are ready for org-wide review asynchronously by email/slack, or by holding another meeting. Ask your reviewers what they'd prefer.

### **Review the problem statement, customer experience, and goals with the whole team**

Once you've gotten consensus that a team-wide meeting would be useful, schedule an hour for the whole team to review the problem statement and goals. Expect to find out about a lot of edge cases / challenges / things people are worried about here. Take lots of notes, and then work with your senior engineering ally to decide which ones should make it into the doc.

If a significant chunk of the project will be done by another team, offer to hold a goals review meeting with that team's org as well.

## **Phase 2: The Design Doc**

### **Write a first draft of the design**

Use the structure outlined in the Guidelines wiki.

The goal of this phase is to define multiple solutions to achieve the customer experience and goals. The best design docs at this phase avoid making a recommendation; instead, the goal is to define multiple viable solutions that could meet the customer's needs.

I generally start at this phase by defining key problems or questions that we need to solve:

How do we know if our IPv6 addresses are reachable from the internet?

How do we route packets northbound, since what we do for IPv4 doesn't have enough bits to support IPv6?

Should we launch with IPv6-only resources? Dual-stack resources? Both?

and then writing multiple feasible answers (solutions) to each question.

By focusing on the feasibility of your options, you give your reviewers an opportunity to help you identify strengths and weaknesses in each option, and make the right recommendation. At this phase, solutions might be speculative - "use the existing [DataPath] data path to send IPv6 traffic" might be an untested hypothesis at this point. That's fine. At this phase, the IPv6 doc had two solutions for source IP preservation, "use the existing (IPv4) data path", and "make a dedicated dual-stack data path". Both seemed feasible, and we eventually did a spike to prove that the first option was feasible before recommending it— but the key was to present multiple feasible options. If the spike had shown it was not possible, then we have a fallback already defined and ready to go. This approach is also good for earning trust with your key allies, because when done well, it shows you understand the problem deeply enough to come up with multiple viable options.

**Red flag: a challenge or problem with only one solution, or only one solution that is well-defined.** Try to present multiple feasible options for each key challenge. When you write each solution, assume that it will be the one chosen, and give it the same rigorous level of detail and argumentation that you'd give an option that you know is correct. Offering 2 or 3 viable solutions is usually ideal.

### **Do the same small-audience, incorporate feedback, re-review again**

Run the whole design by the same audience you ran the goals by, get their feedback, incorporate, repeat.

### **Move options that are invalid / impossible to appendixes**

Keep the doc crisp. Punt stuff that is no longer relevant / will definitely not be chosen to an appendix. Mention that it is in an appendix in the section it came from.

### **Punt implementation details to Implementation Designs**

For features of significant size (I'll somewhat arbitrarily say 5 engineers working on it or more), keep the high-level design high-level. Define the strategy ("We will assign each ipAddress:port pair a unique port on the load balancer"), and punt the implementation to a separate doc. [Feature B] (linked) is a great example of this; the high-level doc defines the strategy, and a number of low-level implementation docs describe how we will implement the strategy.

Most designs of significant size (5 or more engineers, or both control and data planes) usually have a high-level design doc and multiple implementation designs. Chat with your senior engineer if you have questions about whether a topic should be in the high-level design, or an implementation design.

One pattern that often helps keep the design doc concise is to describe the viable solution spaces for a problem, while punting the actual implementation details to a dedicated doc. If the high-level design can convince us that there are 2+ viable options for a problem, diving deep into them and choosing one is often better suited for an implementation design. The [Feature B] doc does a good job of this, and it helps keep the high level design short (less than 6 pages), and therefore easily reviewable in an hour-long meeting.

## **Phase 3: Implementation**

### **Start Implementation**

You don't necessarily need to wait for org-wide review to start implementing.

### **Org wide review**

The final review step is for the engineer to schedule an org wide review of the design to give visibility into the project to the rest of the team. Here, the org is [Org] which includes people under [leadership]@.

A good review usually means lots of feedback. By the end of the review, you'll want to have identified:

1. A list of blockers (if you're not sure whether a comment called out is a blocker or not, ask!)

2. A name next to each blocker, representing the person who raised the blocker or has the most vested interest in seeing it resolved.

You now have a list of blockers and a list of nice-to-haves. Follow up on the blockers - generally 1:1's or tightly focused meetings with the relevant parties (3-5 people) tends to be the most productive. If you feel like an issue is significant enough to hold a larger meeting - hold a follow-up review targeted specifically at that topic. Here's an example of a follow-up implementation design.

The Meeting Host can help you identify which comments are blockers, and which are suggestions that do not need follow up during (and after) the meeting.

## **Phase 4: When unexpected challenges come up, use this process again**

The core of this approach generalizes to any kind of doc, or any kind of persuasion you need to do at work: write a doc, review it with one or two people, incorporate feedback, and gradually increase the number of people who are reading it until you’ve aligned the key stakeholders on the path forward. I call this the “onion model”, and while this doc describes how to use it for a High Level Design doc, it also works for PR/FAQs, implementation designs, process changes (we did onion reviews for this doc itself!), and more.

*Define the problem and the goals. Get alignment on the problem and the goals. Propose multiple feasible solutions. Review those solutions with a small audience and then a bigger one. It doesn't have to be the whole org (maybe you review these designs with your senior engineering ally and then with the project team, as the small audience and the large one), but the general idea is the same: Goals first, small audience, big audience; multiple viable solutions, small audience, big audience.*
