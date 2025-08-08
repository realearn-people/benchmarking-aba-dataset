# benchmarking-aba-dataset
This repository provides datasets, prompt configurations, and evaluation scripts for benchmarking **Large Language Models (LLMs)** on structured argument mining. The task focuses on classifying **topics and sentiments** in hotel reviews based on the **Assumption-Based Argumentation (ABA)** framework.

We explore how different LLMs (e.g., GPT-4o, Gemini 2.5 Pro, LLaMA 3, Mistral) perform under varied prompt structures and decoding configurations.

---

## Repository Structure

```
benchmarking-aba-dataset/
├── Dataset 1/
│   ├── ABA Dataset - Label Topic (For Tasks 1 & 2).xlsx
│   ├── Cosine.ipynb
│   ├── Gpt_dataset1_shot_running.ipynb
│   ├── Prompt Version 1/
│   │   ├── GPT_7_shot.ipynb
│   │   ├── Result-3-shot/
│   │   ├── Result-4-shot/
│   │   ├── Result-5-shot/
│   │   ├── Result-6-shot/
│   │   └── Result-7-shot/
│   └── Prompt Version 2/
│       ├── Sentiment.ipynb
│       └── Topic.ipynb
│
├── Dataset 2/
│   ├── Gemini 2.5 Pro/
│   ├── Gpt-4o/
│   ├── Llama3/
│   └── Mistral/
│
├── Remove Disagreement Version(2).xlsx
└── README.md
```

---

## Project Objective

We investigated the use of **Large Language Models (LLMs)** to automate a key step in ABA-based opinion mining: the classification of **topics** and **sentiments** in hotel reviews.

Building on the framework proposed by Racharak et al.~\cite{racharak2023}, this project focuses on **Task 1** and explores how prompt engineering enables LLMs—such as **GPT-4o**, **Gemini 2.5 Pro**, **LLaMA 3**, and **Mistral**—to perform structured classification tasks effectively.

---

## Tasks & Evaluation

We evaluate model performance on three dimensions:

| Task              | Script                | Description                                  |
|-------------------|------------------------|----------------------------------------------|
| **Topic Match**    | `Topic.ipynb`          | Checks if predicted topic matches the label  |
| **Sentiment Match**| `Sentiment.ipynb`      | Compares predicted sentiment polarity        |
| **Span Similarity**| `Cosine.ipynb`         | Measures cosine similarity of extracted text |

---

## ⚙️ Prompt Versions & Configurations

### Dataset 1

- **Prompt Version 1**:
  - Few-shot configurations: `3-shot` to `7-shot`
  - Decoding settings:
    - `Temperature = 1`, `Top-p = 1`
    - `Temperature = 0`, `Top-p = 0.05`

- **Prompt Version 2**:
  - Used only `Temperature = 0`, `Top-p = 0.05`

### Dataset 2

Evaluated on four LLMs:

- **GPT-4o**
- **Gemini 2.5 Pro**
- **LLaMA 3**
- **Mistral**

Each folder contains:

- Few-shot execution scripts
- Evaluation results
- Original annotated dataset

---

## How to Use

### 1. **Set Up Your Environment**
- Recommended: **Python 3.8+**

You can run the notebooks using either **Jupyter Notebook** or **VSCode**.

#### Option 1: Jupyter Notebook
1. Install required libraries:
   ```bash
   pip install pandas openpyxl scikit-learn numpy matplotlib notebook
   ```
2. Launch:
   ```bash
   jupyter notebook
   ```
3. Navigate to any `.ipynb` file under `Dataset 1` or `Dataset 2` and run the cells.

#### Option 2: VSCode with Conda
1. Create and activate a Conda environment:
   ```bash
   conda create -n aba-env python=3.8
   conda activate aba-env
   ```
2. Install required packages:
   ```bash
   pip install pandas openpyxl scikit-learn numpy matplotlib ipykernel
   ```
3. Open the project in VSCode, select the `aba-env` kernel, and run any notebook.

---
