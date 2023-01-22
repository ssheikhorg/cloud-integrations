""" dynamodb crud operations """

from pynamodb.exceptions import DoesNotExist


class Dynamo:
    """ DynamoDB CRUD operations """

    def __init__(self, model):
        self.model = model

    def get(self, pk: str, sk: str = None) -> dict:
        """ get one item """
        if sk:
            return self.model.get(pk, sk).attribute_values
        return self.model.get(pk).attribute_values

    def scan(self, kw=None) -> list:
        """ get all items """
        if kw:
            items = self.model.scan(kw)
        else:
            items = self.model.scan()
        return [item.attribute_values for item in items]

    def count(self, pk: str) -> int:
        """ count items """
        items = self.model.query(pk)
        return items.count()

    def query(self, pk: str, sk=None, index=None) -> list:
        """ get all items """
        if sk:
            items = self.model.query(pk, self.model.sk == sk)
        elif index:
            items = self.model.index.query(pk)
        else:
            items = self.model.query(pk)
        return [item.attribute_values for item in items]

    def create(self, **kw) -> dict:
        """ create item """
        return self.model(**kw).save()

    def update(self, pk: str, sk: str = None, **kw) -> dict:
        """ update item """
        if sk:
            item = self.query(pk, sk)
        else:
            item = self.query(pk)
        for k, v in kw.items():
            item[0][k] = v
        return self.model(**item[0]).save()

    def delete(self, pk: str, sk: str = None) -> None:
        """ delete item """
        if sk:
            item = self.model.get(pk, sk)
        else:
            item = self.model.get(pk)
        return item.delete()

    def delete_all(self, pk: str) -> None:
        """ delete all items """
        items = self.model.query(pk)
        for item in items:
            item.delete()
