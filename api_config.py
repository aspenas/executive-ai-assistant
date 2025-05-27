"""API configuration for LangGraph 0.3.x deployment."""
from langgraph.pregel.api import create_app
from eaia.main.graph import graph as main_graph
from eaia.cron_graph import graph as cron_graph
from eaia.reflection_graphs import general_reflection_graph, multi_reflection_graph

# Create the FastAPI app with all graphs
app = create_app(
    graphs={
        "main": main_graph,
        "cron": cron_graph,
        "general_reflection_graph": general_reflection_graph,
        "multi_reflection_graph": multi_reflection_graph,
    },
    title="Executive AI Assistant",
    version="1.0.0",
    path_prefix="/",  # Ensure root path works
)

# Add root endpoint for health check
@app.get("/")
def root():
    return {"status": "ok", "message": "Executive AI Assistant API is running"}

# Add health check endpoint
@app.get("/health")
def health_check():
    return {"status": "healthy"}
