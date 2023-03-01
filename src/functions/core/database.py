""" dynamodb crud operations """
from typing import Optional


class DynamoDB:
    """ DynamoDB CRUD operations """

    def __init__(self, model):
        self.model = model

    async def get(self, pk: str, sk: str) -> dict:
        """ get one item """
        return self.model.get(pk, sk).attribute_values

    async def scan(self, limit=None, offset=None) -> list:
        """ get all items """
        items = self.model.scan()
        if limit:
            items = items.limit(limit)
        if offset:
            items = items.start_at(offset)
        return [item.attribute_values for item in items]

    async def count(self, pk: str, sk: Optional[str] = None, index_name: Optional[str] = None) -> int:
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

    async def query(self, pk: str, sk: Optional[str] = None, index_name: Optional[str] = None) -> list:
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

    async def create(self, **kw) -> dict:
        """ create item """
        return self.model(**kw).save()

    async def update(self, items) -> dict:
        """ update item """
        return items.update(actions=[self.model(**items).save()])

    async def delete(self, pk: str, sk: str) -> None:
        """ delete item """
        return self.model.get(pk, sk).delete()

    async def delete_all(self, pk: str, sk: str) -> None:
        """ delete all items """
        items = self.model.query(pk, self.model.sk == sk)
        for item in items:
            item.delete()
