---
order: 70
icon: check
tags: [docs, documentation, retype, best practices]
---
# Best Practices

## Introduction

The best documentation is documentation that teaches without getting in your way. Some folks are better at it than others, which is why we [take inspiration from DigitalOcean](https://www.digitalocean.com/) and [their fantastic documentation and tutorials](https://www.digitalocean.com/community/tutorials). In a talk at PyCon 2022, [Mason Egger](https://mason.dev/), a former member of the DigitalOcean Tutorials team, broke down [exactly what makes their documentation so great](https://mason.dev/speaking/docs-devs-love/). This page takes the principles discussed in the talk and on the slides and reproduces them in long form (with permission from the author).

## Best Practices in Documentation

### Make Your End Goal Clear

In the introduction section, explain exactly what the purpose of the page is and what the reader should accomplish by the time they are done.

* you will install X
* you will configure Y

Be concise; while it's fun to wax poetic about things sometimes, it should be immediately clear why the reader is here and why the page is here.

### Don't Be Overly Verbose

> Why waste time say lot word when few word do trick?
> 
> ~ _Kevin Malone (The Office (US))_

Maybe don't go to quite such lengths (or lack thereof), but definitely do try to keep it short. There's no reason to write a book on something that should only take a few paragraphs to explain, so when writing about something, try and remove extra words that aren't necessary.

### Aim for a Low Reading Level

Not everyone has the same proficiency of language, especially folks who are reading as a second, third, or even fourth language. Try to not use complex words (like 'proficiency') and use [external tooling](https://hemingwayapp.com) to check the grade level of the text. Completed documentation should not go above the 6th grade level.

### Use Inclusive Language

Sometimes language can be accidentally _exclusive_ if we're not careful of how it's applied. A great example of this is gendered language like 'he', 'she', or 'guys' -- it's much easier (and much more inclusive) to use 'they', 'them', or the second person 'you'.

Some common slang terms in tech ("noob", "dummies") can be derogatory and make people feel unwelcome to a project or to documentation, even if the documentation is meant to be welcoming (like the _Idiot's Guide_ books, for example).

Words that can make people doubt their own skills, like 'easy' or 'simple', should also be avoided. What is simple to one person might be rocket science to another, and we never want someone to feel inferior while they're trying to learn. (Or ever, but you get my point.)

### Limit Technical Jargon

> _jargon_
> 
> Special words or expressions that are used by a particular profession or group and are difficult for others to understand.
> 
> ~ _Oxford Languages_

Take a good look at any word that has special meaning in your industry -- 'unicorn', 'ideate', 'bleeding edge', 'sunset', and 'grok' are good examples in tech -- and strike it from your documentation. Newcomers unfamiliar with the intended meaning will feel alienated and unwelcome; because this specific documentation is intended for people with limited or no technical experience, any jargon should be avoided.

### Define All Acronyms

Ensure that every acronym has an easily accessible definition and that it is defined (or redefined) as many times as needed. Write the full name of the acronym the first time it's used, and don't be afraid to do it again later if it's possible that the reader could have skipped the first definition. For example, "...using HTML (hypertext markup language) and CSS (cascading style sheets), we can...".

Acronyms cannot usually be puzzled out by context clues alone. Definition can be done in either order (acronym first, then definition, or definition and then acronym) but it must be defined even if you expect everyone reading it to know what it means.

### Avoid In-jokes, Idioms, and Regional Language

Though some sentences may make sense to you, unless you're writing for people who live in your city, keep an eye out for language and idioms that might confuse people who either aren't from your area or are not as familiar with language. For example, in the midwest USA we may say that something "needs doing", but it might not be easy to translate that something needs to be done if they've never seen that expression before.

Other examples of regional slang from my corner of the world include 'schnookered' and the fact that "sweeping" and "vacuuming" are interchangeable. Don't ask me why; I don't know either.

### Use Meaningful Examples and Variable Names

When writing out examples, make sure they're actually relevant to the content that you're writing about and that they actually show what the code is supposed to do -- try to not make up examples just for the sake of having examples.

Ensure your variable names are relevant to the work that you're showing; `foo` and `bar` are... variables, yes, but they're not _descriptive_ variables. What do they do? Why are they here? One can only guess. With variable names that are more descriptive, like `person` and `person_name`, then it's more clear what your example is trying to do.

### Don't Make the Reader Leave the Docs

This point is discussed more thoroughly in the documentation layout section. Place everything that _could_ make a reader leave (like things they need to do before they tackle whatever the page is about) in the very beginning so that they have a reason to come back. We don't want the reader to get distracted because they had to open a new tab halfway through a tutorial; everything after the beginning should be self-contained.

### Make Content Scannable

Break up the page into logically defined sections. If a reader is going to be looking for a specific piece of important information, put it in a section that clearly shows where it's located; someone who is not familiar with the docs should be able to scan the page to identify all the major pieces of information.

The search bar can help, but there's only so much that it can do; ensure that the sections can be used to quickly narrow down where something might be.

### Verify the Documentation!

Make sure it works. It's as simple as that. When writing out instructions, test as you go, then go back and verify that your instructions work. Setting up a virtual machine (VM) is a great way to test installation instructions and verify that there's nothing extra waiting to surprise newcomers; bad documentation or incomplete documentation is worse than no documentation at all.

## Thanks

Thanks to [Mason Egger](https://mason.dev/) for allowing this retelling of his talk and slides. The [original slides can be found here](https://mason.dev/speaking/docs-devs-love/), and Mason is [on Twitter at @masonegger](https://twitter.com/masonegger/).
