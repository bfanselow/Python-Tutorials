## Running python instructions from the command-line

### Examples
1) convert a dict to json and printing
```
python3 -c 'import sys, json; d={"foo":"bar"}; print(json.dumps(d))'
```

2) similar thing, taking a json, converting to dict and then back to json output
```
echo '{"foo", "bar"}' | python3 -c 'import sys, json; d=json.loads(sys.stdin.read()); print(json.dumps(d))'
```
