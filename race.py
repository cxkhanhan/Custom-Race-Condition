import sys
import threading
import mimetypes

from argparse import ArgumentParser
from collections import defaultdict
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor
import random

import aiohttp
import asyncio
import time


USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/119.0"
]

class Solver:
    def __init__(self, args):  # 新增proxy参数
        self.detail_req = args.detail or args.detail_req
        self.detail_res = args.detail or args.detail_res
        self.state = args.state
        self.configs = []
        self.content_type2=None
        self.rate=args.rate
        self.content_type1=None
        self.m1 = args.m1
        self.m2 = args.m2
        self.updata1=None
        self.updata2=None
        self.content_transfer_encoding1=None
        self.content_transfer_encoding2=None
        self.args = args  # 新增：保存args到实例变量
        # self._prepare_configs(args)
        # self.concurrency = args.concurrency
        self.timeout = args.timeout
        self.total_requests = args.requests
        self.headers = {'User-Agent': random.choice(USER_AGENTS)}
        # 根据模式选择锁类型
        self.lock = asyncio.Lock() if self.state == 'async' else threading.Lock()
        self.stop_cleanup = False
        self.endpoint = args.endpoint
        self.should_stop = False
        self.matched_response = None
        # self.baseUrl = baseUrl
        self.proxy = args.proxy  # 存储代理配置
        # self.READ_FILE_ENDPOINT = f'{self.baseUrl}'
        # self.VALID_CHECK_PARAMETER = '/read?name=AAA'
        # self.INVALID_CHECK_PARAMETER = '/read?name=../../../../../flag'
        self.batch=args.batch
        self.RACE_CONDITION_JOBS = self.batch
        self.FLAG=False
        self.templist=None
        self.content1 = None
        self.content2 = None

    async def setSessionCookie(self, session):
        await session.get(self.baseUrl)

    async def async_send_get(self, session,url ,parameter,):
        url = f'{url}?{parameter}'
        async with session.get(url,proxy=self.proxy,timeout=aiohttp.ClientTimeout(total=self.timeout)) as response:  # 添加proxy参数
            return await response.text(),response.status

    async def async_send_post(self, session,url, parameter):
        #url直接写在post尽量减缩代码
        async with session.post(url,proxy=self.proxy,data=parameter,timeout=aiohttp.ClientTimeout(total=self.timeout)) as response:  # 添加proxy参数
            return await response.text(),response.status

    async def async_send_upload(self, session, url,uploadkey,content,filename,content_type=None,content_transfer_encoding=None,updata=None):
        files = aiohttp.FormData()
        files.add_field(
            uploadkey,
            content,
            filename=filename,
            content_type=content_type,
            content_transfer_encoding=content_transfer_encoding,


        )
        if updata and isinstance(updata, dict):
            for key, value in updata.items():
                files.add_field(key, value[0] if isinstance(value, list) else value)

        async with session.post(  # 使用传入的 session
                url,
                proxy=self.proxy,
                data=files,
                timeout=aiohttp.ClientTimeout(total=self.timeout)
        ) as response:
            status_code = response.status
            return await response.text(),response.status

        # async with session.post(args.u2,proxy=self.proxy,data=parameter) as response:  # 添加proxy参数
        #     return await response.text()

    @staticmethod
    def recognize_content_type(file_path):
        content_type, encoding = mimetypes.guess_type(file_path)
        return content_type or 'application/octet-stream'


    async def raceCondition(self, session):
        tasks = list()
        # if self.FLAG==True:
        #     tasks=self.templist
        # else:
        tempdata=self.rate.split(":")
        for _ in range(self.RACE_CONDITION_JOBS):
            if self.m1 == "get":
                for iii in tempdata[0]:
                    tasks.append(self.async_send_get(session, args.u1, args.p1))
            elif self.m1 == "post":
                for iii in tempdata[0]:
                    tasks.append(self.async_send_post(session, args.u1, args.d1))
            elif self.m1 == "upload":
                for iii in tempdata[0]:
                    tasks.append(self.async_send_upload(session, args.u1,args.uploadkey1,self.content1, args.fn1,self.content_type1,self.content_transfer_encoding1,self.updata1))
            if self.m2 == "get":
                for iii in tempdata[1]:
                    tasks.append(self.async_send_get(session, args.u2, args.p2))
            elif self.m2 == "post":
                for iii in tempdata[1]:
                    tasks.append(self.async_send_post(session, args.u2, args.d2))
            elif self.m2 == "upload":
                for iii in tempdata[1]:
                    tasks.append(self.async_send_upload(session, args.u2,args.uploadkey2,self.content2, args.fn2,self.content_type2,self.content_transfer_encoding2,self.updata2))

            # self.FLAG=True
            # self.templist=tasks
        #
        # for _ in range(self.RACE_CONDITION_JOBS):
        #     tasks.append(self.async_send_get(session,args.u1, args.p1))
        #     tasks.append(self.async_send_get(session,args.u2, args.p2))

        return await asyncio.gather(*tasks)

    async def solve(self):
        sumtest=0
        # 在ClientSession中全局设置代理
        async with aiohttp.ClientSession(trust_env=True) as session:  # trust_env允许从环境变量读取代理
            result_status = defaultdict(int)
            attempts = 1
            finishedRaceConditionJobs = 0
            while True:
                print(f'    [*] Attempts #{attempts} - Finished race condition jobs: {finishedRaceConditionJobs}', end='\r')

                results = await self.raceCondition(session)
                attempts += 1

                finishedRaceConditionJobs += self.RACE_CONDITION_JOBS
                for result,status in results:
                    result_status[status] += 1
                    if args.detail:
                        print("\rresult:",result,"status_code:",status)
                        print(f'\r[*] status #{result_status}')
                    else:
                        print(f'\r[*] status #{result_status} ', end='')
                    if self.endpoint not in result:
                        continue
                    print(f'\n[+]返回的内容检测到{self.endpoint}内容如下: {result.strip()}')
                    print(f'[*] Attempts #{attempts} - Finished race condition jobs: {finishedRaceConditionJobs}', end='\n')



                    exit(0)



    def run(self):
        print("[*] 启动RACE条件竞争脚本")
        print(f"执行模式: {self.state.upper()}")
        # self._print_configs()
        # print(f"并发数: {self.concurrency}")
        if self.total_requests == -1:
            print("总请求数: 无限循环模式")
            self.total_requests = sys.maxsize
        else:
            print(f"总请求数: {self.total_requests}")
        print(f"User-Agent: {self.headers['User-Agent']}")
        if self.endpoint:
            print(f"检测端点字符串: '{self.endpoint}'")
        if self.batch:
            print("每次循环发count(urls)*batch请求:",self.batch)
            #如果有两个url则每轮循环发送2*batch个请求

        if any(c.mode == 'upload' for c in self.configs) and self.state != 'async':
            threading.Thread(target=self.auto_cleanup, daemon=True).start()

        if args.fn1 or args.fn2:
            #这里用fn1和fn2以及file1

            print(f"检测到文件上传,filename准备上传给远端的文件名: '{args.fn1}|{args.fn2}'")
            if getattr(args, 'file1', None):
                with open(args.file1, 'rb') as f:
                    self.content1 = f.read()
            elif getattr(args, 'content1', None):
                self.content1 = args.content1.encode()

            if getattr(args, 'file2', None):
                with open(args.file2, 'rb') as f:
                    self.content2 = f.read()
            elif getattr(args, 'content2', None):
                self.content2 = args.content2.encode()
            print(f"文件解析完成")


            if args.content_type1 or args.content_type2:
                print(f"用户已经指定content-type:'{args.content_type1}|{args.content_type2}'")
                self.content_type1=args.content_type1
                self.content_type2=args.content_type2
            else:
                FLAG = False
                print(f"尝试识别需要上传的文件content-type")
                if getattr(args, 'file1', None):
                    self.content_type1 = self.recognize_content_type(args.file1)
                    FLAG = True

                if getattr(args, 'file2', None):
                    self.content_type2 = self.recognize_content_type(args.file2)
                    FLAG = True
                if FLAG:
                    print(f"文件content-type识别成功{self.content_type1}|{self.content_type2}")
                else:
                    print("content-type识别失败")


        if args.upload_data1 or args.upload_data2:
            print(f"检测到文件上传中其他的数据: '{args.upload_data1}|{args.upload_data2}'")
            if getattr(args, 'upload_data1', None):
                pairs = [item.split('=', 1) for item in args.upload_data1.split("&")]  # 用=分割成key-value
                self.updata1 = dict(pairs)

            if getattr(args, 'upload_data2', None):
                    pairs = [item.split('=', 1) for item in args.upload_data2.split("&")]  # 用=分割成key-value
                    self.updata2 = dict(pairs)



        if self.state == 'async':
            asyncio.run(self.solve())
        # else:
        #     if self.state == "parallel":
        #         executor_class = ProcessPoolExecutor
        #     else:
        #         executor_class = ThreadPoolExecutor
        #
        #         # 生成请求序列
        #     request_sequence = self._generate_request_sequence()
        #
        #     with executor_class(max_workers=self.concurrency) as executor:
        #         # 使用严格序列提交任务
        #         futures = [executor.submit(self.send_strict_request, config)
        #                    for config in request_sequence]
        #         stats = self._collect_stats(futures)
        #
        #     self.stop_cleanup = True
        #     self._print_results(stats)


    # def _print_results(self, stats):
    #     print("\n\n[+] 详细测试结果:")
    #     print(f"总请求数: {stats['total']}")
    #     success_total = sum(stats['success'].values())
    #     print(f"成功率: {success_total / stats['total'] * 100:.2f}%")
    #
    #     if self.matched_response is not None:
    #         print(f"\n检测到端点字符串 '{self.endpoint}'，响应内容如下：")
    #         print(self.matched_response)
    #
    #     print("\n状态码分布:")
    #     for code, count in sorted(stats['status_codes'].items()):
    #         percentage = count / stats['total'] * 100
    #         if code == -1:
    #             # 显示详细的错误类型分布
    #             print(f"▏网络错误 ({count}次 {percentage:.2f}%):")
    #             error_details = stats.get('error_details', {})
    #             for err_type, err_count in error_details.items():
    #                 err_percent = err_count / count * 100
    #                 print(f"  ├─ {err_type}: {err_count}次 ({err_percent:.2f}%)")
    #         else:
    #             print(f"▏HTTP {code}: {count}次 ({percentage:.2f}%)")
    #             if code >= 400:
    #                 example = stats['details'][code]['example']
    #                 print(f"  示例响应: {example}...")


if __name__ == '__main__':

    parser = ArgumentParser(description='高级混合模式并发测试工具')
    detail_group = parser.add_mutually_exclusive_group()
    detail_group.add_argument('--detail', action='store_true', help='输出每个响应包')
    # detail_group.add_argument('--detail-req', action='store_true', help='仅输出请求包')
    # detail_group.add_argument('--detail-res', action='store_true', help='仅输出响应包')
    parser.add_argument('--proxy', help='指定代理地址和端口，如--proxy=http://127.0.0.1:8080')

    # 新增状态参数
    parser.add_argument('--state',
                        choices=['concurrent', 'parallel', 'async'],
                        default='async',
                        help='执行模式: concurrent(线程并发)/parallel(进程并行)/async(异步线程池，默认)')
    # parser.add_argument('--raw-params',
    #                     action='store_true',
    #                     help='保持参数原始格式，不进行URL编码')

    # 基础参数
    # parser.add_argument('-c', '--concurrency', type=int, default=50, help='并发数')
    parser.add_argument('-r', '--requests', type=int, default=100, help='总请求数（设置为-1则无限循环）')
    parser.add_argument('-t', '--timeout', type=float, default=10.0, help='超时时间')
    parser.add_argument('-e', '--endpoint', help='检测返回内容中的字符串，出现则中断程序')
    parser.add_argument('-b', '--batch', type=int, default=100, help='如果只设置了一个url每轮只发送batch个请求,batch的作用是在这里对他每次循环,进行批量的发包,增加吞吐量,每次循环发送多少个包,如果是两个url,每次循环总发送2*batch.默认100')
    # 单模式参数
    # parser.add_argument('-u', '--url', help='目标URL')
    # parser.add_argument('-m', '--mode', choices=['get', 'post', 'upload'], help='操作模式')
    # parser.add_argument('-p', '--params', help='GET参数')
    # parser.add_argument('-d', '--data', help='POST数据')

    # 多模式参数
    parser.add_argument('-u1', help='第一阶段目标URL')
    parser.add_argument('-m1', choices=['get', 'post', 'upload'], help='第一阶段模式')
    parser.add_argument('-p1', help='第一阶段GET参数')
    parser.add_argument('-d1', help='第一阶段POST数据')
    parser.add_argument('-fn1', help='第一阶段上传文件名')
    parser.add_argument('-uk1','--uploadkey1', help='第一阶段上传文件的key')
    parser.add_argument('-f1', '--file1', help='上传文件路径,file和content二选一即可')
    parser.add_argument('-ct1', '--content1', help='文件内容,file和content二选一即可')
    parser.add_argument('-updata1', '--upload-data1', help='upload中除了文件上传还需要传值其他key和value的情况下写法跟post相同key1=value1&key2=value2')
    parser.add_argument('-cy1', '--content-type1',default=None,
                        help='文件上传的content-type指定,如果没有则自动检测content-type并写入.如果检测不出是什么content-type那么默认application/octet-stream')
    # parser.add_argument('-cte1', '--content-transfer-encoding1', default=None,
    #                     help='文件上传之前对文件内容的编码,比如base64,默认None')
    # content_type2
    # args.content_transfer_encoding

    parser.add_argument('-u2', help='第二阶段目标URL')
    parser.add_argument('-m2', choices=['get', 'post', 'upload'], help='第二阶段模式')
    parser.add_argument('-p2', help='第二阶段GET参数')
    parser.add_argument('-d2', help='第二阶段POST数据')
    parser.add_argument('-fn2', help='第二阶段上传文件名')
    parser.add_argument('-uk2','--uploadkey2', help='第二阶段上传文件的key')
    parser.add_argument('-f2', '--file2', help='本地要上传文件的路径,file和content二选一即可')
    parser.add_argument('-ct2', '--content2', help='文件内容,file和content二选一即可')
    parser.add_argument('-updata2', '--upload-data2', help='upload中除了文件上传还需要传值其他key和value的情况下写法跟post相同key1=value1&key2=value2')
    parser.add_argument('-cy2', '--content-type2', default=None,
                        help='文件上传的content-type指定,如果没有则自动检测content-type并写入.如果检测不出是什么content-type那么默认application/octet-stream')
    # parser.add_argument('-cte2', '--content-transfer-encoding2', default=None,
    #                     help='文件上传之前对文件内容的编码,比如base64,默认None')


    parser.add_argument('--rate', default='1:1', help='请求比例 (格式: 1:1 或 0.7) 默认1:1')

    # 文件参数
    # parser.add_argument('-f', '--file', help='上传文件路径')
    # parser.add_argument('-ct', '--content', help='文件内容')
    # parser.add_argument('-ext', help='文件扩展名')
    # parser.add_argument('-up', '--upload-path', help='上传路径')
    # parser.add_argument('-cp', '--cleanup-path', help='清理路径')
    # parser.add_argument('-cd', '--cleanup-delay', type=float, help='清理间隔')
    # parser.add_argument('-cmd', '--command', help='执行命令')

    args = parser.parse_args()

    solver = Solver(args)
    # baseUrl = 'http://49.13.169.154:8088'

    # 代理配置（支持HTTP/HTTPS/SOCKS）
    # proxy_url = "socks5://user:pass@host:port"  # SOCKS5代理示例

    # proxy_url = "http://127.0.0.1:8080"  # 替换为你的代理地址

    # solver = Solver(baseUrl, proxy=proxy_url)  # 传入代理参数

    solver.run()
