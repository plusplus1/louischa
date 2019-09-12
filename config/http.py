#!/usr/bin/env python
# -*- coding: utf-8 -*-


default_header = dict([[str.strip(x) for x in str.split(line, ':', 1)] for line in '''
Host: www.jinyongwang.com
Connection: keep-alive
Cache-Control: max-age=0
Upgrade-Insecure-Requests: 1
User-Agent: Mozilla/5.0 WebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.100
DNT: 1
Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3
Accept-Encoding: gzip, deflate
Accept-Language: zh-CN,zh;q=0.9,en;q=0.8
'''.strip().split('\n') if line])

