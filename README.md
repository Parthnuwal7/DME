# Data Mapping System

## Overview
This system allows users to upload multiple CSVs and automatically detects relationships between them. The detected schema is visualized as an editable graph, and users can add/remove/edit relationships manually.

## Features
- Auto-detection of relationships using `core_data_engine`
- Editable graph using PyVis + vis.js
- Save user-edited models
- Clean modular architecture

## Setup

pip install -r requirements.txt
python app.py

## To-Do
- Add datatype-aware validation
- Integrate LLM schema understanding (future)