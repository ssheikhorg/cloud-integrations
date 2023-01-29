""" dynamodb crud operations """
from pynamodb.exceptions import DoesNotExist


class DynamoDB:
    """ DynamoDB CRUD operations """

    def __init__(self, model):
        self.model = model

    async def get(self, pk: str) -> dict:
        """ get one item """
        return self.model.get(pk).attribute_values

    async def scan(self, limit=None, offset=None) -> list:
        """ get all items """
        items = self.model.scan()
        if limit:
            items = items.limit(limit)
        if offset:
            items = items.start_at(offset)
        return [item.attribute_values for item in items]

    async def count(self, pk: str, index_name=None) -> int:
        """ count items """
        if index_name:
            if index_name == "role_index":
                items = self.model.role_index.query(pk)
            elif index_name == "username_index":
                items = self.model.username_index.query(pk)
            else:
                items = self.model.email_index.query(pk)
        else:
            items = self.model.query(pk)
        return items.total_count

    async def query(self, pk: str, sk=None, index_name=None) -> list:
        """ get all items """
        if sk:
            items = self.model.query(pk, self.model.sk == sk)
        elif index_name:
            if index_name == "role_index":
                items = self.model.role_index.query(pk)
            elif index_name == "username_index":
                items = self.model.username_index.query(pk)
            else:
                items = self.model.email_index.query(pk)
        else:
            items = self.model.query(pk)
        return [item.attribute_values for item in items]

    async def create(self, **kw) -> dict:
        """ create item """
        return self.model(**kw).save()

    async def update(self, items) -> dict:
        """ update item """
        return items.update(actions=[self.model(**items).save()])

    async def delete(self, pk: str, sk: str = None) -> None:
        """ delete item """
        if sk:
            return self.model.get(pk, sk).delete()
        return self.model.get(pk).delete()

    async def delete_all(self, pk: str) -> None:
        """ delete all items """
        items = self.model.query(pk)
        for item in items:
            item.delete()
