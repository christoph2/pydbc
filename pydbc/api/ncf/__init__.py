#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Creational API for NCF (Network Configuration File) components.

This module provides a high-level API for creating and manipulating NCF components
such as vehicles, ECUs, networks, and gateways.
"""

__copyright__ = """
   pySART - Simplified AUTOSAR-Toolkit for Python.

   (C) 2010-2023 by Christoph Schueler <cpu12.gems.googlemail.com>

   All Rights Reserved

   This program is free software; you can redistribute it and/or modify
   it under the terms of the GNU General Public License as published by
   the Free Software Foundation; either version 2 of the License, or
   (at your option) any later version.

   This program is distributed in the hope that it will be useful,
   but WITHOUT ANY WARRANTY; without even the implied warranty of
   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
   GNU General Public License for more details.

   You should have received a copy of the GNU General Public License along
   with this program; if not, write to the Free Software Foundation, Inc.,
   51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.

   s. FLOSS-EXCEPTION.txt
"""
__author__ = 'Christoph Schueler'
__version__ = '0.1.0'

from typing import Optional, List, Union, Dict, Any

from pydbc.db import VNDB
from pydbc.db.model import (
    Network, Node, Signal, ECU, Vehicle, Gateway_Signal,
    EnvVar, EnvVar_AccessNode, ECU_EnvVar, ECU_Node,
    Vehicle_ECU, Vehicle_Network, Network_Node,
    EnvironmentVariablesData
)


class NCFCreator:
    """High-level API for creating NCF components."""
    
    def __init__(self, db_path: str = ":memory:", debug: bool = False):
        """Initialize a new NCF creator.
        
        Args:
            db_path: Path to the database file or ":memory:" for in-memory database
            debug: Enable debug mode
        """
        self.db = VNDB.create(db_path, debug=debug)
        self.session = self.db.session
        self._networks = {}
        self._nodes = {}
        self._signals = {}
        self._ecus = {}
        self._vehicles = {}
        self._env_vars = {}
    
    def create_network(self, name: str, **kwargs) -> Network:
        """Create a new network.
        
        Args:
            name: Name of the network
            **kwargs: Additional network attributes
            
        Returns:
            The created Network object
        """
        network = Network(name=name, **kwargs)
        self.session.add(network)
        self._networks[name] = network
        return network
    
    def create_node(self, name: str, **kwargs) -> Node:
        """Create a new node.
        
        Args:
            name: Name of the node
            **kwargs: Additional node attributes
            
        Returns:
            The created Node object
        """
        node = Node(name=name, **kwargs)
        self.session.add(node)
        self._nodes[name] = node
        return node
    
    def create_ecu(self, name: str, **kwargs) -> ECU:
        """Create a new ECU.
        
        Args:
            name: Name of the ECU
            **kwargs: Additional ECU attributes
            
        Returns:
            The created ECU object
        """
        ecu = ECU(name=name, **kwargs)
        self.session.add(ecu)
        self._ecus[name] = ecu
        return ecu
    
    def create_vehicle(self, name: str, **kwargs) -> Vehicle:
        """Create a new vehicle.
        
        Args:
            name: Name of the vehicle
            **kwargs: Additional vehicle attributes
            
        Returns:
            The created Vehicle object
        """
        vehicle = Vehicle(name=name, **kwargs)
        self.session.add(vehicle)
        self._vehicles[name] = vehicle
        return vehicle
    
    def create_env_var(self, name: str, var_type: str, unit: Optional[str] = None,
                     minimum: Optional[float] = None, maximum: Optional[float] = None,
                     initial_value: Optional[str] = None, access_type: Optional[str] = None,
                     access_node: Optional[int] = None, **kwargs) -> EnvVar:
        """Create a new environment variable.
        
        Args:
            name: Name of the environment variable
            var_type: Type of the environment variable
            unit: Unit of the environment variable
            minimum: Minimum value
            maximum: Maximum value
            initial_value: Initial value
            access_type: Access type
            access_node: Access node ID
            **kwargs: Additional environment variable attributes
            
        Returns:
            The created EnvVar object
        """
        env_var = EnvVar(
            name=name,
            var_type=var_type,
            unit=unit,
            minimum=minimum,
            maximum=maximum,
            initial_value=initial_value,
            access_type=access_type,
            access_node=access_node,
            **kwargs
        )
        self.session.add(env_var)
        self._env_vars[name] = env_var
        return env_var
    
    def create_gateway_signal(self, source_signal: Union[str, Signal, int],
                            target_signal: Union[str, Signal, int],
                            **kwargs) -> Gateway_Signal:
        """Create a new gateway signal mapping.
        
        Args:
            source_signal: Source signal name, Signal object, or rid
            target_signal: Target signal name, Signal object, or rid
            **kwargs: Additional gateway signal attributes
            
        Returns:
            The created Gateway_Signal object
        """
        if isinstance(source_signal, str):
            source_signal = self.session.query(Signal).filter_by(name=source_signal).first().rid
        elif isinstance(source_signal, Signal):
            source_signal = source_signal.rid
            
        if isinstance(target_signal, str):
            target_signal = self.session.query(Signal).filter_by(name=target_signal).first().rid
        elif isinstance(target_signal, Signal):
            target_signal = target_signal.rid
            
        gateway_signal = Gateway_Signal(
            source_signal=source_signal,
            target_signal=target_signal,
            **kwargs
        )
        self.session.add(gateway_signal)
        return gateway_signal
    
    def add_node_to_network(self, network: Union[str, Network],
                          node: Union[str, Node],
                          connector_name: Optional[str] = None) -> Network_Node:
        """Add a node to a network.
        
        Args:
            network: Network name or Network object
            node: Node name or Node object
            connector_name: Name of the connector
            
        Returns:
            The created Network_Node object
        """
        if isinstance(network, str):
            network = self._networks[network]
        if isinstance(node, str):
            node = self._nodes[node]
            
        network_node = Network_Node(
            network=network,
            node=node,
            connector_name=connector_name
        )
        self.session.add(network_node)
        return network_node
    
    def add_ecu_to_vehicle(self, vehicle: Union[str, Vehicle],
                         ecu: Union[str, ECU]) -> Vehicle_ECU:
        """Add an ECU to a vehicle.
        
        Args:
            vehicle: Vehicle name or Vehicle object
            ecu: ECU name or ECU object
            
        Returns:
            The created Vehicle_ECU object
        """
        if isinstance(vehicle, str):
            vehicle = self._vehicles[vehicle]
        if isinstance(ecu, str):
            ecu = self._ecus[ecu]
            
        vehicle_ecu = Vehicle_ECU(
            vehicle=vehicle,
            ecu=ecu
        )
        self.session.add(vehicle_ecu)
        return vehicle_ecu
    
    def add_network_to_vehicle(self, vehicle: Union[str, Vehicle],
                             network: Union[str, Network]) -> Vehicle_Network:
        """Add a network to a vehicle.
        
        Args:
            vehicle: Vehicle name or Vehicle object
            network: Network name or Network object
            
        Returns:
            The created Vehicle_Network object
        """
        if isinstance(vehicle, str):
            vehicle = self._vehicles[vehicle]
        if isinstance(network, str):
            network = self._networks[network]
            
        vehicle_network = Vehicle_Network(
            vehicle=vehicle,
            network=network
        )
        self.session.add(vehicle_network)
        return vehicle_network
    
    def add_node_to_ecu(self, ecu: Union[str, ECU],
                      node: Union[str, Node]) -> ECU_Node:
        """Add a node to an ECU.
        
        Args:
            ecu: ECU name or ECU object
            node: Node name or Node object
            
        Returns:
            The created ECU_Node object
        """
        if isinstance(ecu, str):
            ecu = self._ecus[ecu]
        if isinstance(node, str):
            node = self._nodes[node]
            
        ecu_node = ECU_Node(
            ecu=ecu,
            node=node
        )
        self.session.add(ecu_node)
        return ecu_node
    
    def add_env_var_to_ecu(self, ecu: Union[str, ECU],
                         env_var: Union[str, EnvVar]) -> ECU_EnvVar:
        """Add an environment variable to an ECU.
        
        Args:
            ecu: ECU name or ECU object
            env_var: Environment variable name or EnvVar object
            
        Returns:
            The created ECU_EnvVar object
        """
        if isinstance(ecu, str):
            ecu = self._ecus[ecu]
        if isinstance(env_var, str):
            env_var = self._env_vars[env_var]
            
        ecu_env_var = ECU_EnvVar(
            ecu=ecu,
            env_var=env_var
        )
        self.session.add(ecu_env_var)
        return ecu_env_var
    
    def add_access_node_to_env_var(self, env_var: Union[str, EnvVar],
                                 node: Union[str, Node],
                                 access_type: str) -> EnvVar_AccessNode:
        """Add an access node to an environment variable.
        
        Args:
            env_var: Environment variable name or EnvVar object
            node: Node name or Node object
            access_type: Access type (e.g., "read", "write", "readWrite")
            
        Returns:
            The created EnvVar_AccessNode object
        """
        if isinstance(env_var, str):
            env_var = self._env_vars[env_var]
        if isinstance(node, str):
            node = self._nodes[node]
            
        env_var_access_node = EnvVar_AccessNode(
            env_var=env_var,
            node=node,
            access_type=access_type
        )
        self.session.add(env_var_access_node)
        return env_var_access_node
    
    def create_env_var_data(self, env_var: Union[str, EnvVar],
                          data: str) -> EnvironmentVariablesData:
        """Create environment variable data.
        
        Args:
            env_var: Environment variable name or EnvVar object
            data: Data value
            
        Returns:
            The created EnvironmentVariablesData object
        """
        if isinstance(env_var, str):
            env_var = self._env_vars[env_var]
            
        env_var_data = EnvironmentVariablesData(
            env_var=env_var,
            data=data
        )
        self.session.add(env_var_data)
        return env_var_data
    
    def commit(self):
        """Commit changes to the database."""
        self.session.commit()
    
    def close(self):
        """Close the database connection."""
        self.session.close()
