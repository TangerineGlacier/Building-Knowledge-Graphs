import os
import json
from dotenv import load_dotenv
from neo4j import GraphDatabase

# Load environment variables from the .env file
load_dotenv()

class KnowledgeGraph:

    def __init__(self, uri, user, password):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))

    def close(self):
        self.driver.close()

    def create_schema(self):
        with self.driver.session() as session:
            # Create constraints if they don't already exist
            session.run("""
                CREATE CONSTRAINT IF NOT EXISTS FOR (u:User) REQUIRE u.id IS UNIQUE;
            """)
            session.run("""
                CREATE CONSTRAINT IF NOT EXISTS FOR (e:Event) REQUIRE e.id IS UNIQUE;
            """)
            session.run("""
                CREATE CONSTRAINT IF NOT EXISTS FOR (c:Category) REQUIRE c.name IS UNIQUE;
            """)

    def populate_graph_from_json(self, json_file):
        with open(json_file, "r") as file:
            data = json.load(file)

        with self.driver.session() as session:
            # Create categories (using MERGE to avoid duplicates)
            for category in data["categories"]:
                session.run(
                    "MERGE (c:Category {name: $name})",
                    name=category["name"]
                )

            # Create events and associate with categories
            for event in data["events"]:
                session.run(
                    """
                    MERGE (e:Event {id: $id})
                    ON CREATE SET e.name = $name, e.location = $location
                    WITH e
                    MATCH (c:Category {name: $category})
                    MERGE (e)-[:BELONGS_TO]->(c)
                    """,
                    id=event["id"], name=event["name"], location=event["location"], category=event["category"]
                )

            # Create users and associate with categories
            for user in data["users"]:
                session.run(
                    "MERGE (u:User {id: $id})",
                    id=user["id"]
                )
                for liked_category in user["likes"]:
                    session.run(
                        """
                        MATCH (u:User {id: $user_id}), (c:Category {name: $category})
                        MERGE (u)-[:LIKES]->(c)
                        """,
                        user_id=user["id"], category=liked_category
                    )

    def query_recommendations(self, user_id):
        with self.driver.session() as session:
            query = """
            MATCH (u:User {id: $user_id})-[:LIKES]->(c:Category)<-[:BELONGS_TO]-(e:Event)
            RETURN e.name AS Event, e.location AS Location
            """
            results = session.run(query, user_id=user_id)
            return [record.data() for record in results]


if __name__ == "__main__":
    # Load Neo4j credentials from environment variables
    URI = os.getenv("NEO4J_URI")
    USERNAME = os.getenv("NEO4J_USER")
    PASSWORD = os.getenv("NEO4J_PASSWORD")

    # Initialize the graph
    graph = KnowledgeGraph(URI, USERNAME, PASSWORD)

    # Create schema
    print("Creating schema...")
    graph.create_schema()

    # Populate graph with data from JSON
    print("Populating graph with data from JSON...")
    graph.populate_graph_from_json("data/data.json")

    # Query for recommendations
    user_id = 1  # Replace with a valid user ID
    print(f"Fetching recommendations for User {user_id}...")
    recommendations = graph.query_recommendations(user_id)

    # Print results
    print(f"Recommendations for User {user_id}:")
    for rec in recommendations:
        print(f"- Event: {rec['Event']} at {rec['Location']}")

    # Close the connection
    graph.close()
