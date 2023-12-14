import datetime
import json
import redis
import os
import importlib
import time

user_module = importlib.util.find_spec('/opt/usermodule.py')

if not user_module:
    print("usermodule.py not found")
    exit(1)

import usermodule

class Context:
    def __init__(self, host, port, input_key, output_key):
        self.host = host
        self.port = port
        self.input_key = input_key
        self.output_key = output_key
        self.last_execution = None
        self.env = {}
        self.update_last_execution_time()

    def set_env(self, env):
        self.env = env

    def update_last_execution_time(self):
        tmp = os.path.getmtime("/serverless-monitoring/usermodule.py")
        self.function_getmtime = datetime.datetime.fromtimestamp(tmp).strftime('%Y-%m-%d %H:%M:%S')
        self.last_execution = datetime.datetime.now()

def main():
    REDIS_HOST = os.getenv('REDIS_HOST', "localhost")
    REDIS_PORT = int(os.getenv('REDIS_PORT', 6379))
    REDIS_INPUT_KEY = os.getenv('REDIS_INPUT_KEY', None)
    REDIS_OUTPUT_KEY = os.getenv('REDIS_OUTPUT_KEY', None)

    SLEEP_TIME = 5

    with redis.Redis(host=REDIS_HOST, port=REDIS_PORT, charset="utf-8", decode_responses=True) as redis_client:
        if not REDIS_OUTPUT_KEY:
            print("Cannot find REDIS OUTPUT KEY")
            exit(1)

        context = Context(host=REDIS_HOST, port=REDIS_PORT, input_key=REDIS_INPUT_KEY, output_key=REDIS_OUTPUT_KEY)

        while True:
            try:
                input_data = redis_client.get(REDIS_INPUT_KEY)
                if input_data:
                    input_data = json.loads(input_data)
                    handle_redis_input(input_data, context, redis_client)

            except Exception as e:
                print(f"An error occurred: {str(e)}")

            time.sleep(SLEEP_TIME)

def handle_redis_input(input_data, context, redis_client):
    try:
        output = usermodule.handler(input_data, context)
        if context.output_key and output:
            redis_client.set(context.output_key, json.dumps(output))

        context.update_last_execution_time()

    except Exception as e:
        print(f"Cannot send the output of handler to Redis: {str(e)}")

if __name__ == '__main__':
    main()
