"""
Drain the marsh
"""
import marshmallow


# TODO test timing on these w/ overpolulated dicts/toastedmarshmallow
class S3SessionSchema(marshmallow.Schema):
    aws_access_key_id = marshmallow.fields.String(required=False)
    aws_secret_access_key = marshmallow.fields.String(required=False)
    aws_session_token = marshmallow.fields.String(required=False)
    region_name = marshmallow.fields.String(required=False)
    profile_name = marshmallow.fields.String(required=False)
    # botocore_session = BotoSession(required=False)


# session and resourceschemas have overp
class S3ResourceSchema(marshmallow.Schema):
    endpoint_url = marshmallow.fields.String(required=False)
    aws_access_key_id = marshmallow.fields.String(required=False)
    aws_secret_access_key = marshmallow.fields.String(required=False)
    aws_session_token = marshmallow.fields.String(required=False)
    region_name = marshmallow.fields.String(required=False)


s3session_schema = S3SessionSchema()
s3resource_schema = S3ResourceSchema()


def load_s3session_dict(input_d):
    return s3session_schema.dump({k: v[-1] for k, v in input_d.items()})


def load_s3resource_dict(input_d):
    return s3resource_schema.dump({k: v[-1] for k, v in input_d.items()})
