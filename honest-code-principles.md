# Honest Code: Coding Principles

Every principle names a category of defect and removes it. A practice that does not eliminate a named category of bug is a style preference, and does not belong here.

This is the single source.

## Lookup Polymorphism
Imperative conditional structures (if/elif/else chains) can easily create order dependent logic that is fragile and difficult to reason about.

Almost any dispatch can be replaced by a dict/array/map mapping keys to functions: `HANDLERS = {"email": send_email, "sms": send_sms}` then `HANDLERS[channel](data)`. The dict is a declarative dispatch table. Adding a new case means adding a row, not modifying potentially fragile control flow. The table is read by a polymorphic pure function whose operations vary depending upon the values looked up by the key.

## Pure Functions Over Methods
Public methods in classes are an open door to promiscuous state mutation that creates a mathematically infinite number of possible call sequences, since calls repeat without bound, which makes it impossible to exhaustively test program behavior.

A method like `user.validate()` that mutates internal state becomes `validate_user(user: dict) -> dict`. Input in, output out. The function has no access to `self` because there is no `self`. No side effects, no surprises.

A `class User` with fields, methods, getters, setters, and lifecycle hooks becomes `User = TypedDict("User", {"email": str, "name": str})`. The data is just data — no behavior attached. If you can't `json.dumps()` it, it's too clever by half.

Java and C# do not allow standalone functions. Honest Code is still writable in them by wrapping the function in a class exposing a single public method, which is the language's syntax for a function and not a return to objects.

## I/O at the Boundary
Sprinkling input/output (I/O) operations—such as database queries, network requests, or file reads/writes—throughout your business logic tightly couples your code to external systems. This creates major structural and performance issues, and it makes the code impossible to keep DRY. The defects follow from the coupling: the logic cannot be tested without the external system standing behind it, none of it can be reused anywhere the system is absent, and there is no single place to change how the program talks to the outside.

Honest Code requires pure business logic functions in the middle; I/O (database, HTTP, file system) happens once, at the edges (route handlers, CLI entry points). The input boundary calls the pure function (either directly or through an orchestrator function that creates chains of functions defined in lookup tables) and then does the I/O with the result. This is why Honest Code has no mocks: the pure core has nothing to mock.

## Composition Over Inheritance
An inheritance chain hides the code that actually runs. `class B extends A extends Base` tells you where a method is declared, not which one executes: that is decided at call time by the resolution order, and a `super()` call can land anywhere in the chain. The code you read and the code that runs are two different things, and nothing in the file marks where they part company.

Instead of `class B extends A extends Base`, use `pipe(validate, authenticate, rate_limit, create_order)`. Each step is an independent function. The pipeline is visible at the point of assembly. No `super()` calls, no hidden method resolution order. Functions are sequenced using orchestrators and the sequencing order is a lookup table. An orchestrator is the root of one operation and does not call another orchestrator: nesting them re-introduces exactly the invisible sequencing this principle removes, which is why honest-check treats it as an error (HC-OR001).

## DOM as State (DATAOS)
Redux/MobX/Zustand synchronize a shadow copy of server state and it is inevitable that this synchronisation will break.

Instead Honest code dictates that the DOM *is* the state. The server renders HTML and HTMX swaps it into the page. `hx-get` + `hx-target` replaces `useState` + `useEffect`. One copy of truth, not two. [DATAOS.software](https://dataos.software) is the canonical reference. This also provides closure for testing. When the server generates the front-end, reasoning about I/O becomes possible in a way that is not possible with the other approaches.

## HTML Attributes Over Imperative DOM Manipulation
Imperative wiring is order-dependent and redundant by construction. Hand-written setup has to run in the right sequence, and a second piece of code touching the same element is a second copy of the same intent that can disagree with the first.

Instead of `addEventListener`, `querySelector` and `innerHTML` in JavaScript, declare `hx-post="/endpoint"`, `hx-target="#result"`, `fx-format="currency"`. The attribute declares intent; the library supplies mechanism. A declaration on the element is that intent stated once, in one place, with no order to get wrong.

## References Resolve Statically
Every identifier a rendered artifact names is a reference across a boundary: an `hx-get` to a route, a `class` to a stylesheet rule, a `{% include %}` to a template. Asserting the artifact contains the string proves it was written, not that it resolves — two green tests can describe a button and a menu that never connect.

Resolve every emitted reference to its definition at the gate, not in a running browser, and generate agreeing artifacts from one declaration so they cannot disagree.

## Typed Exceptions at the Boundary
A `try` inside business logic ends the caller's ability to know what happened. The fault is caught, something is logged or a default returned, and the function reports success to a caller with no way to ask. Every catch in the interior is a fault that stops at that line and never reaches anyone who could act on it.

Don't catch inside business logic. Let functions raise. The route handler (or supervisor) catches, inspects the exception type (`ValidationError`, `GatewayTimeout`), and returns the appropriate status code. Retry logic belongs in the task queue infrastructure, not inline in the function.

## SQL Over Application Caches
A cache is a second copy of data that is already authoritative somewhere else, and the two agree only until something changes. Every write becomes two writes that can disagree, and the disagreement is silent: a stale answer is shaped exactly like a fresh one, so nothing downstream can tell them apart.

Before adding a cache, profile the query. A single SQL join with proper indexes runs under 3ms. The cache adds invalidation bugs, stale data, and a second source of truth. Fix the query or the schema first. Only cache after measurement proves it necessary. In our measurements SQLite outperformed Redis, because a local read beats a network round trip. Redis earns its place only where mutable state has to be shared across server instances, such as auth tokens.

## Pure Function Assertions Over Mocks
A mock makes a test agree with itself. It replaces the thing under test with a description of what you already believe, so the test passes when the belief matches the code and keeps passing when belief and code are wrong together. A suite built on mocks tells you the code still does what it did, never that it does what it should.

`assert f(input) == expected_output` — that's the whole test. If you need 9 mocks to test a function, the function has 9 hidden dependencies. Extract the pure logic; test it directly. Test the wiring separately with integration tests that hit real services. NO MOCKS.

## Type Declarations Over Imperative Validation
A hand-written check is a copy of a constraint that already exists elsewhere. The column is `varchar(255)`, the field is typed, the form says `type="email"`, and then a function checks all three again in its own words. Copies drift, and the copy that drifts is the one on the path nobody exercised.

Instead of writing `if not isinstance(x, str)`, `if len(x) > 255`, `if not re.match(...)` — declare a schema in your language's validation layer, a TypedDict, a SQL column constraint, or an `<input type="email">`. The runtime, type checker, database, or browser enforces the constraint. The programmer declares it; the machinery enforces it.

## Context Managers Over Instance State
A resource stored on an instance outlives the work it was opened for. Nothing in the code says when it closes, so closing becomes somebody else's job, and on the path where that somebody is a crash it does not happen at all.

Instead of `self._connection = await connect()` stored on a class, use `async with create_connection(config) as conn:`. The connection opens and closes within the scope. No persistent state leaks into the caller. Crash recovery is trivial because there's nothing to clean up.

## Configuration as Parameters
Configuration set in a constructor is a dependency the signature does not mention. A reader cannot see what a function needs, a caller cannot supply it, and the order things are constructed in becomes load-bearing, so the program works or fails on a sequence nobody wrote down.

Instead of `self._config` set in `__init__`, pass `config: dict` as an argument to each function that needs it. The dependency is visible in the signature. No hidden state, no initialization order bugs.

## No Implicit Defaults
`def f(x, timeout=30)` silently absorbs the caller's omission. Afterwards the program cannot distinguish a caller who chose thirty seconds from one who forgot, and the non-default region is invisible at every call site, so nothing exercises it. A default is catch-and-swallow applied to inputs, and it manufactures an untested input region by construction.

Encode absence as an explicit member of a bounded type, a Maybe or a named `Nothing`, resolved in a visible boundary step and exercised by a test. The `=` is the swallow; the boundary resolve is the surfaced decision.

## Dispatch Tables Close Open Input
An open input space cannot be tested in full, so the work is to close it, and a table with its keys written out is how you close it. The keys are the type. `HANDLERS = {"email": send_email, "sms": send_sms}` declares that exactly two channels exist, so the partition a test must cover is two, whatever the caller passes. The same move works whether the value selects a handler, a format, a parser or a node kind, and it is why `getattr(obj, name)` is honest when `name` ranges over a declared set and dishonest when it ranges over the request. The line is bounded against unbounded, never static against dynamic.

The half that gets dropped is the miss. Read the table by subscript and let an unknown key raise. `table.get(key, default)` files an input nobody wrote a rule for under an answer somebody wrote for a different input, and afterwards nothing can tell the two apart. That is the input side of silent failure, and it does more damage here than anywhere else: the table was the thing that made the space enumerable, so a default quietly re-opens it while the code still reads closed. Where a miss is genuinely expected, return it as a named case the caller has to handle, never as a value shaped like a hit.

Then record what missed. An unknown key is not the caller's mistake, it is a gap in your table, and a table only grows correctly if the misses are collected rather than absorbed. The bug category this eliminates is an unhandled input read as a handled one.

## Atomic Test-and-Set Over Check-Then-Act
A guard that reads a shared value and then writes it is not a guard. Between the read and the write another caller reads the same answer, and both proceed believing they hold the thing exclusively. Under real threads this is rare enough to be unreproducible from a bug report; under an async runtime it is not rare at all — any await between the two, a log line or a metric or any I/O, makes the race certain rather than occasional, and the code that does it looks completely ordinary.

Express the guard as one operation whose return value distinguishes "I took it" from "someone else holds it": an atomic insert, a compare-and-swap, an insert-if-absent. The token written must be unique to the caller, because a shared sentinel is not a fix — every later caller reads it back, matches it, and reports success. The bug category this eliminates is a guard that reports protection while protecting nothing.

## Logging Is a Declared Boundary, and an Error Is Returned
A log line written from inside a function is a return value that skipped the type system. The function produces an observable output its signature never admits, so no caller can see it, no test can assert on it without capturing output, and no caller can decline it.

Two rules follow. **An error is returned, never written**: a function that logs a failure and carries on has reported it somewhere the caller cannot reach, and logging instead of returning is how a failure gets lost. **Information goes through one logging function of your own**, declared as a boundary, and every other function calls that one. `logger.info(...)` reaches a global you did not declare and cannot substitute, so twenty-four call sites become twenty-four independent edges; one declared function is a single edge that decides format, level, destination, and whether to write at all.

## Constrain AI with Data Shape Contracts
**This one mitigates. It does not eliminate, and it is the only entry here that does not.** Instead of "write a notification system", say: write a function taking `{channel, recipient, message}` and returning `{status}`. A defined input and output contract is verifiable by reading the signature and running one example, where a class with five methods requires tracing every call sequence. That lowers the cost of finding a fault; it makes no category of fault impossible. It is kept because it works, and marked because everything else in this document promises removal.

## One Gherkin Per Function
A missing test, a test that asserts nothing, and a test whose subject no longer exists are all invisible one at a time. Nothing about a suite that passes distinguishes a function nobody covered from one covered well.

Every function carries exactly one gherkin scenario naming it. The rule is a bijection, and the point of a bijection is that the two sets reconcile mechanically: a function with no scenario is code nothing describes, and a scenario with no function describes code that does not exist. The counts having to match is what makes all three obvious. Step-definition length is the secondary signal: thirty lines of setup means the code under test has hidden dependencies, and when the function is pure the step is call it and check the result.

## Declarative Equivalents Over Framework Lifecycle Hooks
Lifecycle hooks are an initialisation order you cannot see. `componentDidMount`, `useEffect` cleanup and `ngOnInit` each run at a moment the framework picks, so the sequence lives in the framework's documentation instead of your file, and two hooks that must happen in an order have no way to say so.

Instead of `componentDidMount`, `useEffect` cleanup, `ngOnInit` — use HTMX attributes that declare when to load (`hx-trigger="load"`), or server-rendered HTML that arrives ready. No client-side initialization sequence.

## Strangler Pattern for Migration
A rewrite defers every fault to a single cutover. The first evidence that the design is wrong arrives with all of it at once, at the moment there is nothing left to fall back to.

Extract one pure function from one class method at a time. The method now calls the function, the class still exists, and the interface does not change. After six months the class is a thin shell and removing it is a cleanup. One function at a time means a fault surfaces at the step that caused it, and the blast radius of any step is that step.
