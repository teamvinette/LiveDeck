# LiveDeck — *Ableton Remote Track Control*

---

## 🎧 What is LiveDeck?

**LiveDeck** is a simple but powerful middleware that allows you to control individual tracks in your Ableton Live session directly from your Streamdeck® using Bitfocus Companion and OSC.

When I was looking for a way to mute/unmute specific tracks in Ableton using my Streamdeck, I couldn't find any solution — so I built my own.  
I’m a 22 y/o producer, having fun with scripting and AI coding. Since this tool has been super helpful for my own sessions, I wanted to share it with anyone who might need something similar.

---

## 🚀 Features

- Mute / Unmute any track in Ableton Live
- Solo / Unsolo any track
- Full synchronization between Ableton and Streamdeck via Companion
- Reliable OSC messaging queue
- Works locally, fast, and completely free

---

## ⚙️ How it works

The system is based on:

- **AbletonOSC** — allows OSC control of Ableton Live
- **Python middleware** — listens to OSC messages and controls Ableton tracks
- **Bitfocus Companion** — sends OSC messages triggered by your Streamdeck

You configure Companion to send simple OSC messages like:

```
/custom/mute_TrackName
/custom/unmute_TrackName
/custom/solo_TrackName
/custom/unsolo_TrackName
```

The middleware extracts the track name, queries Ableton for all track names via AbletonOSC, finds the correct track index, and executes the requested action.

All messages are handled via a queue to ensure that even rapid button presses won’t lose commands.

---

## 🔧 Setup Guide

### 1️⃣ Install AbletonOSC

Follow the official instructions here:  
👉 https://github.com/ideoforms/AbletonOSC?tab=readme-ov-file#installation

---

### 2️⃣ Install Bitfocus Companion

👉 https://bitfocus.io/companion

> _(Optional: You can download my Companion configuration here: [⬇ Download Companion Config](LiveDeck.companionconfig)
The provided Companion configuration uses purely local connections (127.0.0.1). No credentials or external endpoints are included.
---

### 3️⃣ Configure Companion

#### 3.1 Create a new OSC connection:

- Go to **Connections**
- Add new connection:
    - Name: `PythonOSC` (or anything you like)
    - Target Hostname: `127.0.0.1`
    - Target Port: `10999`  
      *(This is where LiveDeck listens for commands)*
    - Protocol: UDP
    - Listen for Feedback: OFF

#### 3.2 Create your first button:

- Go to **Buttons** and create a new button.
- Add first press action:
    - **PythonOSC > Send message without arguments**
    - OSC Path: `/custom/mute_MIX BUS`  
      *(Simply use `/custom/`, then the action, then `_TrackName`)*

- Add a second step for toggling back:
    - **PythonOSC > Send message without arguments**
    - OSC Path: `/custom/unmute_MIX BUS`

You can repeat this for any track name.

---

### 4️⃣ Install *Bitfocus Companion Plugin* in Streamdeck software

> _(You might need to restart Streamdeck to see Companion as an option.)_

---

### 5️⃣ Start the LiveDeck Python script

In terminal:

```bash
python3 /path/to/LiveDeck.py
```

> _(You can also start this via a Companion button — see below)_

---

### ✅ Done!

Your first button should now work. You can add as many buttons as you want.

---

### 🔴 Shutdown button (recommended)

You can add a shutdown button to safely stop the script:

- Create a new Companion button
- OSC Path: `/shutdown`

The Python script listens for this message and shuts down cleanly.

---

### (Optional) Create a Startup Button in Companion

- **Action:** Internal > System: Run shell path (local)
- **Path:** `/path/to/start_livedeck.sh`  
  _(You'll find an example `.sh` startup script in this repository) [⬇ Download .sh startup script](start_livedeck.sh)_
- **Timeout:** `5000ms`
- **Target Variable:** none

---

## ⚠️ Notes

- The script is **case-sensitive** — track names must match exactly.
- Avoid renaming tracks during active sessions, as OSC messages rely on correct names.
- All OSC messages are queued to ensure reliable processing even under heavy load.

---

## 🎯 Roadmap

- Make the installation progress way easier - any ideas?

---

## 💡 About the author

> I’m a 22-year-old music producer who is trying to create ways, when there havn't been any.
> Feel free to open issues or contribute — pull requests are always welcome!

---

## 📄 License

> This project is licensed under the **Creative Commons Attribution-NonCommercial 4.0 International (CC BY-NC 4.0)** license.  
>   
> You are free to use, share, and modify the code for non-commercial purposes.  
> Full license text: https://creativecommons.org/licenses/by-nc/4.0/legalcode

---

