import os
from IPython.display import Markdown, display, HTML
from pathlib import Path

# Function to load markdown files
def load_markdown_file(file_path):
    """
    Load a markdown file and return its content as a string.
    Args:
        file_path (str): Path to the markdown file.
    Returns:
        str: Content of the markdown file.
    """
    with open(file_path, 'r') as f:
        content = f.read()
    return content

def display_sample(content, title, num_lines=10):
    """
    Display a sample of the content with a title and total length information.
    Args:
        content (str): Content to display.
        title (str): Title for the content.
        num_lines (int): Number of lines to display from the content.
    """
    print(f"## {title}")
    print("-" * 80)
    lines = content.split("\n")
    sample = "\n".join(lines[:num_lines])
    print(f"{sample}\n...")
    print(f"[Total length: {len(lines)} lines, {len(content)} characters]")
    print("-" * 80 + "\n")


def display_formatted_sample(content, title, num_lines=10):
    lines = content.split("\n")
    sample = "\n".join(lines[:num_lines])

    html = f"""
    <div style="background-color: #2c3033; color: white; padding: 15px; border-radius: 6px; margin-bottom: 20px;">
        <h3 style="color: #ffd43b; border-bottom: 1px solid #555; padding-bottom: 5px;">{title}</h3>
        <pre style="background-color: #3a3f45; padding: 10px; border-radius: 4px; white-space: pre-wrap;">{sample}
        ...</pre>
        <p style="color: #aaa; margin-top: 10px; font-size: 0.9em;">
            Total length: {len(lines)} lines, {len(content)} characters
        </p>
    </div>
    """

    display(HTML(html))


def display_agent_review(result):
    """
    Formats agent output as Markdown code for display in the notebook.
    
    Args:
        result: The AgentRunResult object containing the review
    """
    review_text = result.output
    
    markdown = f"""
```markdown
{review_text}
```
"""
    
    return Markdown(markdown)