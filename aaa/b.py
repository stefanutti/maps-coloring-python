import os.path, sys
sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), os.pardir))

from aaa.a import echo_function

echo_function("aaaa")
