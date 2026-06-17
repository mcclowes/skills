# Is a central 400-line types.ts a good idea?

We keep all our shared TypeScript types in one src/types.ts file. It's about 400 lines now and basically every component and service imports from it. It felt clean to have a single source of truth. We do most of our editing through Claude Code now. Is a central types file a good idea, or should types live somewhere else?
