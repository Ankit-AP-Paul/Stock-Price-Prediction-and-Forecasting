"""
Simple image server to serve generated plots
Add this to your existing API or run separately
"""
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import os
import glob
from typing import List, Dict

# Create a simple FastAPI app for images
image_app = FastAPI(title="Stock Plot Image Server")

# Enable CORS
image_app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
image_app.mount("/static", StaticFiles(directory="static"), name="static")

@image_app.get("/images")
async def list_all_images():
    """List all available stock plot images"""
    try:
        images = []
        
        # Get all PNG files from static directory
        static_images = glob.glob("static/*.png")
        
        for img_path in static_images:
            filename = os.path.basename(img_path)
            
            # Determine image type from filename
            img_type = "unknown"
            if "_vs_" in filename or "comparison" in filename:
                img_type = "comparison"
            elif "_stock_plot" in filename:
                img_type = "stock_analysis" 
            elif "performance" in filename:
                img_type = "performance"
            
            images.append({
                "filename": filename,
                "url": f"http://localhost:8002/static/{filename}",
                "type": img_type,
                "description": filename.replace("_", " ").replace(".png", "")
            })
        
        return {
            "images": images,
            "count": len(images),
            "message": "Available stock plot images"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error listing images: {str(e)}")

@image_app.get("/images/latest")
async def get_latest_image():
    """Get the most recently created image"""
    try:
        images = glob.glob("static/*.png")
        if not images:
            raise HTTPException(status_code=404, detail="No images found")
        
        # Get most recent image
        latest_image = max(images, key=os.path.getctime)
        filename = os.path.basename(latest_image)
        
        return {
            "filename": filename,
            "url": f"http://localhost:8002/static/{filename}",
            "message": "Latest generated plot"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting latest image: {str(e)}")

@image_app.get("/images/type/{image_type}")
async def get_images_by_type(image_type: str):
    """Get images by type (comparison, stock_analysis, performance)"""
    try:
        pattern_map = {
            "comparison": "*comparison*.png",
            "stock_analysis": "*stock_plot*.png",
            "performance": "*performance*.png"
        }
        
        if image_type not in pattern_map:
            raise HTTPException(status_code=400, detail="Invalid image type")
        
        pattern = f"static/{pattern_map[image_type]}"
        images = glob.glob(pattern)
        
        if not images:
            raise HTTPException(status_code=404, detail=f"No {image_type} images found")
        
        result_images = []
        for img_path in images:
            filename = os.path.basename(img_path)
            result_images.append({
                "filename": filename,
                "url": f"http://localhost:8002/static/{filename}"
            })
        
        return {
            "type": image_type,
            "images": result_images,
            "count": len(result_images)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting {image_type} images: {str(e)}")

@image_app.get("/")
async def image_server_root():
    """Image server information"""
    return {
        "message": "Stock Plot Image Server",
        "version": "1.0.0",
        "endpoints": {
            "list_all": "GET /images - List all available images",
            "latest": "GET /images/latest - Get latest image",
            "by_type": "GET /images/type/{type} - Get images by type",
            "static_files": "/static/{filename} - Direct image access"
        },
        "available_types": ["comparison", "stock_analysis", "performance"]
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(image_app, host="0.0.0.0", port=8002)
