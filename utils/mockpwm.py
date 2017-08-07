class MockPWM(object):
    class PCA9685(object):
        def __init__(self, address, verbose=True):
            print 'PWM: Using MockPWM'
            if not address:
                print 'PWM: no address specified'
            else:
                self.address = address

            self.verbose = verbose
            if self.verbose:
                print 'PMW: [initiated] ' + repr(address)

        def set_pwm(self, channel, start, end):
            if self.verbose:
                print 'PMW: [channel ' + repr(channel) + '] ' + repr(start) + ':' + repr(end)
