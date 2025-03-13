"""
Visualization generator for SR&ED documentation.

This module creates various visualizations to include in SR&ED documentation packages,
showing experimental results and research findings in a visual format.
"""

import io
import numpy as np
import matplotlib
matplotlib.use('Agg')  # Required for non-interactive environments
import matplotlib.pyplot as plt
from matplotlib.patches import Patch
import pandas as pd
from PIL import Image, ImageDraw, ImageFont

def generate_experiment_timeline():
    """
    Generate a visual timeline of SR&ED experimental activities.
    
    Returns:
        bytes: PNG image data
    """
    # Set up the figure
    fig, ax = plt.subplots(figsize=(12, 6))
    
    # Define the timeline events
    events = [
        {"phase": "Problem Definition", "start": 0, "end": 2, "color": "#3498db"},
        {"phase": "Research", "start": 1, "end": 3, "color": "#2980b9"},
        {"phase": "Hypothesis Formulation", "start": 2, "end": 3, "color": "#e74c3c"},
        {"phase": "Experimental Design", "start": 3, "end": 4.5, "color": "#9b59b6"},
        {"phase": "Algorithm Development", "start": 4, "end": 7, "color": "#8e44ad"},
        {"phase": "Prototype Implementation", "start": 6, "end": 8, "color": "#1abc9c"},
        {"phase": "Testing & Validation", "start": 7, "end": 10, "color": "#27ae60"},
        {"phase": "Analysis & Refinement", "start": 9, "end": 11, "color": "#f1c40f"},
        {"phase": "Documentation", "start": 11, "end": 12, "color": "#e67e22"}
    ]
    
    # Plot the timeline
    y_pos = 0
    for event in events:
        ax.barh(y_pos, event["end"] - event["start"], left=event["start"], 
                height=0.6, color=event["color"], alpha=0.8)
        ax.text(event["start"] + 0.1, y_pos, event["phase"], 
                va='center', fontweight='bold', color='white')
        y_pos += 1
    
    # Configure the plot
    ax.set_yticks([])  # Hide y-axis labels
    ax.set_xlim(0, 12)
    ax.set_xticks(range(13))
    ax.set_xticklabels(['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 
                        'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec', ''])
    ax.set_xlabel('2024')
    ax.set_title('SR&ED Experimental Timeline', fontsize=16, pad=20)
    
    # Add a grid for better readability
    ax.grid(True, axis='x', linestyle='--', alpha=0.3)
    
    # Save to bytesio
    buffer = io.BytesIO()
    plt.tight_layout()
    fig.savefig(buffer, format='png', dpi=300)
    plt.close(fig)
    buffer.seek(0)
    return buffer.getvalue()

def generate_anomaly_detection_comparison():
    """
    Generate a bar chart comparing anomaly detection algorithm performance.
    
    Returns:
        bytes: PNG image data
    """
    # Set up the figure
    fig, ax = plt.subplots(figsize=(10, 6))
    
    # Data for the chart
    algorithms = ['Baseline', 'Variation 1', 'Variation 2', 'Variation 3', 'Variation 4']
    precision = [68.2, 74.5, 79.8, 83.2, 91.6]
    recall = [71.4, 77.9, 80.1, 84.7, 90.1]
    f1_score = [69.7, 76.2, 79.9, 83.9, 90.8]
    
    # Width of each bar
    width = 0.25
    
    # Positions of bars on x-axis
    r1 = np.arange(len(algorithms))
    r2 = [x + width for x in r1]
    r3 = [x + width for x in r2]
    
    # Create the bars
    ax.bar(r1, precision, width, label='Precision', color='#3498db')
    ax.bar(r2, recall, width, label='Recall', color='#2ecc71')
    ax.bar(r3, f1_score, width, label='F1-Score', color='#e74c3c')
    
    # Add labels and customize
    ax.set_xlabel('Algorithm Variation', fontweight='bold')
    ax.set_ylabel('Percentage (%)', fontweight='bold')
    ax.set_title('Anomaly Detection Algorithm Performance Comparison', fontsize=16, pad=20)
    ax.set_xticks([r + width for r in range(len(algorithms))])
    ax.set_xticklabels(algorithms)
    ax.legend()
    
    # Add a grid for better readability
    ax.grid(True, axis='y', linestyle='--', alpha=0.3)
    
    # Add value labels on top of each bar
    for i, bar in enumerate(ax.patches):
        ax.text(bar.get_x() + bar.get_width()/2., bar.get_height() + 1, 
                f'{bar.get_height():.1f}%', ha='center', va='bottom', fontsize=9)
    
    # Add SR&ED compliance note
    fig.text(0.5, 0.01, 'SR&ED Documentation - Experimental Results', ha='center', fontsize=8, 
             style='italic', bbox={'facecolor': 'lightgray', 'alpha': 0.5, 'pad': 5})
    
    # Save to bytesio
    buffer = io.BytesIO()
    plt.tight_layout(rect=[0, 0.03, 1, 0.97])
    fig.savefig(buffer, format='png', dpi=300)
    plt.close(fig)
    buffer.seek(0)
    return buffer.getvalue()

def generate_prediction_lead_time_chart():
    """
    Generate a chart showing prediction lead time improvements.
    
    Returns:
        bytes: PNG image data
    """
    # Set up the figure
    fig, ax = plt.subplots(figsize=(10, 6))
    
    # Data for the chart
    models = ['Temperature\nOnly', 'Vibration\nOnly', 'Power\nOnly', 
              'Multi-sensor\n(Basic)', 'Multi-sensor\n(Advanced)']
    lead_times = [36, 48, 29, 56, 72]
    accuracy = [67, 73, 69, 82, 98]
    false_positive = [32, 28, 34, 22, 7]
    
    # Create the primary bar chart for lead times
    bars = ax.bar(models, lead_times, width=0.6, color='#3498db', alpha=0.8)
    
    # Add labels and customize
    ax.set_xlabel('Model Type', fontweight='bold')
    ax.set_ylabel('Average Prediction Lead Time (hours)', fontweight='bold', color='#3498db')
    ax.set_title('Failure Prediction Lead Time Comparison', fontsize=16, pad=20)
    ax.tick_params(axis='y', labelcolor='#3498db')
    
    # Create a secondary y-axis for accuracy
    ax2 = ax.twinx()
    ax2.plot(models, accuracy, 'o-', linewidth=3, markersize=10, color='#2ecc71', label='Accuracy (%)')
    ax2.plot(models, false_positive, 's--', linewidth=2, markersize=8, color='#e74c3c', label='False Positive Rate (%)')
    ax2.set_ylabel('Percentage (%)', fontweight='bold')
    ax2.tick_params(axis='y')
    
    # Add legend
    lines, labels = ax2.get_legend_handles_labels()
    bars_legend = [Patch(facecolor='#3498db', label='Lead Time (hours)')]
    ax2.legend(bars_legend + lines, ['Lead Time (hours)'] + labels, loc='upper left')
    
    # Add value labels on top of each bar
    for bar in bars:
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height + 2, f'{height}h', 
                ha='center', va='bottom', fontsize=10, fontweight='bold')
    
    # Add SR&ED compliance note
    fig.text(0.5, 0.01, 'SR&ED Documentation - Experimental Results', ha='center', fontsize=8, 
             style='italic', bbox={'facecolor': 'lightgray', 'alpha': 0.5, 'pad': 5})
    
    # Add improvement highlight
    ax.annotate('31% Improvement', xy=(4, 72), xytext=(3, 85),
                arrowprops=dict(facecolor='black', shrink=0.05, width=2, headwidth=8),
                fontsize=12, fontweight='bold')
    
    # Add grid for better readability
    ax.grid(True, axis='y', linestyle='--', alpha=0.3)
    
    # Save to bytesio
    buffer = io.BytesIO()
    plt.tight_layout(rect=[0, 0.03, 1, 0.97])
    fig.savefig(buffer, format='png', dpi=300)
    plt.close(fig)
    buffer.seek(0)
    return buffer.getvalue()

def generate_research_methodology_diagram():
    """
    Generate a diagram illustrating the SR&ED research methodology.
    
    Returns:
        bytes: PNG image data
    """
    # Create a new PIL image
    width, height = 1200, 800
    background_color = (255, 255, 255)
    image = Image.new('RGB', (width, height), background_color)
    draw = ImageDraw.Draw(image)
    
    # Try to load a font, or fall back to default
    try:
        title_font = ImageFont.truetype("Arial", 40)
        header_font = ImageFont.truetype("Arial", 30)
        text_font = ImageFont.truetype("Arial", 20)
    except IOError:
        title_font = ImageFont.load_default()
        header_font = ImageFont.load_default()
        text_font = ImageFont.load_default()
    
    # Draw title
    draw.text((600, 50), "SR&ED Research Methodology", fill=(0, 0, 0), font=title_font, anchor="mm")
    draw.text((600, 100), "Systematic Investigation Process", fill=(100, 100, 100), font=header_font, anchor="mm")
    
    # Define methodology steps and positions
    steps = [
        {"title": "Problem Definition", "desc": "Identification of technical\nuncertainties and knowledge gaps", "x": 300, "y": 200, "color": (53, 152, 219)},
        {"title": "Hypothesis Formulation", "desc": "Development of testable hypotheses\nregarding technological solutions", "x": 900, "y": 200, "color": (231, 76, 60)},
        {"title": "Experimental Design", "desc": "Creation of test environments\nand measurement protocols", "x": 900, "y": 350, "color": (155, 89, 182)},
        {"title": "Algorithm Development", "desc": "Implementation of candidate\nsolutions and approaches", "x": 900, "y": 500, "color": (26, 188, 156)},
        {"title": "Testing & Validation", "desc": "Rigorous testing against\ncontrol groups and baselines", "x": 600, "y": 650, "color": (39, 174, 96)},
        {"title": "Analysis & Refinement", "desc": "Statistical analysis and\niterative improvements", "x": 300, "y": 500, "color": (241, 196, 15)},
        {"title": "Documentation", "desc": "Comprehensive recording of\nall SR&ED-eligible activities", "x": 300, "y": 350, "color": (230, 126, 34)}
    ]
    
    # Draw the steps and connections
    for i, step in enumerate(steps):
        # Draw box
        x, y = step["x"], step["y"]
        box_width, box_height = 250, 80
        color = step["color"]
        lighter_color = tuple(min(c + 50, 255) for c in color)
        
        # Draw rounded rectangle with gradient
        for i in range(box_height):
            # Calculate gradient color
            gradient_factor = i / box_height
            gradient_color = tuple(int(color[j] + (lighter_color[j] - color[j]) * gradient_factor) for j in range(3))
            
            # Draw a line of the gradient
            draw.line([(x - box_width//2, y - box_height//2 + i), 
                       (x + box_width//2, y - box_height//2 + i)], 
                      fill=gradient_color)
        
        # Draw border
        draw.rectangle([(x - box_width//2, y - box_height//2), 
                        (x + box_width//2, y + box_height//2)], 
                       outline=(0, 0, 0), width=2)
        
        # Draw title and description
        draw.text((x, y - 15), step["title"], fill=(0, 0, 0), font=header_font, anchor="mm")
        draw.text((x, y + 25), step["desc"], fill=(50, 50, 50), font=text_font, anchor="mm")
    
    # Draw arrows connecting the steps
    arrows = [
        (steps[0]["x"] + 125, steps[0]["y"], steps[1]["x"] - 125, steps[1]["y"]),
        (steps[1]["x"], steps[1]["y"] + 40, steps[1]["x"], steps[2]["y"] - 40),
        (steps[2]["x"], steps[2]["y"] + 40, steps[2]["x"], steps[3]["y"] - 40),
        (steps[3]["x"] - 125, steps[3]["y"], steps[4]["x"] + 125, steps[4]["y"]),
        (steps[4]["x"] - 125, steps[4]["y"], steps[5]["x"] + 125, steps[5]["y"]),
        (steps[5]["x"], steps[5]["y"] - 40, steps[5]["x"], steps[6]["y"] + 40),
        (steps[6]["x"], steps[6]["y"] - 40, steps[6]["x"], steps[0]["y"] + 40)
    ]
    
    for start_x, start_y, end_x, end_y in arrows:
        # Draw arrow line
        draw.line([(start_x, start_y), (end_x, end_y)], fill=(0, 0, 0), width=3)
        
        # Calculate arrowhead
        angle = np.arctan2(end_y - start_y, end_x - start_x)
        arrow_length = 15
        arrow_width = 10
        
        # Points for the arrowhead
        arrow_p1 = (
            end_x - arrow_length * np.cos(angle) + arrow_width * np.sin(angle),
            end_y - arrow_length * np.sin(angle) - arrow_width * np.cos(angle)
        )
        arrow_p2 = (
            end_x - arrow_length * np.cos(angle) - arrow_width * np.sin(angle),
            end_y - arrow_length * np.sin(angle) + arrow_width * np.cos(angle)
        )
        
        # Draw arrowhead
        draw.polygon([arrow_p1, (end_x, end_y), arrow_p2], fill=(0, 0, 0))
    
    # Add SR&ED compliance note
    draw.rectangle([(400, height - 50), (800, height - 20)], fill=(240, 240, 240))
    draw.text((600, height - 35), "SR&ED Documentation - Research Methodology", 
             fill=(100, 100, 100), font=text_font, anchor="mm")
    
    # Save to bytesio
    buffer = io.BytesIO()
    image.save(buffer, format='PNG')
    buffer.seek(0)
    return buffer.getvalue()

def generate_technical_advancement_chart():
    """
    Generate a chart showing technical advancements achieved through SR&ED activities.
    
    Returns:
        bytes: PNG image data
    """
    # Set up the figure
    fig, ax = plt.subplots(figsize=(10, 6))
    
    # Data for the chart
    categories = ['Processing\nSpeed', 'Anomaly\nDetection', 'Failure\nPrediction', 'False\nPositives', 'Maintenance\nPlanning']
    before = [100, 68, 33, 100, 40]  # Baseline values (100 = reference)
    after = [143, 91, 94, 55, 78]    # After SR&ED improvements
    
    # Create the bars
    x = np.arange(len(categories))
    width = 0.35
    
    rects1 = ax.bar(x - width/2, before, width, label='Before SR&ED Project', color='#95a5a6')
    rects2 = ax.bar(x + width/2, after, width, label='After SR&ED Project', color='#3498db')
    
    # Calculate and display improvement percentages
    for i in range(len(categories)):
        if categories[i] == 'False\nPositives':
            # For false positives, reduction is good
            change = ((before[i] - after[i]) / before[i]) * 100
            color = 'green'
            text = f"-{change:.0f}%"
        else:
            # For others, increase is good
            change = ((after[i] - before[i]) / before[i]) * 100
            color = 'green'
            text = f"+{change:.0f}%"
        
        # Draw the improvement percentage
        ax.text(i, max(before[i], after[i]) + 5, text, ha='center', color=color, 
                fontweight='bold', bbox=dict(facecolor='white', alpha=0.8, pad=3))
    
    # Add labels and customize
    ax.set_xlabel('Performance Category', fontweight='bold')
    ax.set_ylabel('Performance Score', fontweight='bold')
    ax.set_title('Technical Advancement Through SR&ED Activities', fontsize=16, pad=20)
    ax.set_xticks(x)
    ax.set_xticklabels(categories)
    ax.legend()
    
    # Add value labels on top of each bar
    for rect in rects1 + rects2:
        height = rect.get_height()
        ax.text(rect.get_x() + rect.get_width()/2., height - 10, 
                f'{height:.0f}', ha='center', va='top', color='white', fontweight='bold')
    
    # Add a grid for better readability
    ax.grid(True, axis='y', linestyle='--', alpha=0.3)
    
    # Add SR&ED compliance note
    fig.text(0.5, 0.01, 'SR&ED Documentation - Technical Advancement Evidence', ha='center', fontsize=8, 
             style='italic', bbox={'facecolor': 'lightgray', 'alpha': 0.5, 'pad': 5})
    
    # Save to bytesio
    buffer = io.BytesIO()
    plt.tight_layout(rect=[0, 0.03, 1, 0.97])
    fig.savefig(buffer, format='png', dpi=300)
    plt.close(fig)
    buffer.seek(0)
    return buffer.getvalue()

def get_all_visualization_data():
    """
    Generate all visualizations and return them as a dictionary.
    
    Returns:
        dict: Dictionary with all visualization data
    """
    return {
        'experiment_timeline.png': generate_experiment_timeline(),
        'anomaly_detection_comparison.png': generate_anomaly_detection_comparison(),
        'prediction_lead_time.png': generate_prediction_lead_time_chart(),
        'research_methodology.png': generate_research_methodology_diagram(),
        'technical_advancement.png': generate_technical_advancement_chart()
    }