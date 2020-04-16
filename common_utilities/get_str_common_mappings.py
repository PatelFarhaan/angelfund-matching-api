import sys
sys.path.append('../')
from project import ma
from project.models import Startup

class GetCommonMappings(ma.Schema):
    class Meta:
        fields = ("first_name", "last_name", "email", "location",
                    "sectors", "company_name", "company_link", "startup_pitch",
                    "bio", "round_size", "raised", "progress", "position",
                    "num_team_members", "slide_deck")


def get_str_users(offset):
    get_obj = Startup.objects.skip(offset).limit(10)
    if not get_obj:
        return {
            "result": False,
            "message": "empty collection"
        }
    else:
        ma_schema = GetCommonMappings()
        res = []
        for i in get_obj:
            schema_obj = ma_schema.dump(i)
            res.append(schema_obj)
        return {
            "result": True,
            "data": res
        }