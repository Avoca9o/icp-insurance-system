import os
import pytest
from unittest.mock import patch, MagicMock

from bot.utils.docx_creator import create_docx_file

@pytest.fixture
def sample_data():
    return {
        'A01': 1.5,
        'B02': 2.0,
        'C03': 1.0
    }

@pytest.fixture
def mock_diagnosis_config():
    return {
        'A01': 'Test Diagnosis 1',
        'B02': 'Test Diagnosis 2',
        'C03': 'Test Diagnosis 3'
    }

@pytest.fixture
def temp_filename(tmp_path):
    return str(tmp_path / "test_diagnosis.docx")

def test_create_docx_file_with_docx_extension(temp_filename, sample_data, mock_diagnosis_config):
    mock_doc = MagicMock()
    
    with patch('bot.utils.docx_creator.Document', return_value=mock_doc) as mock_document, \
         patch.dict('bot.utils.docx_creator.diagnosis_config', mock_diagnosis_config, clear=True):
        
        create_docx_file(temp_filename, sample_data)

        # Verify document was created
        mock_document.assert_called_once()

        # Verify heading was added
        mock_doc.add_heading.assert_called_once_with('Diagnosis Coefficients', level=0)

        # Verify paragraphs were added for each diagnosis
        assert mock_doc.add_paragraph.call_count == len(sample_data)

        # Verify file was saved
        mock_doc.save.assert_called_once_with(temp_filename)

def test_create_docx_file_without_extension(temp_filename, sample_data, mock_diagnosis_config):
    filename_without_extension = temp_filename.replace('.docx', '')
    mock_doc = MagicMock()
    
    with patch('bot.utils.docx_creator.Document', return_value=mock_doc) as mock_document, \
         patch.dict('bot.utils.docx_creator.diagnosis_config', mock_diagnosis_config, clear=True):
        
        create_docx_file(filename_without_extension, sample_data)

        # Verify file was saved with .docx extension
        mock_doc.save.assert_called_once_with(filename_without_extension + '.docx') 