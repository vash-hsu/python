__author__ = 'vash_hsu'

from collections import OrderedDict, defaultdict
import unittest
import copy

class ResourceLimitation:
    def __init__(self, max_wip, soft_limit, hard_limit):
        self.wip_max = max_wip if max_wip > 0 else 65535
        self.soft_limit = soft_limit if soft_limit > 0 else 65535
        self.hard_limit = hard_limit if hard_limit > 0 else 65535

    def get_wip(self):
        return self.wip_max

    def get_soft_limit(self):
        return self.soft_limit

    def get_hard_limit(self):
        return self.hard_limit


class Passport:
    def __init__(self):
        self.footprint = dict()
        self.footprint['disk'] = list()
        self.footprint['cpu'] = list()
        self.footprint['memory'] = list()

    def step(self, disk, cpu=0, memory=0):
        self.footprint['disk'].append(disk)
        self.footprint['cpu'].append(cpu)
        self.footprint['memory'].append(memory)

    def max(self, type='all'):
        if type == 'all':
            return (max(self.footprint['disk']),
                    max(self.footprint['cpu']),
                    max(self.footprint['memory']))
        elif type in self.footprint.keys():
            return max(self.footprint[type])
        else:
            return 0

    def dump_footprint(self):
        return (self.footprint['disk'])


class Passports:
    def __init__(self):
        self.passport = OrderedDict()

    def update(self, taskid, disk=0, cpu=0, memory=0):
        if taskid not in self.passport:
            self.passport[taskid] = Passport()
        self.passport[taskid].step(disk, cpu, memory)

    def historic_max(self):
        material = dict()
        for i in self.passport.keys():
            material[i] = self.passport[i].max(type='all')
        return material

    def historic(self):
        material = []
        for task_id in self.passport.keys():
            material.append([task_id, self.passport[task_id].dump_footprint()])
        return material


class WorkerError(Exception):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)


class TaskCostList():
    def __init__(self, input_list):
        self.__costs = list(input_list)

    def next(self):
        if len(self.__costs) == 0:
            return -1
        # assume the cost of last one is 0
        elif len(self.__costs) == 1:
            self.__costs = []
            return 0
        else:
            self.__costs = self.__costs[1:]
            return self.__costs[0]

    def cost(self):
        if len(self.__costs):
            return self.__costs[0]
        else:
            return 0

    def cost_list(self):
        return str(self.__costs)

    def __str__(self):
        return self.cost_list()

    def __len__(self):
        return len(self.__costs)


class Worker:
    def __init__(self, resource, tasks_queue=OrderedDict()):
        self.task_history = tasks_queue
        self.backlog = copy.deepcopy(self.task_history)
        self.doing = OrderedDict()
        self.done = OrderedDict()
        self.passports = Passports()
        self.iteration = 0
        self.resource_peak = 0
        self.max_wip = resource.get_wip()
        self.soft_limit = resource.get_soft_limit()
        self.hard_limit = resource.get_hard_limit()
        self.unlimited = False
        if self.unlimited:
            self.max_wip = 65535
            self.soft_limit = 65535
            self.hard_limit = 65535

    def update_resource(self, resource):
        self.max_wip = resource.get_wip()
        self.soft_limit = resource.get_soft_limit()
        self.hard_limit = resource.get_hard_limit()

    def get_resource_peak(self):
        return self.resource_peak

    def get_iteration(self):
        return self.iteration

    def get_taskids_of_doing(self):
        return self.doing.keys()

    def get_cost_of_taskid(self, task_id):
        try:
            return self.doing[task_id].cost()
        except IndexError:
            return 0

    def get_tasks_of_done(self):
        return self.done.items()

    def remove_taskid_from_doing(self, task_id):
        self.doing.pop(task_id)

    def insert_taskid_to_done(self, task_id):
        self.done[task_id] = self.iteration

    def is_taskid_finished(self, task_id):
        return self.doing[task_id].next() < 0

    def track_footprint(self):
        for task_id in self.get_taskids_of_doing():
            self.passports.update(task_id,
                                  disk=self.get_cost_of_taskid(task_id))

    def purge_tasks_from_doing_to_done(self):
        for task_id in self.get_taskids_of_doing():
            if self.is_taskid_finished(task_id):
                self.remove_taskid_from_doing(task_id)
                self.insert_taskid_to_done(task_id)

    # to show how it looks like internally
    # cycle, resource_peak, doing, done
    def check_status(self):
        cycle = str(self.get_iteration())
        resource_peak = str(self.get_resource_peak())
        running = []
        for task_id in self.get_taskids_of_doing():
            running.append("%s:%d" % (task_id,
                                      self.get_cost_of_taskid(task_id)))
        doing = ';'.join(running)
        done = str(self.get_tasks_of_done())
        return cycle, resource_peak, doing, done

    # True: there is at least one task not yet finish
    # False: no task need to be processed
    # WorkerError: resource not enough
    def pre_process(self):
        if self.is_quota_available():
            return self.update_task_between_backlog_and_doing()
        else:
            raise WorkerError('Resource (%s) is not enough'
                              % self.soft_limit)

    def process(self):
        self.iteration += 1
        # doing something
        resource_occupied = self.get_resource_prediction_from_doing()
        if resource_occupied > self.hard_limit:
            raise WorkerError('Run Out of Resource (%s)'
                              % self.hard_limit)
        if self.resource_peak < resource_occupied:
            self.resource_peak = resource_occupied

    def post_process(self):
        self.track_footprint()
        self.purge_tasks_from_doing_to_done()

    def insert_incoming_task(self, task_id, task_cost_list):
        if isinstance(task_cost_list, TaskCostList) and \
                task_id not in self.backlog:
            self.backlog[task_id] = task_cost_list
        else:
            raise WorkerError('Insertion Fail for Task %s' % task_id)

    def is_quota_available(self):
        if self.unlimited or \
                self.get_resource_prediction_from_doing() < self.soft_limit:
            return True
        return False

    def get_resource_prediction_from_doing(self):
        prediction = 0
        for task_id in self.get_taskids_of_doing():
            prediction += self.get_cost_of_taskid(task_id)
        return prediction

    def pickup_martyr(self, doing):
        candidate = OrderedDict()
        # pickup victim who is younger
        the_one, the_costs = doing.popitem()
        candidate[the_one] = the_costs
        return candidate

    def update_task_between_backlog_and_doing(self):
        new_pickup = []
        # sync news from input to running
        if len(self.doing) < self.max_wip:
            for task_id, task_costs in sorted(self.backlog.iteritems()):
                if len(self.doing) < self.max_wip:
                    self.doing[task_id] = task_costs
                    new_pickup.append(task_id)
            for task_id in new_pickup:
                self.backlog.pop(task_id)
        # drop tasks and move them to backlog
        elif len(self.doing) > self.max_wip:
            push_back = self.pickup_martyr(self.doing)
            for task_id in push_back.keys():
                self.backlog[task_id] = copy.deepcopy(self.task_history[task_id])
        if len(self.doing) > 0:
            return True
        else:
            return False


class WorkerHelper:

    def __init__(self, wip, soft_limit, hard_limit):
        self.resource = ResourceLimitation(wip, soft_limit, hard_limit)
        self.worker = None
        self.ready2go = False

    def setup(self, tasks_queue):
        if isinstance(tasks_queue, OrderedDict):
            self.worker = Worker(self.resource, tasks_queue)
            self.ready2go = True
        return self.ready2go

    def update_wip(self, wip):
        self.resource = ResourceLimitation(wip,
                                           self.resource.get_soft_limit(),
                                           self.resource.get_hard_limit())
        self.worker.update_resource(self.resource)

    def insert_task(self, task_id, task_cost_list):
        try:
            self.worker.insert_incoming_task(task_id, task_cost_list)
        except WorkerError as err:
            print err.message

    def run(self):
        string2debug = ''
        if not self.ready2go:
            return string2debug
        if self.worker.pre_process():
            self.worker.process()
            string2debug = self.worker.check_status()
            self.worker.post_process()
        else:
            string2debug = self.worker.check_status()
            self.ready2go = False
        return string2debug

    def dump_footprint(self):
        #return self.worker.passports.historic_max()
        return self.worker.passports.historic()


if __name__ == '__main__':
    pass