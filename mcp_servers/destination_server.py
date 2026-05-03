from mcp.server.fastmcp import FastMCP

DESTINATIONS = {
    "barcelona": {
        "attractions": [
            "Sagrada Família — Gaudí's breathtaking basilica",
            "Park Güell — colorful mosaic park with city views",
            "Las Ramblas — famous pedestrian boulevard",
            "Camp Nou — iconic FC Barcelona stadium",
            "Gothic Quarter — medieval streets and architecture",
            "Barceloneta Beach — city beach with great vibes",
        ],
        "food": ["Tapas at a local bodega", "Paella at La Barceloneta", "Churros with chocolate"],
        "tips": "Best explored on foot. Get a T-Casual metro card for transport.",
    },
    "paris": {
        "attractions": [
            "Eiffel Tower — go at sunset for best views",
            "The Louvre — world's largest art museum",
            "Montmartre — charming artistic neighborhood",
            "Notre-Dame Cathedral — currently being restored",
            "Musée d'Orsay — Impressionist masterpieces",
        ],
        "food": ["Croissants at a local boulangerie", "Steak frites", "French onion soup"],
        "tips": "Buy museum passes in advance. Metro is efficient and affordable.",
    },
}


def search_destination(destination: str) -> dict[str, object]:
    city = destination.lower()
    if city in DESTINATIONS:
        data = DESTINATIONS[city]
    else:
        data = {
            "attractions": ["Historical city center", "Local markets", "Museums", "Natural parks"],
            "food": ["Local cuisine", "Street food markets"],
            "tips": f"Explore {destination} at your own pace. Ask locals for hidden gems.",
        }

    return {"destination": destination, **data}

from starlette.responses import PlainTextResponse

server = FastMCP(
    name="Destination Search MCP Server",
    instructions="Provide destination attractions, food, and travel tips for a location.",
)
server.add_tool(
    search_destination,
    name="DestinationSearch",
    description="Look up attractions, local cuisine, and travel tips for a destination.",
)
app = server.streamable_http_app()

def health(request):
    return PlainTextResponse("OK")

app.add_route("/health", health, methods=["GET"])

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=3004)
