import os
import json
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from neo4j import GraphDatabase
from typing import List
from transformers import pipeline

# Load environment variables
from dotenv import load_dotenv

load_dotenv()

# Set up FastAPI app
app = FastAPI()

# Initialize Neo4j connection
uri = os.getenv("NEO4J_URI", "neo4j://localhost:7687")
username = os.getenv("NEO4J_USERNAME", "neo4j")
password = os.getenv("NEO4J_PASSWORD", "password")
driver = GraphDatabase.driver(uri, auth=(username, password))

# NLP pipeline for Query endpoint
nlp_pipeline = pipeline("zero-shot-classification")

# Pydantic models for input validation
class Customer(BaseModel):
    id: int
    name: str
    email: str
    phone: str

class Opportunity(BaseModel):
    id: int
    name: str
    value: float
    status: str
    customer_id: int

class Interaction(BaseModel):
    id: int
    date: str
    notes: str
    customer_id: int
    sales_rep_id: int

# Model for the query request
class QueryRequest(BaseModel):
    query: str

# Helper functions
def create_schema():
    with driver.session() as session:
        # Check and create Customer constraint if it doesn't exist
        session.run("""
            CREATE CONSTRAINT IF NOT EXISTS FOR (c:Customer) REQUIRE c.id IS UNIQUE
        """)
        
        # Check and create Opportunity constraint if it doesn't exist
        session.run("""
            CREATE CONSTRAINT IF NOT EXISTS FOR (o:Opportunity) REQUIRE o.id IS UNIQUE
        """)
        
        # Check and create Interaction constraint if it doesn't exist
        session.run("""
            CREATE CONSTRAINT IF NOT EXISTS FOR (i:Interaction) REQUIRE i.id IS UNIQUE
        """)


def populate_graph_from_json(json_data):
    with driver.session() as session:
        for customer in json_data['customers']:
            session.run("MERGE (c:Customer {id: $id, name: $name, email: $email, phone: $phone})",
                        id=customer['id'], name=customer['name'], email=customer['email'], phone=customer['phone'])
        
        for opportunity in json_data['opportunities']:
            session.run("MERGE (o:Opportunity {id: $id, name: $name, value: $value, status: $status})"
                        "MERGE (c:Customer {id: $customer_id}) "
                        "MERGE (c)-[:HAS_OPPORTUNITY]->(o)",
                        id=opportunity['id'], name=opportunity['name'], value=opportunity['value'],
                        status=opportunity['status'], customer_id=opportunity['customer_id'])
        
        for interaction in json_data['interactions']:
            session.run("MERGE (i:Interaction {id: $id, date: $date, notes: $notes})"
                        "MERGE (c:Customer {id: $customer_id}) "
                        "MERGE (s:SalesRep {id: $sales_rep_id}) "
                        "MERGE (c)-[:HAS_INTERACTION]->(i)-[:CONDUCTED_BY]->(s)",
                        id=interaction['id'], date=interaction['date'], notes=interaction['notes'],
                        customer_id=interaction['customer_id'], sales_rep_id=interaction['sales_rep_id'])

# API endpoints
@app.post("/init/")
async def init_schema():
    try:
        create_schema()
        return {"message": "Schema created successfully"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/create/")
async def create_data(json_data: dict):
    try:
        populate_graph_from_json(json_data)
        return {"message": "Data populated successfully"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.put("/update/{entity}/{id}/")
async def update_entity(entity: str, id: int, updated_data: dict):
    try:
        with driver.session() as session:
            if entity == "customer":
                session.run("""
                    MATCH (c:Customer {id: $id})
                    SET c.name = $name, c.email = $email, c.phone = $phone
                    """, id=id, **updated_data)
            elif entity == "opportunity":
                session.run("""
                    MATCH (o:Opportunity {id: $id})
                    SET o.name = $name, o.value = $value, o.status = $status
                    """, id=id, **updated_data)
            elif entity == "interaction":
                session.run("""
                    MATCH (i:Interaction {id: $id})
                    SET i.date = $date, i.notes = $notes
                    """, id=id, **updated_data)
            else:
                raise HTTPException(status_code=400, detail="Invalid entity type")
        return {"message": "Entity updated successfully"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.delete("/delete/{entity}/{id}/")
async def delete_entity(entity: str, id: int):
    try:
        with driver.session() as session:
            if entity == "customer":
                session.run("MATCH (c:Customer {id: $id}) DETACH DELETE c", id=id)
            elif entity == "opportunity":
                session.run("MATCH (o:Opportunity {id: $id}) DETACH DELETE o", id=id)
            elif entity == "interaction":
                session.run("MATCH (i:Interaction {id: $id}) DETACH DELETE i", id=id)
            else:
                raise HTTPException(status_code=400, detail="Invalid entity type")
        return {"message": "Entity deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/retrieve/{entity}/{id}/")
async def retrieve_entity(entity: str, id: int):
    try:
        with driver.session() as session:
            if entity == "customer":
                result = session.run("MATCH (c:Customer {id: $id}) RETURN c", id=id)
            elif entity == "opportunity":
                result = session.run("MATCH (o:Opportunity {id: $id}) RETURN o", id=id)
            elif entity == "interaction":
                result = session.run("MATCH (i:Interaction {id: $id}) RETURN i", id=id)
            else:
                raise HTTPException(status_code=400, detail="Invalid entity type")
            return {"data": result.single()}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/query/")
async def query_nlp(query_request: QueryRequest):
    try:
        query = query_request.query  # Extract the query string from the request body
        result = nlp_pipeline(query, candidate_labels=["customer", "opportunity", "interaction"])
        label = result['labels'][0]  # Get the top label
        
        with driver.session() as session:
            if label == "customer":
                result = session.run("MATCH (c:Customer) RETURN c LIMIT 1")
            elif label == "opportunity":
                result = session.run("MATCH (o:Opportunity) RETURN o LIMIT 1")
            elif label == "interaction":
                result = session.run("MATCH (i:Interaction) RETURN i LIMIT 1")
            else:
                raise HTTPException(status_code=400, detail="Unknown query type")
            
            # Retrieve all results before consuming the result
            data = result.data()  # This fetches all records in the result
            
        if data:
            return {"query_result": data[0]}  # Return the first record if available
        else:
            raise HTTPException(status_code=404, detail="No records found")
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
