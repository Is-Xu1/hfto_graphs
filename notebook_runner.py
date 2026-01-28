import nbformat
import papermill as pm
import glob
import os

# 1. Parameterize the Notebook
notebook_path = 'visualization_script_HFTOGraphOnly1.ipynb'
with open(notebook_path, 'r', encoding='utf-8') as f:
    nb = nbformat.read(f, as_version=4)

# Add parameters tag to the first relevant cell or insert a new one
# The original notebook has a hardcoded string in the second cell.
# We'll insert a new cell at the top for clarity.
param_cell = nbformat.v4.new_code_cell("input_csv = 'DATAMwEDR_UofU 650-05-211 BHA 23 - output data.csv'")
param_cell.metadata['tags'] = ['parameters']
nb.cells.insert(0, param_cell)

# Add robust column mapping and Image Saving logic
mapping_logic = """
# Robust column detection
import os
import matplotlib.pyplot as plt

def find_col(data, suffix):
    for col in data.columns:
        if suffix in col:
            return col
    return None

torsionalCol = find_col(data, 'ShYpeak(g)') or "Bit Box_ShYpeak(g)"
lateralCol = find_col(data, 'ShZpeak(g)') or "Bit Box_ShZpeak(g)"
axialCol = find_col(data, 'ShXpeak(g)') or "Bit Box_ShXpeak(g)"

# Ensure image directory exists
if not os.path.exists('output_images'):
    os.makedirs('output_images')
"""

# Update the second cell (now at index 2 due to insert and existing imports at index 1)
# We will replace the hardcoded column assignments with our mapping logic.
for cell in nb.cells:
    if 'pd.read_csv' in cell.source:
        cell.source = cell.source.replace("'DATAMwEDR_UofU 650-05-211 BHA 23 - output data.csv'", "input_csv")
        # Find the lines that set the column names and replace them
        lines = cell.source.splitlines()
        new_lines = []
        for line in lines:
            if any(col_name in line for col_name in ['torsionalCol', 'lateralCol', 'axialCol']):
                continue
            new_lines.append(line)
        cell.source = "\n".join(new_lines) + "\n" + mapping_logic

# Update the plot_state call or definition to save images
# We'll replace 'plt.show()' with figure saving logic
for cell in nb.cells:
    if 'plt.show()' in cell.source:
        save_logic = """
    img_name = f"{input_csv}_{state_name}.png".replace(' ', '_').replace('(', '').replace(')', '')
    plt.savefig(f"output_images/{img_name}", bbox_inches='tight')
    plt.show()
"""
        cell.source = cell.source.replace("plt.show()", save_logic)

# Save the parameterized notebook
parameterized_nb_path = 'parameterized_visualization.ipynb'
with open(parameterized_nb_path, 'w', encoding='utf-8') as f:
    nbformat.write(nb, f)

print(f"Parameterized notebook saved to {parameterized_nb_path}")

# 2. Batch Process CSVs
output_dir = 'output_notebooks'
if not os.path.exists(output_dir):
    os.makedirs(output_dir)

csv_files = glob.glob('*output data.csv')
print(f"Found {len(csv_files)} CSV files to process.")

processed_images = []

for csv_file in csv_files:
    output_nb = os.path.join(output_dir, f"Executed_{csv_file.replace('.csv', '.ipynb')}")
    print(f"Processing {csv_file} -> {output_nb} ...")
    try:
        pm.execute_notebook(
            parameterized_nb_path,
            output_nb,
            parameters=dict(input_csv=csv_file)
        )
    except Exception as e:
        print(f"Error processing {csv_file}: {e}")

# 3. Create Summary Report Notebook
summary_nb = nbformat.v4.new_notebook()
markdown_content = "# Combined Output Graphs\n\n"

# Re-list files to ensure we get all states
all_images = os.listdir('output_images')

for csv_file in csv_files:
    csv_sanitized = csv_file.replace(' ', '_').replace('(', '').replace(')', '')
    markdown_content += f"## {csv_file}\n"
    
    # Find all images that belong to this CSV
    matched_images = sorted([img for img in all_images if img.startswith(csv_sanitized)])
    
    for img in matched_images:
        state_label = img.replace(csv_sanitized + "_", "").replace(".png", "").replace("_", " ")
        markdown_content += f"### {state_label}\n"
        markdown_content += f"![{state_label}](output_images/{img})\n\n"

summary_cell = nbformat.v4.new_markdown_cell(markdown_content)
summary_nb.cells.append(summary_cell)

with open('Summary_Report.ipynb', 'w', encoding='utf-8') as f:
    nbformat.write(summary_nb, f)

print("Batch processing complete. Summary_Report.ipynb generated with all plots.")
