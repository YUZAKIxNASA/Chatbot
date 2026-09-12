@echo off
where python >nul 2>nul || (
    echo Python is required.
    exit /b 1
)

python -c "import nltk, sklearn" >nul 2>nul || (
    echo Dependencies are missing. Run: python -m pip install -r requirements.txt
    exit /b 1
)

python main.py
