from fastapi import UploadFile, HTTPException

async def validate_file_size(file: UploadFile, max_size: int):
    """
    Validate that the file size doesn't exceed the maximum allowed size.
    
    Args:
        file: The uploaded file
        max_size: Maximum allowed file size in bytes
    
    Raises:
        HTTPException: If the file size exceeds the maximum allowed size
    """
    # Get the file size
    file.file.seek(0, 2)  # Move to the end of the file
    file_size = file.file.tell()  # Get the position (size)
    file.file.seek(0)  # Reset file position
    
    if file_size > max_size:
        raise HTTPException(
            status_code=413,
            detail=f"File size ({file_size} bytes) exceeds the maximum allowed size ({max_size} bytes)"
        )
