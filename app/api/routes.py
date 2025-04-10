from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from fastapi.responses import JSONResponse
from app.services.extractors import (
    extract_text_from_pdf,
    extract_text_from_image,
    extract_text_from_docx
)
from app.core.config import settings
from app.utils.file_handlers import validate_file_size

router = APIRouter(prefix="/api", tags=["extraction"])

@router.post("/extract-text/", response_class=JSONResponse)
async def extract_text(file: UploadFile = File(...)):
    """
    Extract text from a PDF, image, or DOCX file.
    
    - **file**: The file to extract text from
    
    Returns:
    - **filename**: Original filename
    - **file_type**: Type of file processed
    - **extracted_text**: Extracted text content
    """
    # Validate file size
    await validate_file_size(file, settings.MAX_FILE_SIZE)
    
    file_extension = file.filename.split('.')[-1].lower()
    file_content = await file.read()
    
    try:
        if file_extension == 'pdf':
            text = await extract_text_from_pdf(file_content)
            file_type = "PDF"
        elif file_extension in ['jpg', 'jpeg', 'png', 'gif', 'bmp']:
            text = await extract_text_from_image(file_content)
            file_type = "image"
        elif file_extension == 'docx':
            text = await extract_text_from_docx(file_content)
            file_type = "DOCX"
        else:
            valid_formats = ", ".join(f.lower() for f in settings.SUPPORTED_FORMATS)
            raise HTTPException(
                status_code=400, 
                detail=f"Unsupported file type: {file_extension}. Supported formats: {valid_formats}"
            )
        
        return {
            "filename": file.filename,
            "file_type": file_type,
            "extracted_text": text
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing file: {str(e)}")