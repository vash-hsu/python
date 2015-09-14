__author__ = 'vash_hsu'

import unittest
from Worker import Worker, TaskCostList, ResourceLimitation, WorkerHelper
from collections import OrderedDict


class TestWorker_WIP(unittest.TestCase):

    def setUp(self):
        self.tasks = OrderedDict()
        self.tasks['A'] = TaskCostList([1, 1, 2, 3, 3])
        self.tasks['B'] = TaskCostList([1, 2, 3, 4, 5, 6, 7])
        self.tasks['C'] = TaskCostList([1, 3, 5, 7, 9])
        self.tasks['D'] = TaskCostList([2, 2, 4, 4, 5, 5, 5])
        self.tasks['E'] = TaskCostList([1, 2, 3, 4, 5, 5, 6, 7])
        print '\n'
        print '.'.join(self.id().split('.')[1:])

    def testRAT_nolimitation(self):
        my_profile = ResourceLimitation(0, 0, 0)
        my_worker = Worker(my_profile, self.tasks)
        # -----
        while True:
            if my_worker.pre_process():
                string2debug = my_worker.check_status()
                print "\t", string2debug
                my_worker.process()
                my_worker.post_process()
            else:
                string2debug = my_worker.check_status()
                print "\t", string2debug
                break
        self.assertEqual(string2debug,
                         ('9', '27', '',
                          "[('A', 6), ('C', 6), ('B', 8), ('D', 8), ('E', 9)]"))

    def testRAT_max_concurrent_1(self):
        my_profile = ResourceLimitation(1, 0, 0)
        my_worker = Worker(my_profile, self.tasks)
        string2debug = my_worker.check_status()
        self.assertEqual(string2debug, ('0', '0', '', '[]'))
        # -----
        while True:
            if my_worker.pre_process():
                my_worker.process()
                my_worker.post_process()
            else:
                break
        string2debug = my_worker.check_status()
        print string2debug
        self.assertEqual(string2debug,
                         ('37', '9', '',
                          "[('A', 6), ('B', 14), ('C', 20), "
                          "('D', 28), ('E', 37)]"))

    def testRAT_max_concurrent_2(self):
        my_profile = ResourceLimitation(2, 0, 0)
        my_worker = Worker(my_profile, self.tasks)
        # -----
        while True:
            if my_worker.pre_process():
                my_worker.process()
                my_worker.post_process()
            else:
                break
        string2debug = my_worker.check_status()
        print string2debug
        self.assertEqual(string2debug,
                         ('21', '13', '',
                          "[('A', 6), ('B', 8), ('C', 12), "
                          "('D', 16), ('E', 21)]"))

    def testRAT_max_concurrent_3(self):
        my_profile = ResourceLimitation(3, 0, 0)
        my_worker = Worker(my_profile, self.tasks)
        # -----
        while True:
            if my_worker.pre_process():
                my_worker.process()
                my_worker.post_process()
            else:
                break
        string2debug = my_worker.check_status()
        print string2debug
        self.assertEqual(string2debug,
                         ('15', '17', '',
                          "[('A', 6), ('C', 6), ('B', 8), "
                          "('D', 14), ('E', 15)]"))

    def testRAT_max_concurrent_4(self):
        my_profile = ResourceLimitation(4, 0, 0)
        my_worker = Worker(my_profile, self.tasks)
        # -----
        while True:
            if my_worker.pre_process():
                my_worker.process()
                my_worker.post_process()
            else:
                break
        string2debug = my_worker.check_status()
        print string2debug
        self.assertEqual(string2debug,
                         ('15', '22', '',
                          "[('A', 6), ('C', 6), ('B', 8), "
                          "('D', 8), ('E', 15)]"))


class TestWorkerHelper(unittest.TestCase):

    def setUp(self):
        self.tasks = OrderedDict()
        self.tasks['A'] = TaskCostList([1, 2, 3])
        self.tasks['B'] = TaskCostList([1, 2, 3, 4, 5, 6, 7])
        self.tasks['C'] = TaskCostList([1, 2, 3, 4, 5])
        self.tasks['D'] = TaskCostList([1, 2, 3, 4, 5, 6, 7])
        self.tasks['E'] = TaskCostList([1, 2, 3, 4, 5, 6, 7, 8])
        print '\n'
        print '.'.join(self.id().split('.')[1:])

    def testRAT_max_wip_1(self):
        helper = WorkerHelper(1, 0, 0)
        self.assertTrue(helper.setup(self.tasks))
        executed = ''
        while True:
            result = helper.run()
            if result:
                executed = result
                print executed
            else:
                break
        self.assertEqual(len(executed), 4)
        self.assertEqual(executed[0], '35')  # sprint
        self.assertEqual(executed[1], '8')   # resource max occupied
        self.assertEqual(executed[2], '')    # doing is clean
        self.assertEqual(executed[3], "[('A', 4), ('B', 12), ('C', 18), "
                                      "('D', 26), ('E', 35)]")

    def testRAT_max_wip_2(self):
        helper = WorkerHelper(2, 0, 0)
        self.assertTrue(helper.setup(self.tasks))
        executed = ''
        while True:
            result = helper.run()
            if result:
                executed = result
                print executed
            else:
                break
        self.assertEqual(len(executed), 4)
        self.assertEqual(executed[0], '19')  # sprint
        self.assertEqual(executed[1], '12')   # resource max occupied
        self.assertEqual(executed[2], '')    # doing is clean
        self.assertEqual(executed[3], "[('A', 4), ('B', 8), ('C', 10), "
                                      "('D', 16), ('E', 19)]")

    def testRAT_max_wip_3(self):
        helper = WorkerHelper(3, 0, 0)
        self.assertTrue(helper.setup(self.tasks))
        executed = ''
        while True:
            result = helper.run()
            if result:
                executed = result
                print executed
            else:
                break
        self.assertEqual(len(executed), 4)
        self.assertEqual(executed[0], '15')  # sprint
        self.assertEqual(executed[1], '12')   # resource max occupied
        self.assertEqual(executed[2], '')    # doing is clean
        self.assertEqual(executed[3], "[('A', 4), ('C', 6), ('B', 8), "
                                      "('D', 12), ('E', 15)]")

    def testRAT_max_wip_4(self):
        helper = WorkerHelper(4, 0, 0)
        self.assertTrue(helper.setup(self.tasks))
        executed = ''
        while True:
            result = helper.run()
            if result:
                executed = result
                print executed
            else:
                break
        self.assertEqual(len(executed), 4)
        self.assertEqual(executed[0], '13')  # sprint
        self.assertEqual(executed[1], '17')   # resource max occupied
        self.assertEqual(executed[2], '')    # doing is clean
        self.assertEqual(executed[3], "[('A', 4), ('C', 6), ('B', 8), "
                                      "('D', 8), ('E', 13)]")

    def testRAT_max_wip_5(self):
        helper = WorkerHelper(5, 0, 0)
        self.assertTrue(helper.setup(self.tasks))
        executed = ''
        while True:
            result = helper.run()
            if result:
                executed = result
                print executed
            else:
                break
        self.assertEqual(len(executed), 4)
        self.assertEqual(executed[0], '9')  # sprint
        self.assertEqual(executed[1], '21')   # resource max occupied
        self.assertEqual(executed[2], '')    # doing is clean
        self.assertEqual(executed[3], "[('A', 4), ('C', 6), ('B', 8), "
                                      "('D', 8), ('E', 9)]")


if __name__ == '__main__':
    unittest.main()
