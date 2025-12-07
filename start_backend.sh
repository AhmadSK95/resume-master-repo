#!/bin/bash
cd backend
source venv/bin/activate
export $(cat ../.env | grep -v '^#' | xargs)
python app.py
