# this is used to generate assert param for output, please check manually to ensure the corectness!
from cp2kdata.output import Cp2kOutput
import json
answer = {}
tmp = Cp2kOutput('./output')
answer["run_type"] = tmp.get_run_type()
with open("answer.json", "w") as fp:
    json.dump(answer, fp)
