# Third-Party Notices and Attribution

This document records the licenses, upstream sources, and attribution notices for third-party software, datasets, model assets, and dependencies utilized within this repository. 

The project's root `LICENSE` file (Apache License 2.0) applies strictly to the original source code authored for this project and does not supersede or subsume the individual licenses of the third-party components listed below.

---

## 1. Project Source Code
- **Scope**: Original implementation in `src/`, `scripts/`, `tests/`, and `experiments/`.
- **License**: Apache License 2.0 (see [`LICENSE`](LICENSE)).

---

## 2. Target Model Architecture & License
- **Model Family**: Google Gemma 4 (`google/gemma-4-31B-it`, `google/gemma-4-31B-it-qat-w4a16-ct`).
- **Official Model License**: Apache License 2.0 (as specified in the official Google Gemma 4 model card).
- **Attribution**: Google DeepMind / Google LLC.

---

## 3. Local Tokenizer Evaluation Artifact
- **Files**: `models/gemma4_tokenizer/tokenizer.json`, `models/gemma4_tokenizer/tokenizer_config.json`.
- **Vocabulary Size**: 262,144 subwords.
- **SHA-256 Hash**: `cc8d3a0ce36466ccc1278bf987df5f71db1719b9ca6b4118264f45cb627bfe0f`.
- **Provenance**: `tokenizer_config.json` was fetched from the public Hugging Face repository `google/gemma-4-31B-it-qat-w4a16-ct`. `tokenizer.json` was provided as a local evaluation asset for subword token length measurement. 
- **Epistemic Distinction**: The official Gemma 4 model is distributed under Apache 2.0. The local standalone JSON artifact contains serialized BPE vocabulary tables without an internal copyright notice; this project uses it solely for offline subword token length calculation.

---

## 4. Benchmark Dataset & Evaluation Harness
- **Dataset**: SWE-bench Lite (`data/tasks.jsonl`, 129 tasks, 127 unique base commits).
- **Authors**: Carlos E. Jimenez, John Yang, Alexander Wettig, Shunyu Yao, Kexin Pei, Ofir Press, Karthik Narasimhan (Princeton NLP).
- **License**: MIT License.
- **Upstream Repository**: https://github.com/princeton-nlp/SWE-bench

---

## 5. Evaluated Upstream Repositories
The 129 SWE-bench Lite tasks evaluated in this research are derived from four open-source Python repositories. Their respective upstream URLs, task allocations, and licenses are:

| Repository | Evaluated Tasks | Unique Base Commits | Upstream URL | License Identifier |
| :--- | :---: | :---: | :--- | :--- |
| **FastAPI** (`fastapi/fastapi`) | 67 | 67 | https://github.com/fastapi/fastapi | MIT License |
| **Rich** (`Textualize/rich`) | 48 | 47 | https://github.com/Textualize/rich | MIT License |
| **Requests** (`psf/requests`) | 13 | 12 | https://github.com/psf/requests | Apache License 2.0 |
| **HTTPX** (`encode/httpx`) | 1 | 1 | https://github.com/encode/httpx | BSD 3-Clause License |
| **Total** | **129** | **127** | — | — |

*(Note: Other SWE-bench repositories such as Pylint, Django, SymPy, and Sphinx are not included in this project's evaluated 129-task corpus).*

---

## 6. Third-Party Python Libraries
The core dependencies specified in `requirements.txt` are distributed under the following OSI-approved open-source licenses:

| Package | Version Specification | License | Copyright / Upstream |
| :--- | :--- | :--- | :--- |
| `transformers` | `>=4.45.0` | Apache License 2.0 | Hugging Face Inc. |
| `scipy` | `>=1.14.0` | BSD 3-Clause License | SciPy Developers |
| `numpy` | `>=1.26.0` | BSD 3-Clause License | NumPy Developers |
| `matplotlib` | `>=3.9.0` | PSF License / BSD-compatible | Matplotlib Development Team |
| `rank_bm25` | `>=0.2.2` | Apache License 2.0 | Doron Adler |
| `pytest` | `>=8.0.0` | MIT License | Holger Krekel & pytest-dev |

