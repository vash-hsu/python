__author__ = 'vash_hsu'

import unittest
from Worker import TaskCostList, WorkerHelper
from collections import OrderedDict


class Test_DynamicWIP_byWorkerHelper(unittest.TestCase):

    def setUp(self):
        self.tasks = OrderedDict()
        self.tasks['A'] = TaskCostList([1, 2, 3])
        self.tasks['B'] = TaskCostList([1, 2, 3, 4, 5, 6, 7])
        self.tasks['C'] = TaskCostList([1, 2, 3, 4, 5])
        self.tasks['D'] = TaskCostList([1, 2, 3, 4, 5, 6, 7])
        self.tasks['E'] = TaskCostList([1, 2, 3, 4, 5, 6, 7, 8])
        print '\n'
        print '.'.join(self.id().split('.')[1:])

    def testRAT_wip_4_3_2_1(self):
        test_wip_limit = 4
        test_looper = 3
        test_index = test_looper
        helper = WorkerHelper(test_wip_limit, 0, 0)
        self.assertTrue(helper.setup(self.tasks))
        executed = ''
        while True:
            test_index -= 1
            result = helper.run()
            if result:
                executed = result
                print executed
                concurrent_workers = len(result[2].split(';'))
                self.assertLessEqual(concurrent_workers, test_wip_limit,
                                     'exceed WIP limitation')
            else:
                break
            if test_index <= 0:
                test_index = test_looper
                # do something to change
                if test_wip_limit > 1:
                    test_wip_limit -= 1
                    helper.update_wip(test_wip_limit)
                    print "~~~ Time to Change WIP to %d ~~~" % test_wip_limit
        self.assertEqual(len(executed), 4)
        self.assertEqual(executed[0], '17')  # sprint
        self.assertEqual(executed[1], '12')   # resource max occupied
        self.assertEqual(executed[2], '')    # doing is clean
        self.assertEqual(executed[3], "[('A', 4), ('C', 6), ('B', 8), "
                                      "('E', 13), ('D', 17)]")


if __name__ == '__main__':
    unittest.main()
