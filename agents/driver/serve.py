from __future__ import annotations

import uvicorn
from google.adk.a2a.utils.agent_to_a2a import to_a2a

from common.config import service_port

from .agent import root_agent


PORT = service_port("driver", 8000)
A2A_APP = to_a2a(root_agent, port=PORT)


if __name__ == "__main__":
    uvicorn.run(A2A_APP, host="127.0.0.1", port=PORT, reload=False)
