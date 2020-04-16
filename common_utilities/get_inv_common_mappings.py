import sys
sys.path.append('../')
from project import ma
from project.models import SignUpMappings

class GetCommonMappings(ma.Schema):
    class Meta:
        fields = ("deals_data", "sector_data", "accreditation_data")


def get_common_mapping():
    get_obj = list(SignUpMappings.objects.all())
    if get_obj == []:
        return {
            "result": False,
            "message": "empty collection"
        }
    else:
        ma_schema = GetCommonMappings()
        schema_obj = ma_schema.dump(get_obj[0])
        schema_obj["result"] = True
        return schema_obj