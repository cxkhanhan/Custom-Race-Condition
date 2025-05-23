## 效果图:

![image-20250510001009144](https://raw.githubusercontent.com/cxkhanhan/tu_chuang/main/image-20250510001009144.png)

## 功能速览:

**执行高并发 HTTP 请求：** 能够使用多线程、多进程或异步方式（目前主要实现异步模式）**同时**发送大量 HTTP 请求。

**支持发送两种不同类型的请求：** 可以配置第一阶段请求 (`-u1`, `-m1` 等参数) 和第二阶段请求 (`-u2`, `-m2` 等参数)，用于模拟复杂的交互或条件竞争场景。

**支持多种请求方法：** 支持 GET, POST 和**复杂的表单文件上传** (`upload` 模式有详细参数)。

**灵活控制发包行为：** 可以设置总请求数 (`-r`)、请求超时 (`-t`)、每批次并发请求数 (`-b`) 以及两种请求类型的发送比例 (`--rate`)。

**支持代理：** 可以通过代理 (`--proxy`) 查看和调试发送的请求。

**提供中断机制：** 可以在检测到返回内容中出现特定字符串 (`-e`) 时立即中断程序。

**输出详细信息：** 可以选择输出每个请求的详细响应包 (`--detail`)。

## 总览

```
PS D:\jiaoben\race> python310.exe .\new.py -h
usage: new.py [-h] [--detail] [--proxy PROXY] [--state {concurrent,parallel,async}] [-r REQUESTS] [-t TIMEOUT]
              [-e ENDPOINT] [-b BATCH] [-u1 U1] [-m1 {get,post,upload}] [-p1 P1] [-d1 D1] [-fn1 FN1] [-uk1 UPLOADKEY1]
              [-f1 FILE1] [-ct1 CONTENT1] [-updata1 UPLOAD_DATA1] [-cy1 CONTENT_TYPE1] [-u2 U2]
              [-m2 {get,post,upload}] [-p2 P2] [-d2 D2] [-fn2 FN2] [-uk2 UPLOADKEY2] [-f2 FILE2] [-ct2 CONTENT2]
              [-updata2 UPLOAD_DATA2] [-cy2 CONTENT_TYPE2] [--rate RATE]

高级混合模式并发测试工具

options:
  -h, --help            show this help message and exit
  --detail              输出每个响应包
  --proxy PROXY         指定代理地址和端口，如--proxy=http://127.0.0.1:8080
  --state {concurrent,parallel,async}
                        执行模式: concurrent(线程并发)/parallel(进程并行)/async(异步线程池，默认)
  -r REQUESTS, --requests REQUESTS
                        总请求数（设置为-1则无限循环）
  -t TIMEOUT, --timeout TIMEOUT
                        超时时间
  -e ENDPOINT, --endpoint ENDPOINT
                        检测返回内容中的字符串，出现则中断程序
  -b BATCH, --batch BATCH
                        如果只设置了一个url每轮只发送batch个请求,batch的作用是在这里对他每次循环,进行批量的发包,增加吞吐量,每次循环发送多少个包,如果是两个url,每次循环总发送2*batch.默
                        认100
  -u1 U1                第一阶段目标URL
  -m1 {get,post,upload}
                        第一阶段模式
  -p1 P1                第一阶段GET参数
  -d1 D1                第一阶段POST数据
  -fn1 FN1              第一阶段上传文件名
  -uk1 UPLOADKEY1, --uploadkey1 UPLOADKEY1
                        第一阶段上传文件的key
  -f1 FILE1, --file1 FILE1
                        上传文件路径,file和content二选一即可
  -ct1 CONTENT1, --content1 CONTENT1
                        文件内容,file和content二选一即可
  -updata1 UPLOAD_DATA1, --upload-data1 UPLOAD_DATA1
                        upload中除了文件上传还需要传值其他key和value的情况下写法跟post相同key1=value1&key2=value2
  -cy1 CONTENT_TYPE1, --content-type1 CONTENT_TYPE1
                        文件上传的content-type指定,如果没有则自动检测content-type并写入.如果检测不出是什么content-type那么默认application/octet-stream
  -u2 U2                第二阶段目标URL
  -m2 {get,post,upload}
                        第二阶段模式
  -p2 P2                第二阶段GET参数
  -d2 D2                第二阶段POST数据
  -fn2 FN2              第二阶段上传文件名
  -uk2 UPLOADKEY2, --uploadkey2 UPLOADKEY2
                        第二阶段上传文件的key
  -f2 FILE2, --file2 FILE2
                        本地要上传文件的路径,file和content二选一即可
  -ct2 CONTENT2, --content2 CONTENT2
                        文件内容,file和content二选一即可
  -updata2 UPLOAD_DATA2, --upload-data2 UPLOAD_DATA2
                        upload中除了文件上传还需要传值其他key和value的情况下写法跟post相同key1=value1&key2=value2
  -cy2 CONTENT_TYPE2, --content-type2 CONTENT_TYPE2
                        文件上传的content-type指定,如果没有则自动检测content-type并写入.如果检测不出是什么content-type那么默认application/octet-stream
  --rate RATE           请求比例 (格式: 1:1 或 0.7) 默认1:1
```

## 参数讲解:

### 基础参数

--state暂时还是只有异步async
其他的并发和并行从http方面的发包效率和有效性等等都比不过async

所以那两个模式的还没写



--endpoint "hello"检测返回的内容里出现hello的时候中断程序

--batch是指每轮并发请求的数量（发包批次大小）

--rate是指每次循环的发包每批次的顺序

比如1:1的情况下

每轮发包的顺序和总量则是

(先发送一个url1的包再发送一个url2的包)*batch

url1,url2,url1,url2.....循环一百次(由于有两个url则总发包量为2*batch)

比如3:1的情况下

每轮发包的顺序和总量则是

(先发送三个url1的包再发送一个url2的包)*batch

url1,url1,url1,url2.....循环一百次(总发包量为4*batch)

### 单个发包和多个发包

当你只需要一个url请求的时候

u1和u2任选一个即可

如果需要两个就两个一起发包

### 文件上传的参数讲解

文件上传的 HTTP 请求本质上就是一个表单提交

当你用到upload模块去发送的时候

-uk,-fn这两个参数必须要有

-f和-ct是二选一.至少有一个(如果同时选是只有-ct的值会被发送出去)

-uk就是上传的时候这个文件字段的key

-fn就是文件的文件名

-f和-ct就是这个表单里的key对应的value值

-updata就是在这个表单里除了文件这个字段以外还有什么字段和值.这里采用post请求的方式写入.会根据&和=自动解析成表单的key和值

-cy就是指定这个文件上传的content-type的值是多少.如果没有就自动识别.识别不出就是application/octet-stream

这里的cy指定的content-type是只改了文件上传这个字段的content-type不影响其他字段的content-type

## 举个例子

```
PS D:\jiaoben\race> python310.exe new.py -m2 upload -u2 http://127.0.0.1:9046/upload -uk2 "this-is-upload-key" -f2 ./ttttt.jpg -fn2 "this-is-upload-filename"  --rate 1:1  -r 1000000 -e "test" --state async -t 10 --batch 10 --proxy=http://127.0.0.1:8080 -updata2 "user=我的世界&women=你好世界" --detail
```

```
POST /upload HTTP/1.1
Host: 127.0.0.1:9046
Accept: */*
Accept-Encoding: gzip, deflate, br
User-Agent: Python/3.10 aiohttp/3.11.14
Content-Length: 2068
Content-Type: multipart/form-data; boundary=76175cb6946848e6a162c37081f0f3de
Connection: keep-alive

--76175cb6946848e6a162c37081f0f3de
Content-Type: image/jpeg
Content-Disposition: form-data; name="this-is-upload-key"; filename="this-is-upload-filename"

...这里是PNG的数据,此处省略...
--76175cb6946848e6a162c37081f0f3de
Content-Type: text/plain; charset=utf-8
Content-Disposition: form-data; name="user"

æçä¸ç
--76175cb6946848e6a162c37081f0f3de
Content-Type: text/plain; charset=utf-8
Content-Disposition: form-data; name="women"

ä½ å¥½ä¸ç
--76175cb6946848e6a162c37081f0f3de--
```

我们得到这样一个包

这里的乱码的hex值是对的.但是没有显示出中文

出现乱码是因为bp好像没有识别出这是个utf-8

但是我这里都加了charset=utf-8

不知道为什么还是不行

所以我们需要去

settings里找到Message editor

把Recognize automatically based on message headers改成Use the platform default (UTF-8)

然后重新发包就可以成功识别出中文

如下:

```
POST /upload HTTP/1.1
Host: 127.0.0.1:9046
Accept: */*
Accept-Encoding: gzip, deflate, br
User-Agent: Python/3.10 aiohttp/3.11.14
Content-Length: 2068
Content-Type: multipart/form-data; boundary=ae860937cbd24cc3bbeb4139442a52dc
Connection: keep-alive

--ae860937cbd24cc3bbeb4139442a52dc
Content-Type: image/jpeg
Content-Disposition: form-data; name="this-is-upload-key"; filename="this-is-upload-filename"

...这里是PNG的数据,此处省略...
--ae860937cbd24cc3bbeb4139442a52dc
Content-Type: text/plain; charset=utf-8
Content-Disposition: form-data; name="user"

我的世界
--ae860937cbd24cc3bbeb4139442a52dc
Content-Type: text/plain; charset=utf-8
Content-Disposition: form-data; name="women"

你好世界
--ae860937cbd24cc3bbeb4139442a52dc--
```

## 例子二:

python310.exe new.py -m1 get -m2 get -u1 http://127.0.0.1:9046/read -u2 http://127.0.0.1:9046/read -p1 "name=aaa" -p2 "name=../../../../flag" --rate 1:1  -r 1000000 -e "CTF{"  --state async -t 10 --batch 1000

超过延迟10s的包就放掉

然后连续发送两个get包

交叉发送

总发包量2*batch

检测到CTF{字符串就结束条件竞争

author:han

blog:http://cxkhanhan.github.io
