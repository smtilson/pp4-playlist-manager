
class DjangoFieldsMixin:
    @classmethod
    def all_fields(cls):
        return cls._meta.get_fields()

    @classmethod
    def all_field_names(cls):
        return [field.name for field in cls._meta.get_fields()]

    @classmethod
    def field_names(cls):
        return [field.name for field in cls._meta.fields]


class ToDictMixin:
    def to_dict_mixin(self,keys,exclude=set()):
        attrs = {key: getattr(self, key, "") for key in keys}
        return {
            key: value
            for key, value in attrs.items()
            if key not in exclude and value
        }