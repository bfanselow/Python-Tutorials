## Running python instructions from the command-line

### Examples
**1) Convert a dict to json and print**
```
$ python3 -c 'import sys, json; d={"foo":"bar"}; print(json.dumps(d))'
```

**2) Similar thing, taking a json string from STDIN, converting to dict and then back to json output**
```
$ echo '{"foo", "bar"}' | python3 -c 'import sys, json; d=json.loads(sys.stdin.read()); print(json.dumps(d))'
```

**3) Implement unix "cut" functionality**
```
$ cat input.txt
1)This is the first line
2)I am in the second line
3)Third and last line

$ python3 -c "import sys; [sys.stdout.write(' '.join(line.split(' ')[2:])) for line in sys.stdin]" < input.txt
the first line
in the second line
last line
```
