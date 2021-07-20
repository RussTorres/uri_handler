"""
Helping to test s3
"""
import contextlib
import copy
import os

from moto import mock_s3
import boto3
import six
from six.moves import urllib


@contextlib.contextmanager
def modified_environment_variables(modify_env=True, **kwargs):
    if modify_env:
        kwargc = copy.deepcopy(kwargs)
        old_envvars = {k: os.environ.get(k)
                       for k in six.viewkeys(kwargc) &
                       six.viewkeys(dict(os.environ))}
        for k, v in kwargc.items():
            os.environ[k] = v
        yield
        for k, v in kwargc.items():
            try:
                oldv = old_envvars[k]
                os.environ[k] = oldv
            except KeyError:
                del os.environ[k]
    else:
        yield


@contextlib.contextmanager
def mock_s3_session_resource_bucket(
        bucketname="testbucket", sessionparams={}, resourceparams={}):
    with mock_s3():
        sess = boto3.session.Session(**sessionparams)
        res = sess.resource('s3', **resourceparams)
        # res.meta.client.meta.events.unregister(
        #     "before-sign.s3", fix_s3_host)

        res.create_bucket(Bucket=bucketname)

        yield sess, res, bucketname


@contextlib.contextmanager
def mock_s3_base_uri(
        bucketname="testbucket", sessionparams={}, resourceparams={},
        include_query=True, access_string="testing", scheme="s3",
        modify_env=True, return_params=False):
    envvars = {
        "AWS_ACCESS_KEY_ID": access_string,
        "AWS_SECRET_ACCESS_KEY": access_string,
        "AWS_SECURITY_TOKEN": access_string,
        "AWS_SESSION_TOKEN": access_string
    }

    with modified_environment_variables(modify_env=modify_env, **envvars):
        with mock_s3_session_resource_bucket(
                bucketname, sessionparams, resourceparams) as (sess, res, b):

            # verify s3 bucket i/o
            buck = res.Bucket(b)
            mybucketmsg = "hello world"
            mymsgkey = "mytestmsg"
            buck.put_object(Key=mymsgkey, Body=mybucketmsg.encode("UTF-8"))

            msg = res.Object(bucketname, mymsgkey).get()["Body"].read().decode(
                "UTF-8")
            assert msg == mybucketmsg

            params = {
                "profile_name": sess.profile_name,
                "region_name": res.meta.client.meta.region_name,
                "endpoint_url": res.meta.client.meta.endpoint_url,
                "aws_access_key_id": access_string,
                "aws_secret_access_key": access_string
            }
            paramstring = (urllib.parse.urlencode(params)
                           if include_query else '')

            uri = urllib.parse.urlunparse(urllib.parse.ParseResult(
                scheme, b, "/", "", paramstring, ""))

            yield (uri, params) if return_params else uri

# instead of testing with parameters, maybe just test marshalling in here
