"""
UI Helper module for the premium UI theme.

This module provides utility functions for loading and displaying premium UI elements.
"""
import os
import base64
import streamlit as st

def load_css():
    """
    Load custom CSS for the premium UI theme.
    """
    # Create the CSS directory if it doesn't exist
    css_dir = os.path.join("assets", "css")
    os.makedirs(css_dir, exist_ok=True)
    
    # CSS file path
    css_file = os.path.join(css_dir, "premium_theme.css")
    
    # Create the CSS file if it doesn't exist
    if not os.path.exists(css_file):
        with open(css_file, "w") as f:
            f.write("""
/* Premium Theme CSS */
:root {
    --font-sans: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
    --font-display: "SF Pro Display", -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
    --font-mono: "SF Mono", SFMono-Regular, ui-monospace, "DejaVu Sans Mono", Menlo, Consolas, monospace;
    
    /* Primary colors - Blue */
    --primary-50: #f0f7ff;
    --primary-100: #e0f0fe;
    --primary-200: #bae0fd;
    --primary-300: #7cc8fc;
    --primary-400: #36aaf8;
    --primary-500: #0c96eb;
    --primary-600: #0078c8;
    --primary-700: #0060a3;
    --primary-800: #00528a;
    --primary-900: #064872;
    
    /* Secondary colors - Amber */
    --amber-50: #fffbeb;
    --amber-100: #fef3c7;
    --amber-200: #fde68a;
    --amber-300: #fcd34d;
    --amber-400: #fbbf24;
    --amber-500: #f59e0b;
    --amber-600: #d97706;
    --amber-700: #b45309;
    --amber-800: #92400e;
    --amber-900: #78350f;
    
    /* Neutral colors */
    --neutral-50: #f9fafb;
    --neutral-100: #f3f4f6;
    --neutral-200: #e5e7eb;
    --neutral-300: #d1d5db;
    --neutral-400: #9ca3af;
    --neutral-500: #6b7280;
    --neutral-600: #4b5563;
    --neutral-700: #374151;
    --neutral-800: #1f2937;
    --neutral-900: #111827;
    
    /* Status colors */
    --success: #10b981;
    --warning: #f59e0b;
    --danger: #ef4444;
    --info: #3b82f6;
}

/* General styles */
body {
    font-family: var(--font-sans);
    color: var(--neutral-800);
}

/* Custom sidebar styling */
.sidebar .sidebar-content {
    background-color: var(--neutral-50);
}

/* Navigation group headings */
.nav-group {
    margin-bottom: 1rem;
}

.nav-group-title {
    font-size: 0.7rem;
    font-weight: 600;
    color: var(--neutral-500);
    margin-bottom: 0.5rem;
    letter-spacing: 0.05em;
}

/* Navigation items */
.nav-item {
    display: flex;
    align-items: center;
    padding: 0.5rem;
    border-radius: 0.25rem;
    margin-bottom: 0.25rem;
    cursor: pointer;
    transition: background-color 0.2s;
}

.nav-item:hover {
    background-color: var(--neutral-100);
}

.nav-item.active {
    background-color: var(--primary-50);
    border-left: 3px solid var(--primary-600);
}

.nav-item-icon {
    width: 20px;
    height: 20px;
    margin-right: 0.75rem;
    color: var(--neutral-600);
}

.nav-item.active .nav-item-icon {
    color: var(--primary-600);
}

.nav-item-label {
    font-size: 0.9rem;
    color: var(--neutral-700);
}

.nav-item.active .nav-item-label {
    color: var(--primary-800);
    font-weight: 500;
}

/* Dashboard cards */
.premium-card {
    background-color: white;
    padding: 1.5rem;
    border-radius: 0.5rem;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
    transition: transform 0.2s, box-shadow 0.2s;
}

.premium-card:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05), 0 10px 15px rgba(0, 0, 0, 0.05);
}

/* Metric cards */
.metric-card {
    padding: 1.5rem;
    background-color: white;
    border-radius: 8px;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.metric-title {
    color: var(--neutral-600);
    font-size: 0.85rem;
    margin-bottom: 0.5rem;
}

.metric-value {
    color: var(--neutral-800);
    font-size: 2rem;
    font-weight: 600;
    font-family: var(--font-display);
}

.metric-trend {
    display: flex;
    align-items: center;
    margin-top: 0.5rem;
    font-size: 0.85rem;
}

.trend-up {
    color: var(--success);
}

.trend-down {
    color: var(--danger);
}

/* Status indicators */
.status-healthy {
    color: var(--success);
    font-weight: 500;
}

.status-warning {
    color: var(--warning);
    font-weight: 500;
}

.status-critical {
    color: var(--danger);
    font-weight: 500;
}

.status-idle {
    color: var(--neutral-500);
    font-weight: 500;
}

.status-dot {
    display: inline-block;
    width: 8px;
    height: 8px;
    border-radius: 50%;
    margin-right: 6px;
}

.status-dot.healthy {
    background-color: var(--success);
}

.status-dot.warning {
    background-color: var(--warning);
}

.status-dot.critical {
    background-color: var(--danger);
}

.status-dot.idle {
    background-color: var(--neutral-500);
}

/* Alert items */
.alert-item {
    display: flex;
    align-items: flex-start;
    padding: 1rem;
    border-radius: 8px;
    margin-bottom: 1rem;
}

.alert-item.warning {
    background-color: var(--amber-50);
    border-left: 3px solid var(--amber-500);
}

.alert-item.danger {
    background-color: #fff5f5;
    border-left: 3px solid var(--danger);
}

.alert-item.success {
    background-color: #f0fff4;
    border-left: 3px solid var(--success);
}

.alert-item.info {
    background-color: #ebf8ff;
    border-left: 3px solid var(--info);
}

.alert-icon {
    margin-right: 1rem;
    flex-shrink: 0;
}

.alert-content {
    flex: 1;
}

.alert-title {
    font-weight: 600;
    margin-bottom: 0.25rem;
}

.alert-message {
    color: var(--neutral-700);
    font-size: 0.9rem;
    line-height: 1.4;
}
            """)
    
    # Load the CSS
    with open(css_file, "r") as f:
        css = f.read()
        st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)

def load_svg(svg_file):
    """
    Load an SVG file and return it as a base64 encoded image.
    
    Args:
        svg_file (str): Path to the SVG file
        
    Returns:
        str: Base64 encoded SVG for use in HTML img tags
    """
    # Create the image directory if it doesn't exist
    img_dir = os.path.join("assets", "images")
    os.makedirs(img_dir, exist_ok=True)
    
    svg_path = os.path.join(img_dir, f"{svg_file}.svg")
    
    # Create default SVG if it doesn't exist
    if not os.path.exists(svg_path):
        if svg_file == "logo":
            with open(svg_path, "w") as f:
                f.write("""
<svg width="40" height="40" viewBox="0 0 40 40" fill="none" xmlns="http://www.w3.org/2000/svg">
  <rect width="40" height="40" rx="8" fill="#0078C8"/>
  <path d="M10 22.5C10 21.1193 11.1193 20 12.5 20H27.5C28.8807 20 30 21.1193 30 22.5V25C30 26.3807 28.8807 27.5 27.5 27.5H12.5C11.1193 27.5 10 26.3807 10 25V22.5Z" fill="white"/>
  <circle cx="15" cy="15" r="3" fill="white"/>
  <circle cx="25" cy="15" r="3" fill="white"/>
  <rect x="18" y="30" width="4" height="2" rx="1" fill="white"/>
</svg>
                """)
        elif svg_file == "dashboard":
            with open(svg_path, "w") as f:
                f.write("""
<svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
  <rect x="3" y="3" width="7" height="7" rx="1" stroke="currentColor" stroke-width="2"/>
  <rect x="3" y="14" width="7" height="7" rx="1" stroke="currentColor" stroke-width="2"/>
  <rect x="14" y="3" width="7" height="7" rx="1" stroke="currentColor" stroke-width="2"/>
  <rect x="14" y="14" width="7" height="7" rx="1" stroke="currentColor" stroke-width="2"/>
</svg>
                """)
        elif svg_file == "equipment":
            with open(svg_path, "w") as f:
                f.write("""
<svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
  <path d="M14 7L17 10" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
  <path d="M5 20L9 16" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
  <path d="M9 16L17 8" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
  <circle cx="11" cy="14" r="2" stroke="currentColor" stroke-width="2"/>
  <circle cx="19" cy="6" r="2" stroke="currentColor" stroke-width="2"/>
</svg>
                """)
        elif svg_file == "alerts":
            with open(svg_path, "w") as f:
                f.write("""
<svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
  <path d="M12 6V12L16 14" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
  <circle cx="12" cy="12" r="9" stroke="currentColor" stroke-width="2"/>
</svg>
                """)
        elif svg_file == "metrics":
            with open(svg_path, "w") as f:
                f.write("""
<svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
  <path d="M3 3V19C3 20.1046 3.89543 21 5 21H21" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
  <path d="M7 14L10 11L13 14L17 10" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
  <circle cx="17" cy="10" r="2" fill="white" stroke="currentColor" stroke-width="2"/>
  <circle cx="13" cy="14" r="2" fill="white" stroke="currentColor" stroke-width="2"/>
  <circle cx="10" cy="11" r="2" fill="white" stroke="currentColor" stroke-width="2"/>
  <circle cx="7" cy="14" r="2" fill="white" stroke="currentColor" stroke-width="2"/>
</svg>
                """)
        elif svg_file == "history":
            with open(svg_path, "w") as f:
                f.write("""
<svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
  <path d="M12 8V12L15 15" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
  <circle cx="12" cy="12" r="9" stroke="currentColor" stroke-width="2"/>
  <path d="M3 6H5" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
  <path d="M3 12H5" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
  <path d="M3 18H5" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
</svg>
                """)
        elif svg_file == "downloads":
            with open(svg_path, "w") as f:
                f.write("""
<svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
  <path d="M12 3V16" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
  <path d="M7 12L12 17L17 12" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
  <path d="M5 21H19" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
</svg>
                """)
    
    # Read the SVG file
    with open(svg_path, "r") as f:
        svg = f.read()
    
    return svg

def get_icon_html(icon_name, active=False):
    """
    Get HTML for an icon with proper styling.
    
    Args:
        icon_name (str): Name of the icon (without path or extension)
        active (bool): Whether the icon should be styled as active
        
    Returns:
        str: HTML for the icon
    """
    svg = load_svg(icon_name)
    svg = svg.replace('currentColor', 'var(--primary-700)' if active else 'var(--neutral-500)')
    return svg

def render_logo():
    """
    Render the premium logo.
    
    Returns:
        str: HTML for the logo
    """
    svg = load_svg("logo")
    return f"""
    <div class="premium-logo">
        {svg}
    </div>
    """

def render_navbar_item(icon_name, label, active=False):
    """
    Render a styled navbar item.
    
    Args:
        icon_name (str): Name of the icon (without path or extension)
        label (str): Label text for the navbar item
        active (bool): Whether the item is active
        
    Returns:
        str: HTML for the navbar item
    """
    icon_html = get_icon_html(icon_name, active)
    active_class = "active" if active else ""
    
    return f"""
    <div class="nav-item {active_class}">
        <div class="nav-item-icon">{icon_html}</div>
        <div class="nav-item-label">{label}</div>
    </div>
    """

def display_premium_header(title, subtitle=None):
    """
    Display a premium header with optional subtitle.
    
    Args:
        title (str): The title text
        subtitle (str): Optional subtitle text
    """
    st.markdown(f"""
    <div style="margin-bottom: 2rem;">
        <h1 style="font-family: var(--font-display); color: var(--primary-900); font-size: 2rem; margin-bottom: 0.5rem;">
            {title}
        </h1>
        {f'<p style="color: var(--neutral-600); font-size: 1.1rem; margin-top: 0;">{subtitle}</p>' if subtitle else ''}
    </div>
    """, unsafe_allow_html=True)

def display_metric_card(title, value, trend=None, trend_value=None, is_up=True):
    """
    Display a metric card with title, value, and optional trend.
    
    Args:
        title (str): Card title
        value (str): Main value to display
        trend (str): Optional trend text
        trend_value (str): Optional trend value
        is_up (bool): Whether trend is upward (True) or downward (False)
    """
    trend_color = "var(--success)" if is_up else "var(--danger)"
    trend_icon = "↑" if is_up else "↓"
    
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-title">{title}</div>
        <div class="metric-value">{value}</div>
        {f'''
        <div class="metric-trend" style="color: {trend_color};">
            {trend_icon} {trend_value} {trend}
        </div>
        ''' if trend else ''}
    </div>
    """, unsafe_allow_html=True)

def display_alert_item(icon, title, message, status="warning"):
    """
    Display an alert item.
    
    Args:
        icon (str): Icon HTML
        title (str): Alert title
        message (str): Alert message
        status (str): Status type (warning, danger, success, info)
    """
    st.markdown(f"""
    <div class="alert-item {status}">
        <div class="alert-icon">{icon}</div>
        <div class="alert-content">
            <div class="alert-title">{title}</div>
            <div class="alert-message">{message}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

def get_status_color(status):
    """
    Get the CSS color class for a status.
    
    Args:
        status (str): Status string
        
    Returns:
        str: CSS class for the status
    """
    status = status.lower()
    if status in ["healthy", "operational", "normal", "good"]:
        return "healthy"
    elif status in ["warning", "needs attention", "maintenance required", "maintenance due"]:
        return "warning"
    elif status in ["critical", "failure", "error", "emergency"]:
        return "critical"
    else:
        return "idle"

def format_status_html(status):
    """
    Format a status string with proper color coding.
    
    Args:
        status (str): Status string
        
    Returns:
        str: HTML for the formatted status
    """
    color_class = get_status_color(status)
    return f"""
    <div>
        <span class="status-dot {color_class}"></span>
        <span class="status-{color_class}">{status}</span>
    </div>
    """