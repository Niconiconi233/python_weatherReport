# -*- coding: utf-8 -*-
import oss2
import os

dir = os.environ

accesskey = dir.get('OSSACCESSKEY')
accesskeysecret = dir.get('OSSACCESSKEYSECRET')
endpoint = dir.get('OSSENDPOINT')
bucket = dir.get('OSSBUCKET')



auth = oss2.Auth(accesskey, accesskeysecret)
# Endpoint以杭州为例，其它Region请按实际情况填写。
bucket = oss2.Bucket(auth, endpoint, bucket)

style = 'image/auto-orient,1/resize,p_50/quality,q_90'

def get_temp_url(image):
# 生成下载文件的签名URL，有效时间为60s。
    return bucket.sign_url('GET', image, 60 * 5, params={'x-oss-process': style})     
