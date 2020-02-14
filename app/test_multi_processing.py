from multiprocessing import Process, Queue
import time

sentinel = -1


def creator(data, q):

    print('Creating data and putting it on the queue')

    for item in data:
        q.put(item)


def my_consumer(q):

    while True:
        data = q.get()
        print('data found to be processed: {}'.format(data))
        processed = data * 2
        print(processed)

        if data is sentinel:
            break
    pass

class TaskQueue(object):

    instance_count = 0

    def __init__(self, params={}):
        self.q = Queue()
        TaskQueue.instance_count += 1

        self.name = None
        self.stop_order = 0


        if self.name is None:
            self.name = 'queue_{:0d}'.format(TaskQueue.instance_count)

    def start(self):
        print('TaskQueue.start')
        self.q.close()
        self.q.join_thread()


    def stop(self):
        self.q.close()
        pass

    def get(self):
        return self.q.get()

    def put(self, data):
        return self.q.put(data)

    def empty(self):
        result = False

        try:
            result = self.q.empty()
        except:
            result = True

        return result

if __name__ == '__main__':

    q = TaskQueue()
    data = [5, 10, 13, -1]

    process_one = Process(target=creator, args=(data, q))
    process_two = Process(target=my_consumer, args=(q,))

    process_one.start()
    process_two.start()

    q.start()

    process_one.join()
    process_two.join()