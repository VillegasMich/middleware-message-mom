"""
This module provides a singleton instance of the RoundRobinManager class. 
"""
from app.RoundRobinManager import RoundRobinManager

round_robin_manager = RoundRobinManager()

def get_round_robin_manager():
    return round_robin_manager
