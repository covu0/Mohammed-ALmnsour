# Mohammed-ALmnsour - Arduino Quiz Game 🎮

An interactive **Arduino quiz game** using **ESP32** and an **OLED screen**, built as part of the Tuwaiq Academy program.

This project helps users practice and test their knowledge of basic Arduino functions by answering code-based questions in real-time.


---

## 🔗 Live Simulation

Try the project live in your browser via Wokwi:  
👉 [Click here to open in Wokwi](https://wokwi.com/projects/435336865772819457)

---

## 🧱 Components Used

- ESP32 Dev Board  
- SSD1306 OLED Display (128x64, I2C)  
- Serial Monitor (for user input)

---

## 🚀 How It Works

1. The OLED shows an Arduino-related question with 3 options.  
2. The user enters their answer (1, 2, or 3) using the Serial Monitor.  
3. The game checks the answer:  
   - ✅ If correct → Score increases  
   - ❌ If wrong → Displays correct answer  
4. A new question is automatically generated.

---

## 📊 Features

- Randomly selected questions  
- Score tracking  
- Real-time feedback  
- OLED-based interface  
- Works perfectly in [Wokwi Simulator](https://wokwi.com)

---

## 🧠 Example Question

**Q:** `digitalWrite(13, HIGH)?`  
**1)** Turn ON LED  
**2)** Turn OFF LED  
**3)** Read pin

---

## 🔮 Future Ideas

- Timer for each question  
- Levels of difficulty  
- High score memory  
- Sound or light feedback using buzzer/LED

---

## 🛠 Setup Instructions

Use [Wokwi](https://wokwi.com) or upload to your own ESP32 board:

**OLED Wiring (I2C):**

| OLED Pin | ESP32 Pin |
|----------|------------|
| VCC      | 3.3V       |
| GND      | GND        |
| SDA      | GPIO 21    |
| SCL      | GPIO 22    |

---

## 📸 Screenshot

![OLED Preview](https://raw.githubusercontent.com/your-username/your-repo/main/screenshot.png)

---

## 👨‍💻 Author

**Mohammed Almansour**  
Tuwaiq Academy - Final Project
