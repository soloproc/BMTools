import fastapi
import uvicorn
from .registry import build_tool, list_tools
from typing import List


def _bind_tool_server(t : "ToolServer"):
    """ Add property API to ToolServer.
    t.api is a FastAPI object
    """
    
    @t.api.get("/") 
    def health():
        return {
            "status": "ok",
        }
    
    @t.api.get("/list")
    def get_tools_list():
        return {
            "tools": t.list_tools(),
        }
    
    @t.api.get("/loaded")
    def get_loaded_tools():
        return {
            "tools": list(t.loaded_tools),
        }

    @t.api.get("/.well-known/ai-plugin.json", include_in_schema=False)
    def get_api_info():
        return {
            "schema_version": "v1",
            "name_for_human": "BMTools",
            "name_for_model": "BMTools",
            "description_for_human": "tools to big models",
            "description_for_model": "tools to big models",
            "auth": {
                "type": "none",
            },
            "api": {
                "type": "openapi",
                "url": "/openapi.json",
                "is_user_authenticated": False,
            },
            "logo_url": None,
            "contact_email": "",
            "legal_info_url": "",
        }

class ToolServer:
    """ This class host your own API backend.
    """
    def __init__(self) -> None:
        # define the root API server
        self.api = fastapi.FastAPI(
            title="BMTools",
            description="Tools for bigmodels",
        )
        self.loaded_tools = set()
        _bind_tool_server(self)
    
    def load_tool(self, name : str, config = {}):
        if self.is_loaded(name):
            raise ValueError(f"Tool {name} is already loaded")
        self.loaded_tools.add(name)
        tool = build_tool(name, config)

        # mount sub API server to the root API server, thus can mount all urls of sub API server to /tools/{name} route
        self.api.mount(f"/tools/{name}", tool, name)
        return
    
    def is_loaded(self, name : str):
        return name in self.loaded_tools
    
    def serve(self, host : str = "0.0.0.0", port : int = 8079):
        uvicorn.run(self.api, host=host, port=port)

    def list_tools(self) -> List[str]:
        return list_tools()
    
