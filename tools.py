from smolagents import Tool
from qdrant_client import QdrantClient

EMBEDDING_MODEL="BAAI/bge-small-en-v1.5"

class QdrantQueryTool(Tool):
    name = "qdrant_query"
    description = "Uses semantic search to retrieve data from the Qdrant collection."
    inputs = {
        "query": {
            "type": "string",
            "description": "The query to perform. This should be semantically close to your target documents.",
        }
    }
    output_type = "string"

    def __init__(self, qdrant_host, qdrant_port, collection_name, vector_name, **kwargs):
        super().__init__(**kwargs)
        self.collection_name = collection_name
        self.vector_name = vector_name
        self.client = QdrantClient(qdrant_host, port=qdrant_port)

    def forward(self, query: str) -> str:
        search_result = self.client.query(
            query_text=query,
            collection_name=self.collection_name,
            limit=5)
        for p in search_result:
            print(f"ID={p.id}, score={p.score}, payload={p.metadata}")
        #docs = "Retrieved documents:\n" + "".join(
        #    [
        #        f"== Document {str(i)} ==\n"
        #        + f"payvload: {point.payload}\n"
        #        for i, point in enumerate(points)
        #    ]
        #)

        #return docs
        return ""
