#!/usr/bin/env python
## EV3 Brick program 
from ev3dev.ev3 import *
import time
import paho.mqtt.client as mqtt

# This is the Subscriber
temp1=300
temp2=-300
color="undifined"
def on_connect(client, userdata, flags, rc):
  print("Connected with result code "+str(rc))
  client.subscribe("topic/test")

def on_message(client, userdata, msg):
  global temp1
  global temp2
  global color
  if msg.payload.isdigit():
    if (int(msg.payload)>-302 and int(msg.payload)<302):
        if (int(msg.payload)<temp1 or int(msg.payload)>temp2):
               
                move(msg.payload)
  else:
       print(str(msg.payload))
       color=str(msg.payload)
  




BASE_GEAR_RATIO = 12.0 / 36.0  # 12-tooth gear turn 36-tooth gear
LIFT_ARM_LIMIT = 25  # reflected light value (units: %)
BASE_EXTRA = 0.03  # to account for slop in gears (units: rotations)


def init():
    global button
    global sound
    global grab_motor
    global lift_motor
    global base_motor
    global base_limit_sensor
    global lift_limit_sensor

    button = Button()
    sound = Sound()

    # setup the motors and sensors

    grab_motor = MediumMotor(OUTPUT_A)
    lift_motor = LargeMotor(OUTPUT_B)
    base_motor = LargeMotor(OUTPUT_C)

    base_limit_sensor = TouchSensor(INPUT_1)
    lift_limit_sensor = ColorSensor(INPUT_3)

    # Set the lift arm to a known position using the color sensor in reflect mode
    # using polarity="inversed" so that lifting up is the positive direction

    lift_limit_sensor.mode = "COL-REFLECT"
    lift_motor.reset()
    lift_motor.stop_action = "hold"
    lift_motor.polarity = "inversed"
    lift_motor.run_forever(speed_sp=450)
    while lift_limit_sensor.value(0) < LIFT_ARM_LIMIT:
        pass
    lift_motor.stop()

    # Set the grabber to a known position by closing it all the way and then opening it

    grab_motor.reset()
    grab_motor.stop_action = "hold"
    grab_motor.run_forever(speed_sp=400)
    time.sleep(1)
    pos = int(grab_motor.count_per_rot * -0.25)  # 90 degrees
    grab_motor.run_to_rel_pos(speed_sp=600, position_sp=pos)

    # set the base rotation to a known position using the touch sensor as a limit switch

    base_motor.reset()
    base_motor.stop_action = "hold"
    base_motor.run_forever(speed_sp=450)
    while not base_limit_sensor.value(0):
        pass
    base_motor.stop()


    pos = int(base_motor.count_per_rot * (0.25 + BASE_EXTRA) / BASE_GEAR_RATIO)
    base_motor.position = pos
    print(pos)
    base_motor.run_to_abs_pos(speed_sp=450, position_sp=pos)#0 before now 90 =302
    while "holding" not in base_motor.state:
        pass
    sound.speak("Ready!")


def move(direction):
    global grab_motor
    global lift_motor
    global base_motor
    global lift_limit_sensor

    # rotate the base 90 degrees and wait for completion

   # pos = int(base_motor.count_per_rot * (0.25 + BASE_EXTRA) / BASE_GEAR_RATIO)
    base_motor.run_to_abs_pos(position_sp=direction)#send from cv
    while "holding" not in base_motor.state:
        pass

    # lower the lift arm and wait for completion

    pos = int(lift_motor.count_per_rot * 280.0 / 360.0)
    lift_motor.run_to_rel_pos(speed_sp=180, position_sp=-pos)
    while "holding" not in lift_motor.state:
        pass

    # grab an object

    grab_motor.run_forever(speed_sp=360)
    time.sleep(1)
    grab_motor.stop()

    # raise the lift to the limit

    lift_motor.run_forever(speed_sp=500)
    while lift_limit_sensor.value(0) < LIFT_ARM_LIMIT:
        pass
    lift_motor.stop()

    # rotate the base back to the center position and wait for completion

    if (color=="b\'RED\'" or color=="b\'ORANGE\'"):
        base_motor.run_to_abs_pos(position_sp=-350)
        while "holding" not in base_motor.state:
            pass
    else:
        base_motor.run_to_abs_pos(position_sp=350)
        while "holding" not in base_motor.state:
            pass
   # lower the lift arm and wait for completion

    pos = int(lift_motor.count_per_rot * 280.0 / 360.0)
    lift_motor.run_to_rel_pos(speed_sp=180, position_sp=-pos)
    while "holding" not in lift_motor.state:
        pass

    # release the object

    pos = int(grab_motor.count_per_rot * 0.25)
    grab_motor.run_to_rel_pos(speed_sp=360, position_sp=-pos)
    while "holding" not in grab_motor.state:
        pass

    # raise the lift arm to the limit

    lift_motor.run_forever(speed_sp=500)
    while lift_limit_sensor.value(0) < LIFT_ARM_LIMIT:
        pass
    lift_motor.stop()
    


def stop():
    global lift_limit_sensor
    global grab_motor
    global lift_motor
    global base_motor

    lift_limit_sensor.mode = "COL-AMBIENT"
    grab_motor.reset()
    lift_motor.reset()
    base_motor.reset()


if __name__ == "__main__":
    init()
    try:
        # main loop checking for button presses
        while "backspace" not in button.buttons_pressed:
            client = mqtt.Client()
            client.connect("192.168.137.3",1883,60)

            client.on_connect = on_connect
            client.on_message = on_message

            client.loop_forever()
            time.sleep(0.1)
    except KeyboardInterrupt:
        pass
    client.disconnect()
    stop()
    sound.speak("Goodbye!").wait()
