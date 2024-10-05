from pydantic import BaseModel
from typing import Any, Dict


class DynamicManager(BaseModel):
    """
    A generic object that allows dynamic addition of attributes.
    """

    def __setattr__(self, name: str, value: Any) -> None:
        """
        Dynamically set an attribute on the instance.

        Args:
            name (str): The name of the attribute.
            value (Any): The value of the attribute.
        """
        self.__dict__[name] = value

    def __getattr__(self, name: str) -> Any:
        """
        Retrieve the value of an attribute by its name.

        Args:
            name (str): The name of the attribute to retrieve.

        Returns:
            Any: The value of the attribute.

        Raises:
            AttributeError: If the attribute does not exist.
        """
        raise AttributeError(f"'{self.__class__.__name__}' object has no attribute '{name}'")

    def __delattr__(self, name: str) -> None:
        """
        Remove an attribute from the instance by its name.

        Args:
            name (str): The name of the attribute to remove.

        Raises:
            AttributeError: If the attribute does not exist.
        """
        if name in self.__dict__:
            del self.__dict__[name]
        else:
            raise AttributeError(f"'{self.__class__.__name__}' object has no attribute '{name}'")

    def add_field(self, key: str, value: Any) -> None:
        """
        Add a new attribute to the template.

        Args:
            key (str): The name for the new attribute.
            value (Any): The value for the new attribute.
        """
        setattr(self, key, value)

    def get_field(self, key: str) -> Any:
        """
        Retrieve the value of an attribute by its name.

        Args:
            key (str): The name of the attribute to retrieve.

        Returns:
            Any: The value of the attribute.

        Raises:
            AttributeError: If the attribute does not exist.
        """
        return getattr(self, key)

    def remove_field(self, key: str) -> None:
        """
        Remove an attribute from the template by its name.

        Args:
            key (str): The name of the attribute to remove.

        Raises:
            AttributeError: If the attribute does not exist.
        """
        delattr(self, key)

    def update_field(self, key: str, value: Any) -> None:
        """
        Update the value of an existing attribute.

        Args:
            key (str): The name of the attribute to update.
            value (Any): The new value for the attribute.

        Raises:
            AttributeError: If the attribute does not exist.
        """
        if hasattr(self, key):
            setattr(self, key, value)
        else:
            raise AttributeError(f"Attribute '{key}' does not exist in the template.")

    def get_all_fields(self) -> Dict[str, Any]:
        """
        Get all attributes in the template.

        Returns:
            Dict[str, Any]: A dictionary containing all attribute-value pairs in the template.
        """
        templates_dict = {}
        for key, value in self.dict().items():
            if isinstance(value, dict):
                templates_dict[key] = value
        return templates_dict
