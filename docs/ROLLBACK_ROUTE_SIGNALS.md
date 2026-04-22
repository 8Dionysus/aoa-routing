# Rollback Route Signals

Version: 1.0.0

## Purpose

Defines rollback signal routing from watchtower, console, and operator actions.

This document belongs to the v1.0 installation and first sovereign release wave. It turns the experience program from forged seed into installable order: landing, migration, smoke testing, operator review, first live assistant office, governed release, rollback drill, replay audit, and post-release watch.

## Owns

- rollback dispatch
- hold routing
- owner fanout

## Must not do

- durable rollback by routing
- meaning theft
- silent suppression

## Flow

```text
owner-local artifact
  -> validation
  -> operator review
  -> activation or denial
```

## Authority Source

Release authority and cross-layer doctrine live in [Agents-of-Abyss](https://github.com/8Dionysus/Agents-of-Abyss/blob/main/docs/EXPERIENCE_WAVE5_SOVEREIGN_OFFICE.md). The no-direct-write boundary for Tree-of-Sophia lives in [Tree-of-Sophia](https://github.com/8Dionysus/Tree-of-Sophia/blob/main/docs/NO_DIRECT_EXPERIENCE_INSTALL_WRITE.md). This `aoa-routing` surface only defines owner-local contract behavior and consumes those upstream gates.

## Exit signal

This surface is ready when it can produce a typed artifact, route it to the true owner, survive replay, and fail closed when authority is missing.
