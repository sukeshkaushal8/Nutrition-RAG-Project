# Problem Statement: Dietary Guidance RAG Chatbot

## 1. Brief

Build the prototype of a chatbot that answers questions about **food, nutrition, and food safety**. Put a retrieval layer under the chatbot, so it answers only from official public dietary guidance documents. Every claim carries a citation. When the guidance doesn't cover a question, the assistant says so.

In the final project this becomes the service that answers *"is this a reasonable way to eat"* and *"how long can I keep this in the fridge"*.

---

## 2. Why RAG?

Health authorities publish long, careful, boring PDFs on exactly this. No API, just written prose — and almost nobody reads them. That gap is what RAG is for.

> **Out of scope:** Nutrient numbers for individual foods are different data and don't belong here. Those come from a structured database in Milestone 3.

---

## 3. The Pipeline

```
┌──────────────┐     ┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│   Corpus     │────▶│   Chunking   │────▶│   Retrieval  │────▶│ Answer Layer │
│  (21 Docs)   │     │  (Metadata)  │     │ (Vector Index)│     │ (Citations)  │
└──────────────┘     └──────────────┘     └──────────────┘     └──────────────┘
```

---

## 4. What You Build

### 4.1 Corpus
- Gather **21 public URLs** of guidance documents from recognised authorities.
- National nutrition institutes, food safety regulators, and international health bodies all work.
- **Written prose only** — anything with a clean API behind it doesn't belong here.
- Store the following metadata with every document:
  - Publisher
  - Year
  - Source URL
  - Retrieval date

### 4.2 Chunking
- Every chunk carries: **document name, publisher, year, and section heading**.
- These documents are full of tables and numbered recommendations that fixed-size chunking will cut in half.
- Document your chunking strategy in the README: what you chose and what it cost you.

### 4.3 Retrieval
- A **vector index** over the chunks.
- Must support:
  - Retrieval **across all documents**
  - Retrieval **filtered to one named document**

### 4.4 Answer Layer
- The assistant answers **only from retrieved chunks**.
- Every claim carries a citation showing:
  - Document name
  - Publisher
  - Year
  - A link to the source

### 4.5 Cross-Document Questions
- Some questions have two documents with something to say (e.g., cooking oil — where a nutrition institute and a food safety regulator both weigh in).
- **Answer per document**, with separate citations.
- **Never blend** two sources into one claim about what "the guidelines say".

### 4.6 Two Kinds of Refusal

Both are required:

| Refusal Type | Behaviour |
|---|---|
| **Not in the corpus** | When the retrieved chunks don't hold the answer, the assistant says the guidance doesn't cover it and names what it searched. |
| **Out of scope by design** | No medical advice, no calorie or weight targets, nothing about what anyone should weigh. Decline and point the person to a qualified professional. **Enforce this in code.** |

---

## 5. Corpus Sources (21 Verified Public URLs)

The following URLs are verified and publicly accessible guidance documents from recognised authorities:

### Nutrition Guidelines

| # | Document | Publisher | URL |
|---|----------|-----------|-----|
| 1 | Healthy Diet Fact Sheet | WHO | https://www.who.int/news-room/fact-sheets/detail/healthy-diet |
| 2 | Canada's Food Guide | Health Canada | https://www.canada.ca/content/dam/hc-sc/documents/services/food-guide/explore/dietary-guidelines/dietary-guidelines.pdf |
| 3 | Healthy Eating Plate | Harvard T.H. Chan School of Public Health | https://www.hsph.harvard.edu/nutritionsource/healthy-eating-plate/ |
| 4 | Eat Well Guide | NHS (UK) | https://www.nhs.uk/live-well/eat-well/food-guidelines-and-food-labels/the-eatwell-guide/ |
| 5 | Balanced Diet Guide | NHS (UK) | https://www.nhs.uk/live-well/eat-well/how-to-eat-a-balanced-diet/eating-a-balanced-diet/ |
| 6 | Dietary Guidelines for Indians (2024) | ICMR-NIN | https://www.nin.res.in |
| 7 | Kids Healthy Eating Plate | Harvard T.H. Chan School of Public Health | https://nutritionsource.hsph.harvard.edu/kids-healthy-eating-plate/ |
| 8 | Whole Grains | Harvard T.H. Chan School of Public Health | https://nutritionsource.hsph.harvard.edu/what-should-you-eat/whole-grains/ |
| 9 | Protein | Harvard T.H. Chan School of Public Health | https://nutritionsource.hsph.harvard.edu/what-should-you-eat/protein/ |
| 10 | Vegetables and Fruits | Harvard T.H. Chan School of Public Health | https://nutritionsource.hsph.harvard.edu/what-should-you-eat/vegetables-and-fruits/ |
| 11 | Healthy Fats | Harvard T.H. Chan School of Public Health | https://nutritionsource.hsph.harvard.edu/what-should-you-eat/healthy-fats/ |
| 12 | Milk and Dairy Choices | Harvard T.H. Chan School of Public Health | https://nutritionsource.hsph.harvard.edu/what-should-you-eat/milk-and-dairy-choices/ |
| 13 | Water | Harvard T.H. Chan School of Public Health | https://nutritionsource.hsph.harvard.edu/what-should-you-eat/water/ |
| 14 | Sodium | Harvard T.H. Chan School of Public Health | https://nutritionsource.hsph.harvard.edu/what-should-you-eat/sodium/ |
| 15 | Sugar-Sweetened Beverages | Harvard T.H. Chan School of Public Health | https://nutritionsource.hsph.harvard.edu/what-should-you-eat/sugar-sweetened-beverages/ |
| 16 | Limiting Red and Processed Meat | Harvard T.H. Chan School of Public Health | https://nutritionsource.hsph.harvard.edu/what-should-you-eat/limiting-red-and-processed-meat/ |
| 17 | Australian Dietary Guidelines | NHMRC | https://www.eatforhealth.gov.au/sites/default/files/2022-09/n55a_australian_dietary_guidelines_summary_131014_1.pdf |

| 18 | Dietary Guidelines for Americans | USDA / HHS | https://cdn.realfood.gov/DGA.pdf |
| 19 | Eat More (Singapore HealthHub) | Health Promotion Board (Singapore) | https://www.healthhub.sg/programmes/nutrition-hub/eat-more |
| 20 | Dietary Guidelines for NIN Website | ICMR-NIN | https://www.nin.res.in/downloads/DietaryGuidelinesforNINwebsite.pdf |

### Food Safety Guidelines

| # | Document | Publisher | URL |
|---|----------|-----------|-----|
| 21 | Five Keys to Safer Food Manual | WHO | https://apps.who.int/iris/bitstream/handle/10665/43546/9789241594639_eng.pdf |

> **Note:** All URLs were verified as accessible at the time of writing. The 21 primary corpus sources should be downloaded, stored locally, and accompanied by retrieval metadata (publisher, year, source URL, retrieval date).