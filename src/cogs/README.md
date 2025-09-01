# Views

We keep the common `cogs` terminology, but this represents the View layer in the MVC design pattern.

In MVC, Views are responsible for interacting with the end user. For this application, the Views define commands and event listeners using discord.py. Views should focus on presentation and user interaction, without containing logic that manipulates application state (e.g., music queues) or external resources (e.g., file system). Instead, they delegate to Controllers for business logic.