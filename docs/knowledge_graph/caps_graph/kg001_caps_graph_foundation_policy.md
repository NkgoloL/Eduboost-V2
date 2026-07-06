---
title: "KG-1 CAPS Graph Foundation Policy"
status: active
owner: knowledge-graph
reviewers: [architecture, curriculum, engineering, privacy]
audience: developer
source_of_truth: false
supersedes: []
superseded_by: null
last_reviewed: 2026-07-05
review_interval_days: 60
evidence_command: make kg001-caps-graph-foundation-check
code_anchors: []
---

# KG-1 CAPS Graph Foundation Policy

CAPS graph foundation recorded: true  
Source-grounded CAPS graph required: true  
Every CAPS node has source provenance: true  
Every CAPS edge has source provenance: true  
Runtime KG authority switch authorised: false  
Database schema migration authorised: false  
Learner-facing model change authorised: false  
Learner graph implementation authorised: false  
Production release authorised: false  
Deployment authorised: false  
Release tag authorised: false  
Public beta authorised: false

## Policy

KG-1 may create deterministic CAPS graph artifacts from approved CAPS topic-map data. It may not make graph state authoritative for learners. It may not create database migrations or learner-facing behaviour changes.

The generated graph is a read-model artifact for later KG gates. KG-2 may consume it to produce target-state graphs only after KG-1 evidence is valid.
