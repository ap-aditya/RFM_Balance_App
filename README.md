# 🌀 Two-Plane Rotor Balancing App

A simple and interactive **Streamlit** web application for calculating two-plane rotor balancing corrections using the **Response Function Matrix (RFM)**, also known as the **Influence Coefficient Method**.

This app takes vibration readings (Amplitude and Phase) from an initial run and two trial runs to calculate the required **correction masses** and their **angular placement** to balance a rotor.

---

## ✨ Features

* **Interactive UI** – Built with [Streamlit](https://streamlit.io) for easy data entry and visualization.
* **Two-Plane Balancing** – Solves the standard two-plane rotor balancing problem.
* **Multi-Sensor Support** – Works with one or more sensors (M×2 data tables).
* **Interactive Plots** – Uses Plotly for dynamic “what-if” analysis:

  * **Mass vs. Radius** – Shows required correction mass across possible radii.
  * **Residual vs. Angle** – Visualizes sensitivity to angular placement errors.
* **Flexible Options**

  * Specify custom final radii for correction masses.
  * Toggle the common “+180°” (opposite to rotation) convention for correction placement.

---

## ⚙️ Installation & Setup

This project is built in **Python** and requires a few scientific libraries.

### 1️⃣ Prerequisites

* Python **3.11+**

### 2️⃣ Installation

Ensure these three files are in the same directory:

```
app.py  
rfm_core.py  
plots.py
```

Then install dependencies:

```bash
uv add streamlit pandas numpy plotly
```

*(Alternatively, create a `pyproject.toml` with these four libraries and run:)*

```bash
uv sync
```

### 3️⃣ Run the Application

From the project directory, start the app with:

```bash
streamlit run app.py
```

Streamlit will launch a local web server and open the app in your browser.

---

## 🧮 How It Works – The RFM Method

The balancing logic assumes a **linear relationship** between unbalance (U) and vibration response (R), defined by the **Response Function Matrix (H):**

```
R = H × U
```

The app uses three measurement runs:

| Symbol | Description                                                    |
| :----: | -------------------------------------------------------------- |
| **R₀** | Initial (unbalanced) vibration                                 |
| **R₁** | Vibration after adding known trial unbalance **U₁** on Plane 1 |
| **R₂** | Vibration after adding known trial unbalance **U₂** on Plane 2 |

The influence coefficients are derived as:

```
H_col1 = (R₁ - R₀) / U₁  
H_col2 = (R₂ - R₀) / U₂
```

To cancel the initial vibration, the correction unbalance vector **Bₙ (bc)** must satisfy:

```
H × bc = -R₀
```

This system is solved using NumPy’s least-squares solver (`np.linalg.lstsq`), which handles both exact (2×2) and overdetermined (M×2) cases gracefully.

The resulting complex vector **bc** (in kg·m) is then converted to practical correction **mass (grams)** and **angle (degrees)** for each plane.

---

## 🗂️ File Structure

| File              | Description                                                                                     |
| ----------------- | ----------------------------------------------------------------------------------------------- |
| **`app.py`**      | The main Streamlit application – handles UI, sidebar, data entry tables, and plots.             |
| **`rfm_core.py`** | The computational “engine.” Implements `balance_rfm_core()` for all numerical operations.       |
| **`plots.py`**    | Helper module containing Plotly figure generators for “Mass vs Radius” and “Residual vs Angle.” |

---

## 📘 Notes

* Units of amplitude can be any consistent set (µm, mm/s, g, etc.).
* Radii should be specified in **meters**.
* Masses are specified in **grams**.
* Works with any number of sensors (rows = sensors, columns = [Amplitude, Phase°]).

---

## 🧩 Example Use Case

1. Run the machine unbalanced → record amplitude and phase at each sensor (**R₀**).
2. Add a known trial mass to Plane 1 → record new readings (**R₁**).
3. Add a known trial mass to Plane 2 → record new readings (**R₂**).
4. Enter all readings and trial details in the app.
5. Click **Compute Balance** to get correction mass and angle per plane.
6. (Optional) Explore “Mass vs Radius” and “Residual vs Angle” plots to fine-tune placements.

---

## 🧠 Credits

Developed using:

* [Streamlit](https://streamlit.io) – frontend framework
* [NumPy](https://numpy.org) – numerical computations
* [Plotly](https://plotly.com/python/) – interactive visualization
* [Pandas](https://pandas.pydata.org/) – tabular data handling

---

## 📜 License

This project is released under the **MIT License**.
Feel free to use, modify, and distribute with attribution.
