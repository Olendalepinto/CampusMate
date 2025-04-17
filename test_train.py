import os
import torch
import numpy as np
from train import all_words, tags, X_train, Y_train, FILE, model


# Test Case 1: Check Data Shape
def test_data_shape():
    assert len(X_train) == len(Y_train)
    assert X_train.shape[1] == len(all_words)


# Test Case 2: Check Unique Tags
def test_unique_tags():
    assert len(tags) > 0
    assert isinstance(tags, list)


# Test Case 3: Check Model Structure
def test_model_structure():
    assert hasattr(model, 'forward')
    input_sample = torch.from_numpy(X_train[0]).float().unsqueeze(0)
    output = model(input_sample)
    assert output.shape[1] == len(tags)


# Test Case 4: Check Model File Creation
def test_model_file_creation():
    assert os.path.exists(FILE)


# Test Case 5: Load and Verify Saved Data
def test_load_saved_data():
    data = torch.load(FILE)
    assert "model_state" in data
    assert "input_size" in data
    assert "output_size" in data
    assert "hidden_size" in data
    assert "all_words" in data
    assert "tags" in data
    assert data["output_size"] == len(tags)

