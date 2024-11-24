import os
import json
from dotenv import load_dotenv
from neo4j import GraphDatabase

# Load environment variables from the .env file
load_dotenv()

class CRMDatastore:

    def __init__(self, uri, user, password):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))

    def close(self):
        self.driver.close()

    def create_schema():
        with self.driver.session() as session:
            session.run("CREATE CONSTRAINT FOR (c:Customer) REQUIRE c.id IS UNIQUE")
            session.run("CREATE CONSTRAINT FOR (o:Opportunity) REQUIRE o.id IS UNIQUE")
            session.run("CREATE CONSTRAINT FOR (i:Interaction) REQUIRE i.id IS UNIQUE")

    def populate_graph_from_json(self, json_file):
        with open(json_file, "r") as file:
            data = json.load(file)

        with self.driver.session() as session:
            # Create Customers
            for customer in data["customers"]:
                session.run(
                    "MERGE (c:Customer {id: $id})"
                    "ON CREATE SET c.name = $name, c.email = $email, c.phone = $phone",
                    id=customer["id"], name=customer["name"], email=customer["email"], phone=customer["phone"]
                )

            # Create Opportunities and associate with customers
            for opportunity in data["opportunities"]:
                session.run(
                    """
                    MERGE (o:Opportunity {id: $id})
                    ON CREATE SET o.name = $name, o.value = $value, o.status = $status
                    WITH o
                    MATCH (c:Customer {id: $customer_id})
                    MERGE (o)-[:BELONGS_TO]->(c)
                    """,
                    id=opportunity["id"], name=opportunity["name"], value=opportunity["value"], 
                    status=opportunity["status"], customer_id=opportunity["customer_id"]
                )

            # Create Interactions and associate with customers and sales reps
            for interaction in data["interactions"]:
                session.run(
                    """
                    MERGE (i:Interaction {id: $id})
                    ON CREATE SET i.date = $date, i.notes = $notes
                    WITH i
                    MATCH (c:Customer {id: $customer_id}), (s:SalesRep {id: $sales_rep_id})
                    MERGE (i)-[:WITH]->(c)
                    MERGE (i)-[:CONDUCTED_BY]->(s)
                    """,
                    id=interaction["id"], date=interaction["date"], notes=interaction["notes"], 
                    customer_id=interaction["customer_id"], sales_rep_id=interaction["sales_rep_id"]
                )

            # Create Products and associate with opportunities
            for product in data["products"]:
                session.run(
                    "MERGE (p:Product {name: $name})",
                    name=product["name"]
                )
                for opportunity_id in product["opportunities"]:
                    session.run(
                        """
                        MATCH (o:Opportunity {id: $opportunity_id}), (p:Product {name: $product_name})
                        MERGE (o)-[:INVOLVES]->(p)
                        """,
                        opportunity_id=opportunity_id, product_name=product["name"]
                    )

            # Create Sales Representatives
            for sales_rep in data["sales_reps"]:
                session.run(
                    "MERGE (s:SalesRep {id: $id})"
                    "ON CREATE SET s.name = $name, s.email = $email",
                    id=sales_rep["id"], name=sales_rep["name"], email=sales_rep["email"]
                )

    def query_opportunities_for_customer(self, customer_id):
        with self.driver.session() as session:
            query = """
            MATCH (c:Customer {id: $customer_id})-[:BELONGS_TO]->(o:Opportunity)
            RETURN o.name AS Opportunity, o.value AS Value, o.status AS Status
            """
            results = session.run(query, customer_id=customer_id)
            return [record.data() for record in results]

    def query_interactions_for_customer(self, customer_id):
        with self.driver.session() as session:
            query = """
            MATCH (c:Customer {id: $customer_id})<-[:WITH]-(i:Interaction)-[:CONDUCTED_BY]->(s:SalesRep)
            RETURN i.date AS Date, i.notes AS Notes, s.name AS SalesRep
            """
            results = session.run(query, customer_id=customer_id)
            return [record.data() for record in results]


if __name__ == "__main__":
    # Load Neo4j credentials from environment variables
    URI = os.getenv("NEO4J_URI")
    USERNAME = os.getenv("NEO4J_USER")
    PASSWORD = os.getenv("NEO4J_PASSWORD")

    # Initialize the CRM datastore
    crm = CRMDatastore(URI, USERNAME, PASSWORD)

    # Create schema
    print("Creating schema...")
    crm.create_schema()

    # Populate graph with data from JSON
    print("Populating graph with data from JSON...")
    crm.populate_graph_from_json("data/crm_data.json")

    # Query for opportunities of a customer
    customer_id = 1  # Replace with a valid customer ID
    print(f"Fetching opportunities for Customer {customer_id}...")
    opportunities = crm.query_opportunities_for_customer(customer_id)

    # Print opportunities
    print(f"Opportunities for Customer {customer_id}:")
    for opportunity in opportunities:
        print(f"- Opportunity: {opportunity['Opportunity']} | Value: {opportunity['Value']} | Status: {opportunity['Status']}")

    # Query for interactions of a customer
    print(f"Fetching interactions for Customer {customer_id}...")
    interactions = crm.query_interactions_for_customer(customer_id)

    # Print interactions
    print(f"Interactions for Customer {customer_id}:")
    for interaction in interactions:
        print(f"- Date: {interaction['Date']} | Notes: {interaction['Notes']} | Sales Rep: {interaction['SalesRep']}")

    # Close the connection
    crm.close()
