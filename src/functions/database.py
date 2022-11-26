""" dynamodb crud operations """

from typing import List, Dict, Union
from pynamodb.exceptions import DoesNotExist


class DynamoDBCRUD:
    """ DynamoDB CRUD operations """

    def __init__(self, model):
        self.model = model

    def get(self, pk: str, sk: str) -> Union[Dict, None]:
        """ get item """
        try:
            return self.model.get(pk, sk).attribute_values
        except DoesNotExist:
            return None

    def get_all(self, pk: str, sk=None) -> List[Dict]:
        """ get all items """
        if sk:
            items = self.model.query(pk, self.model.sk == sk)
        else:
            items = self.model.query(pk)
        return [item.attribute_values for item in items]

    def create(self, **kwargs) -> Dict:
        """ create item """
        return self.model(**kwargs).save()

    def update(self, pk: str, sk: str, kwargs, arr=False) -> Dict:
        """ update and append item """
        item = self.model.get(pk, sk)
        for k, v in kwargs.items():
            if arr:
                item[f"{k}"].append(v)
            else:
                item[f"{k}"] = v
        return item.save()

    def delete(self, pk: str, sk: str) -> None:
        """ delete item """
        item = self.model.get(pk, sk)
        return item.delete()

    def delete_all(self, pk: str) -> None:
        """ delete all items """
        items = self.model.query(pk)
        for item in items:
            item.delete()
