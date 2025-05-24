# photoviewer
Photo viewer with metadata and analytics

# Install

```
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
```

# Run processor
```
python -m app.processors.preview --input_root /home/oleg_kudashev/data/pap_haircuts/test_data/hair_live --output_root /home/oleg_kudashev/data/pap_haircuts/test_data/hair_live/.photoviewer
```

# Run app
```
uvicorn app.main:app --reload --port 9000
```
