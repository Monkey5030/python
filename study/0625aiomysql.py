# encoding=utf-8
# 作者：Admin
# 日期：2021/6/25 15:51
# 工具：PyCharm
import asyncio
import logging
import time
import traceback

import aiomysql

logobj = logging.getLogger('mysql')


class Pmysql():
    def __init__(self):
        self.coon = None
        self.pool = None

    async def initpool(self):
        try:
            logobj.debug("will connect mysql~")
            __pool = await aiomysql.create_pool(
                minsize=5,  # 连接池最小值
                maxsize=10,  # 连接池最大值
                host='127.0.0.1',
                port=3306,
                user='root',
                password='popeye12.',
                db='work',
                autocommit=True,  # 自动提交模式
            )
            return __pool
        except:
            logobj.error('connect error.', exc_info=True)

    async def getCurosr(self):
        conn = await self.pool.acquire()
        # 返回字典格式
        cur = await conn.cursor(aiomysql.DictCursor)
        return conn, cur

    async def query(self, query, param=None):
        """
        查询操作
        :param query: sql语句
        :param param: 参数
        :return:
        """
        conn, cur = await self.getCurosr()
        try:
            await cur.execute(query, param)
            return await cur.fetchall()
        except:
            logobj.error(traceback.format_exc())
        finally:
            if cur:
                await cur.close()
            # 释放掉conn,将连接放回到连接池中
            await self.pool.release(conn)

    async def execute(self, query, param=None):
        conn, cur = await self.getCurosr()
        try:
            if param is not None:
                await cur.executemany(query, param)
            else:
                await cur.execute(query, param)
            if cur.rowcount == 0:
                return False
            else:
                return True
        except:
            logobj.error(traceback.format_exc())
        finally:
            if cur:
                await cur.close()
            # 释放掉conn,将连接放回到连接池中
            await self.pool.release(conn)


async def getAmysqlobj():
    mysqlobj = Pmysql()
    pool = await mysqlobj.initpool()
    mysqlobj.pool = pool
    return mysqlobj


async def test_select():
    mysqlobj = await getAmysqlobj()
    # UPDATE `youku`.`person` SET `psName` = '张三丰' WHERE (`id` = '3');
    exeRtn = await mysqlobj.query("select * from cnblog limit 1")
    # print("查询结果",exeRtn)
    return exeRtn


async def test_update():
    mysqlobj = await getAmysqlobj()
    # UPDATE `youku`.`person` SET `psName` = '张三丰' WHERE (`id` = '3');
    exeRtn = await mysqlobj.execute("update users set username='xiao1' where id='1'")
    # print("exeRtn", exeRtn, type(exeRtn))
    if exeRtn:
        # print('操作成功')
        return '操作成功'
    else:
        # print('操作失败')
        return '操作失败'


async def main():  # 调用方
    tasks = [test_update(), test_select()]  # 把所有任务添加到task中
    done, pending = await asyncio.wait(tasks)  # 子生成器
    for r in done:  # done和pending都是一个任务，所以返回结果需要逐个调用result()
        # print('协程无序返回值：'+r.result())
        print(r.result())


if __name__ == '__main__':
    start = time.time()
    loop = asyncio.get_event_loop()  # 创建一个事件循环对象loop
    try:
        loop.run_until_complete(main())  # 完成事件循环，直到最后一个任务结束
    finally:
        loop.close()  # 结束事件循环
    # 或者执行
    # asyncio.run(main())
    print('所有IO任务总耗时%.5f秒' % float(time.time() - start))
