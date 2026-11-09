# Gesture Access Control with PYNQ-Z2

**Members:**
- Mikail Vidal
- Carlos Heras Pardo

## The idea

Controlling a set of door locks with hand gestures instead of numbers entered on a keypad. The user shows a lock number and then a 4-digit code with their fingers to the camera, and the PYNQ-Z2 recognizes each gesture, checks the code and unlocks the chosen lock if the code is correct. The board gives feedback on the OLED screen and the buzzer, and every lock can be monitored and controlled remotely over MQTT.

The locks are **simulated**. Instead of wiring physical hardware, several virtual locks (for example `front_door`, `server_room`, `lab` and `storage`) run as independent MQTT clients, each with its own state, access code and event log. The board acts as the gesture-driven controller, and all communication with the locks goes through an MQTT broker.

## Hardware used

Only two peripherals are required on top of the board and the camera:

- **OLED screen:** shows instructions, the selected lock, entered digits (masked) and the result of each attempt.
- **Buzzer:** audio feedback for accepted digits, unlock, wrong codes and the lockout alarm.

The camera is the input device, and the onboard switches and buttons are used for modes. No other sensors or actuators are needed.

## How it works

1. **Idle:** the OLED shows a "show your hand" prompt. The system wakes up when the camera detects a hand in the frame.
2. **Select lock:** the user shows the number (1 to 5) of the lock they want. The OLED confirms the lock name.
3. **Input:** the camera reads finger counts (0 to 5). A digit is accepted once it is held stable for about one second, with a short beep and a masked digit on the OLED.
4. **Check:** the controller publishes an unlock request for the selected lock over MQTT. A correct code unlocks the simulated lock for 5 seconds and then relocks it. 3x wrong code on a lock triggers a 60-second lockout for that lock, with the buzzer alarm and a phone notification.
5. **Overrides:** remote unlock, lock and lockdown of any lock over MQTT, and an admin mode for changing a lock's code.

## Simulated locks and MQTT

Each simulated lock is a small Python client with the states `locked`, `unlocked` and `lockdown`. They run in the same notebook (or as separate processes) and are indistinguishable from real devices as far as the broker is concerned, so real locks could replace them later without changing the controller.

| Topic                                  | Direction                    | Content                                                         |
| -------------------------------------- | ---------------------------- | --------------------------------------------------------------- |
| `gestureaccess/locks/<lock_id>/cmd`    | controller / phone → lock    | `unlock`, `lock`, `lockdown`, `set_code`                        |
| `gestureaccess/locks/<lock_id>/state`  | lock → everyone (retained)   | current state, last change and failed attempt count             |
| `gestureaccess/locks/<lock_id>/event`  | lock → everyone              | access granted, access denied, lockout started, remote override |
| `gestureaccess/controller/status`      | controller → everyone        | selected lock, recognition result, gesture confidence           |
| `gestureaccess/alerts`                 | controller / locks → phone   | brute-force and lockout notifications                           |

The phone (an MQTT dashboard app) subscribes to all lock states and can send commands to any individual lock or to all of them.

## How the project meets the requirements

| Requirement                                              | How it is covered                                                                                                                                                                                                                                                 |
| -------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| a) Two digital sensors/actuators                         | __**Digital:**__ OLED (instructions and status messages), buzzer (feedback and alarm). The camera is the main input device. The locks are simulated actuators managed through MQTT.                                                                              |
| b) Switches                                              | SW0 enables admin mode for setting a new code, SW1 activates lockdown on all locks.                                                                                                                                                                              |
| c) Libraries, OpenCV mandatory                           | `OpenCV` for hand segmentation and finger counting, `numpy` and `scikit-learn` for the classifier, `paho-mqtt` for the controller and the simulated locks, `matplotlib` for results.                                                                              |
| d) Central notebook                                      | One Jupyter notebook with setup, OLED and buzzer functions, gesture detection, simulated locks, model evaluation, MQTT client, main loop and analysis.                                                                                                           |
| e) Data analysis and modelling                           | Two gesture recognizers compared (classic OpenCV vs. a trained classifier), confusion matrices, recognition accuracy as a function of image brightness measured from the camera frames, and analysis of the access logs of all locks (success rate, unlock time, brute-force detection per lock). |
| f) Remote interaction via MQTT                           | Multiple simulated locks are managed entirely through MQTT. Locks publish state and events and subscribe to commands (unlock, lock, lockdown, set code), and the controller publishes recognition status and alerts.                                              |
| Documentation                                            | Report with objectives, methodology, analysis, critical discussion and references.                                                                                                                                                                                |
| Demonstrable                                             | Live demo plus a backup video.                                                                                                                                                                                                                                    |

## Demo plan

1. Select the front door, enter the correct code and watch it unlock in the MQTT dashboard, then relock.
2. Select a different lock (for example the server room) and unlock it with its own code, showing that the locks are independent.
3. Enter a wrong code three times on one lock, which triggers the buzzer alarm, a lockout on that lock only and a phone notification.
4. Unlock a lock remotely from the phone.
5. Flip SW1 to put every lock into lockdown and show all states change over MQTT.
6. Show the OLED prompts throughout and the access log analysis from the notebook.

## Getting started

### 1. Development environment

The project uses [uv](https://docs.astral.sh/uv/) for dependencies. The notebook is paired with a plain-text script through jupytext (`jupytext.toml`), so only `gesture_access.py` is committed to git and `*.ipynb` is ignored.

```
uv sync
uv run jupyter lab
```

Always open and save the notebook through this Jupyter instance. Jupytext then keeps `gesture_access.ipynb` and `gesture_access.py` in sync on every save. If Jupyter complains that one file is more recent than the other, sync them with `uv run jupytext --sync gesture_access.ipynb`. Commit the `.py` file, never the `.ipynb`.

> `pyproject.toml` pins a recent Python for the laptop environment. The PYNQ-Z2 image ships its own, older Python, so check that the code you write runs on both before relying on newer language features.

### 2. MQTT broker

Install and start Mosquitto on your laptop (or on the board):

```
brew install mosquitto
mosquitto -c /opt/homebrew/etc/mosquitto/mosquitto.conf
```

Mosquitto 2.x only accepts local connections by default. For the board and the phone to connect over the lab network, add this to the config file:

```
listener 1883
allow_anonymous true
```

Check it works with two terminals:

```
mosquitto_sub -t "gestureaccess/#" -v
mosquitto_pub -t "gestureaccess/test" -m "hello"
```

Then install an MQTT dashboard app on your phone, point it at the broker's IP address and subscribe to `gestureaccess/#`.

### 3. Suggested order of work

Each step produces something that runs, so you can test it before moving on.

1. **Hardware check on the PYNQ-Z2:** boot the board, open its Jupyter, grab a camera frame with OpenCV, show text on the OLED and make the buzzer beep. Do this first, because hardware problems take the longest to fix.
2. **Simulated locks (laptop only):** write a `Lock` class with the states `locked`, `unlocked` and `lockdown`, a code, a failed-attempt counter and an event log. Connect it to the topics in [Simulated locks and MQTT](#simulated-locks-and-mqtt) and create 3 to 4 instances. Test them from the phone dashboard.
3. **Gesture recognition (laptop first):** count fingers (0 to 5) with OpenCV using skin segmentation, contour, convex hull and convexity defects. Add the "held stable for about one second" debounce, and save labelled images as you go for the classifier and the analysis.
4. **Controller state machine:** idle → select lock → enter 4 digits → check → result. Gestures drive MQTT commands to the locks. Use a mocked OLED and buzzer on the laptop, then run it on the board.
5. **Extras:** SW0 admin mode, SW1 lockdown for all locks, lockout logic, phone alerts and remote unlock.
6. **Analysis and modelling:** train the `scikit-learn` classifier, compare it with the OpenCV method, plot accuracy against image brightness and analyse the lock logs.
7. **Report and demo:** write the report as you go, and record the backup video once the demo works.

### 4. Splitting the work

- **Recognition:** gesture detection, dataset, classifier and model evaluation (steps 3 and 6).
- **System:** board setup, OLED, buzzer, MQTT, simulated locks and the controller (steps 1, 2, 4 and 5).

Meet at step 4, once both sides work separately.
