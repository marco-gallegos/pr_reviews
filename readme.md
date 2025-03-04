# code review cli

according diagrams below, giveme the code for the cli review and the code review function, considering all params should be defined on cli call. all using python and ollama api with codellama model.

## cli review

```mermaid
---
title: "cli review"
description: "code review cli for git changes in another branch"
---

graph TD
    A[cd to workdir] --> B[get dev branch and changes branch from params]
    B --> C[clean unestaged to stash and checkout dev branch]
    C --> D[pull dev branch and changes branch on its own branch and move to changes branch] 
    D --> E["get all files changed against dev branch"] 
    E --> F[save changed files to var array]
    F --> G[run code review on every file]
    G --> H[save code all files code review in the same file]
```

### code review function

```mermaid
---
title: "code review"
description: "code review for every file using ollama and codellama"
---

graph TD
    A[get review prompt filename from params] --> B[read review prompt file]
    B --> C[get file changes vs dev branch]
    C --> D[run code review replacing changes in prompt file content]
    D --> E[print and return code review]
```