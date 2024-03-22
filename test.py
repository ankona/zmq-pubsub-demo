import typing as t

foo: t.Collection = {"a": 111}


def show_collection(col: t.Collection):
    for item in col:
        print(item)

show_collection(foo)
