# Suppose we have a time sensitive test. We can use freezegun, or a couple simpler approaches without having to install any
# additional libs. We can *patch* or *mock* the module that you are using for getting date/time/datetime values


# Approach 1
# Suppose you are using time.time() to get your time values and you need the returned value to be 60 seconds in future.
# We can patch the "time" lib's time() method to return a specific value.
def test_some_time_sensitive_thing(target):
    # arrange
    ...
    # act
    with patch.object(time, 'time', return_value=time.time()+60):
        target.test_some_time_sensitive_method()
    # assert
    ...


# Approach 2
# Suppose we have a method write_to_queue() in a module transport/telem.py, which adds {'time': datetime.utcnow().isoformat()} to the telem dict
# upon pushing the this dict onto a queue.
# We need to mock the datetime lib so that we can pin the return-value of utcnow() to a spcecific value.
# Note that we are not mocking the return value of isoformat(), though we could. But this is just a formatting function
# so it's cleaner to mock the utcnow() function.
@patch('transport.telem.datetime')
def test_write_to_queue(mock_dt, target: TelemWriter): # mock_dt must be first arg; target is fixture for our target object that has the write_to_queue() method.
    dt_now = datetime.utcnow()  # returns a datetime object
    mock_dt.utcnow = Mock(return_value=dt_now) # utcnow() will always return the datetime object "dt_now" when called
    for i in range(4):
        push = {'data': i, 'meta': {}}
        target._write_to_queue(push, HK_TELEM_TYPE)
    for i in range(4):
        pull = (HK_TELEM_TYPE, {'data': i, 'attempts': 1, 'meta': {'time': dt_now.isoformat()}}, False)
        result = target._telem_queue.get()
        assert result == pull


