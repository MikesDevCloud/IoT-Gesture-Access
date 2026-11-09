# ---
# jupyter:
#   jupytext:
#     text_representation:
#       extension: .py
#       format_name: percent
#       format_version: '1.3'
#       jupytext_version: 1.19.6
#   kernelspec:
#     display_name: Python 3
#     language: python
#     name: python3
# ---

# %% [markdown]
# # IoT Project: Gesture Access Control with PYNQ-Z2

# %%
import uuid

# Test paho-mqtt
import paho.mqtt.client as mqtt
from paho.mqtt.enums import CallbackAPIVersion

def on_connect(client, userdata, flags, rc, properties=None):
    print("Connected with result code "+str(rc))
    client.subscribe("gestureaccess/access")

def on_message(client, userdata, msg):
    print(msg.topic, " ", str(msg.payload.decode("utf-8")))

client = mqtt.Client(CallbackAPIVersion.VERSION2)
client.on_connect = on_connect
client.on_message = on_message

client.connect("localhost", 1883, 60)
client.loop_forever()

# %%
from pydantic import BaseModel
from typing import Annotated
from annotated_types import Gt, Lt

class Lock(BaseModel):
    """ Lock class to manage the state of the lock/lockdown status as well as counting failed attempts.

    @param id: unique identifier for each lock
    @param locked: boolean indicating if the lock is currently locked or unlocked
    @param lockdown: boolean indicating if the lock is in lockdown mode, blocking any access attempts.
    @param failed_attempts: integer counting the number of failed access attempts
    """
    id: str = str(uuid.uuid4())
    code: Annotated[int, Gt(0), Lt(10)]
    locked: bool = True
    lockdown: bool = False
    failed_attempts: int = 0

    def toggle_lock(self):
        """ Lock the lock """
        self.locked = not self.locked
        print("Lock is now locked.")

    def toggle_lockdown(self):
        """ Enter lockdown mode, blocking any access attempts """
        self.lockdown = not self.lockdown
        print("Lock is now in lockdown mode.")




