# Should a 550-line grab-bag helpers.ts stay as one file?

We have a single helpers.ts file that's grown to about 550 lines. It's got date formatting functions, a currency formatter, a thin fetch wrapper, a bunch of form-validation predicates, and some array/object utilities. They don't really call each other — it's just where everything landed. It's imported all over the app. I've been reading that big files are actually fine for AI agents now, so should I just leave it as one file?
