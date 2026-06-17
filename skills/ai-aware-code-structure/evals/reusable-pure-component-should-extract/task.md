# Inline Avatar in 12 components, or extract a shared one?

We've got basically the same ~50-line Avatar markup (image with fallback initials, presence dot, size variants) copy-pasted inline inside about 12 different components. One of the seniors is arguing we should leave it inline in each file so that when Claude opens any one of those components it sees everything self-contained, rather than chasing an import. The other camp wants to extract a shared <Avatar/> component. Given we lean hard on AI assistants, who's right?
