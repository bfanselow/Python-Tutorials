# Suppose we have a time sensitive test. We can use freezegun, or a simpler approach without having to install any
# additional libs is just to *patch* the module that you are using for time.
# For example suppose you are using time.time() to your time values and you need the time returned to be 60 seconds in future


def test_some_time_sensitive_thing(target):
    # arrange

    # act
    with patch.object(time, 'time', return_value=time.time()+60):
        target.test_some_time_sensitive_method()
    # assert

