# honest-code-principles

The Honest Code principles, as one file, so a project can depend on them instead of copying them.

`honest-code-principles.md` is the whole content. Everything else here exists to keep it single.

## Why this repository exists

The text lived in twelve places across as many projects. Between them they held twenty-two principles, and no single copy held all twenty-two. Four principles were missing from the folder the framework itself called canonical, including No Implicit Defaults. One, Constrain AI With Data Shape Contracts, existed only in downstream projects and had never reached the framework at all. Two more existed only in the framework and nowhere else. One principle was filed under two different names, so a mechanical comparison saw two principles where there was one.

None of that was anyone's mistake. It is what copying does, and the only fix that holds is to stop copying.

## Using it

Depend on this repository. Do not paste the text into your project, and do not summarise it in a CLAUDE.md — a summary is a copy with the drift built in. Point at the file.

## Governance

Apache-2.0. Governed by the Open Honest Foundation. A change here is a change to the standard, so it goes through the same review as a change to a specification: state which category of defect the principle removes, or it does not belong.
