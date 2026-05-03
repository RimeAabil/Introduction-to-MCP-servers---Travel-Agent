from datetime import datetime
from mcp.server.fastmcp import FastMCP

WEATHER_DATA = {
    "barcelona": {
        "summer": {"condition": "Hot and sunny", "temp_c": 30, "tip": "Great for beaches, stay hydrated"},
        "spring": {"condition": "Warm and mild", "temp_c": 20, "tip": "Perfect for sightseeing"},
        "autumn": {"condition": "Mild with occasional rain", "temp_c": 18, "tip": "Bring a light jacket"},
        "winter": {"condition": "Cool and rainy", "temp_c": 10, "tip": "Fewer crowds, good for museums"},
    },
    "paris": {
        "summer": {"condition": "Warm and pleasant", "temp_c": 25, "tip": "Book attractions in advance"},
        "spring": {"condition": "Mild with rain", "temp_c": 15, "tip": "Classic Paris weather"},
        "autumn": {"condition": "Cool and cloudy", "temp_c": 12, "tip": "Great for museums"},
        "winter": {"condition": "Cold and grey", "temp_c": 5, "tip": "Christmas markets are lovely"},
    },
    "default": {
        "summer": {"condition": "Warm", "temp_c": 25, "tip": "Enjoy the weather"},
        "spring": {"condition": "Mild", "temp_c": 18, "tip": "Pleasant travel weather"},
        "autumn": {"condition": "Cool", "temp_c": 14, "tip": "Pack layers"},
        "winter": {"condition": "Cold", "temp_c": 5, "tip": "Dress warmly"},
    },
}


def get_season(month: int) -> str:
    if month in (12, 1, 2):
        return "winter"
    if month in (3, 4, 5):
        return "spring"
    if month in (6, 7, 8):
        return "summer"
    return "autumn"


def get_weather(destination: str, month: int | None = None) -> dict[str, object]:
    if month is None:
        month = datetime.now().month
    season = get_season(month)
    city_data = WEATHER_DATA.get(destination.lower(), WEATHER_DATA["default"])
    weather = city_data[season]
    return {
        "destination": destination,
        "season": season,
        "month": month,
        **weather,
    }

from starlette.responses import PlainTextResponse

server = FastMCP(
    name="Weather MCP Server",
    instructions="Return expected weather for a destination and month.",
)
server.add_tool(
    get_weather,
    name="WeatherChecker",
    description="Get typical weather conditions for a destination and a month.",
)
app = server.streamable_http_app()

def health(request):
    return PlainTextResponse("OK")

app.add_route("/health", health, methods=["GET"])

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=3002)
