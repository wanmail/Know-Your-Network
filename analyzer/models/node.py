from neomodel import StructuredNode


# class UpsertNode(StructuredNode):
#     def __init__(self, unique_index: str):
#         self.unique_index = unique_index

#     def save(self):

#         node = self.__class__.nodes.first_or_none(resource_id=self.resource_id)
#         if node is not None:
#             # if hasattr(self, "element_id_property"):
#             self.element_id_property = node.element_id_property

#         return super().save()


# class StructuredNodeSkipNone(StructuredNode):
#     def deflate(cls, properties, obj=None, skip_empty=True):
#         return super().inflate(cls, properties, obj, skip_empty)


def upsert_decorator(unique_index: str):
    """
    A decorator to handle upsert operations for StructuredNode instances. This decorator checks if a node with the 
    specified unique index already exists. If it does, it updates the instance's element_id_property and returns the 
    existing node if no other properties need to be updated. If the node does not exist or other properties need to be 
    updated, it proceeds with the decorated function.
    
    Note: StructuredNode will update None properties when use save() !
    
    Args:
        unique_index (str): The name of the unique index property to check for existing nodes.
    Returns:
        function: The decorated function with upsert logic applied.
    """
    def decorate(func):
        def wrapper(cls: StructuredNode):
            id = getattr(cls, unique_index)
            node = cls.nodes.first_or_none(**{unique_index: id})
            if node is not None:
                cls.element_id_property = node.element_id_property

                # if no params, return directly
                params = cls.deflate(cls.__properties__, cls, skip_empty=True)

                keys = list(params.keys())
                if len(keys) == 0:
                    return node
                if len(keys) == 1 and keys[0] == unique_index:
                    return node
                
            return func(cls)
        return wrapper
    return decorate
