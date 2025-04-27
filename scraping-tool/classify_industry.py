import pandas as pd
from transformers import pipeline

# Load your Excel file
df = pd.read_excel('database.xlsx')

# Initialize the zero-shot classification model
classifier = pipeline("zero-shot-classification", model="facebook/bart-large-mnli")

# Define industry labels
industry_labels = [
    "Agriculture", "Technology", "Construction", "Transportation",
    "Retail", "Food", "Healthcare", "Education", "Finance",
    "Tourism", "Real Estate", "Manufacturing", "Services", "Energy",
    "Consulting", "Telecommunications", "Media", "Entertainment", "Legal"
]

# List to hold results
classified_industries = []

# Loop through each description
for idx, description in enumerate(df['Objekti i Veprimtarise']):
    if pd.isnull(description) or str(description).strip() == '':
        classified_industries.append(None)
        continue

    # Perform classification
    result = classifier(
        description,
        candidate_labels=industry_labels,
        multi_label=False
    )

    # Choose the top predicted label
    top_label = result['labels'][0]
    classified_industries.append(top_label)

    # Optional: Progress tracking
    print(f"Classified row {idx + 1}/{len(df)}: {top_label}")

# Add INDUSTRY column
df['INDUSTRY'] = classified_industries

# Save the updated DataFrame
df.to_excel('output_classified.xlsx', index=False)

print("\n✅ All done! Check your file: output_classified.xlsx")
