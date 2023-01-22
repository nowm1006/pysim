from block import Step, FirstOrderDelay, Add, Recorder, System


if __name__ == '__main__':
    system = System()

    s = Step()
    t = Step(ts=2, yi=0, yf=-1)
    u = Add(inputs=[s, t], name='s+t')
    f = FirstOrderDelay(input=u, T=0.1)
    r = Recorder([f, u])
    system.add(r)
    system.run(3, 0.01)

    r.plot()
