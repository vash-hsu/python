__author__ = 'vash_hsu'

import unittest
from Worker import TaskCostList, WorkerHelper
from collections import OrderedDict
import copy


sample_set_for_testing = OrderedDict()
sample_set_for_testing['A'] = TaskCostList([1, 2, 3])
sample_set_for_testing['B'] = TaskCostList([1, 2, 3, 4, 5, 6, 7])
sample_set_for_testing['C'] = TaskCostList([1, 2, 3, 4, 5])
sample_set_for_testing['D'] = TaskCostList([1, 2, 3, 4, 5, 6, 7])
sample_set_for_testing['E'] = TaskCostList([1, 2, 3, 4, 5, 6, 7, 8])


class Test_DynamicWIP_byWorkerHelper(unittest.TestCase):

    def setUp(self):
        print '\n', '.'.join(self.id().split('.')[1:])
        for i, j in sample_set_for_testing.iteritems():
            print i, j
        print '-' * 20
        self.tasks = copy.deepcopy(sample_set_for_testing)

    def testRAT_wip_4_3_2_1(self):
        # testing scenario to 4, 3(4-1), 2(4-2), ...
        test_wip_limit = 4
        test_looper = 3
        test_index = test_looper
        # testing environment
        # work in process, softlimit, hardlimit
        helper = WorkerHelper(test_wip_limit, 0, 0)
        self.assertTrue(helper.setup(self.tasks))
        executed = ''
        print "~~~ Initialize WIP as %d ~~~" % test_wip_limit
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
        self.assertEqual(executed[0], '21')  # sprint
        self.assertEqual(executed[1], '12')   # resource max occupied
        self.assertEqual(executed[2], '')    # doing is clean
        self.assertEqual(executed[3], "[('A', 4), ('C', 6), ('B', 8), "
                                      "('D', 12), ('E', 21)]")
        print '-' * 20
        print '~~~ Historic Footprint of each Task ~~~'
        for i in helper.dump_footprint():
            print i



if __name__ == '__main__':
    unittest.main()
