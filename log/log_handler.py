import logging
import datetime
import asyncio
import threading
from fastapi.encoders import jsonable_encoder
from asyncio import run_coroutine_threadsafe
from database.mongo import get_async_mongo_client
from config import get_settings

settings = get_settings()
mongo_config = settings.mongo


class AsyncMongoLogHandler(logging.Handler):
    def __init__(self):
        super().__init__()
        self.queue = asyncio.Queue()
        self.shutdown_flag = False

        # 루프 설정
        try:
            self.loop = asyncio.get_running_loop()
        except RuntimeError:
            self.loop = asyncio.new_event_loop()
            threading.Thread(target=self._start_loop, daemon=True).start()

        # Mongo 클라이언트 설정
        self.client = get_async_mongo_client()
        self.db = self.client[mongo_config.mongodb_db]

        # 루프에서 워커 생성
        def create_worker():
            self.task = asyncio.create_task(self._log_worker())

        self.loop.call_soon_threadsafe(create_worker)

    def _start_loop(self):
        asyncio.set_event_loop(self.loop)
        self.loop.run_forever()

    def emit(self, record):
        try:
            log_data = {
                "level": record.levelname,
                "message": record.getMessage(),
                "fileName": record.filename,
                "functionName": record.funcName,
                "threadName": record.threadName,
                "processName": record.processName,
                "when": datetime.datetime.utcnow(),
            }

            # MCP 루프와 로그 핸들러 루프가 다를 수 있으므로 안전하게 실행
            if self.loop.is_running():
                run_coroutine_threadsafe(self.queue.put(log_data), self.loop)
            else:
                print("[Logger] 루프가 실행 중이 아님")
        except Exception as e:
            print(f"[Logger] emit() 실패: {e}")

    async def _log_worker(self):
        print("[Logger] log_worker 시작")
        while not self.shutdown_flag or not self.queue.empty():
            try:
                log = await self.queue.get()
                print("[Logger]:", log["message"])
                await self.db[mongo_config.mongodb_log].insert_one(
                    jsonable_encoder(log)
                )
                self.queue.task_done()
            except Exception as e:
                print("[Logger] 실패:", e)
        print("[Logger] log_worker 종료")

    async def shutdown(self):
        print("[Logger] shutdown 시작")
        self.shutdown_flag = True
        await self.queue.join()
        await self.task
        self.client.close()
        print("[Logger] shutdown 완료")
