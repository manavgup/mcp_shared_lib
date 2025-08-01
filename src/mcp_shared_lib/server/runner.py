from mcp_shared_lib.transports.factory import get_transport


def run_server(mcp_server, transport_config, server_name="MCP Server"):
    transport = get_transport(transport_config)
    print(f"Starting {server_name} with transport: {transport_config.type}")
    transport.run(mcp_server)
