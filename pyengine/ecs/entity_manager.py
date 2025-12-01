from typing import Dict, Type, TypeVar, Optional, Generator, Tuple
from pyengine.ecs.component import Component

# We define a generic type "T".
# "bound=Component" means T must be Component or a subclass of Component.
T = TypeVar("T", bound=Component)

class EntityManager:
    def __init__(self):
        self.next_id = 0
        # Corrected key type from 'str' to 'Type[Component]' to match logic
        self.components: Dict[Type[Component], Dict[int, Component]] = {}

    def create_entity(self) -> int:
        entity = self.next_id
        self.next_id += 1
        return entity
    
    def add_component(self, entity: int, component: Component) -> None:
        comp_type = type(component)
        
        if comp_type not in self.components:
            self.components[comp_type] = {}

        self.components[comp_type][entity] = component

    def get_component(self, entity: int, comp_type: Type[T]) -> Optional[T]:
        """
        Retrieves a component of a specific type for an entity.
        :param comp_type: The class of the component to retrieve (e.g. Transform)
        :return: An instance of T (e.g. Transform) or None if not found.
        """
        # We access the dictionary for this specific component type
        store = self.components.get(comp_type)
        
        if store:
            return store.get(entity)
        return None
    
    def get_entities_with(self, *comp_types: Type[Component]) -> Generator[Tuple[int, Tuple[Component, ...]], None, None]:
        """
        Yields (EntityID, (Component1, Component2, ...)) for entities having ALL requested components.
        """
        if not comp_types:
            return
        
        first_type = comp_types[0]
        first_store = self.components.get(first_type, {})
        
        for entity in first_store:
            is_valid = True
            for ct in comp_types[1:]:
                if entity not in self.components.get(ct, {}):
                    is_valid = False
                    break
            
            if is_valid:
                fetched_components = tuple(self.components[ct][entity] for ct in comp_types)
                
                yield entity, fetched_components
