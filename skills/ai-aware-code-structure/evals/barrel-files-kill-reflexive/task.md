# Are reflexive barrel files helping or hurting AI editing?

Our React + TypeScript app re-exports everything through barrel files: every folder has an index.ts that re-exports its contents, and there's a big src/components/index.ts too. Imports look like `import { Button, Modal, Card } from '@/components'`. We now do almost all our editing through Claude Code and Cursor. Is the barrel-file pattern helping or hurting us, and would you keep it?
