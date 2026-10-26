# Gesture Access Control with PYNQ-Z2

**Members:**
- Mikail Vidal
- Carlos Heras Pardo

## The idea

Simulating a door lock that opens with a sequence of hand gestures instead of entered numbers on a keypad. User shows a 4-digit code with their fingers to the camera, and the PYNQ-Z2 recognizes each gesture, checks the code and opens the lock if the correct code has been entered. The system wakes up when someone approaches, reacts to failed attempts and can be monitored and controlled remotely from a phone.

## How it works

1. **Idle:** the ultrasonic sensor waits for someone to come close, about 1m.
2. **Input:** the camera reads finger counts (0 to 5). A digit is accepted once it is held stable for about one second.
3. **Check:** a correct code opens the servo lock for 5 seconds. 3x wrong code entered triggers a 60-second lockout with an alarm (buzzer) and a phone notification.
4. **Overrides:** remote unlock via MQTT, an automatic unlock if the temperature rises above a safety threshold (fire scenario), and an admin mode for changing the code.

## How the project meets the requirements

| Requirement                                              | How it is covered                                                                                                                                                                                                                              |
| -------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| a) At least two digital and two analog sensors/actuators | __**Digital:**__ ultrasonic (presence), servo (lock), buzzer and RGB LED strip (feedback), OLED (user istructions and status messages). __**Analog:**__ light sensor (low-light handling), temperature sensor (fire-safety override).                                                       |
| b) Switches                                              | SW0 enables admin mode for setting a new code, SW1 activates lockdown.                                                                                                                                                                         |
| c) Libraries, OpenCV mandatory                           | `OpenCV` for hand segmentation and finger counting, `numpy` and `scikit-learn` for the classifier, `matplotlib` for results.                                                                                                                           |
| d) Central notebook                                      | One Jupyter notebook with setup, hardware functions, gesture detection, model evaluation, MQTT client, main loop and analysis.                                                                                                                         |
| e) Data analysis and modelling                           | Two gesture recognizers compared (classic OpenCV vs. a trained classifier), confusion matrices, recognition accuracy as a function of measured light level, and analysis of the access log (success rate, unlock time, brute-force detection). |
| f) Remote interaction via MQTT                           | The board publishes status, events and sensor values, and subscribes to commands (unlock, lock, lockdown).                                                                                  |
| Documentation                                            | Report with objectives, methodology, analysis, critical discussion and references.                                                                                                                                                             |
| Demonstrable                                             | Live demo plus a backup video.                                                                                                                                                                                                                 |

## Demo plan

1. Enter the correct code and the door opens.
2. Enter a wrong code three times, which triggers the alarm and a phone notification.
3. Unlock remotely from the phone.
4. Cover the light sensor to show low-light mode.
5. Warm the temperature sensor to trigger the safety unlock.