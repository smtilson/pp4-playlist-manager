from django.db import models



class ResourceID:
    #kind = models.CharField(max_length=100,default="",null=True,blank=True)
    #resource_id = models.CharField(max_length=100, default="",null=True,blank=True)

    @property
    def resourceId(self):
        if self.kind and self.yt_id:
            return {"kind":self.kind, "id":self.yt_id}
        print(f"No ResourceId attached to {self.__class__.__name__} {self.title} yet.")

    def set_resource_id(self,response_item):
        # save is done after this is called in order to be explicit
        self.kind = response_item['kind']
        self.yt_id = response_item['id']
        self.save()
        print(self.kind, self.yt_id)

    def clear_resource_id(self):
        self.kind = ""
        self.yt_id = ""
        self.save()
class DjangoFieldsMixin:
    #added these meta things because of a comment i saw on so
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
        attrs = {key: getattr(self, key) for key in keys}
        return {
            key: value
            for key, value in attrs.items()
            if key not in exclude and value
        }