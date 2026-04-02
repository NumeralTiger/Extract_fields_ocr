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

**Mac (using Homebrew):**
```bash
brew install poppler
```

**Windows:**
1. Download the latest Poppler for Windows (e.g., from [Release poppler-windows](https://github.com/oschwartz10612/poppler-windows/releases)).
2. Extract the downloaded folder to a permanent location like `C:\Program Files\poppler`.
3. Add the `bin` directory (e.g., `C:\Program Files\poppler\Library\bin`) to your system's PATH environment variable.

### 2. Create a virtual environment and install dependencies

**Mac/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

**Windows:**
```cmd
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Add your OpenAI API key

You will need an environment file to store your credentials safely:
1. In the root directory of this project, create a new file named exactly `.env` (don't forget the leading dot).
2. Open the `.env` file in your text editor.
3. Add the following line, replacing the placeholder with your actual OpenAI key:

```env
OPENAI_API_KEY=sk-your-actual-key-here
```

## Usage

Ensure your virtual environment is still activated before running the script.

**Mac:**
```bash
source venv/bin/activate
python3 extract_aps.py <path-to-aps.pdf>
```

**Windows:**
```cmd
venv\Scripts\activate
python extract_aps.py <path-to-aps.pdf>
```

Multi-page PDFs are handled automatically. You can also pass multiple files at once:

**Mac:**
```bash
python3 extract_aps.py document1.pdf document2.pdf
```

**Windows:**
```cmd
python extract_aps.py document1.pdf document2.pdf
```

Results are printed to the terminal and saved to `aps_extracted.json`.
