# Honest Code Principles

The Honest Code Principles, as one file, so a project can depend on them instead of copying them. Twenty-three principles, each naming a category of defect and removing it.

Read them: [`honest-code-principles.md`](honest-code-principles.md). That file is the whole content, and everything else here exists to keep it single.

Canonical page: <https://honestframework.software>. Maintained by the [Open Honest Foundation](https://openhonest.org).

## Why this repository exists

The Honest Code Principles lived in twelve places across as many projects. Between them they held twenty-two principles, and no single copy held all twenty-two. Four principles were missing from the folder the framework itself called canonical, including No Implicit Defaults. One, Constrain AI With Data Shape Contracts, existed only in downstream projects and had never reached the framework at all. Two more existed only in the framework and nowhere else. One principle was filed under two different names, so a mechanical comparison saw two principles where there was one.

None of that was anyone's mistake. It is what copying does, and the only fix that holds is to stop copying.

## Using it

Depend on this repository for the Honest Code Principles. Do not paste the text into your project, and do not summarise it in a CLAUDE.md — a summary is a copy with the drift built in. Point at the file.

## Governance

Apache-2.0. Governed by the Open Honest Foundation. A change here is a change to the standard, so it goes through the same review as a change to a specification: state which category of defect the principle removes, or it does not belong.
