$ python movie_lazy_pack.py
Usage: --if input.csv --of output.csv
       --gray <DIR_GRAYLIST>
       --black <BLACK_BLACKLIST>
       --deny <DIR_DENYLIST>


$ python movie_lazy_pack.py --if test_sample.csv --of output --gray graylist --black blacklist --deny denylist
SKIP: ['\xa8\xcf\xa5\xce\xaa\xcc', '\xa7\xeb\xb2\xbc\xa4\xe9\xb4\xc1', '\xb9q\xbcv\xa6W\xba\xd9']
input(8); gray(1); black(1); deny(1);
DENY: removing [Michael Jordan]
Monster2 #(2)
X-Ray #(3)
Monster1 #(2)
output.1.csv: Monster2
output.2.csv: X-Ray
output.3.csv: Monster1