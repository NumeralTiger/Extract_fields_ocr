"""
Extract specific fields from an APS (Agreement of Purchase and Sale) document
using OpenAI GPT-4o vision.

Supports multi-page PDFs — they are automatically converted to images.
"""

import sys
import os
import json
import base64
import tempfile
from openai import OpenAI
from dotenv import load_dotenv
from pdf2image import convert_from_path

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def encode_image(image_path: str) -> str:
    with open(image_path, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")


def get_mime_type(path: str) -> str:
    ext = os.path.splitext(path)[1].lower()
    return {
        ".png": "image/png",
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".gif": "image/gif",
        ".webp": "image/webp",
    }.get(ext, "image/png")


def pdf_to_images(pdf_path: str) -> list[str]:
    """Convert a multi-page PDF into a list of temporary PNG file paths."""
    pages = convert_from_path(pdf_path, dpi=300)
    tmp_paths = []
    for i, page in enumerate(pages):
        tmp = tempfile.NamedTemporaryFile(suffix=f"_page{i+1}.png", delete=False)
        page.save(tmp.name, "PNG")
        tmp_paths.append(tmp.name)
    print(f"  Converted '{os.path.basename(pdf_path)}' → {len(tmp_paths)} page(s)")
    return tmp_paths


def extract_fields(file_paths: list[str]) -> dict:
    """Send document images/pages to GPT-4o and extract APS fields."""

    prompt = """You are an expert at reading Ontario real-estate APS (Agreement of Purchase and Sale) documents.

Extract ONLY the following fields from the document. Return valid JSON and nothing else.

{
  "buyers": ["list of all buyer full names"],
  "sellers": ["list of all seller full names"],
  "address": "Full property address (e.g. 123 John Street, Toronto, ON A1B 2C3)",
  "purchase_price": "Purchase price as stated (e.g. $500,000.00)",
  "completion_date": "Completion date from Item #2",
  "title_search_date": "Title search date from Item #8",
  "listing_brokerage": {
    "name": "Brokerage name",
    "phone": "Phone number",
    "representative": "Representative name"
  },
  "coop_buyer_brokerage": {
    "name": "Brokerage name",
    "phone": "Phone number",
    "representative": "Representative name"
  }
}

If a field is not found, set its value to null. Return ONLY the JSON object."""

    # Build the message content with all pages/images
    content = [{"type": "text", "text": prompt}]

    for path in file_paths:
        mime = get_mime_type(path)
        b64 = encode_image(path)
        content.append({
            "type": "image_url",
            "image_url": {
                "url": f"data:{mime};base64,{b64}",
                "detail": "high",
            },
        })

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": content}],
        temperature=0,
        max_tokens=1024,
    )

    raw = response.choices[0].message.content.strip()

    # Strip markdown fences if present
    if raw.startswith("```"):
        raw = raw.split("\n", 1)[1]
        raw = raw.rsplit("```", 1)[0]

    return json.loads(raw)


def print_results(data: dict):
    print("\n" + "=" * 60)
    print("  APS EXTRACTED FIELDS")
    print("=" * 60)

    print(f"\n📌 Buyers:            {', '.join(data.get('buyers') or ['N/A'])}")
    print(f"📌 Sellers:           {', '.join(data.get('sellers') or ['N/A'])}")
    print(f"🏠 Address:           {data.get('address') or 'N/A'}")
    print(f"💰 Purchase Price:    {data.get('purchase_price') or 'N/A'}")
    print(f"📅 Completion Date:   {data.get('completion_date') or 'N/A'}")
    print(f"🔍 Title Search Date: {data.get('title_search_date') or 'N/A'}")

    lb = data.get("listing_brokerage") or {}
    print(f"\n🏢 Listing Brokerage:")
    print(f"     Name:           {lb.get('name') or 'N/A'}")
    print(f"     Phone:          {lb.get('phone') or 'N/A'}")
    print(f"     Representative: {lb.get('representative') or 'N/A'}")

    cb = data.get("coop_buyer_brokerage") or {}
    print(f"\n🏢 Co-op/Buyer Brokerage:")
    print(f"     Name:           {cb.get('name') or 'N/A'}")
    print(f"     Phone:          {cb.get('phone') or 'N/A'}")
    print(f"     Representative: {cb.get('representative') or 'N/A'}")

    print("\n" + "=" * 60)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python extract_aps.py <file1.pdf> [file2.png] ...")
        print("  Supports: PDF (multi-page), PNG, JPG, JPEG, WEBP, GIF")
        sys.exit(1)

    input_paths = sys.argv[1:]

    for p in input_paths:
        if not os.path.isfile(p):
            print(f"Error: File not found: {p}")
            sys.exit(1)

    # Expand PDFs into per-page images; keep image files as-is
    image_paths = []
    temp_files = []

    for p in input_paths:
        if p.lower().endswith(".pdf"):
            converted = pdf_to_images(p)
            image_paths.extend(converted)
            temp_files.extend(converted)
        else:
            image_paths.append(p)

    print(f"Processing {len(image_paths)} page(s) total...")

    try:
        result = extract_fields(image_paths)
    finally:
        # Clean up temporary converted images
        for tmp in temp_files:
            try:
                os.unlink(tmp)
            except OSError:
                pass

    print_results(result)

    # Also save raw JSON
    output_path = "aps_extracted.json"
    with open(output_path, "w") as f:
        json.dump(result, f, indent=2)
    print(f"\n✅ Raw JSON saved to {output_path}")
