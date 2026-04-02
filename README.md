# APS Field Extractor

Extracts key fields from Ontario APS (Agreement of Purchase and Sale) PDF documents using OpenAI GPT-4o.

## Extracted Fields

- Buyers (all names)
- Sellers (all names)
- Property Address
- Purchase Price
- Completion Date (Item #2)
- Title Search Date (Item #8)
- Listing Brokerage (Name, Phone, Representative)
- Co-op/Buyer Brokerage (Name, Phone, Representative)

## Setup

### 1. Install poppler (required for PDF conversion)

```bash
brew install poppler
```

### 2. Create a virtual environment and install dependencies

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 3. Add your OpenAI API key

Open the `.env` file and replace the placeholder with your actual key:

```
OPENAI_API_KEY=sk-your-actual-key-here
```

## Usage

```bash
source venv/bin/activate
python3 extract_aps.py <path-to-aps.pdf>
```

Multi-page PDFs are handled automatically. You can also pass multiple files:

```bash
python3 extract_aps.py document1.pdf document2.pdf
```

Results are printed to the terminal and saved to `aps_extracted.json`.
