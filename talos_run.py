import sys

from arc.core.behave import runner
from arc.core.behave.runner import make_behave_argv

if sys.argv[1:]:
    runner.main(' '.join(sys.argv[1:]))

else:
    runner.main(make_behave_argv(
        conf_properties='local',
        tags=['san_web']
    ))
