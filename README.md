# ACME Ltd. Financial Data Warehouse

A fictional company (**ACME Ltd.**) requires a platform capable of collecting financial market data, preserving historical information, performing analytical processing, generating investment recommendations, and exposing the warehouse through REST APIs and a natural-language assistant.

---

# Implemented Scope

## UC1 – Data Ingestion and Provenance

### Ingestion API

```http
POST /ingestion
```

### Pipeline

```text
Market Provider
      ↓
MarketDataProvider
      ↓
MarketTransformer
      ↓
Cassandra Load
      ↓
Ingest Logging
```

### Provenance

Data lineage is preserved through:

* `source_id` stored on every time-series record
* ingestion metadata stored in `ingest_log`
* source metadata stored in `data_sources`

This allows all analytical results to be traced back to the original provider.

---

## UC2 – REST API for Warehouse Data

### Instruments

```http
GET /instruments
```

Returns all available financial instruments.

```http
GET /instruments/{instrument_id}
```

Returns details for a specific instrument.

---

### Data Sources

```http
GET /sources
```

Returns all available market data providers.

```http
GET /sources/{source_id}
```

Returns details for a specific provider.

---

### Time Series

```http
GET /timeseries/{instrument_id}/{source_id}
```

Returns historical OHLCV market data for an instrument and source.

---

## UC3 – Analytics

### Aggregations

```http
GET /analytics/{instrument_id}/{source_id}
```

Returns:

* Record count
* Minimum close price
* Maximum close price
* Average close price
* Total volume

---

### Trend Analysis

```http
GET /analytics/{instrument_id}/{source_id}/trend
```

Computes:

* Trend direction
* Percentage change

---

### Volatility Analysis

```http
GET /analytics/{instrument_id}/{source_id}/volatility
```

Computes historical volatility based on stored market data.

---

### Asset Comparison

```http
GET /analytics/compare
```

Compares two financial instruments using:

* Trend
* Volatility
* Recommendation
* Confidence level

---

## UC4 – Recommendations

### Recommendation API

```http
GET /recommendations/{instrument_id}
```

Returns recommendation information:

* BUY
* HOLD
* SELL

Each recommendation includes:

* Confidence level
* Supporting signal
* Generated timestamp

---

# UC5 – Natural Language Assistant

## Overview
The Natural Language Assistant is an intelligent agent workspace that provides natural-language exploration over the financial data warehouse. Instead of relying on static database queries or generic financial training data, the assistant utilizes a Model Context Protocol (MCP)-style tool layer to query your Apache Cassandra cluster live. This ensures all generated responses are strictly grounded in verified, internal warehouse records.

---

## System Architecture

The assistant operates at the surface of a decoupled, end-to-end data pipeline. It coordinates background analytical signals, asset listings, and historical market data to build context-aware responses:

```text
       External Providers
               │
               ▼
       Ingestion Pipeline
               │
               ▼
        Apache Cassandra
               │
 ┌─────────────┼─────────────┐
 ▼             ▼             ▼
Analytics     Risk    Recommendations
 └─────────────┼─────────────┘
               │
               ▼
            FastAPI
               │
               ▼
           Assistant (Groq LLM Engine)

---
```
# Chat API Specification
## Post Prompt Endpoint
## POST /chat

Submits a natural-language inquiry string to the assistant. The underlying engine automatically dissects the question, selects the appropriate tracking tools, executes the storage query, and outputs a formatted interpretation.

## Verified Sample Inquiries
You can interface directly with Swagger UI to run target evaluations using these supported query patterns:

Metadata Inspections: "What assets are available?" or "What data sources are available?"

Cross-Asset Analytical Slices: "Compare AAPL and IBM."

Trend Auditing: "What are the latest investment recommendations generated in the warehouse?"

# Technology Stack

## Backend

* Python 3.13
* FastAPI
* Pydantic
* Groq API/ Cloud Client

## Data Warehouse

* Apache Cassandra

## Messaging

* RabbitMQ

## Containerization

* Docker
* Docker Compose

## Assistant Integration

* MCP-style tool layer
* Warehouse-grounded responses

## Data Providers

* Alpha Vantage
---

# Cassandra Schema

Core warehouse tables:

```text
financial_instruments
data_sources
time_series
analytics_results
recommendations
ingest_log
```

---

## Financial Instruments

Stores:

* Instrument identifier
* Symbol
* Name
* Asset class
* Region
* Currency

Examples:

* AAPL
* IBM
* KO

---

## Data Sources

Stores:

* Provider name
* Provider type
* Base URL
* Available attributes

Examples:

* ALPHAVANTAGE

---

## Time Series

Stores historical market information:

* Open price
* Close price
* High price
* Low price
* Adjusted close
* Volume

---

## Analytics Results

Stores precomputed analytical metrics:

* Trend
* Volatility
* Aggregations

---

## Recommendations

Stores generated recommendation signals:

* BUY
* HOLD
* SELL

with confidence levels and explanations.

---

## Ingest Log

Stores ingestion metadata:

* Source
* Instrument
* Record count
* Status
* Duration
* Error information

---

# MCP Tool Layer

The assistant accesses warehouse functionality through tools.

Available tools:

```text
list_assets
get_asset_details
list_data_sources
get_data_source_details
get_time_series_data
compare_assets
```

Workflow:

```text
User Question
      ↓
 Assistant
      ↓
 Warehouse Tool
      ↓
 Cassandra Query
      ↓
 Grounded Response
```

---

# Running the Project

## Prerequisites

* Docker
* Docker Compose

---

## Start Services

```bash
docker compose up --build
```

---

## API Documentation

Swagger UI:

```text
http://localhost:8080/docs
```

---

## Health Check

```http
GET /health
```

Expected response:

```json
{
  "status": "ok"
}
```

---

# Example Workflow

## 1. Ingest Market Data

```http
POST /ingestion
```

Loads data from an external provider into the warehouse.

---

## 2. Explore Warehouse Data

```http
GET /instruments
```

```http
GET /timeseries/{instrument_id}/{source_id}
```

---

## 3. Run Analytics

```http
GET /analytics/{instrument_id}/{source_id}
```

---

## 4. Retrieve Recommendations

```http
GET /recommendations/{instrument_id}
```

---

## 5. Query the Assistant

```text
What assets are available?
```

```text
What data sources are available?
```

```text
Compare AAPL and IBM.
```

---

# Testing

Run all tests:

```bash
pytest
```

Current tests cover:

* Assistant tool execution
* Ingestion pipeline functionality
* Repository integration

---

# DEMO
[link to demo](https://drive.google.com/file/d/18kTty5o7eye98a3e1VLEqxXuv7AETRzm/view?usp=sharing)
