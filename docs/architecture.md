# Architecture

## Overview
This document describes the high-level architecture for the My Arxiv Listener project.

### Components
1. **Frontend**: React-based dashboard that allows users to input their arXiv channel, area of interest, and email.
2. **Backend**: FastAPI/Node backend that processes incoming requests, stores user preferences, and runs scheduled tasks.
3. **Database**: Postgres (example) storing user data and fetched articles.
4. **Cron / Scheduler**: A daily job to fetch and filter new arXiv articles, generate summaries, and email reports.

### Data Flow
```mermaid
flowchart LR
    A[User inputs channel, interest, email] --> B[Backend stores in DB]
    C[Cron job triggered daily] --> D[Fetch new arXiv articles]
    D --> E[Filter & Summarize]
    E --> F[Generate PDF & TXT]
    F --> G[Send email with attachments]
