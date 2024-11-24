
# Smart CRM with NLP and Neo4j

**Smart CRM with NLP and Neo4j** is a powerful Customer Relationship Management (CRM) system that leverages Natural Language Processing (NLP) to interpret user queries and interact with customer data stored in a Neo4j graph database. This project enables easy querying and analysis of customer interactions, opportunities, and relationships through conversational queries.

# Motive
To improve how businesses manage customer relationships by making the CRM smarter. By combining Natural Language Processing (NLP) and Neo4j, the system can better understand and organize customer data, helping businesses make more informed decisions. It simplifies workflows, reveals important connections, and adapts to new data more easily, ultimately making the CRM more efficient and valuable for managing customer interactions and opportunities.

## Features

- **Graph Database Backend (Neo4j)**: Store and manage customer, opportunity, and interaction data in a graph format for easy traversal and relationship mapping.
- **Natural Language Querying**: Use NLP techniques to parse and interpret user queries in natural language, making it easy to retrieve relevant customer insights.
- **Flexible API**: Built with FastAPI to provide a set of RESTful endpoints for managing customer data and interacting with the graph database.
- **Zero-shot Classification**: Utilizes Hugging Face's transformer models for zero-shot classification to classify queries into categories like "customer," "opportunity," and "interaction."

## Installation

### Prerequisites

Before running the project, ensure you have the following dependencies installed:

- Python 3.9 or higher
- Neo4j (locally or using a cloud instance)
- `.env` file with Neo4j credentials

### Clone the Repository

```bash
git clone https://github.com/yourusername/smart-crm-nlp-neo4j.git
cd smart-crm-nlp-neo4j
```

### Install Dependencies

Create a virtual environment (optional but recommended):

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows use `venv\Scripts\activate`
```

Install the required Python packages:

```bash
pip install -r requirements.txt
```

### Set Up Environment Variables

Create a `.env` file in the root directory and add the following credentials:

```env
NEO4J_URI=neo4j://localhost:7687
NEO4J_USERNAME=neo4j
NEO4J_PASSWORD=password
```

Make sure your Neo4j instance is running and accessible with the provided credentials.

## API Endpoints

### `/init/` (POST)

**Purpose**: Initializes the schema in the Neo4j database (creates necessary constraints for `Customer`, `Opportunity`, and `Interaction` nodes).

**Usage**:

```bash
curl -X 'POST' http://localhost:8000/init/
```

### `/create/` (POST)

**Purpose**: Populates the graph database with customer, opportunity, and interaction data from a JSON object.

**Usage**:

```bash
curl -X 'POST' -H 'Content-Type: application/json' \
  -d '{"customers": [...], "opportunities": [...], "interactions": [...]}'
  http://localhost:8000/create/
```

### `/update/{entity}/{id}/` (PUT)

**Purpose**: Updates an existing `Customer`, `Opportunity`, or `Interaction` entity by its ID.

**Usage**:

```bash
curl -X 'PUT' -H 'Content-Type: application/json' \
  -d '{"name": "John Doe", "email": "john@example.com"}' \
  http://localhost:8000/update/customer/1/
```

### `/delete/{entity}/{id}/` (DELETE)

**Purpose**: Deletes an existing `Customer`, `Opportunity`, or `Interaction` entity by its ID.

**Usage**:

```bash
curl -X 'DELETE' http://localhost:8000/delete/customer/1/
```

### `/retrieve/{entity}/{id}/` (GET)

**Purpose**: Retrieves a `Customer`, `Opportunity`, or `Interaction` entity by its ID.

**Usage**:

```bash
curl -X 'GET' http://localhost:8000/retrieve/customer/1/
```

### `/query/` (POST)

**Purpose**: Accepts a natural language query and returns relevant data by interpreting the query using zero-shot classification.

**Usage**:

```bash
curl -X 'POST' -H 'Content-Type: application/json' \
  -d '{"query": "Tell me about customer 1"}' \
  http://localhost:8000/query/
```

## Technologies Used

- **FastAPI**: Web framework for building the API.
- **Neo4j**: Graph database for storing customer and interaction data.
- **Hugging Face Transformers**: For zero-shot classification in NLP queries.
- **Python 3.9+**: Python programming language.
- **Docker** (optional): For running Neo4j in a container.

## Running the Application

To run the application, use the following command:

```bash
uvicorn main:app --reload
```

This will start the server at `http://localhost:8000`. You can now interact with the API using tools like `curl`, `Postman`.

You can also interact with the APIs at `http://localhost:8000/docs`.


## Example Queries



- **Query**: "Tell me about customer 1"
  - **Response**: Returns data about the customer with ID `1`.

- **Query**: "What are the opportunities with customer 2?"
  - **Response**: Returns the opportunities linked to customer `2`.

- **Query**: "List recent interactions with customer 3"
  - **Response**: Returns the interactions for customer `3`.


## Roadmap

1. **Enhance Database Schema**: Expand and refine the schema to better support a wider range of CRM use cases and improve data modeling flexibility.

2. **Dockerize the Application**: Containerize the entire application, including Neo4j, to simplify deployment and ensure environment consistency.

3. **Integrating a Frontend application**: Develop and integrate a user-friendly frontend to provide a seamless CRM experience, allowing users to interact with data through an intuitive interface.

4. **Data Ingestion and Transformation**: Implement functionality to ingest raw, unstructured data, automatically map it to the schema, and store it in Neo4j for efficient querying and analysis.

5. Analytics: Build analytics features that allow users to extract valuable insights from CRM data, such as customer trends, opportunities, and interactions, to make data-driven decisions and drive business growth.
## Contact

- [Sreevatsan](https://github.com/TangerineGlacier)

