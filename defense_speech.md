# Graduation Defense Script (20 Minutes)

**Topic:** Numerical Instabilities in AI Compilers: Operator-Level Input Generation and Evaluation Using FPGen
**Speaker:** Yushan Xie

> **Note to Speaker**: This script is designed for a **20-minute** presentation.
> *   **Bold text** indicates emphasizing key points.
> *   *(Italic text in parentheses)* indicates actions (e.g., changing slides, pointing).

---

## **Part 1: Introduction (0-3 mins)**

### **Slide 1: Title Slide**
**(Action: Stand confidently, make eye contact)**

"Good afternoon, Professors. My name is Yushan Xie.

Today, I am gonna to present my graduation project: **'Numerical Instabilities in AI Compilers: Operator-Level Input Generation and Evaluation Using FPGen'**.

Before I begin, I would like to include a brief personal note. I had originally planned to complete and defend this project next semester. However, due to sudden changes in the school's filing policy, I had to conclude my research and prepare this defense within a very compressed timeline. As a result, the completeness of the project may not fully reflect my original vision, and I sincerely appreciate your understanding and consideration regarding this constraint.

This project addresses a critical, often invisible threat in modern Artificial Intelligence systems: the reliability of floating-point arithmetic in Deep Learning compilers."

### **Slide 2: The Hidden Danger in AI**
**(Action: Switch to Slide 2)**

"As we know, Deep Learning is being deployed everywhere—from autonomous driving vehicles to medical diagnostic systems. We trust these models to make life-critical decisions.

However, beneath the high accuracy metrics lies a hidden danger. Neural networks rely heavily on **floating-point arithmetic** (IEEE 754 standard).

Unlike logical bugs—which usually crash a program immediately—**numerical bugs are often silent**.
*   A tiny precision error in one layer can accumulate.
*   An 'Infinity' value can propagate unnoticed.
*   This leads to catastrophic decision failures without any warning errors."

### **Slide 3: What are Numerical Instabilities?**
**(Action: Switch to Slide 3, point to the diagram)**

"So, what exactly are we looking for?

In this project, I target specific numerical anomalies:
1.  **NaN (Not a Number)**: The most destructive error. If one neuron outputs NaN, it spreads like a virus, corruption the entire network output.
2.  **Infinity (Inf)**: Caused by overflow, destroying gradient information.
3.  **Underflow & Precision Loss**: Where small numbers round down to zero, erasing subtle features.

These errors are triggered by **mathematical edge cases** in operators—like dividing by a near-zero number, or calculating the exponential of a large input."

### **Slide 4: Why Existing Testing Fails**
**(Action: Switch to Slide 4)**

"You might ask: *'Can't we just test for this?'*
Unfortunately, existing methods fail in this domain:

1.  **Manual Testing** is too slow and biased by human intuition. We can't manually write test cases for every possbile floating-point value.
2.  **Random Fuzzing** is inefficient. The space of 64-bit floating-point numbers is vast. Trying to hit a specific 'crash value' by random guessing is like looking for a needle in a haystack.

Therefore, we need a **systematic, mathematical approach** to actively search for these traps. That is what my system provides."

---

## **Part 2: Methodology (3-10 mins)**

### **Slide 5: System Overview (The Pipeline)**
**(Action: Switch to Slide 5, Gesture to the whole flow)**

"To solve this, I designed and implemented an **end-to-end automated testing pipeline**.

As shown in this diagram, the system consists of four key stages:
1.  **Symbolic Input Generation**: Creating the 'ammunition' using FPGen and KLEE.
2.  **Model Composition**: Automatically building the test targets.
3.  **Cross-Framework Evaluation**: Running differential tests between PyTorch and ONNX.
4.  **Analysis**: Visualizing the results.

The entire system is automated via Docker and Python scripts. Let me walk you through the core technologies."

### **Slide 6: Method 1 - Symbolic Input Generation (The Core)**
**(Action: Switch to Slide 6. This is the most technical part, slow down slightly)**

"The core innovation of my project is using **Symbolic Execution**.

Instead of guessing random inputs, I utilize **KLEE**, a symbolic execution engine.
*   KLEE treats input variables not as concrete numbers (like 5 or 3.14), but as **symbols** subject to mathematical constraints.
*   It explores the execution paths of C implementations of math operators.
*   When it finds a path that leads to a potential error (like a domain error in log), it queries a **Constraint Solver (Z3)**.
*   It asks: *'What input value would cause this path to be taken?'*

To enable this, I use a specialized environment called **FPGen**, which allows KLEE to handle floating-point constraints effectively. This gives us mathematically guaranteed 'trigger inputs' for potential bugs."

### **Slide 7: Method 2 - Operator Composition**
**(Action: Switch to Slide 7)**

"Testing single operators isn't enough. In real neural networks, numerical errors often accumulate over a sequence of operations.

My system automatically generates **Composed Models**.
For example, it chains `Input -> Add -> Exp -> Softmax`.
*   Maybe `Exp` alone is stable.
*   But `Add` pushes the value into a dangerous range for `Exp`.

Each generated model is exported to two industry-standard formats: **TorchScript** (for PyTorch) and **ONNX** (for ONNX Runtime), ensuring we compare apples to apples."

### **Slide 8: Method 3 - Differential Testing (The Oracle)**
**(Action: Switch to Slide 8)**

"A major challenge in compiler testing is: *'How do we know the correct answer?'* We don't have a ground truth.

I solve this using **Differential Testing**.
I feed the *same* symbolic input into *both* frameworks: **PyTorch** and **ONNX Runtime**.
I define a bug if:
1.  **Instability**: One framework crashes (outputs NaN) while the other doesn't.
2.  **Inconsistency**: Both return numbers, but the difference exceeds a safety threshold (measured by ULP - Unit in the Last Place).

This 'Cross-Reference' validation helps us identify inconsistencies caused by aggressive compiler optimizations."

---

## **Part 3: Implementation & Results (10-15 mins)**

### **Slide 9: Implementation Details**
**(Action: Switch to Slide 9)**

"I implemented this system integrating several technologies:
*   **Docker Container**: To encapsulate the complex KLEE/FPGen environment, solving dependency hell.
*   **Python Automation**: A centralized script `run_pipeline.sh` that orchestrates the entire workflow.
*   **Deep Learning Stack**: Integrating PyTorch 2.x and ONNX Runtime.

This engineering effort makes the tool reproducible and easy to use—you just run one command."

### **Slide 10: Experimental Setup**
**(Action: Switch to Slide 10)**

"For my experiments, I generated hundreds of models covering 9 common operators (like exp, log, sigmoid, softmax).
I utilized pre-computed symbolic inputs from KLEE to simulate a rigorous testing environment.
The experiments were conducted on a standard CPU inference setup to verify stability."

### **Slide 11: Result Analysis I (Instability Distribution)**
**(Action: Switch to Slide 11, Point to the chart)**

"Here are the macro results.
This bar chart shows the count of **NaN** and **Infinity** triggers across different model types.

**Key Finding**: **Transcendental functions**—specifically `exp`, `log`, and `pow`—are the most fragile.
We also observed that combinations involving `division` and `softmax` (which involves division) showed high instability rates. This proves that our operator chaining strategy successfully identifying accumulated errors."

### **Slide 12: Result Analysis II (Framework Comparison)**
**(Action: Switch to Slide 12, Point to the heatmap)**

"This heatmap reveals the robustness difference between PyTorch and ONNX.
*   Darker cells indicate more frequent failures.
*   We found cases where **ONNX Runtime** was more aggressive in optimization, leading to NaNs where PyTorch remained stable.
*   Conversely, PyTorch showed instabilities in certain `pow` operations that ONNX handled correctly.

This confirms that different compilers have different 'safety profiles', information that is vital for developers choosing a deployment runtime."

---

## **Part 4: Live Demo (15-18 mins)**

### **Slide 13: Live Demo Strategy**
**(Action: Pause. Look at the audience.)**
"Talking about code is abstract. I would now like to demonstrate the system in action.

**A quick note on the data source**: For this live demonstration, I am using **pre-computed symbolic inputs**.
*   Running the full `FPGen` process involves solving complex mathematical constraints with KLEE, which typically takes hours to achieve full coverage. It is not feasible to run live on stage.
*   Furthermore, since the mathematical properties of operators (like `exp` or `log`) do not change, these generated 'attack inputs' are reusable. We only need to re-run generation if we introduce new, unsupported operators.
*   However, the rest of the pipeline—**Model Generation, Execution, and Evaluation**—is running **live right now**."

**(Action: Exit Slides (Alt-Tab). Switch to the Browser showing the Dashboard.)**

"Here is the visualization dashboard. The interface is divided into **four main sections** to help developers navigate the data:

1.  **Summary Cards (Top)**: These provide a high-level health check. You can see the total number of models tested (e.g., 300+) and, crucially, the **Total NaN Count** across all tests. This gives an immediate sense of the system's stability.

2.  **Charts Panel (Middle)**:
    *   **To the left**, we have the **Instability Bar Chart**. It breaks down errors by type: Purple for NaNs, Red for Infinities. This helps us see *what kind* of errors are prevalent.
    *   **To the right**, the **Framework Comparison**. This visually contrasts PyTorch vs. ONNX failures, highlighting which backend is more robust.

3.  **Top Offenders List**: On the bottom left, we list the **'Top Models by NaN Count'**. This is a prioritized 'Fix-It' list for developers, showing which operator combinations are most broken.

4.  **Detail Table with Search (Bottom)**: This is the interactive investigation area.
    *   I can filter by Run ID or Dataset.
    *   Let me search for **`model_exp`**...
    *   *(Action: Type 'model_exp' in the search box)*
    *   Now I can see specific test cases where `exp` caused a crash in PyTorch but not in ONNX. This granular view is essential for debugging."

**(Action: Switch back to Slides)**

---

## **Part 5: Conclusion (18-20 mins)**

### **Slide 14: Limitations**
**(Action: Switch to Slide 14)**

"Of course, there are limitations to this work.
1.  **Cost**: Symbolic execution is computationally expensive. Generating constraint solutions for complex functions takes time.
2.  **Scope**: Currently, I focus on small operator chains. Testing full-scale networks (like ResNet) with this method would require significant optimization to handle the state space explosion."

### **Slide 15: Conclusion & Future Work**
**(Action: Switch to Slide 15)**

"In conclusion, my project bridges the gap between **Formal Methods** and **AI Engineering**.
I have built an automated tool that successfully detects hidden numerical bugs that traditional testing misses.

For future work, I plan to:
1.  Parallelize the KLEE execution to improve speed.
2.  Extend support to hardware-specific compilers like **TVM** and **TensorRT**."

### **Slide 16: Q&A**
**(Action: Switch to Slide 16)**

"Thank you for your attention. I am now happy to answer any questions you may have."
