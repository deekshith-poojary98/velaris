# Project: Velaris

You are a Principal Software Architect with experience designing testing frameworks, language runtimes, plugin ecosystems, and developer tools.

I want to design a next-generation general-purpose testing framework called Velaris.

IMPORTANT:
Do not start writing code.
Do not create files.
Do not generate implementation details yet.

Your first responsibility is to analyze, challenge, and refine the architecture. If any part of the design is weak, call it out and propose alternatives.

## Vision

Velaris is NOT an automation framework.

Velaris is a general-purpose test framework similar to pytest, Robot Framework, JUnit, and NUnit.

It must support:

* Unit testing
* Integration testing
* API testing
* UI testing
* Mobile testing
* Desktop testing
* Performance testing
* Custom domains

through plugins.

Velaris itself should know nothing about browsers, APIs, databases, mobile devices, or desktop applications.

Those capabilities must come from plugins.

## Core Philosophy

Pytest:
Execution Engine + Plugin System

Robot Framework:
Execution Engine + DSL + Libraries

JUnit:
Execution Engine + Annotations

NUnit:
Execution Engine + Attributes

Proposed Velaris:

Execution Engine + Capability Model + Plugin System

## Key Idea: Capability Model

Instead of tests depending on concrete implementations:

```python
def test_login(playwright_browser):
```

tests depend on capabilities:

```python
def test_login(browser):
```

The configuration decides which implementation provides that capability.

Example:

capabilities:
browser: playwright

or

capabilities:
browser: selenium

The test remains unchanged.

The same concept should apply to:

* browser
* api
* database
* filesystem
* messaging
* desktop
* mobile
* cloud
* custom user-defined capabilities

## Multiple Authoring Styles

Velaris should eventually support multiple test authoring styles.

Examples:

1. Python code style
2. YAML declarative style
3. BDD/Gherkin style

All authoring styles should compile into a single execution model internally.

The execution engine should never care how the test was written.

## High-Level Goals

* Simple core
* Extremely extensible
* Plugin-first architecture
* Capability-driven dependency injection
* Parallel execution
* Modern reporting
* Rich extension APIs
* Cross-platform
* Open-source

## Non-Goals

Velaris should NOT:

* Become another Selenium wrapper
* Become another Playwright wrapper
* Become another Robot clone
* Contain browser automation logic
* Contain API client logic
* Contain database drivers

Those belong in plugins.

## What I Need From You

I do NOT want code yet.

I want a detailed architectural review and phased roadmap.

Please provide:

### Part 1

Critical analysis of this idea.

Identify:

* Strengths
* Weaknesses
* Risks
* Existing frameworks that solve similar problems
* Reasons this project could fail

### Part 2

Refine the architecture.

Define:

* Core engine responsibilities
* Plugin responsibilities
* Capability model responsibilities
* Reporting responsibilities
* Dependency injection model
* Test discovery model
* Configuration model

### Part 3

Design the internal architecture.

Include:

* Major modules
* Package boundaries
* Public APIs
* Internal APIs
* Lifecycle events
* Plugin loading process
* Capability registration process

### Part 4

Create a realistic phased roadmap.

Phase 0:
Architecture and RFCs

Phase 1:
Minimal executable prototype

Phase 2:
Capability system

Phase 3:
Plugin SDK

Phase 4:
Reporting

Phase 5:
Parallel execution

Phase 6:
Alternative authoring styles

Phase 7:
Ecosystem building

For each phase provide:

* Goals
* Deliverables
* Risks
* Estimated complexity
* Exit criteria

### Part 5

Challenge the entire idea.

Answer:

"If this project is a bad idea, why?"

and

"If this project could realistically succeed, what would make it different from pytest?"

Be brutally honest.
