#!/bin/python

import time
import shlex
from subprocess import check_output
from functools import reduce
from statistics import stdev, mean

class Result:
    def __init__(self, name, time_avg, time_stdev, output):
        self.name = name
        self.time_avg = str(round(time_avg / 1000000, 3))
        self.time_stdev = str(round(time_stdev / 1000000, 3))
        self.output = str(output)

    def display(self, name_len, avg_len, stdev_len, output_len):
        name_str = self.name.ljust(name_len)
        avg_str = self.time_avg.rjust(avg_len)
        stdev_str = self.time_stdev.rjust(stdev_len)
        output_str = self.output.rjust(output_len)
        print(f"    {name_str} : {avg_str} ms +/- {stdev_str}  ->  {output_str} matches")

class Benchmark:
    def __init__(self, name, pattern, search_text, commands):
        self.name = name
        self.pattern = pattern
        self.search_text = search_text
        self.commands = commands

    def run(self):
        results = []
        
        for command in self.commands:
            cmd_args = command[1](self.pattern, self.search_text)
            cmd_args = shlex.split(cmd_args)

            # warmup to bring search text into page cache
            # see https://blog.burntsushi.net/ripgrep/#benchmark-runner
            for i in range(3):
                check_output(cmd_args)

            times = []
            outputs = [] # num lines in each output
            # get 10 sample times, return avg and standard deviation
            for i in range(10):
                start = time.monotonic_ns()
                output = check_output(cmd_args)
                end = time.monotonic_ns()

                times.append(end - start)
                outputs.append(len(output.decode().splitlines()))

            results.append(Result(command[0], mean(times), stdev(times), outputs[0]))

        return results

benchmarks = [
    Benchmark(
        "find 'on' in 3.7Ki of randomly generated text (dummy.txt)",
        "on", "bench_data/dummy.txt",
        [   ("bmh", lambda p,t: f"./target/bmh {p} {t}"),
            ("grep", lambda p,t: f"grep -ob {p} {t}"),
            ("fixed grep", lambda p,t: f"grep -F -ob {p} {t}"),
            ("ripgrep", lambda p,t: f"rg -ob {p} {t}"),
            ("fixed ripgrep", lambda p,t: f"rg -F -ob {p} {t}"),
        ]
    )
]

print("running benchmarks\n")

for benchmark in benchmarks:
    print(benchmark.name)
    results = [result for result in benchmark.run()]
    
    max_name_len = reduce(lambda l, r: max(l, len(r.name)), results, 0)
    max_avg_len = reduce(lambda l, r: max(l, len(r.time_avg)), results, 0)
    max_stdev_len = reduce(lambda l, r: max(l, len(r.time_stdev)), results, 0)
    max_output_len = reduce(lambda l, r: max(l, len(r.output)), results, 0)

    for result in results:
        result.display(max_name_len, max_avg_len, max_stdev_len, max_output_len)

