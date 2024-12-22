# Road Map
**********************************
# Step 1: Documentation
**********************************

# Requirements Specification

This document outlines the tasks and milestones necessary to complete the imlementation of alugAE. Each task ensures that the requirements are well-defined and documented before proceeding to the subsequent development stages.

## 1. Project Overview

### Tasks
- [x] Define the project's main objective and goals.
  - Key objectives: Provide a web-based system for managing media collections and user interactions.
- [x] Identify the stakeholders and their primary concerns.

## 2. Actors and User Stories

### Tasks
- [x] Define all system actors and their roles.
  - Key actors: User, Visitor, Reader, Owner, Administrator.
- [x] Document user stories for each actor.
- [x] Supplement user stories with business rules:

## 3. Information Architecture

### Tasks
- [x] Develop a sitemap to represent the relationship between all planned pages.
- [ ] Create wireframes for critical pages.

## 4. Technical Requirements

### Tasks
- [x] Specify technical constraints and requirements.
  - Adaptive design for multi-device compatibility.
  - Integration with external systems (e.g., OAuth for authentication).
- [ ] Define security and data handling protocols.

## 5. Documentation and Review

### Tasks
- [x] Consolidate all artifacts into a single document.
  - Include project overview, user stories, architecture, and technical requirements.


## Milestones
1. Initial draft of project goals and actors: **[Deadline TBD]**
2. Completion of user stories and business rules: **[Deadline TBD]**
3. Approval of sitemap and wireframes: **[Deadline TBD]**
4. Finalization of requirements specification: **[Deadline TBD]**

---

# Database Specification 

This document outlines the tasks and milestones necessary to complete the Database Specification (EBD) phase for the MediaLibrary system. This phase ensures the data model, relational schema, and database implementation are thoroughly planned and validated.

## 1. Conceptual Data Model

### Tasks
- [x] Define entities and relationships using a UML class diagram.
- [x] Document business rules not captured in the UML diagram:


## 2. Relational Schema

### Tasks
- [x] Convert the conceptual model to a relational schema.
  - Define tables, attributes, domains, primary keys, and foreign keys.
- [x] Apply normalization to ensure the schema is in BCNF.
  - Validate functional dependencies.
- [x] Specify additional integrity constraints:
- [x] Validate the relational schema using sample data.

## 3. Physical Schema and Performance Optimization

### Tasks
- [x] Identify indexes to optimize query performance.
- [ ] Develop triggers to enforce data integrity rules.
- [ ] Define database transactions and isolation levels to handle concurrency.
- [ ] Create SQL scripts for database creation and population.


## 4. Documentation and Review

### Tasks
- [x] Consolidate all artifacts into a single database specification document.
- [ ] Incorporate feedback and finalize the database specification document.

## Milestones
1. Completion of the conceptual data model: **[Deadline TBD]**
2. Approval of the relational schema: **[Deadline TBD]**
3. Validation of SQL scripts and database population: **[Deadline TBD]**
4. Finalization of the database specification: **[Deadline TBD]**

---

# Architecture Specification and Prototype 

#### **Tasks**
1. **Define System Architecture Overview**
   - [x] Choose technologies for backend, frontend, and database.
   - [x] Define development and deployment infrastructure.
   - [x] Document the justification for chosen technologies.

2. **Logical View**
   - [x] Detail the application architecture (Model-View-Template).
   - [x] Map the interaction between layers (request, view, template, response).

3. **Physical View**
   - [x] Plan local development environment with Docker Compose.
   - [x] Propose hosting options and static file management for future deployment.

4. **Prototype**
   - [x] Identify key interfaces for landlords and tenants.
   - [x] Define components for each interface:
     - Dashboard for landlords.
     - Property and tenant management.
     - Payment history for tenants.
   - [x] Remove unnecessary features from the prototype (e.g., analytics for initial release).

#### **Milestones**
- **Initial Draft of Architecture:** **[Completed]**
- **Wireframes for Interfaces:** **[Deadline TBD]**
- **Docker Compose Configuration Finalized:** **[Deadline TBD]**
- **Prototype Validation:** **[Deadline TBD]**

**********************************
# Step 2: Setup
**********************************

### **Setup Roadmap**

#### **Tasks**

1. **Environment Configuration**
   - [ ] Install and configure Docker and Docker Compose.
   - [ ] Set up Django project structure.
   - [ ] Configure PostgreSQL database service in Docker Compose.
   - [ ] Create a `requirements.txt` file with project dependencies.

2. **Database Initialization**
   - [ ] Configure Django settings for PostgreSQL connection.
   - [ ] Run initial migrations to set up the database schema.
   - [ ] Verify database connection and schema integrity.

3. **Core Application Setup**
   - [ ] Create the core Django apps:
     - **Accounts** (User authentication and management).
     - **Properties** (Property and unit management).
     - **Payments** (Payment records and tenant history).
   - [ ] Define models based on the database schema from the EBD document.
   - [ ] Register models in the Django admin panel for testing and management.

4. **Static and Media Files Management**
   - [ ] Set up static file handling for CSS, JS, and images.
   - [ ] Configure media files storage for file uploads.

5. **Testing and Debugging**
   - [ ] Install debugging tools (e.g., Django Debug Toolbar).
   - [ ] Test basic CRUD operations for properties and tenants.
   - [ ] Verify API endpoints (if applicable).

#### **Milestones**
- **Environment Ready:** **[Deadline TBD]**
- **Database Configured:** **[Deadline TBD]**
- **Core Apps Functional:** **[Deadline TBD]**
- **Static and Media Files Working:** **[Deadline TBD]**
