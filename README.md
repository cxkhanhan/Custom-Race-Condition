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

### 其他:做个开发笔记跟脚本无关

**复用Session减少连接开销**

- 在并发请求（如条件竞争漏洞测试）时，复用`requests.Session()`或`aiohttp.ClientSession`

- **优势**：避免重复TCP握手/SSL协商，提升20%~50%吞吐量

- **示例**：

  ```
  async with aiohttp.ClientSession() as session:  # 全局复用
      tasks = [send_request(session) for _ in range(100)]
      await asyncio.gather(*tasks)
  ```

**把一些数据处理等等都写在外面**

**数据预处理原则**

 - **循环外预处理**：

   - 将**固定的数据计算**（如加密、签名）提前处理
   - 避免在循环中重复初始化工具（如`hashlib.md5()`）

 - **示例**：

   ```
   # 错误：循环内重复计算
   for i in range(1000):
       data = expensive_processing(input)  # 每次循环都计算
       send(data)
   
   # 正确：提前计算
   processed_data = expensive_processing(input)  # 只算1次
   for i in range(1000):
       send(processed_data)
   ```

------



最终需要循环发包的代码不要添加太多垃圾和其他数据处理

能在循环之前处理就处理

 **保持发包循环纯净**

- 循环内**只保留必要网络I/O**（如`requests.post()`）
- 禁止在循环内：
  - 日志打印（应异步记录）
  - 复杂业务逻辑（应提前处理）
- **坏味道检测**：如果循环内有`if/else`分支，大概率需要重构

虽然asyncio.gather(*tasks)里的任务顺序好像是根据系统那边的去调度顺序没有说一定是按照tasks数组的顺序

但是按照调度顺序也基本是正常的顺序很少会打乱

但是返回的结果是按照顺序的

**asyncio.gather的任务顺序规则**

- **输入顺序**：`gather(t1, t2, t3)`的**返回结果顺序**保证与输入一致

- **执行顺序**：任务实际执行是**乱序**的（取决于事件循环调度）

- **关键结论**：

  ```
  # 返回的results顺序一定是 [r1, r2, r3]
  r1, r2, r3 = await asyncio.gather(task1(), task2(), task3())
  ```

author:han

blog:http://cxkhanhan.github.io
