
## Examples of one-line python executions on the command line

1) convert a dict to json
python3 -c 'import sys, json; d={"foo":"bar"}; print(json.dumps(d))'

2) similar thing, taking a json,
2) echo '{"foo", "bar"}' | python3 -c 'import sys, json; d=json.loads(sys.stdin.read()); print(json.dumps(d))'
