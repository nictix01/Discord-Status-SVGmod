import a2s
import logging
import socket

def get_server_status(ip: str, port: int):
    try:
        address = (ip, port)
        info = a2s.info(address, timeout=3.0)  # Changed from query_info to info
        players = a2s.players(address, timeout=3.0)  # Changed from query_players to players
        
        logging.info(f"Successfully queried server at {ip}:{port}")
        
        return {
            "success": True,
            "name": info.server_name,
            "map": info.map_name,
            "players": f"{info.player_count}/{info.max_players}",
            "game": info.game,  # Changed from game_id to game
            "players_list": ", ".join([p.name for p in players]) if players else "No players",
            "status": "Online"
        }
    except socket.timeout:
        logging.error(f"Timeout connecting to {ip}:{port}")
        return {
            "success": False,
            "status": "Server timeout"
        }
    except Exception as e:
        logging.error(f"Error querying server: {str(e)}")
        return {
            "success": False,
            "status": "Server offline or not responding"
        }