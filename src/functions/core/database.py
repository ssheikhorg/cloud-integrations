""" dynamodb crud operations """
from typing import Optional, Any, Mapping, MutableMapping


class DynamoDB:
    """ DynamoDB CRUD operations """

    def __init__(self, model: Any) -> None:
        self.model = model

    async def get(self, pk: str, sk: str) -> Any:
        """ get one item """
        try:
            return self.model.get(pk, sk).attribute_values
        except self.model.DoesNotExist:
            return None

    async def scan(self, limit: int, offset: int) -> Any:
        """ get all items """
        items = self.model.scan()
        result = [item.attribute_values for item in items]
        # skip the first few items
        if offset > 0:
            skip = offset * limit
            result = result[skip:]
        # limit the number of items
        if limit > 0:
            result = result[:limit]
        return result

    async def count(self, pk: str, sk: Optional[str] = None, index_name: Optional[str] = None) -> Any:
        """ count items """
        if index_name:
            if index_name == "role_index":
                items = self.model.role_index.query(pk)
            elif index_name == "username_index":
                items = self.model.username_index.query(pk)
            else:
                items = self.model.email_index.query(pk)
        else:
            items = self.model.query(pk, self.model.sk == sk)
        return items.total_count

    async def query(self, pk: str, sk: Optional[str] = None, index_name: Optional[str] = None) -> Any:
        """ get all items """
        if index_name:
            if index_name == "role_index":
                items = self.model.role_index.query(pk)
            elif index_name == "username_index":
                items = self.model.username_index.query(pk)
            else:
                items = self.model.email_index.query(pk)
        else:
            items = self.model.query(pk, self.model.sk == sk)
        return [item.attribute_values for item in items]

    async def create(self, data: Mapping) -> Any:
        """ create item """
        try:
            return self.model(**data).save()
        except self.model.DoesNotExist:
            return None

    async def update(self, items: MutableMapping) -> None:
        """ update item """
        return items.update(actions=[self.model(**items).save()])

    async def delete(self, pk: str, sk: str) -> None:
        """ delete item """
        self.model.get(pk, sk).delete()

    async def delete_all(self, pk: str, sk: str) -> None:
        """ delete all items """
        items = self.model.query(pk, self.model.sk == sk)
        for item in items:
            item.delete()
