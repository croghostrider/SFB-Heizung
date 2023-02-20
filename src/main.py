import time

from pyModbusTCP.client import ModbusClient
from simple_pid import PID

host = "192.168.10.220"
regTemperature = 0
kp = 10
ki = 20
kd = 0.05
shouldTemperature = 30

client = ModbusClient(host=host, auto_open=True, auto_close=True)

pid = PID(kp, ki, kd, setpoint=shouldTemperature, output_limits=(0, 32767))

# main read loop

while True:
    if regs := client.read_holding_registers(regTemperature, 1):
        temperature = regs[0] / 10
        print(f"current temperature is: {temperature} °C")
        control = int(pid(temperature))
        client.write_single_register(32000, control)
        print(control)
    else:
        print("unable to read registers")

    # sleep 2s before next polling
    time.sleep(2)
