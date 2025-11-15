import random
from fastmcp import FastMCP

#create a FastMCP server instance
mcp = FastMCP(name="Fast MCP Demo Server")


@mcp.tool
def roll_dice(n_dice: int = 6) -> list[int]:
    """Roll a dice with the specified number of n_dice."""
    return [random.randint(1, 6) for _ in range(n_dice)]


@mcp.tool
def add_numbers(a: int, b: int) -> int:
    """Add two numbers together."""
    return a + b

if __name__ == "__main__":
    mcp.run()
    

